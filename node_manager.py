#!/usr/bin/env python3
import argparse, ipaddress, json, os, shutil, sys, tempfile, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from adapters import singbox,hysteria2,xray,xui
from adapters.common import vmess_link,vless_link

def setup():
    for n in ("config","backups","output","logs"):
        p=ROOT/n; p.mkdir(parents=True,exist_ok=True); os.chmod(p,0o700)

def settings():
    setup(); p=ROOT/"config/settings.json"
    if not p.exists():
        shutil.copyfile(ROOT/"config/settings.example.json",p); os.chmod(p,0o600)
    return json.loads(p.read_text(encoding="utf-8"))

def public_ip(urls):
    errors=[]
    for url in urls:
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"vps-node-manager"})
            with urllib.request.urlopen(req,timeout=8) as r: return str(ipaddress.IPv4Address(r.read(128).decode().strip()))
        except Exception as e: errors.append(type(e).__name__)
    raise RuntimeError("公网 IPv4 获取失败，已中止更新："+",".join(errors))

def discover(c):
    p=c["paths"]; nodes=[]; errors=[]
    for label,fn in [("sing-box",lambda:singbox.discover(p["singbox_config"],c)),
        ("Hysteria2",lambda:hysteria2.discover(p["hysteria2_config"],c)),
        ("x-ui/Xray",lambda:xray.discover(p["xray_config"],c))]:
        try: nodes.extend(fn())
        except Exception as e: errors.append(label+": "+str(e))
    db=xui.inspect_database(p["xui_database"])
    if not db["exists"]: errors.append("x-ui database not found: "+p["xui_database"])
    return nodes,errors

def validate(nodes,c):
    expected={"hysteria2":1,"reality":1,"argo":1,"vmess_tls_ws":1,"vmess_ws":1}
    actual={k:sum(1 for n in nodes if n["kind"]==k) for k in expected}
    return ["{} expected {}, found {}".format(k,v,actual[k]) for k,v in expected.items() if actual[k]!=v]

def render(nodes,ip):
    import urllib.parse
    groups={"hysteria2":[],"reality":[],"argo":[],"vmess":[]}; safe=[]
    for old in nodes:
        n=dict(old)
        if n["kind"]!="argo": n["address"]=ip
        if n["kind"]=="hysteria2":
            link="hysteria2://{}@{}:{}?sni={}&insecure={}".format(urllib.parse.quote(n["password"],safe=""),
                n["address"],n["port"],urllib.parse.quote(n["sni"]),1 if n["insecure"] else 0)
            groups["hysteria2"].append(link); safe.append({k:v for k,v in n.items() if k not in ("password","key")})
        elif n["kind"] in ("reality","argo"):
            link=vless_link(n); groups["reality" if n["kind"]=="reality" else "argo"].append(link)
            safe.append({k:v for k,v in n.items() if k!="uuid"})
        else:
            groups["vmess"].append(vmess_link(n)); safe.append({k:v for k,v in n.items() if k!="uuid"})
    all_lines=sum(groups.values(),[])
    return {"all-nodes.txt":"\n".join(all_lines)+"\n",
        "hysteria2.txt":"\n".join(groups["hysteria2"])+"\n",
        "reality.txt":"\n".join(groups["reality"])+"\n","argo.txt":"\n".join(groups["argo"])+"\n",
        "vmess.txt":"\n".join(groups["vmess"])+"\n",
        "nodes.json":json.dumps({"public_ip":ip,"nodes":safe},ensure_ascii=False,indent=2)+"\n"}

def write(files):
    out=ROOT/"output"; backup=ROOT/"backups"; stamp=time.strftime("%Y%m%d-%H%M%S"); staged=[]
    try:
        for name,content in files.items():
            target=out/name
            if target.exists(): shutil.copy2(target,backup/(stamp+"-"+name))
            fd,tmp=tempfile.mkstemp(dir=str(out),prefix=".tmp-")
            with os.fdopen(fd,"w",encoding="utf-8") as f: f.write(content); f.flush(); os.fsync(f.fileno())
            os.chmod(tmp,0o600); staged.append((Path(tmp),target))
        for tmp,target in staged: os.replace(str(tmp),str(target)); os.chmod(target,0o600)
    except Exception:
        for tmp,_ in staged:
            try: tmp.unlink()
            except OSError: pass
        raise

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("command",choices=["audit","export","update","status"]); ap.add_argument("--dry-run",action="store_true")
    a=ap.parse_args(); c=settings(); nodes,errors=discover(c); problems=validate(nodes,c)
    print("VPS Node Manager | read-only server mode"); print("Detected:",len(nodes))
    for n in nodes: print("- {} port {}".format(n["name"],n["port"]))
    for e in errors: print("ERROR:",e)
    for e in problems: print("VALIDATION:",e)
    if errors or problems: print("ABORTED: existing output preserved"); return 2
    if a.command in ("audit","status"): return 0
    ip=public_ip(c["ip_providers"]); files=render(nodes,ip)
    print("Public IPv4:",ip); print("Files:",", ".join(files))
    if a.dry_run: print("DRY RUN: no files written"); return 0
    write(files); print("Export complete. Server config changes: 0; service restarts: 0."); return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except Exception as e: print("FATAL:",type(e).__name__,str(e),file=sys.stderr); raise SystemExit(2)

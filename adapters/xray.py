import json

def discover(path,cfg):
    with open(path,encoding="utf-8") as f: d=json.load(f)
    spec=cfg["nodes"]; out=[]
    for ib in d.get("inbounds",[]):
        port=int(ib.get("port",0) or 0)
        if port not in (spec["vmess_tls_ws_port"],spec["vmess_ws_port"]) or ib.get("protocol")!="vmess": continue
        st=ib.get("streamSettings") or {}
        if st.get("network")!="ws": continue
        tls=st.get("security")=="tls"; ws=st.get("wsSettings") or {}
        expected=spec["vmess_tls_ws_path"] if tls else spec["vmess_ws_path"]
        if ws.get("path","/")!=expected: raise ValueError("VMess WS path mismatch on port {}".format(port))
        clients=(ib.get("settings") or {}).get("clients") or []
        if not clients: raise ValueError("VMess inbound has no clients on port {}".format(port))
        for c in clients:
            if c.get("id"):
                out.append({"kind":"vmess_tls_ws" if tls else "vmess_ws",
                    "name":"VMess TLS WS" if tls else "VMess WS","address":"","port":port,
                    "uuid":c["id"],"alterId":int(c.get("alterId",0)),"security":c.get("security","auto"),
                    "tls":tls,"path":ws.get("path","/"),"host":(ws.get("headers") or {}).get("Host",""),
                    "sni":spec["vmess_tls_sni"] if tls else ""})
    return out

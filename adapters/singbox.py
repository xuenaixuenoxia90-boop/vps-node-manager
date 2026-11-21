import base64, json, os, subprocess, tempfile

def public_key(private):
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    raw=base64.urlsafe_b64decode(private+"="*(-len(private)%4))
    pub=X25519PrivateKey.from_private_bytes(raw).public_key()
    return base64.urlsafe_b64encode(pub.public_bytes(Encoding.Raw,PublicFormat.Raw)).decode().rstrip("=")

def discover(path, cfg):
    with open(path,encoding="utf-8") as f: data=json.load(f)
    out=[]; spec=cfg["nodes"]
    for ib in data.get("inbounds",[]):
        port=int(ib.get("listen_port",0) or 0); proto=ib.get("type",ib.get("protocol",""))
        users=ib.get("users") or ib.get("settings",{}).get("clients") or []
        if proto!="vless": continue
        tls=ib.get("tls") or {}; reality=tls.get("reality") or {}
        if port==spec["reality_port"]:
            if not reality.get("private_key"): raise ValueError("Reality private_key missing")
            ids=reality.get("short_id") or reality.get("short_ids") or []
            if isinstance(ids,str): ids=[ids]
            pbk=public_key(reality["private_key"])
            for u in users:
                uid=u.get("uuid") or u.get("id")
                if uid: out.append({"kind":"reality","name":"VLESS Reality","address":"","port":port,
                    "uuid":uid,"flow":u.get("flow",""),"security":"reality","sni":spec["reality_sni"],
                    "pbk":pbk,"sid":ids[0] if ids else ""})
        elif port==spec["argo_port"]:
            tr=ib.get("transport") or {}
            if tr.get("type")!="ws": continue
            for u in users:
                uid=u.get("uuid") or u.get("id")
                if uid: out.append({"kind":"argo","name":"VLESS Argo WS","address":tls.get("server_name",""),
                    "port":port,"uuid":uid,"security":"tls","type":"ws","path":tr.get("path","/"),
                    "host":(tr.get("headers") or {}).get("Host","")})
    return out

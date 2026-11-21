import yaml

def discover(path,cfg):
    with open(path,encoding="utf-8") as f: d=yaml.safe_load(f) or {}
    auth=d.get("auth") or {}; password=auth.get("password")
    if not password: raise ValueError("Hysteria2 auth.password not found")
    listen=str(d.get("listen","")); port=cfg["nodes"]["hysteria2_port"]
    if ":" in listen:
        try: port=int(listen.rsplit(":",1)[1])
        except ValueError: pass
    tls=d.get("tls") or {}
    pref=cfg.get("hysteria2",{})
    return [{"kind":"hysteria2","name":"Hysteria2","address":"","port":port,"password":password,
        "cert":tls.get("cert"),"key":tls.get("key"),"quic":d.get("quic"),"masquerade":d.get("masquerade"),
        "sni":pref.get("client_sni","www.bing.com"),"insecure":bool(pref.get("insecure",True))}]

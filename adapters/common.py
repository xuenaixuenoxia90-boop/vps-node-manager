import base64, json, urllib.parse

def vmess_link(n):
    p={"v":"2","ps":n["name"],"add":n["address"],"port":str(n["port"]),"id":n["uuid"],
       "aid":str(n.get("alterId",0)),"scy":n.get("security","auto"),"net":"ws","type":"none",
       "host":n.get("host",""),"path":n.get("path","/"),"tls":"tls" if n.get("tls") else "",
       "sni":n.get("sni","")}
    return "vmess://"+base64.b64encode(json.dumps(p,separators=(",",":")).encode()).decode()

def vless_link(n):
    q={"encryption":"none","security":n.get("security","none")}
    for k in ("flow","sni","fp","pbk","sid","type","path","host"):
        if n.get(k): q[k]=n[k]
    return "vless://{}@{}:{}?{}#{}".format(urllib.parse.quote(n["uuid"]),n["address"],n["port"],
        urllib.parse.urlencode(q,quote_via=urllib.parse.quote),urllib.parse.quote(n["name"]))

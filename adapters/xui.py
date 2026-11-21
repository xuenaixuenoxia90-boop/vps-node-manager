import os, sqlite3

def inspect_database(path):
    if not os.path.isfile(path): return {"exists":False,"tables":[]}
    conn=sqlite3.connect("file:{}?mode=ro".format(path),uri=True)
    try: return {"exists":True,"tables":[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]}
    finally: conn.close()

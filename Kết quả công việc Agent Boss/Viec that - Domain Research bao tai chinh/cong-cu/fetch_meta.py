import re,sys,json,subprocess,html,time,os
from concurrent.futures import ThreadPoolExecutor
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
urls=json.load(open(sys.argv[1])); out=sys.argv[2]
done=set()
if os.path.exists(out):
    for l in open(out): done.add(json.loads(l)['url'])
def meta(h,key):
    m=re.search(r'<meta[^>]+(?:property|name)="%s"[^>]*content="([^"]*)"'%re.escape(key),h) or re.search(r'<meta[^>]+content="([^"]*)"[^>]*(?:property|name)="%s"'%re.escape(key),h)
    return html.unescape(m.group(1)).strip() if m else ""
def get(u):
    for i in range(4):
        r=subprocess.run(["curl","-sS","-L","-A",UA,"--max-time","40",u],capture_output=True)
        if r.returncode==0 and len(r.stdout)>2000: return r.stdout.decode('utf-8','replace')
        time.sleep(2**i)
    return ""
def work(p):
    site,u=p
    h=get(u)
    bc=""
    m=re.search(r'(breadcrumb|cat-name|bread-crumb|post-cate|article__cate|fon23|catename)[^>]*>(.{0,1500})',h,re.S|re.I)
    if m: bc=" | ".join(x.strip() for x in re.findall(r'>([^<>]{2,60})</a>',m.group(2))[:4])
    return dict(site=site,url=u,title=meta(h,"og:title"),sapo=meta(h,"og:description") or meta(h,"description"),
      section=meta(h,"article:section"),pub=meta(h,"article:published_time"),tags=meta(h,"keywords") or meta(h,"article:tag"),bc=html.unescape(bc),ok=bool(h))
todo=[p for p in urls if p[1] not in done]
with open(out,"a") as f, ThreadPoolExecutor(8) as ex:
    for i,r in enumerate(ex.map(work,todo)):
        f.write(json.dumps(r,ensure_ascii=False)+"\n")
        if i%500==0: f.flush(); print(i,flush=True)
print("done")

import re,sys,subprocess,html,json,time
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
out=sys.argv[1]
def get(u):
    for i in range(4):
        r=subprocess.run(["curl","-sS","-A",UA,"--max-time","40",u],capture_output=True)
        if r.returncode==0 and r.stdout: return r.stdout.decode('utf-8','replace')
        time.sleep(2**i)
    return ""
cats="tai-chinh ngan-hang-bao-hiem chung-khoan bat-dong-san chinh-sach-moi doanh-nghiep doanh-nghiep/san-pham-tieu-dung phap-luat kinh-te goc-chuyen-gia-nha-quan-ly chuyen-de-nghien-cuu xa-hoi thoi-su".split()
res={}
def parse(h,cat):
    oldest=None
    for m in re.finditer(r'href="(https://tapchikinhtetaichinh.vn/[a-z0-9-]+-\d+\.html)"',h):
        res.setdefault(m.group(1),set()).add(cat)
    ds=[tuple(map(int,d.split('/'))) for d in re.findall(r'(\d{2}/\d{2}/20\d{2})',h)]
    ds=[(y,mo,d) for d,mo,y in ds]
    return min(ds) if ds else None
for c in cats:
    h=get("https://tapchikinhtetaichinh.vn/"+c)
    parse(h,c)
    m=re.search(r'__MB_NEXT_URL"\s*value="([^"]+)"',h)
    if not m: print(c,"no next");continue
    base=html.unescape(m.group(1)); off=0; pages=0
    while True:
        off+=15; pages+=1
        hh=get(re.sub(r'BRSR=\d+','BRSR=%d'%off,base))
        o=parse(hh,c)
        if not o or o<(2026,7,8) or pages>200: break
    print(c,pages,o,file=sys.stderr)
json.dump({k:sorted(v) for k,v in res.items()},open(out,"w"),ensure_ascii=False)
print(len(res))

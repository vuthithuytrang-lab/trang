import json,sys,re,os
sheet=json.load(open(sys.argv[1]))["values"]
D=os.path.dirname(os.path.abspath("ghi_sheet.py"))
def norm(u): return re.sub(r'[?#].*$','',u.strip()).rstrip('/').lower()
url2so={}
for f in os.listdir("nguon"):
    if f.endswith(".txt"):
        for line in open("nguon/"+f,encoding="utf-8",errors="ignore"):
            if line.startswith("URL:"): url2so[norm(line[4:])]=int(f[:-4]); break
start={}
for i,r in enumerate(sheet):
    b=(r+["",""])[1]
    if b and norm(b) in url2so: start[url2so[norm(b)]]=i+1
lab={"wix":"Wix","gg":"GG Group"}
done=set(map(tuple,json.load(open("da-ghi-sheet.json"))))
recs=[x for x in map(json.loads,open("da-dang.jsonl")) if x.get("ok") and x["nen"] in lab and x["luc"]>="2026-11-04"]
from datetime import datetime,timezone,timedelta
VN=timezone(timedelta(hours=7))
for x in recs:
    k=(x["so"],x["nen"])
    if list(k) in [list(d) for d in done]: continue
    s=start.get(x["so"])
    row=None
    if s:
        for j in range(s,s+5):
            r=(sheet[j-1]+["","",""]) if j-1<len(sheet) else ["","","",""]
            if r[2]==lab[x["nen"]]: row=j;break
    t=datetime.fromisoformat(x["luc"]).astimezone(VN).strftime("%H:%M %d/%m/%Y")
    print(json.dumps({"so":x["so"],"nen":x["nen"],"row":row,"link":x["link"],"time":t}))

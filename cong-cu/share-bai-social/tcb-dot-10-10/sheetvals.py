import json,sys,datetime as D
S={s['row']:s for s in json.load(open('schedule.json'))}
P={}
for j in map(json.loads,open('posted.jsonl')):
  if 'url' in j: P[(j['platform'],j['row'])]=j
rows=[int(r) for r in sys.argv[1:]]
for r in rows:
  s=S[r]; out=[]
  for p,name in (('blogger','Blogger - Trang'),('wp','WordPress - Trang')):
    j=P.get((p,r))
    if not j: out.append(None); continue
    t=D.datetime.fromisoformat(j['when']).astimezone(D.timezone(D.timedelta(hours=7)))
    url=j['url']
    if p=='wp':
      slug=json.load(open(f'bai/{r}/meta.json'))['slug']
      url=f"https://techcombankvietnam.wordpress.com/{t:%Y/%m/%d}/{slug}/"
    out.append([name,url,f"{t.day}/{t.month}/{t.year}"])
  print(r, s['blogger_row'], json.dumps(out,ensure_ascii=False))

import json,subprocess,sys,os,time,datetime as D
rows=set(int(r) for r in sys.argv[1:])
S=json.load(open('schedule.json'))
drafts=json.load(open('drafts.json')) if os.path.exists('drafts.json') else {}
done={(j['platform'],j['row']) for j in map(json.loads,open('posted.jsonl')) if 'url' in j}
tz=D.timezone(D.timedelta(hours=7))
for s in S:
  if s['row'] not in rows: continue
  for p in ('blogger','wp'):
    if (p,s['row']) in done: continue
    now=D.datetime.now(tz); t=D.datetime.fromisoformat(s[p])
    if t<now+D.timedelta(minutes=3): t=now+D.timedelta(minutes=5)
    args=['python3','post.py',p,str(s['row']),t.isoformat()]
    if p=='blogger' and str(s['row']) in drafts: args.append(drafts[str(s['row'])])
    out=subprocess.run(args,capture_output=True,text=True)
    line=(out.stdout or out.stderr).strip().splitlines()[-1]
    print(line); open('posted.jsonl','a').write(line+'\n')
    if p=='blogger': time.sleep(15)

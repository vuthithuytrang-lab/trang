import json,subprocess,time,datetime as D
tz=D.timezone(D.timedelta(hours=7))
S=json.load(open('schedule.json'))
def done():
  return {j['row'] for j in map(json.loads,open('posted.jsonl')) if j.get('platform')=='blogger' and 'url' in j}
for s in S:
  if s['row'] in done(): continue
  while True:
    now=D.datetime.now(tz); t=D.datetime.fromisoformat(s['blogger'])
    if t<now+D.timedelta(minutes=3): t=now+D.timedelta(minutes=5)
    out=subprocess.run(['python3','post.py','blogger',str(s['row']),t.isoformat()],capture_output=True,text=True)
    line=(out.stdout or out.stderr).strip().splitlines()[-1]
    open('posted.jsonl','a').write(line+'\n'); print(now.strftime('%H:%M'),line,flush=True)
    if '"url"' in line: time.sleep(1200); break
    time.sleep(1800)

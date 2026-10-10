import json,random,datetime as D,sys
sys.argv=['x','wp','0','now']
exec(open('post.py').read().split('\ndef main')[0])
tz=D.timezone(D.timedelta(hours=7)); random.seed(23)
tok=json.load(open(os.path.join(SKILLS,'share-bai-wp/wp-accounts.local.json')))[WP_SITE]['access_token']
posts=sorted([j for j in map(json.loads,open('posted.jsonl')) if j.get('platform')=='wp' and 'url' in j],key=lambda j:j['row'])
now=D.datetime.now(tz)
todo=[j for j in posts if D.datetime.fromisoformat(j['when'])>now+D.timedelta(minutes=5)]
start=now+D.timedelta(minutes=25); end=D.datetime(2026,10,11,19,0,tzinfo=tz)
gap=(end-start)/(len(todo)-1)
for i,j in enumerate(todo):
  t=(start+gap*i+D.timedelta(minutes=random.randint(-8,8) if 0<i<len(todo)-1 else 0)).replace(second=0,microsecond=0)
  code,r=curl([f'https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}/posts/{j["id"]}'],{'date':t.isoformat(),'status':'future'},tok)
  rec=dict(platform='wp',row=j['row'],id=j['id'],url=j['url'],status=r.get('status'),when=t.isoformat()) if code==200 else dict(error='resched',row=j['row'],code=code,detail=str(r)[:200])
  print(json.dumps(rec,ensure_ascii=False)); open('posted.jsonl','a').write(json.dumps(rec,ensure_ascii=False)+'\n')
print('gap',gap,'n',len(todo))

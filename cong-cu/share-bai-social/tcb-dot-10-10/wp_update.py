import json,sys,datetime as D
rows=[int(x) for x in sys.argv[1:]]
sys.argv=['x','wp','0','now']
exec(open('post.py').read().split('\ndef main')[0])
tok=json.load(open(os.path.join(SKILLS,'share-bai-wp/wp-accounts.local.json')))[WP_SITE]['access_token']
ids={}
for j in map(json.loads,open('posted.jsonl')):
  if j.get('platform')=='wp' and 'id' in j: ids[j['row']]=j['id']
for r in rows:
  html=to_gutenberg(open(f'bai/{r}/wp.html').read())
  code,res=curl([f'https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}/posts/{ids[r]}?fields=ID,status,URL'],{'content':html},tok)
  print(r,code,res)

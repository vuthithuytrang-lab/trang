import json,os,subprocess,tempfile,time,datetime as D,sys
sys.argv=['x','wp','0','now']
exec(open('post.py').read().split('\ndef main')[0])
tok=json.load(open(os.path.join(SKILLS,'share-bai-wp/wp-accounts.local.json')))[WP_SITE]['access_token']
posts={}
for j in map(json.loads,open('posted.jsonl')):
  if j.get('platform')=='wp' and 'id' in j and 'url' in j: posts[j['row']]=j
order=sorted(posts.values(),key=lambda j:j['when'])
done=set()
if os.path.exists('thumbs_done.jsonl'): done={json.loads(l)['row'] for l in open('thumbs_done.jsonl') if '"ok"' in l}
kw={x['row']:x['kw'] for x in json.load(open('plan.json'))}
for j in order:
  r=j['row']
  if r in done: continue
  h=tempfile.NamedTemporaryFile('w',delete=False); h.write('Authorization: Bearer '+tok+'\n'); h.close()
  out=subprocess.run(['curl','-s','-m','120','-H','@'+h.name,'-F',f'media[]=@thumb/{r}.png','-F',f'attrs[0][alt]={kw[r]}','-F',f'attrs[0][title]={kw[r]}',
     f'https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}/media/new'],capture_output=True,text=True).stdout
  os.unlink(h.name)
  try: mid=json.loads(out)['media'][0]['ID']
  except Exception: rec={'row':r,'err':'upload','detail':out[:200]}; open('thumbs_done.jsonl','a').write(json.dumps(rec)+'\n'); print(rec,flush=True); time.sleep(900); continue
  code,res=curl([f'https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}/posts/{j["id"]}?fields=ID,status,featured_image'],{'featured_image':mid},tok)
  rec={'row':r,'post':j['id'],'media':mid,'code':code,'status':res.get('status'),'ok':code==200 and bool(res.get('featured_image')),'at':D.datetime.now().isoformat()}
  open('thumbs_done.jsonl','a').write(json.dumps(rec)+'\n'); print(rec,flush=True)
  time.sleep(900)

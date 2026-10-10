import json,os,subprocess,sys,hashlib,datetime as D
S=os.path.dirname(os.path.abspath(__file__)); os.chdir(S)
SK='/home/user/trang/.claude/skills/share-bai-webflow'
acc=json.load(open(SK+'/webflow-accounts.local.json'))['ngahangtechcombankvn.webflow.io']
T,SID,CID=acc['token'],acc['site_id'],acc['collection_id']
tz=D.timezone(D.timedelta(hours=7)); now=D.datetime.now(tz)
recs=[json.loads(l) for l in open('posted.jsonl')]
pub={j['row'] for j in recs if j.get('platform')=='webflow' and j.get('status')=='published'}
drafts={j['row']:j for j in recs if j.get('platform')=='webflow' and j.get('status')=='draft'}
sched=json.load(open('wf_schedule.json'))
def sh(*a): return subprocess.run(list(a),capture_output=True,text=True,cwd=SK).stdout
def log(rec): open('posted.jsonl','a').write(json.dumps(rec,ensure_ascii=False)+'\n'); print(json.dumps(rec,ensure_ascii=False))
did=None
for s in sched:
  r=s['row']
  if r in pub: continue
  if r in drafts and D.datetime.fromisoformat(s['when'])<=now+D.timedelta(minutes=2):
    j=drafts[r]; hf=S+'/wfh'; open(hf,'w').write('Authorization: Bearer '+T+'\n')
    subprocess.run(['curl','-s','-X','PATCH','-H','@'+hf,'-H','Content-Type: application/json','--data','{"isDraft":false}',f'https://api.webflow.com/v2/collections/{CID}/items/{j["id"]}'],capture_output=True); os.unlink(hf)
    sh('bash','scripts/webflow-http.sh','publish-item',CID,T,j['id'],S+'/wf_pub.json')
    p=json.load(open('wf_pub.json'))
    if j['id'] in p.get('publishedItemIds',[]): log(dict(j,status='published',when=now.isoformat()))
    else: print('PUBLISH_ERR',str(p)[:300])
    did='publish'; break
  if r not in drafts and D.datetime.fromisoformat(s['prep'])<=now+D.timedelta(minutes=2):
    d=f'bai/{r}'; m=json.load(open(d+'/meta.json'))
    if os.path.exists(d+'/webflow.html'): body,title,slug=d+'/webflow.html',m['title_webflow'],m['slug_webflow']
    elif r>=738: body,title,slug=d+'/blogger.html',m['title_blogger'],m['slug']
    else: print('NO_CONTENT',r); did='wait'; break
    env=dict(os.environ,NODE_PATH=subprocess.run(['npm','root','-g'],capture_output=True,text=True).stdout.strip())
    subprocess.run(['node','thumbs_wf2.js',str(r)],env=env,check=True)
    img=f'thumb_wf/{r}.png'; md5=hashlib.md5(open(img,'rb').read()).hexdigest()
    sh('bash','scripts/webflow-http.sh','create-asset',SID,T,f'{slug}.png',md5,S+'/wf_asset.json')
    sh('bash','scripts/webflow-http.sh','upload-asset',json.load(open('wf_asset.json'))['uploadUrl'],S+'/wf_asset.json',S+'/'+img,S+'/wf_up.json')
    hurl=sh('node','scripts/webflow-json.js','show-asset-hosted-url',S+'/wf_asset.json').strip()
    sh('node','scripts/webflow-json.js','build-item-payload',S+'/'+body,title,slug,'post-body','thumbnail',hurl,S+'/wf_payload.json')
    pl=json.load(open('wf_payload.json')); pl['isDraft']=True; json.dump(pl,open('wf_payload.json','w'),ensure_ascii=False)
    sh('bash','scripts/webflow-http.sh','create-item',CID,T,S+'/wf_payload.json',S+'/wf_create.json')
    it=json.load(open('wf_create.json'))
    if 'id' not in it: print('CREATE_ERR',str(it)[:300]); did='err'; break
    log(dict(platform='webflow',row=r,id=it['id'],url=f"https://ngahangtechcombankvn.webflow.io/blog-posts/{it['fieldData']['slug']}",status='draft',when=s['when'],prepared=now.isoformat()))
    did='prep'; break
  break
# next wake
recs=[json.loads(l) for l in open('posted.jsonl')]
pub={j['row'] for j in recs if j.get('platform')=='webflow' and j.get('status')=='published'}
drafts={j['row'] for j in recs if j.get('platform')=='webflow' and j.get('status')=='draft'}-pub
nxt=None
for s in sched:
  if s['row'] in pub: continue
  nxt=s['when'] if s['row'] in drafts else s['prep']; break
print('DID',did,'NEXT',nxt)

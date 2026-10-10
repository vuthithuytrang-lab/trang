import json,os,subprocess,sys,datetime as D
S=os.path.dirname(os.path.abspath(__file__)); os.chdir(S); sys.path.insert(0,S)
from wixlib import *
tz=D.timezone(D.timedelta(hours=7)); now=D.datetime.now(tz)
recs=[json.loads(l) for l in open('posted.jsonl')]
pub={j['row'] for j in recs if j.get('platform')=='wix' and j.get('status')=='published'}
drafts={j['row']:j for j in recs if j.get('platform')=='wix' and j.get('status')=='draft'}
sched=json.load(open('wix_schedule.json'))
def log(rec): open('posted.jsonl','a').write(json.dumps(rec,ensure_ascii=False)+'\n'); print(json.dumps(rec,ensure_ascii=False))
did=None
for s in sched:
  r=s['row']
  if r in pub: continue
  if r in drafts and D.datetime.fromisoformat(s['when'])<=now+D.timedelta(minutes=2):
    j=drafts[r]; c,res=api('POST',f"https://www.wixapis.com/blog/v3/draft-posts/{j['id']}/publish")
    if c==200:
      c2,p=api('GET',f"https://www.wixapis.com/blog/v3/posts/{res.get('postId',j['id'])}?fieldsets=URL")
      u=p.get('post',{}).get('url',{}); url=(u.get('base','')+u.get('path','')) if u else ''
      log(dict(j,status='published',url=url or j.get('url',''),when=now.isoformat()))
    else: print('PUBLISH_ERR',c,str(res)[:300])
    did='publish'; break
  if r not in drafts and D.datetime.fromisoformat(s['prep'])<=now+D.timedelta(minutes=2):
    d=f'bai/{r}'; m=json.load(open(d+'/meta.json'))
    if not os.path.exists(d+'/wix.html') or 'title_wix' not in m: print('NO_CONTENT',r); did='wait'; break
    env=dict(os.environ,NODE_PATH=subprocess.run(['npm','root','-g'],capture_output=True,text=True).stdout.strip())
    subprocess.run(['node','thumbs_wix.js',str(r)],env=env,check=True)
    f,err=upload_image(f'thumb_wix/{r}.png',m['slug_wix']+'.png')
    if err: print('UPLOAD_ERR',err); did='err'; break
    nodes=to_ricos(open(d+'/wix.html').read())
    c,res=api('POST','https://www.wixapis.com/blog/v3/draft-posts?fieldsets=URL',{'draftPost':{'title':m['title_wix'],'memberId':MEMBER,'richContent':{'nodes':nodes},'media':{'wixMedia':{'image':{'id':f['id']}},'displayed':True,'custom':True}},'publish':False})
    if c!=200: print('CREATE_ERR',c,str(res)[:300]); did='err'; break
    pid=res['draftPost']['id']
    api('PATCH',f'https://www.wixapis.com/blog/v3/draft-posts/{pid}',{'draftPost':{'id':pid,'seoSlug':m['slug_wix']}})
    log(dict(platform='wix',row=r,id=pid,url=f"https://trangjena3.wixsite.com/techcombankvietnam/post/{m['slug_wix']}",status='draft',when=s['when'],prepared=now.isoformat()))
    did='prep'; break
  break
recs=[json.loads(l) for l in open('posted.jsonl')]
pub={j['row'] for j in recs if j.get('platform')=='wix' and j.get('status')=='published'}
dr={j['row'] for j in recs if j.get('platform')=='wix' and j.get('status')=='draft'}-pub
nxt=next(((s['when'] if s['row'] in dr else s['prep']) for s in sched if s['row'] not in pub),None)
print('DID',did,'NEXT',nxt)

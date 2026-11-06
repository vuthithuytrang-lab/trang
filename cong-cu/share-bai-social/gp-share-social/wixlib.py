import json,os,re,subprocess,tempfile,html as H,uuid
SK='/home/user/trang/.claude/skills/share-bai-wix'
acc=json.load(open(SK+'/wix-accounts.local.json'))['trangjena3.wixsite.com/techcombankvietnam']
KEY,SITE,MEMBER=acc['api_key'],acc['site_id'],acc['member_id']
def api(method,url,data=None,raw=None,ctype='application/json',auth=True):
    hf=tempfile.NamedTemporaryFile('w',delete=False)
    if auth: hf.write(f'Authorization: {KEY}\nwix-site-id: {SITE}\n')
    hf.close()
    cmd=['curl','-s','-m','120','-X',method,'-H','@'+hf.name,'-w','\n%{http_code}']
    tmp=None
    if data is not None:
        tmp=tempfile.NamedTemporaryFile('w',delete=False,suffix='.json'); json.dump(data,tmp,ensure_ascii=False); tmp.close()
        cmd+=['-H','Content-Type: application/json','--data-binary','@'+tmp.name]
    if raw: cmd+=['-H','Content-Type: '+ctype,'--data-binary','@'+raw]
    out=subprocess.run(cmd+[url],capture_output=True,text=True).stdout
    os.unlink(hf.name); tmp and os.unlink(tmp.name)
    body,_,code=out.rpartition('\n')
    try: return int(code),json.loads(body) if body.strip() else {}
    except: return int(code or 0),{'raw':body[:300]}
def inline(s):
    """parse inline html with <strong>, <a href> -> list of text nodes"""
    nodes=[]; pos=0; bold=False; link=None
    for m in re.finditer(r'<(/?)(strong|b|a)([^>]*)>',s):
        t=H.unescape(s[pos:m.start()])
        if t: nodes.append((t,bold,link))
        close,tag,attrs=m.group(1)=='/',m.group(2),m.group(3)
        if tag in('strong','b'): bold=not close
        else: link=None if close else re.search(r'href="([^"]+)"',attrs).group(1)
        pos=m.end()
    t=H.unescape(s[pos:]); t and nodes.append((t,bold,link))
    out=[]
    for t,b,l in nodes:
        dec=[]
        if b: dec.append({'type':'BOLD','fontWeightValue':700})
        if l: dec.append({'type':'LINK','linkData':{'link':{'url':l,'target':'BLANK','rel':{'noreferrer':True}}}})
        out.append({'type':'TEXT','id':'','nodes':[],'textData':{'text':t,'decorations':dec}})
    return out
def nid(): return uuid.uuid4().hex[:8]
def para(inner): return {'type':'PARAGRAPH','id':nid(),'nodes':inline(inner),'paragraphData':{}}
def to_ricos(src):
    nodes=[]; cur=None
    for line in [l.strip() for l in src.splitlines() if l.strip()]:
        m=re.match(r'<(p|h2|h3|li)>(.*)</\1>$',line)
        if line in('<ul>','<ol>'):
            cur={'type':'BULLETED_LIST' if line=='<ul>' else 'ORDERED_LIST','id':nid(),'nodes':[],
                 ('bulletedListData' if line=='<ul>' else 'orderedListData'):{'indentation':0}}
        elif line in('</ul>','</ol>'): nodes.append(cur); cur=None
        elif m and m.group(1)=='li': cur['nodes'].append({'type':'LIST_ITEM','id':nid(),'nodes':[para(m.group(2))]})
        elif m and m.group(1)=='p': nodes.append(para(m.group(2)))
        elif m: nodes.append({'type':'HEADING','id':nid(),'nodes':inline(m.group(2)),'headingData':{'level':int(m.group(1)[1])}})
        else: nodes.append(para(re.sub('<[^>]+>','',line)))
    return nodes
def upload_image(path,name):
    c,r=api('POST','https://www.wixapis.com/site-media/v1/files/generate-upload-url',{'mimeType':'image/png','fileName':name})
    if c!=200: return None,('gen',c,r)
    import urllib.parse
    url=r['uploadUrl']+('&' if '?' in r['uploadUrl'] else '?')+'filename='+urllib.parse.quote(name)
    c,r2=api('PUT',url,raw=path,ctype='image/png',auth=False)
    if c!=200: return None,('put',c,r2)
    return r2.get('file',r2),None

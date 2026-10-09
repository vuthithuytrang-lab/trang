"""Build + validate Docs HTML from a draft JSON.
usage: python3 -I build.py <scratch_dir> <slug>   -> writes out/<slug>__<Platform>.html, prints report, exit 1 on errors
"""
import json, re, sys, os, unicodedata, html
D=sys.argv[1]; slug=sys.argv[2]
plan={a['slug']:a for a in json.load(open(f'{D}/plan.json'))}[slug]
art=json.load(open(f'{D}/art/{slug}.json'))
dr=json.load(open(f'{D}/drafts/{slug}.json'))
DATE='09/10'
LONG={'Webflow','Wix','Weebly','WordPress'}
def tag(s):
    s=s.lower().replace('đ','d'); s=unicodedata.normalize('NFD',s)
    s=''.join(c for c in s if unicodedata.category(c)!='Mn'); return '#'+re.sub(r'[^a-z0-9]','',s)
def norm(s): return re.sub(r'\s+',' ',s.lower()).strip()
src_text=' '.join([art['title'],art['sapo']]+[s['h2']+' '+' '.join(s['content']) for s in art['sections']]+[i['alt'] for i in art['images']])
src_nums=set(re.findall(r'\d+(?:[.,]\d+)*',src_text))
def words(s): return re.findall(r'\w+',s.lower())
def ngrams(s,n=12):
    w=words(s); return {' '.join(w[i:i+n]) for i in range(len(w)-n+1)}
src_ng=ngrams(src_text)
BANNED=['tốt nhất','chắc chắn','hàng đầu','số 1','số một','đảm bảo 100','tuyệt đối','cam kết lợi nhuận','lợi nhuận chắc']
kw=plan['kw']; kws=dr['kw_phu']; assert len(kws)==2
hashtags=[tag(kw),tag(kws[0]),tag(kws[1]),'#techcombank #techcombankvn']
url=plan['url']
errs=[]; warns=[]; report=[]
def chk_common(p,txt,title):
    if norm(title)==norm(art['title']): errs.append(f'{p}: title trùng title gốc')
    if norm(kw) not in norm(title): errs.append(f'{p}: title thiếu keyword chính')
    for b in BANNED:
        if b in txt.lower() and b not in norm(src_text) : errs.append(f'{p}: có từ cấm "{b}"')
    for n in set(re.findall(r'\d+(?:[.,]\d+)*',txt)):
        if n not in src_nums and n not in ('1','2','3','4','5','6','7','8','9','10') and n not in url and not re.fullmatch(r'0?\d|1\d',n):
            errs.append(f'{p}: số "{n}" không có trong bài gốc')
    kwn=' '.join(words(kw))
    strip=lambda x: ' '.join(words(x)).replace(kwn,' kwtok ')
    cp=[g for g in ngrams(strip(txt))&ngrams(strip(src_text)) if 'kwtok' not in g]
    if cp: errs.append(f'{p}: {len(cp)} cụm 12 từ chép nguyên văn bài gốc: '+' / '.join(sorted(cp)[:6]))
def img(i):
    return art['images'][i]['src']
def caption_ok(p,c):
    if not (norm(kw) in norm(c) or any(norm(k) in norm(c) for k in kws)): errs.append(f'{p}: chú thích ảnh thiếu keyword chính/phụ')
os.makedirs(f'{D}/out',exist_ok=True)
E=html.escape
H2S=[s['h2'] for s in art['sections']]
built={}
for row in plan['platforms']:
    p=row['p']; d=dr['docs'][p]
    fname=f"{p} - {kw} - {DATE}"
    if not art['images']: errs.append(f'{p}: bài gốc không có ảnh')
    if p in LONG:
        t=d['title']; m=d['meta']
        if not 50<=len(t)<=65: errs.append(f'{p}: title {len(t)} ký tự (cần 50–65)')
        if not 140<=len(m)<=160: errs.append(f'{p}: meta {len(m)} ký tự (cần 140–160)')
        if [s['h2'] for s in d['sections']]!=H2S: errs.append(f'{p}: danh sách H2 không khớp bài gốc')
        ii=d['image']['index']; after=d['image']['after_section']
        caption_ok(p,d['image']['caption'])
        parts=[f"<p><b>Tiêu đề:</b> {E(t)}</p>",f"<p><b>Meta:</b> {E(m)} ({len(m)} ký tự)</p>","<p><b>Nội dung bài viết:</b></p>",f"<p>{E(d['sapo'])}</p>"]
        body=[d['sapo']]
        for k,s in enumerate(d['sections']):
            parts.append(f"<h2>{E(s['h2'])}</h2>"); body.append(s['h2'])
            for para in s['paras']:
                if para.startswith('- '): parts.append(f"<ul><li>{E(para[2:])}</li></ul>")
                else: parts.append(f"<p>{E(para)}</p>")
                body.append(para)
            if k==after:
                parts.append(f'<p style="text-align:center"><img src="{img(ii)}" width="600"></p>')
                parts.append(f'<p style="text-align:center"><i>{E(d["image"]["caption"])}</i></p>')
        parts+= [f"<p>{E(d['conclusion'])}</p>",f"<p>{E(d['cta'])}</p>",f"<p>{url}</p>","<p></p>"]+[f"<p>{h}</p>" for h in hashtags]
        body+=[d['conclusion'],d['cta']]
        txt='\n'.join(body); wc=len(words(txt))
        lo=min(600,150*len(H2S)+150)
        if not lo<=wc<=1100: errs.append(f'{p}: {wc} chữ (cần ~{lo}–1.000)')
        chk_common(p,'\n'.join(b for b in body if b not in H2S)+' '+t+' '+m+' '+d['image']['caption'],t)
        report.append(f'{p}: title {len(t)}, meta {len(m)}, {wc} chữ, ảnh #{ii} sau H2 {after+1}')
    elif p=='Mastodon':
        post='\n'.join([d['open'],d['points'],d['close_cta'],url]+hashtags)
        n=len(post)
        if n>=500: errs.append(f'Mastodon: {n} ký tự (cần <500)')
        caption_ok(p,d['caption'])
        chk_common(p,post+' '+d['caption'],d['open'])
        parts=[f"<p>{E(d['open'])}</p>"]+[f"<p>{E(x)}</p>" for x in d['points'].split('\n')]+[f"<p>{E(d['close_cta'])}</p>",f"<p>{url}</p>"]+[f"<p>{h}</p>" for h in hashtags]+[
               f'<p style="text-align:center"><img src="{img(d["image_index"])}" width="600"></p>',f'<p style="text-align:center"><i>{E(d["caption"])}</i></p>',
               f"<p><b>Tổng số ký tự bài đăng (gồm link và hashtag, không tính chú thích ảnh): {n}/500</b></p>"]
        report.append(f'Mastodon: {n} ký tự, ảnh #{d["image_index"]}')
    elif p=='Pinterest':
        t=d['title']; desc='\n'.join([d['desc'],url]+hashtags); n=len(desc)
        if len(t)>100: errs.append(f'Pinterest: title {len(t)} ký tự (>100)')
        if n>500: errs.append(f'Pinterest: mô tả {n} ký tự (>500)')
        caption_ok(p,d['caption']); chk_common(p,desc+' '+t+' '+d['caption'],t)
        parts=[f"<p><b>Tiêu đề pin:</b> {E(t)} ({len(t)} ký tự)</p>",f'<p style="text-align:center"><img src="{img(d["image_index"])}" width="600"></p>',f'<p style="text-align:center"><i>{E(d["caption"])}</i></p>',
               "<p><b>Mô tả:</b></p>"]+[f"<p>{E(x)}</p>" for x in d['desc'].split('\n')]+[f"<p>{url}</p>"]+[f"<p>{h}</p>" for h in hashtags]+[f"<p><b>Số ký tự mô tả (gồm link và hashtag): {n}/500</b></p>"]
        report.append(f'Pinterest: title {len(t)}, mô tả {n}, ảnh #{d["image_index"]}')
    else: errs.append(f'nền tảng lạ {p}')
    parts=[x for x in '\n'.join(parts).replace('</ul>\n<ul>','\n').split('\n')]
    built[p]={'row':row['row'],'title':fname,'html':'<html><head><meta charset="utf-8"></head><body>'+'\n'.join(parts)+'</body></html>'}
# cross-version similarity for long versions
longs=[p for p in built if p in LONG]
for i in range(len(longs)):
    for j in range(i+1,len(longs)):
        a=dr['docs'][longs[i]]; b=dr['docs'][longs[j]]
        ta=' '.join(sum([s['paras'] for s in a['sections']],[])); tb=' '.join(sum([s['paras'] for s in b['sections']],[]))
        c=ngrams(ta,7)&ngrams(tb,7)
        if len(c)>3: errs.append(f'{longs[i]} và {longs[j]} trùng {len(c)} cụm 7 từ — cần viết khác câu chữ')
for p,b in built.items():
    open(f'{D}/out/{slug}__{p}.html','w').write(b['html'])
json.dump({p:{'row':b['row'],'title':b['title']} for p,b in built.items()},open(f'{D}/out/{slug}__meta.json','w'),ensure_ascii=False)
print('\n'.join(report)); print('Hashtag:',' | '.join(hashtags))
if errs: print('LỖI:\n- '+'\n- '.join(errs)); sys.exit(1)
print('OK')

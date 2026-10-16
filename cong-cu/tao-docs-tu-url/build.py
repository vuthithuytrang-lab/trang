import sys, re, json, unicodedata, html
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urljoin
import os
SP=os.environ.get('SP','./')  # thư mục chứa urls.txt, raw/, out/
BASE='https://techcombank.com'
J='text-align:justify;'
def strip_acc(t):
    t=t.replace('đ','d').replace('Đ','D')
    return ''.join(c for c in unicodedata.normalize('NFD',t) if unicodedata.category(c)!='Mn').lower()
def keyword(slug, texts):
    words=slug.split('-')
    for t in texts:
        toks=re.findall(r'[\wÀ-ỹ]+',t)
        n=len(words)
        for i in range(len(toks)-n+1):
            if [strip_acc(x) for x in toks[i:i+n]]==words:
                k=' '.join(toks[i:i+n]); return k[0].upper()+k[1:].lower()
    return None
ALLOWED={'p','h2','h3','h4','h5','ul','ol','li','b','strong','i','em','u','a','table','tbody','thead','tr','td','th','img','br','span','sup','sub'}
def clean(node):
    for t in node.find_all(['script','style','noscript','button','svg','form','iframe']): t.decompose()
    for t in node.find_all(True):
        if t.name not in ALLOWED:
            t.unwrap(); continue
        attrs={}
        if t.name=='a' and t.get('href'): attrs['href']=urljoin(BASE,t['href'])
        if t.name=='img':
            src=t.get('src') or t.get('data-src')
            if not src or src.startswith('data:') or src.endswith('.svg'): t.decompose(); continue
            attrs['src']=urljoin(BASE,src); attrs['width']='500'
        if t.name in ('td','th') :
            for k in ('colspan','rowspan'):
                if t.get(k): attrs[k]=t[k]
        if t.name=='table': attrs['border']='1'; attrs['style']='border-collapse:collapse;width:100%'
        if t.name in ('p','li','h2','h3','h4','h5'): attrs['style']=J
        if t.name=='p' and t.find('img'): attrs['style']='text-align:center;'  # ảnh + chú thích căn giữa
        if t.name=='span': t.unwrap(); continue
        t.attrs=attrs
    # ảnh + chú thích ảnh căn giữa (Trang yêu cầu 15/10/2026)
    for im in node.find_all('img'):
        par=im.find_parent('p')
        if par is None:
            par=BeautifulSoup('<p></p>','lxml').p
            im.wrap(par)
        par['style']='text-align:center;'
        if not (im.next_sibling is not None and getattr(im.next_sibling,'name',None)=='br'):
            im.insert_after(BeautifulSoup('<br/>','lxml').br)
        # chú thích ở đoạn riêng ngay sau: toàn chữ nghiêng, ngắn
        nx=par.find_next_sibling()
        while nx is not None and nx.name=='br': nx=nx.find_next_sibling()
        if nx is not None and nx.name in ('i','em') and len(nx.get_text(strip=True))<300:
            cap=BeautifulSoup('<p></p>','lxml').p; nx.wrap(cap); cap['style']='text-align:center;'
        elif nx is not None and nx.name=='p' and not nx.find('img'):
            it=nx.find('i'); txt=nx.get_text(' ',strip=True)
            if it is not None and txt and it.get_text(' ',strip=True)==txt and len(txt)<300:
                nx['style']='text-align:center;'
    return node
def article(s):
    a=s.select_one('.article-text')
    if a: return a
    return None
def product(s):
    m=s.find('main') or s.body
    for t in m.find_all(['header','footer','nav','script','style','noscript']): t.decompose()
    for x in m.select('[class*=header],[class*=footer],[class*=navigation],[class*=modal],[class*=popup],[class*=breadcrumb]'): x.decompose()
    out=[];seen=set()
    JUNK={'chevron_left','chevron_right','arrow_forward','Xem thêm','Quay về','Đi tiếp','hoặc','đã hết hạn','Khám phá ngay','Liên hệ ngay','Mở tài khoản ngay'}
    for t in m.find_all(['h1','h2','h3','h4','p','li']):
        if t.find(['h1','h2','h3','h4','p','li']): continue
        x=t.get_text(' ',strip=True)
        if not x or x in JUNK or x in seen: continue
        seen.add(x)
        tag={'h1':'h2'}.get(t.name,t.name)
        if tag=='li': tag='p'; x='• '+x
        out.append(f'<{tag} style="{J}">{html.escape(x)}</{tag}>')
    return '\n'.join(out)
rows=[l.split() for l in open(SP+'urls.txt')]
res=[]
for id,url in rows:
    s=BeautifulSoup(open(SP+f'raw/{id}.html',encoding='utf-8').read(),'lxml')
    title=s.title.get_text(strip=True) if s.title else ''
    md=s.find('meta',attrs={'name':'description'}); md=md['content'].strip() if md else ''
    h1=s.find('h1'); h1=h1.get_text(' ',strip=True) if h1 else ''
    if 'Không tìm thấy' in title:
        res.append(dict(id=id,url=url,status='404')); continue
    a=article(s)
    if a:
        body=str(clean(a)); kind='blog'
        # remove leftover related/cta? keep all of article-text
    else:
        body=product(s); kind='product'
    slug=url.rstrip('/').split('/')[-1]
    kw=keyword(slug,[h1,title,md,BeautifulSoup(body,'lxml').get_text(' ')])
    doc=f'''<html><head><meta charset="utf-8"></head><body style="font-family:Arial">
<p>URL: <a href="{url}">{url}</a></p><p></p>
<p style="text-align:center"><b>{html.escape(title)}</b></p><p></p>
<p style="text-align:center;color:#888888">{html.escape(md)}</p><p></p>
{body}
</body></html>'''
    open(SP+f'out/{id}.html','w',encoding='utf-8').write(doc)
    res.append(dict(id=id,url=url,kind=kind,kw=kw,title=title,h1=h1,size=len(doc),imgs=doc.count('<img')))
json.dump(res,open(SP+'out/index.json','w'),ensure_ascii=False,indent=1)
for r in res: print(r.get('id'),r.get('kind',r.get('status')),'|',r.get('kw'),'|',r.get('h1','')[:60],r.get('size'),r.get('imgs'))

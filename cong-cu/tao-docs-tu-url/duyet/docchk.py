# docchk.py <rows.json> <row> <saved html-export json> — soát bản Docs đã sửa (xuất HTML):
# mỗi anchor sheet là chữ nguyên văn của 1 link đúng URL; in vị trí % các link tô vàng; in đoạn có chữ tô vàng.
import json,sys,re,base64,urllib.parse
from bs4 import BeautifulSoup
rows={r['row']:r for r in json.load(open(sys.argv[1]))}; r=rows[int(sys.argv[2])]
d=json.load(open(sys.argv[3])); c=d['content']
try: html=base64.b64decode(c).decode('utf-8')
except Exception: html=c
s=BeautifulSoup(html,'lxml')
css=' '.join(t.get_text() for t in s.find_all('style'))
yel={m.group(1) for m in re.finditer(r'\.(c\d+)\{[^}]*background-color:#ff0',css)}
def url(a):
    h=a.get('href','')
    if 'google.com/url' in h: h=urllib.parse.parse_qs(urllib.parse.urlparse(h).query).get('q',[h])[0]
    return h
def slug(u): return u.split('?')[0].rstrip('/').split('/')[-1]
norm=lambda x:re.sub(r'\s+',' ',x.replace('\xa0',' ')).strip()
isy=lambda e:any('background-color:#ffff00' in (x.get('style') or '') or set(x.get('class',[]))&yel for x in [e]+e.find_parents('span')+e.find_all('span'))
links=s.find_all('a',href=True)
can=([(r['F'],r['G'])] if r['F'] and r['G'] else [])+[tuple(x) for x in r['pairs']]
loi=[]
for a,u in can:
    hit=[x for x in links if norm(x.get_text(''))==norm(a) and slug(url(x))==slug(u)]
    if not hit: loi.append('THIẾU: '+a)
    elif not any(isy(x) for x in hit): loi.append('chưa vàng: '+a)
ps=[p for p in s.find_all(['p','li','h1','h2','h3'])]
tot=sum(len(p.get_text()) for p in ps) or 1; acc=0
for p in ps:
    if any(isy(x) for x in p.find_all('a')) and p.name.startswith('h'): loi.append('link vàng trong heading')
    acc+=len(p.get_text())
print(d.get('title'),'|', 'OK' if not loi else loi)

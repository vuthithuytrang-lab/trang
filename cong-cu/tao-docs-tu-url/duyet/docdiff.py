# docdiff.py <prev html> <saved html-export json> — so chữ Docs hiện tại với bản trước khi sửa (prev/): in từng chỗ khác nhau (theo từ, kèm ngữ cảnh)
import json,sys,re,base64,difflib,unicodedata
from bs4 import BeautifulSoup
def words(s):
    for x in s.find_all(['sup']): 
        if re.fullmatch(r'\[\w+\]',x.get_text().strip()): x.decompose()
    for x in s.find_all('div'):
        if x.find('a',id=re.compile('^cmnt')): x.decompose()
    B=['p','li','h1','h2','h3','h4','td']
    out=[]
    for e in s.find_all(B):
        if e.find(B): 
            t=''.join(x for x in e.find_all(string=True,recursive=False))
            t+=''.join(c.get_text('') for c in e.children if getattr(c,'name',None) and c.name not in B and not c.find(B))
        else: t=e.get_text('')
        t=unicodedata.normalize('NFC',t.replace('\xa0',' '))
        out+=re.findall(r'\S+',re.sub(r'\s*([,.;:)])',r'\1 ',t))
    return out
a=words(BeautifulSoup(open(sys.argv[1],encoding='utf-8').read(),'lxml'))
d=json.load(open(sys.argv[2])); c=d['content']
try: h=base64.b64decode(c).decode('utf-8')
except Exception: h=c
b=words(BeautifulSoup(h,'lxml'))
sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
for op,i1,i2,j1,j2 in sm.get_opcodes():
    if op=='equal': continue
    ctx=' '.join(a[max(0,i1-8):i1])
    print(f'[{op}] …{ctx} | - {" ".join(a[i1:i2])[:500]} | + {" ".join(b[j1:j2])[:500]}')

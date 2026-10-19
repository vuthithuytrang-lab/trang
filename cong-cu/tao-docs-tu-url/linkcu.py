# linkcu.py <dir>/ — mọi link gốc của bài (out/) phải còn trong bản cuối (final/), trừ link được chuyển (chuyenlink)
import sys,glob,os,json
from bs4 import BeautifulSoup
D=sys.argv[1]
plan=json.load(open(D+'plan.json')) if os.path.exists(D+'plan.json') else {}
for f in sorted(glob.glob(D+'final/r*.html')):
    rid=os.path.basename(f)[:-5]
    o=BeautifulSoup(open(D+f'out/{rid}.html',encoding='utf-8').read(),'lxml'); n=BeautifulSoup(open(f,encoding='utf-8').read(),'lxml')
    moved={op['slug'] for op in plan.get(rid,[]) if op['t']=='chuyenlink'}
    from collections import Counter
    co=Counter(a.get('href') for a in o.find_all('a') if a.get('href')); cn=Counter(a.get('href') for a in n.find_all('a') if a.get('href'))
    lost=[h for h,c in co.items() if cn[h]<c and not any(h.split('?')[0].rstrip('/').endswith(m) for m in moved)]
    if lost: print(D.split('/')[-2], rid, 'MẤT LINK GỐC:', lost)

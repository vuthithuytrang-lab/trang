# cautruc.py <dir>/ — bản cuối không được mất bảng, hàng, gạch đầu dòng, ảnh so với bản gốc
import sys,glob,os
from bs4 import BeautifulSoup
D=sys.argv[1]
for f in sorted(glob.glob(D+'final/r*.html')):
    rid=os.path.basename(f)[:-5]
    o=BeautifulSoup(open(D+f'out/{rid}.html',encoding='utf-8').read(),'lxml'); n=BeautifulSoup(open(f,encoding='utf-8').read(),'lxml')
    bad=[t for t in ['table','tr','td','li','img','h2','h3'] if len(n.find_all(t))<len(o.find_all(t))]
    if bad: print(D.split('/')[-2],rid,'MẤT CẤU TRÚC:',{t:(len(o.find_all(t)),len(n.find_all(t))) for t in bad})

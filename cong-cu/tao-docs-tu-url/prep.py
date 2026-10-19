# Bỏ phần không thuộc bài trong khung .article-text: công cụ quy đổi tiền, thẻ "Tìm hiểu thêm"
import sys,glob
from bs4 import BeautifulSoup
for f in sys.argv[1:]:
    s=BeautifulSoup(open(f,encoding='utf-8').read(),'lxml')
    a=s.select_one('.article-text')
    n=0
    if a:
        for sel in ['.currency-converter','.listtiles','.list-tile']:
            for x in a.select(sel): x.decompose(); n+=1
    open(f,'w',encoding='utf-8').write(str(s)); print(f,'removed',n)

# -*- coding: utf-8 -*-
import sys, os, re, html as H
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from noidung_a import A
from noidung_b import B
from noidung_c import C
from noidung_d import D
from noidung_e import E
BLOCKS=A+B+C+D+E

RAW=('https://raw.githubusercontent.com/vuthithuytrang-lab/trang/claude/serene-noether-tnjmy3/'
     'K%E1%BA%BFt%20qu%E1%BA%A3%20c%C3%B4ng%20vi%E1%BB%87c%20Agent%20Boss/'
     'Viec%20that%20-%20Phan%20tich%20SEO%20van%20phong%2070m2/bai-viet/anh-bai-viet/{}.jpg')
U70='https://www.deco-crystal.com/wp-content/uploads/2026/08/thiet-ke-van-phong-70m2-%s.webp'
U80='https://www.deco-crystal.com/wp-content/uploads/2026/05/top-mau-thiet-ke-van-phong-80m2-%s.webp'
def url(k):
    if k.startswith('a70-'): return U70%k[4:]
    if k.startswith('b80-'): return U80%k[4:]
    return RAW.format(k)

def inl(t):
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', H.escape(t))

o=[]
W=620
for b in BLOCKS:
    k=b[0]
    if k=='h1':   o.append('<h1>%s</h1>'%inl(b[1]))
    elif k=='meta': o.append('<p><i>%s</i></p>'%inl(b[1]))
    elif k=='sapo': o.append('<p>%s</p>'%inl(b[1]))
    elif k=='h2': o.append('<h2>%s</h2>'%inl(b[1]))
    elif k=='h3': o.append('<h3>%s</h3>'%inl(b[1]))
    elif k=='h4': o.append('<h4>%s</h4>'%inl(b[1]))
    elif k=='lead': o.append('<p><b>%s</b></p>'%inl(b[1]))
    elif k=='p': o.append('<p>%s</p>'%inl(b[1]))
    elif k=='note': o.append('<p><i>%s</i></p>'%inl(b[1]))
    elif k=='ul': o.append('<ul>'+''.join('<li>%s</li>'%inl(i) for i in b[1])+'</ul>')
    elif k=='table':
        t='<table border="1" cellpadding="6" cellspacing="0"><tr>'
        t+=''.join('<td bgcolor="#0B3D91"><b><font color="#FFFFFF">%s</font></b></td>'%inl(h) for h in b[1])+'</tr>'
        for r in b[2]:
            t+='<tr>'+''.join('<td>%s</td>'%inl(c) for c in r)+'</tr>'
        o.append(t+'</table><p></p>')
    elif k in ('img','sodo'):
        alt=re.sub(r'\s*\((Nguồn: Internet|Ảnh tham khảo)\)$','',b[2])
        o.append('<p><img src="%s" alt="%s" width="%d"></p><p><i>%s</i></p>'
                 %(url(b[1]),H.escape(alt),W,inl(b[2])))
    elif k=='box_tacgia':
        o.append('<p><b>%s</b><br>%s</p>'%(inl(b[1]),inl(b[2])))

doc=('<html><head><meta charset="utf-8"><title>Thiết kế văn phòng 70m2: bố trí thế nào cho đủ 10–15 chỗ ngồi</title></head>'
     '<body>'+'\n'.join(o)+'</body></html>')
p='/tmp/claude-0/-home-user-trang/b01499db-3e47-587b-84ec-f73e3ff320ac/scratchpad/bai/cho-google-docs.html'
open(p,'w',encoding='utf-8').write(doc)
print(p, len(doc), 'ky tu', doc.count('<img'), 'anh')

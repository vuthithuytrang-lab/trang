# -*- coding: utf-8 -*-
import sys, os, re, base64, html as H
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from noidung_a import A
from noidung_b import B
from noidung_c import C
from noidung_d import D
from noidung_e import E
BLOCKS = A+B+C+D+E
SCR='/tmp/claude-0/-home-user-trang/b01499db-3e47-587b-84ec-f73e3ff320ac/scratchpad'
OUT=SCR+'/bai'; JPG=OUT+'/anh_jpg'

URL70='https://www.deco-crystal.com/wp-content/uploads/2026/08/thiet-ke-van-phong-70m2-%s.webp'
URL80='https://www.deco-crystal.com/wp-content/uploads/2026/05/top-mau-thiet-ke-van-phong-80m2-%s.webp'
def weburl(k):
    if k.startswith('a70-'): return URL70 % k[4:]
    if k.startswith('b80-'): return URL80 % k[4:]
    return 'CAN-TAI-LEN-WORDPRESS/%s.png' % k   # 3 so do tu ve

def b64(k):
    p=os.path.join(JPG,k+'.jpg')
    return 'data:image/jpeg;base64,'+base64.b64encode(open(p,'rb').read()).decode()

def inl(t):
    t=H.escape(t)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)

CSS = """
:root{--nav:#0B3D91;--ink:#1F2A44;--mute:#5B6478;--line:#DDE3EC;--bg:#F7F9FC}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:'Segoe UI',system-ui,-apple-system,Arial,sans-serif;line-height:1.75;font-size:16.5px}
.wrap{max-width:820px;margin:0 auto;background:#fff;padding:38px 34px 56px;min-width:0}
h1{font-size:31px;line-height:1.3;color:var(--ink);margin:0 0 6px}
.meta{color:var(--mute);font-size:13.5px;font-style:italic;margin:0 0 22px}
.sapo{font-size:17.5px;margin:0 0 12px}
h2{font-size:23px;color:var(--nav);margin:38px 0 12px;padding-top:14px;border-top:2px solid var(--line)}
h3{font-size:18.5px;margin:26px 0 8px}
h4{font-size:16.5px;color:var(--nav);margin:22px 0 6px}
.lead{font-weight:700;color:#0D6E4F;margin:14px 0 2px;font-size:15.5px}
p{margin:0 0 12px;text-align:justify}
ul{margin:0 0 14px;padding-left:22px}
li{margin:0 0 7px}
.note{background:#F2F5FA;border-left:4px solid var(--nav);padding:11px 14px;
 color:var(--mute);font-size:14px;font-style:italic;margin:0 0 16px;border-radius:0 6px 6px 0}
.bang-cuon{overflow-x:auto;margin:0 0 20px;min-width:0}
table{border-collapse:collapse;width:100%;font-size:14.5px}
th{background:var(--nav);color:#fff;text-align:left;padding:9px 11px;border:1px solid var(--nav)}
td{padding:9px 11px;border:1px solid var(--line);vertical-align:top}
tr:nth-child(even) td{background:#F7F9FC}
figure{margin:0 0 22px}
figure img{width:100%;height:auto;display:block;border-radius:8px;border:1px solid var(--line)}
figcaption{color:var(--mute);font-size:13.5px;font-style:italic;text-align:center;margin-top:7px}
.tacgia{background:#F2F5FA;border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin:24px 0}
.tacgia b{color:var(--nav);font-size:16px}
.tacgia p{margin:5px 0 0;font-size:14.5px;color:#333A48;text-align:left}
@media(max-width:640px){.wrap{padding:24px 16px 40px}h1{font-size:25px}h2{font-size:20px}body{font-size:16px}}
"""

def render(mode):
    """mode='soat' -> anh nhung base64 ; mode='wp' -> anh dung URL"""
    o=[]
    for b in BLOCKS:
        k=b[0]
        if k=='h1': o.append('<h1>%s</h1>'%inl(b[1]))
        elif k=='meta': o.append('<p class="meta">%s</p>'%inl(b[1]))
        elif k=='sapo': o.append('<p class="sapo">%s</p>'%inl(b[1]))
        elif k=='h2': o.append('<h2>%s</h2>'%inl(b[1]))
        elif k=='h3': o.append('<h3>%s</h3>'%inl(b[1]))
        elif k=='h4': o.append('<h4>%s</h4>'%inl(b[1]))
        elif k=='lead': o.append('<p class="lead">%s</p>'%inl(b[1]))
        elif k=='p': o.append('<p>%s</p>'%inl(b[1]))
        elif k=='note': o.append('<p class="note">%s</p>'%inl(b[1]))
        elif k=='ul':
            o.append('<ul>'+''.join('<li>%s</li>'%inl(i) for i in b[1])+'</ul>')
        elif k=='table':
            t='<div class="bang-cuon"><table><thead><tr>'
            t+=''.join('<th>%s</th>'%inl(h) for h in b[1])+'</tr></thead><tbody>'
            for r in b[2]:
                t+='<tr>'+''.join('<td>%s</td>'%inl(c) for c in r)+'</tr>'
            o.append(t+'</tbody></table></div>')
        elif k in ('img','sodo'):
            src = b64(b[1]) if mode=='soat' else weburl(b[1])
            alt = re.sub(r'\s*\((Nguồn: Internet|Ảnh tham khảo)\)$','',b[2])
            o.append('<figure><img src="%s" alt="%s" loading="lazy"><figcaption>%s</figcaption></figure>'
                     %(src,H.escape(alt),inl(b[2])))
        elif k=='box_tacgia':
            o.append('<div class="tacgia"><b>%s</b><p>%s</p></div>'%(inl(b[1]),inl(b[2])))
    return '\n'.join(o)

TITLE='Thiết kế văn phòng 70m2: bố trí thế nào cho đủ 10–15 chỗ ngồi'
page=('<!doctype html><html lang="vi"><head><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width,initial-scale=1">'
      '<title>%s</title><style>%s</style></head><body><div class="wrap">%s</div></body></html>')

open(OUT+'/ban-doc-duyet.html','w',encoding='utf-8').write(page%(TITLE,CSS,render('soat')))
open(OUT+'/ma-dan-vao-wordpress.html','w',encoding='utf-8').write(render('wp'))
print('xong 2 file html')

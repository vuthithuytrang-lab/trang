# -*- coding: utf-8 -*-
import sys,os,re,html as H
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from bc90_a import A
from bc90_b import B
from bc90_c import C
from bc90_d import D
BL=A+B+C+D

CSS="""
:root{--nav:#0B3D91;--ink:#1F2A44;--mute:#5B6478;--line:#DDE3EC;--bg:#F7F9FC;--vang:#B4690E;--tot:#0D6E4F;--xau:#B42318}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:'Segoe UI',system-ui,-apple-system,Arial,sans-serif;line-height:1.72;font-size:16px}
.wrap{max-width:940px;margin:0 auto;background:#fff;padding:36px 32px 56px;min-width:0}
h1{font-size:29px;line-height:1.3;margin:0 0 6px}
.meta{color:var(--mute);font-size:13.5px;font-style:italic;margin:0 0 24px}
h2{font-size:22px;color:var(--nav);margin:36px 0 12px;padding-top:14px;border-top:2px solid var(--line)}
h3{font-size:17.5px;margin:24px 0 8px}
p{margin:0 0 12px}
ul,ol{margin:0 0 14px;padding-left:22px}li{margin:0 0 6px}
.note{background:#FFF8E8;border-left:4px solid var(--vang);padding:11px 14px;font-size:14.5px;margin:0 0 16px;border-radius:0 6px 6px 0}
.quote{background:#F2F5FA;border-left:4px solid var(--nav);padding:14px 16px;margin:0 0 16px;font-size:16px;border-radius:0 6px 6px 0}
.big{background:var(--nav);color:#fff;padding:16px 18px;border-radius:8px;font-size:19px;margin:0 0 16px;text-align:center}
.big b{color:#7FE3BC}
.bang-cuon{overflow-x:auto;margin:0 0 20px;min-width:0}
table{border-collapse:collapse;width:100%;font-size:14px}
th{background:var(--nav);color:#fff;text-align:left;padding:8px 10px;border:1px solid var(--nav);white-space:nowrap}
td{padding:8px 10px;border:1px solid var(--line);vertical-align:top}
tr:nth-child(even) td{background:#F7F9FC}
.vang{color:var(--vang)}.tot{color:var(--tot)}.xau{color:var(--xau)}
@media(max-width:640px){.wrap{padding:22px 16px 40px}h1{font-size:24px}h2{font-size:19px}.big{font-size:17px}}
"""
o=[]
for b in BL:
    k=b[0]
    if k=='h1': o.append('<h1>%s</h1>'%b[1])
    elif k=='meta': o.append('<p class="meta">%s</p>'%b[1])
    elif k=='h2': o.append('<h2>%s</h2>'%b[1])
    elif k=='h3': o.append('<h3>%s</h3>'%b[1])
    elif k=='p': o.append('<p>%s</p>'%b[1])
    elif k=='note': o.append('<p class="note">%s</p>'%b[1])
    elif k=='quote': o.append('<p class="quote">%s</p>'%b[1])
    elif k=='big': o.append('<p class="big">%s</p>'%b[1])
    elif k=='ul': o.append('<ul>'+''.join('<li>%s</li>'%i for i in b[1])+'</ul>')
    elif k=='ol': o.append('<ol>'+''.join('<li>%s</li>'%i for i in b[1])+'</ol>')
    elif k=='table':
        t='<div class="bang-cuon"><table><thead><tr>'+''.join('<th>%s</th>'%h for h in b[1])+'</tr></thead><tbody>'
        for r in b[2]: t+='<tr>'+''.join('<td>%s</td>'%c for c in r)+'</tr>'
        o.append(t+'</tbody></table></div>')
body='\n'.join(o)
TITLE='Phân tích SEO và đề xuất outline — thiết kế văn phòng 90m2'
page=('<!doctype html><html lang="vi"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 '<title>%s</title><style>%s</style></head><body><div class="wrap">%s</div></body></html>')%(TITLE,CSS,body)
S='/tmp/claude-0/-home-user-trang/b01499db-3e47-587b-84ec-f73e3ff320ac/scratchpad'
open(S+'/phan-tich-va-outline-90m2.html','w',encoding='utf-8').write(page)
# ban cho google docs (khong CSS)
docs='<html><head><meta charset="utf-8"><title>%s</title></head><body>%s</body></html>'%(TITLE,
   body.replace('<div class="bang-cuon">','').replace('</table></div>','</table>')
       .replace('<table>','<table border="1" cellpadding="6" cellspacing="0">')
       .replace('<p class="note">','<p><i>').replace('<p class="quote">','<p><i>')
       .replace('<p class="big">','<p><b>').replace('<p class="meta">','<p><i>'))
docs=re.sub(r'(<p><i>.*?)</p>',r'\1</i></p>',docs,flags=re.S)
open(S+'/cho-docs-90m2.html','w',encoding='utf-8').write(docs)
n=len(re.sub(r'<[^>]+>',' ',body).split())
print('xong |',n,'chữ |',len(page),'ký tự HTML |',len(docs),'ký tự bản Docs')

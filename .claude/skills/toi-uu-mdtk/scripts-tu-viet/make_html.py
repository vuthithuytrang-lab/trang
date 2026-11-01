"""Tải bài Techcombank -> HTML gọn (Title, Meta, H1, nội dung) để tạo Google Docs.
Dùng: python3 -I make_html.py <url> <out.html>"""
import sys, re, html as H, subprocess
from html.parser import HTMLParser
url, out = sys.argv[1], sys.argv[2]
import time
raw=''
for k in range(5):
    raw = subprocess.run(['curl','-sS','-m','40','-A','Mozilla/5.0',url],capture_output=True).stdout.decode('utf-8','replace')
    if 'class="cmp-text' in raw: break
    time.sleep(2*(k+1))
def grab(p):
    m = re.search(p, raw, re.S); return H.unescape(re.sub(r'\s+',' ',m.group(1))).strip() if m else ''
title = grab(r'<title>(.*?)</title>')
meta = grab(r'<meta name="description" content="([^"]*)"')
h1 = re.sub('<[^>]+>','',grab(r'<h1[^>]*>(.*?)</h1>')).strip()
i = raw.find('class="cmp-text')
if i < 0: sys.exit('LỖI: không thấy khối nội dung cmp-text')
start = raw.find('>', i) + 1
# lấy đến hết div cmp-text (đếm div lồng nhau)
depth, j = 1, start
for m in re.finditer(r'<(/?)div\b', raw[start:]):
    depth += -1 if m.group(1) else 1
    if depth == 0: j = start + m.start(); break
body = raw[start:j]
KEEP = {'p','h2','h3','h4','ul','ol','li','b','strong','i','em','table','tbody','tr','td','th','br','a'}
class P(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.o=[]
    def handle_starttag(s,t,a):
        if t=='img':
            alt=dict(a).get('alt') or ''
            if alt: s.o.append(f'<p><i>[Ảnh: {H.escape(alt)}]</i></p>')
        elif t in KEEP:
            if t=='a': s.o.append('<a href="%s">'%H.escape(dict(a).get('href') or '',quote=True))
            elif t=='table': s.o.append('<table border="1" style="border-collapse:collapse">')
            else: s.o.append(f'<{t}>')
    def handle_endtag(s,t):
        if t in KEEP and t!='br': s.o.append(f'</{t}>')
    def handle_data(s,d): s.o.append(H.escape(d))
p=P(); p.feed(body)
clean=''.join(p.o)
clean=re.sub(r'\s+',' ',clean)
clean=re.sub(r'<(p|li|h2|h3)>\s*</\1>','',clean)
words=len(re.sub('<[^>]+>',' ',clean).split())
css='body{font-family:Arial;font-size:15pt;line-height:1.15} p,li,td{font-size:15pt;line-height:1.15}'
doc=f'''<html><head><meta charset="utf-8"><style>{css}</style></head><body>
<p>URL: <a href="{H.escape(url,quote=True)}">{H.escape(url)}</a></p>
<p><b>Title:</b> {H.escape(title)}</p>
<p><b>Meta description:</b> {H.escape(meta)}</p>
<h1>{H.escape(h1)}</h1>
{clean}
</body></html>'''
open(out,'w',encoding='utf-8').write(doc)
print(f'OK title="{title[:70]}" words={words} bytes={len(doc.encode())}')

#!/usr/bin/env python3
"""Đăng 1 bài lên Google Group techcombank-viet-nam (gửi email HTML qua Gmail API, ảnh nhúng cid).
Cách chạy: python3 gg_post.py <dòng nhóm GG> ; in PUBLISHED {...}. Không in chìa."""
import json, os, re, sys, base64, subprocess, urllib.request, urllib.parse, datetime as D
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
ACC = '/home/user/trang/.claude/skills/share-bai-ggr/ggr-accounts.local.json'
G = 'techcombank-viet-nam@googlegroups.com'
VN = D.timezone(D.timedelta(hours=7))
grow = int(sys.argv[1]); row = grow - 4
a = json.load(open(ACC))[G]
tok = json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', urllib.parse.urlencode(dict(client_id=a['client_id'], client_secret=a['client_secret'], refresh_token=a['refresh_token'], grant_type='refresh_token')).encode()))['access_token']
def api(method, url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None, method=method, headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req))
m = json.load(open(f'bai/{row}/meta.json')); html = open(f'bai/{row}/post.html').read()
def clean(h):
    def cap(mo): return mo.group(1) + mo.group(2).upper()
    h = re.sub(r'(?i)\b(theo (gợi ý|hướng dẫn|chia sẻ) (trong|của|từ) bài gốc|theo bài gốc|như bài gốc (nêu|chia sẻ)),\s*', '', h)
    h = re.sub(r'(<(?:p|li|h2|h3)>)(\w)', cap, h)
    return re.sub(r'(?i)\s*\((theo|như) bài gốc\)', '', h)
html = clean(html)
assert 'bài gốc' not in html.lower(), 'con cum bai goc'
if not os.path.exists(f'thumb/{row}.png'):
    env = dict(os.environ, NODE_PATH=subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip())
    subprocess.run(['node', 'thumbs.js', str(row)], env=env, check=True)
msg = MIMEMultipart('related'); msg['To'] = G; msg['From'] = a.get('from', 'me'); msg['Subject'] = Header(m['title'], 'utf-8')
msg.attach(MIMEText(f'<p><img src="cid:anh{row}" alt="{m["title"]}" style="max-width:100%"></p>\n' + html, 'html', 'utf-8'))
img = MIMEImage(open(f'thumb/{row}.png', 'rb').read(), 'png'); img.add_header('Content-ID', f'<anh{row}>'); img.add_header('Content-Disposition', 'inline', filename=f'{m["slug"]}.png'); msg.attach(img)
r = api('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/send', {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()})
md = api('GET', f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{r["id"]}?format=metadata&metadataHeaders=Message-Id')
mid = next((h['value'] for h in md['payload']['headers'] if h['name'].lower() == 'message-id'), '').strip('<>')
rec = {'platform': 'ggroup', 'row': grow, 'main_row': row, 'source': m['source'], 'title': m['title'], 'when': D.datetime.now(VN).isoformat(timespec='seconds'),
       'url': 'https://groups.google.com/d/msgid/techcombank-viet-nam/' + urllib.parse.quote(mid, safe='')}
open('gg_posted.jsonl', 'a').write(json.dumps(rec, ensure_ascii=False) + '\n')
print('PUBLISHED', json.dumps(rec, ensure_ascii=False))

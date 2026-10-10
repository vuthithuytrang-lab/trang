#!/usr/bin/env python3
"""Hẹn giờ bài 'Wix - Tuấn' lên accyenthang2.wixsite.com/techcombankvietnam.
Mỗi bài: tạo ảnh bìa (thumb.py) -> tải lên Wix Media -> tạo nháp (Ricos) có ảnh bìa -> hẹn giờ đăng.
Usage: dang_wix.py check <row> | post <row> | run      (run: lần lượt các bài chưa đăng, cách nhau 8–12 phút)
Ghi kết quả vào da-dang.jsonl. Không in chìa."""
import datetime, html, json, os, random, re, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__))
KEY = 'accyenthang2.wixsite.com/techcombankvietnam'
A = json.load(open('/home/user/trang/.claude/skills/share-bai-wix/wix-accounts.local.json'))[KEY]
LOG = os.path.join(HERE, 'da-dang.jsonl')
CAM = re.compile(r'\b(duy nhất|(?<!Mẫu )(?<!Phụ lục )số 1(?![\d/])|hàng đầu|tốt nhất|cao nhất|rẻ nhất|lớn nhất|uy tín nhất|nhanh nhất|thấp nhất|hiệu quả nhất)\b', re.I)

def say(*a): print(datetime.datetime.now().strftime('%H:%M:%S'), *a, flush=True)

def call(method, path, data=None):
    with tempfile.NamedTemporaryFile('w', delete=False) as h:
        h.write(f"Authorization: {A['api_key']}\nwix-site-id: {A['site_id']}\nContent-Type: application/json\n")
    cmd = ['curl', '-s', '-m', '90', '-w', '\n%{http_code}', '-X', method, '-H', '@' + h.name]
    if data is not None: cmd += ['--data-binary', json.dumps(data, ensure_ascii=False)]
    out = subprocess.run(cmd + ['https://www.wixapis.com' + path], capture_output=True, text=True).stdout
    os.unlink(h.name)
    body, _, code = out.rpartition('\n')
    try: return int(code or 0), (json.loads(body) if body else {})
    except ValueError: return int(code or 0), {'raw': body[:300]}

def plan(): return json.load(open(os.path.join(HERE, 'plan.json')))
def item(row): return next(x for x in plan() if str(x['row']) == str(row))

def check(row):
    x = item(row); d = os.path.join(HERE, 'bai', str(row))
    h = open(os.path.join(d, 'wix.html'), encoding='utf-8').read()
    meta = json.load(open(os.path.join(d, 'meta.json'), encoding='utf-8'))
    text = re.sub(r'<[^>]+>', ' ', h); words = len(text.split()); errs = []
    if not 900 <= words <= 1100: errs.append(f'so tu {words}')
    if re.findall(r'<a\s+href="([^"]+)"', h) != [x['url']]: errs.append('link sai')
    if set(re.findall(r'</?([a-z0-9]+)', h)) - {'p', 'h2', 'h3', 'ul', 'ol', 'li', 'strong', 'a'}: errs.append('the la')
    if CAM.search(text): errs.append('tu cam: ' + CAM.search(text).group(0))
    if re.search(r'<h[23][^>]*>[^<]*(kết luận|tóm lại|tổng kết|tóm tắt|lời kết)', h, re.I): errs.append('co ket luan')
    if not 55 <= len(meta['title']) <= 70: errs.append(f"tieu de {len(meta['title'])}")
    if x['kw'].lower() not in meta['title'].lower(): errs.append('tieu de thieu kw')
    if 'checklist' in meta['title'].lower(): errs.append('tieu de co checklist')
    if not meta.get('thumb'): errs.append('thieu thumb')
    return x, h, meta, words, errs

# ---------- HTML (mỗi khối một dòng) -> Ricos ----------
_n = [0]
def nid(): _n[0] += 1; return f'n{_n[0]}'

def inline(s):
    """<strong>, <a href> -> các node TEXT có decoration (mỗi node một kiểu, không dùng offset)."""
    nodes = []
    for m in re.finditer(r'<strong>(.*?)</strong>|<a href="([^"]+)">(.*?)</a>|([^<]+)', s):
        if m.group(1) is not None: t, dec = m.group(1), [{'type': 'BOLD', 'fontWeightValue': 700}]
        elif m.group(2) is not None: t, dec = m.group(3), [{'type': 'LINK', 'linkData': {'link': {'url': m.group(2), 'target': 'BLANK'}}}]
        else: t, dec = m.group(4), []
        t = html.unescape(re.sub(r'<[^>]+>', '', t))
        if t: nodes.append({'type': 'TEXT', 'id': '', 'nodes': [], 'textData': {'text': t, 'decorations': dec}})
    return nodes

def para(s): return {'type': 'PARAGRAPH', 'id': nid(), 'nodes': inline(s), 'paragraphData': {}}

def to_ricos(h):
    out, lst = [], None
    for line in [l.strip() for l in h.splitlines() if l.strip()]:
        m = re.match(r'<(p|h2|h3|li)>(.*)</\1>$', line)
        if line in ('<ul>', '<ol>'):
            lst = {'type': 'BULLETED_LIST' if line == '<ul>' else 'ORDERED_LIST', 'id': nid(), 'nodes': [],
                   ('bulletedListData' if line == '<ul>' else 'orderedListData'): {'indentation': 0}}
        elif line in ('</ul>', '</ol>'): out.append(lst); lst = None
        elif m and m.group(1) == 'li': lst['nodes'].append({'type': 'LIST_ITEM', 'id': nid(), 'nodes': [para(m.group(2))]})
        elif m and m.group(1) == 'p': out.append(para(m.group(2)))
        elif m: out.append({'type': 'HEADING', 'id': nid(), 'nodes': inline(m.group(2)), 'headingData': {'level': int(m.group(1)[1])}})
        else: raise ValueError('dong khong hieu: ' + line[:80])
    return out

def upload_thumb(row, meta):
    png = os.path.join(tempfile.gettempdir(), f'thumb-{row}.png')
    subprocess.run([sys.executable, os.path.join(HERE, 'thumb.py'), str(row), png], check=True)
    code, r = call('POST', '/site-media/v1/files/generate-upload-url', {'mimeType': 'image/png', 'fileName': f"{meta['slug']}.png"})
    if code != 200: return None, f'upload-url {code}'
    out = subprocess.run(['curl', '-s', '-m', '120', '-X', 'PUT', '-H', 'Content-Type: image/png', '--data-binary', '@' + png, r['uploadUrl']],
                         capture_output=True, text=True).stdout
    os.unlink(png)
    try: f = json.loads(out)['file']
    except Exception: return None, 'upload loi: ' + out[:200]
    return {'id': f['id'], 'url': f['url'], 'width': 1200, 'height': 675}, None

def post(row):
    x, h, meta, words, errs = check(row)
    if errs: return 0, {'error': errs}
    t = datetime.datetime.fromisoformat(x['when'])
    if (t - datetime.datetime.now(datetime.timezone.utc)).total_seconds() < 300: return 0, {'error': 'qua gio hen'}
    img, err = upload_thumb(row, meta)
    if err: return 0, {'error': err}
    draft = {'title': meta['title'], 'memberId': A['member_id'], 'richContent': {'nodes': to_ricos(h)},
             'heroImage': {'id': img['id'], 'url': img['url'], 'altText': meta['thumb']},
             'media': {'wixMedia': {'image': {'id': img['id'], 'url': img['url'], 'width': 1200, 'height': 675}}, 'displayed': True, 'custom': True}}
    code, r = call('POST', '/blog/v3/draft-posts', {'draftPost': draft, 'publish': False})
    if code != 200: return code, r
    pid = r['draftPost']['id']
    when = t.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    code, r = call('PATCH', f'/blog/v3/draft-posts/{pid}?fieldsets=URL',
                   {'draftPost': {'id': pid, 'memberId': A['member_id']}, 'action': 'UPDATE_SCHEDULE', 'scheduledPublishDate': when})
    if code != 200 or r.get('draftPost', {}).get('status') != 'SCHEDULED': return code or 1, {'draft_id': pid, **r}
    # seoSlug bị bỏ qua khi hẹn giờ -> sửa riêng bằng action UPDATE (vẫn giữ trạng thái SCHEDULED)
    code, r = call('PATCH', f'/blog/v3/draft-posts/{pid}?fieldsets=URL',
                   {'draftPost': {'id': pid, 'memberId': A['member_id'], 'seoSlug': meta['slug']}, 'action': 'UPDATE'})
    d = r.get('draftPost', {})
    if code != 200 or d.get('status') != 'SCHEDULED': return code or 1, {'draft_id': pid, **r}
    url = f"https://{KEY}/post/{meta['slug']}"  # url trả về đôi khi còn là đường dẫn cũ có dấu
    res = {'row': x['row'], 'tuan_row': x['tuan_row'], 'id': pid, 'url': url, 'status': d['status'], 'when': x['when'], 'words': words, 'thumb': img['url']}
    open(LOG, 'a').write(json.dumps(res, ensure_ascii=False) + '\n')
    return 200, res

def done(): return {json.loads(l)['row'] for l in open(LOG)} if os.path.exists(LOG) else set()

def ready():
    f = os.path.join(HERE, 'san-sang.txt')  # các row đã được soát xong, cho phép đăng
    return {int(l) for l in open(f) if l.strip()} if os.path.exists(f) else set()

def run():
    """Chạy tới khi đăng đủ: mỗi lượt lấy bài sẵn sàng có giờ sớm nhất, xong nghỉ 8–12 phút."""
    while True:
        left = [x for x in plan() if x['row'] not in done()]
        if not left: say('XONG'); return
        todo = [x for x in left if x['row'] in ready()]
        if not todo: time.sleep(60); continue
        x = min(todo, key=lambda x: x['when'])
        code, r = post(x['row'])
        if code == 200: say('OK', x['stt'], x['row'], r['when'], r['url'])
        else:
            say('LOI', x['stt'], x['row'], code, str(r)[:250])
            if 'draft_id' in r or code in (403, 429): raise SystemExit('dung')
            open(os.path.join(HERE, 'san-sang.txt'), 'w').write(''.join(f'{r}\n' for r in ready() - {x['row']}))
            continue
        time.sleep(random.randint(int(os.environ.get('GIAN_MIN', 480)), int(os.environ.get('GIAN_MAX', 720))))

if __name__ == '__main__':
    if sys.argv[1] == 'check':
        x, _, meta, w, e = check(sys.argv[2]); print(x['row'], w, meta['title'], len(meta['title']), e or 'OK')
    elif sys.argv[1] == 'post': print(post(sys.argv[2]))
    else: run()

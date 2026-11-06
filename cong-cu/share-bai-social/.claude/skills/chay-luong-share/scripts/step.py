#!/usr/bin/env python3
"""Mỗi lần chạy: với mỗi nền tảng (wp, wix), nếu đến giờ thì đăng 1 bài kế tiếp đã viết xong.
In các bản ghi vừa đăng (dòng PUBLISHED {...}) và WAKE_AT <giờ VN> cho lần chạy sau. Không in chìa."""
import json, os, re, random, subprocess, sys, tempfile, datetime as D
# Cách chạy: python3 step.py <thư mục dự án>   (thư mục có du-an.json, tasks_raw.txt, bai/)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
PROJ = os.path.abspath(sys.argv[1]); os.chdir(PROJ)
CFG = json.load(open('du-an.json'))
if CFG.get('wix', {}).get('site'): os.environ['WIX_SITE'] = CFG['wix']['site']
from wixlib import api as wix_api, to_ricos, upload_image, MEMBER

TZ = D.timezone(D.timedelta(hours=7))
DEADLINE = D.datetime.fromisoformat(CFG['han_chot'])
WIN = tuple(CFG.get('khung_gio', [7, 0, 23, 0]))   # chỉ đăng trong khung giờ này
GAP_MIN, GAP_MAX = CFG.get('cach_nhau_phut', [30, 58])   # phút giữa 2 bài cùng nền tảng
SKILLS = '/home/user/trang/.claude/skills'
WP_SITE = CFG.get('wordpress', {}).get('site', '')
WIX_BASE = CFG.get('wix', {}).get('url_bai', '')
now = D.datetime.now(TZ)

tasks = [l.split() for l in open('tasks_raw.txt') if l.strip()]
recs = [json.loads(l) for l in open('posted.jsonl')] if os.path.exists('posted.jsonl') else []
done = {(r['platform'], r['row']) for r in recs if r.get('status') == 'published'}
state = json.load(open('state.json')) if os.path.exists('state.json') else {p: D.datetime.now(TZ).isoformat() for p in ('wp', 'wix')}
PLAN = {p: json.load(open(f'{p}_plan.json')) for p in ('wp', 'wix') if os.path.exists(f'{p}_plan.json')}


def in_window(t):
    return D.time(WIN[0], WIN[1]) <= t.timetz().replace(tzinfo=None) < D.time(WIN[2], WIN[3])


def to_window(t):
    if in_window(t): return t
    if t.hour >= WIN[2]: t = t + D.timedelta(days=1)
    return t.replace(hour=WIN[0], minute=WIN[1] + random.randint(0, 12), second=0, microsecond=0)


def window_minutes(a, b):
    m, t = 0, a
    while t < b:
        if in_window(t): m += 1
        t += D.timedelta(minutes=1)
    return m


def next_gap(plat, t):
    left = sum(1 for _, p, _ in tasks if p == plat) - sum(1 for p, _ in done if p == plat)
    if left <= 0: return None
    target = window_minutes(t, DEADLINE) / max(left, 1)
    return max(GAP_MIN, min(GAP_MAX, target * random.uniform(0.82, 1.0)))


def log(rec):
    open('posted.jsonl', 'a').write(json.dumps(rec, ensure_ascii=False) + '\n')
    print('PUBLISHED', json.dumps(rec, ensure_ascii=False)); recs.append(rec); done.add((rec['platform'], rec['row']))


def curl(args, data=None, token=None):
    cmd = ['curl', '-s', '-m', '120', '-w', '\n%{http_code}']; tmp = []
    if token:
        h = tempfile.NamedTemporaryFile('w', delete=False); h.write('Authorization: Bearer ' + token + '\n'); h.close()
        cmd += ['-H', '@' + h.name]; tmp.append(h.name)
    if data is not None:
        f = tempfile.NamedTemporaryFile('w', delete=False, suffix='.json'); json.dump(data, f, ensure_ascii=False); f.close()
        cmd += ['-H', 'Content-Type: application/json; charset=utf-8', '--data-binary', '@' + f.name]; tmp.append(f.name)
    out = subprocess.run(cmd + args, capture_output=True, text=True).stdout
    for x in tmp: os.unlink(x)
    body, _, code = out.rpartition('\n')
    try: return int(code), json.loads(body) if body.strip() else {}
    except ValueError: return int(code or 0), {'raw': body[:300]}


def to_gutenberg(html):
    out = []
    for line in [l.strip() for l in html.splitlines() if l.strip()]:
        if line.startswith('<p'): out.append('<!-- wp:paragraph -->\n' + line + '\n<!-- /wp:paragraph -->')
        elif line.startswith('<h2'): out.append('<!-- wp:heading {"style":{"typography":{"fontSize":"26px"}}} -->\n' + line.replace('<h2>', '<h2 class="wp-block-heading" style="font-size:26px">') + '\n<!-- /wp:heading -->')
        elif line.startswith('<h3'): out.append('<!-- wp:heading {"level":3,"style":{"typography":{"fontSize":"21px"}}} -->\n' + line.replace('<h3>', '<h3 class="wp-block-heading" style="font-size:21px">') + '\n<!-- /wp:heading -->')
        elif line == '<ul>': out.append('<!-- wp:list -->\n<ul class="wp-block-list">')
        elif line == '<ol>': out.append('<!-- wp:list {"ordered":true} -->\n<ol class="wp-block-list">')
        elif line == '</ul>': out.append('</ul>\n<!-- /wp:list -->')
        elif line == '</ol>': out.append('</ol>\n<!-- /wp:list -->')
        elif line.startswith('<li'): out.append('<!-- wp:list-item -->\n' + line + '\n<!-- /wp:list-item -->')
        else: out.append(line)
    return '\n\n'.join(out)


def thumb(row):
    env = dict(os.environ, NODE_PATH=subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip())
    subprocess.run(['node', os.path.join(HERE, 'thumbs.js'), str(row)], env=env, check=True)
    return f'thumb/{row}.png'


def http_ok(url):
    import time
    for _ in range(8):   # Wix cần ~3 phút mới hiện bài mới
        if _http(url): return True
        time.sleep(30)
    return False


def _http(url):
    return subprocess.run(['curl', '-s', '-L', '-o', '/dev/null', '-w', '%{http_code}', '-m', '40', url],
                          capture_output=True, text=True).stdout == '200'


def publish_wp(row, m, html):
    tok = json.load(open(os.path.join(SKILLS, 'share-bai-wp/wp-accounts.local.json')))[WP_SITE]['access_token']
    img = thumb(row)
    h = tempfile.NamedTemporaryFile('w', delete=False); h.write('Authorization: Bearer ' + tok + '\n'); h.close()
    out = subprocess.run(['curl', '-s', '-m', '120', '-H', '@' + h.name, '-F', f'media[]=@{img}',
                          '-F', f'attrs[0][alt]={m["keyword"]}', '-F', f'attrs[0][title]={m["keyword"]}',
                          f'https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}/media/new'], capture_output=True, text=True).stdout
    os.unlink(h.name)
    try: mid = json.loads(out)['media'][0]['ID']
    except Exception: return None, 'MEDIA_ERR ' + out[:200]
    code, r = curl([f'https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}/posts/new'],
                   {'title': m['title'], 'content': to_gutenberg(html), 'slug': m['slug'], 'status': 'publish', 'featured_image': mid}, tok)
    if code != 200: return None, f'CREATE_ERR {code} {str(r)[:200]}'
    return {'id': r['ID'], 'url': r['URL'], 'media': mid, 'thumb': bool(r.get('featured_image'))}, None


def publish_wix(row, m, html):
    img = thumb(row)
    f, err = upload_image(img, m['slug'] + '.png')
    if err: return None, f'UPLOAD_ERR {err}'
    # Đăng thẳng 1 lệnh (publish=True), không để bản nháp tồn tại — theo yêu cầu Trang 05/11
    c, res = wix_api('POST', 'https://www.wixapis.com/blog/v3/draft-posts', {'draftPost': {
        'title': m['title'], 'memberId': MEMBER, 'richContent': {'nodes': to_ricos(html)}, 'seoSlug': m['slug'],
        'media': {'wixMedia': {'image': {'id': f['id']}}, 'displayed': True, 'custom': True}}, 'publish': True})
    if c != 200: return None, f'CREATE_ERR {c} {str(res)[:200]}'
    pid = res['draftPost']['id']
    c2, p = wix_api('GET', f"https://www.wixapis.com/blog/v3/posts/{pid}?fieldsets=URL")
    u = p.get('post', {}).get('url', {}) if c2 == 200 else {}
    url = (u.get('base', '') + u.get('path', '')) if u else ''
    if not url or url.endswith('/'): url = WIX_BASE + m['slug']
    return {'id': pid, 'url': url, 'thumb': True}, None


BANNED = re.compile(r'(?<!chậm )(?<!sớm )(?<!mới )(?<!thứ )\b(duy nhất|số 1|hàng đầu|tốt nhất|rẻ nhất|cao nhất|thấp nhất|lớn nhất)\b', re.I)


def check(d, src):
    """Bài phải qua cổng soát mới được đăng (phòng file đang viết dở)."""
    if not os.path.exists(d + '/meta.json'): return 'chua co meta'
    if time_since_mod(d) < 120: return 'dang viet'
    h = open(d + '/post.html').read()
    try: m = json.load(open(d + '/meta.json'))
    except ValueError: return 'meta loi'
    words = len(re.sub('<[^>]+>', ' ', h).split())
    links = re.findall(r'href="([^"]+)"', h)
    tags = set(re.findall(r'</?([a-z0-9]+)', h)) - {'p', 'h2', 'h3', 'ul', 'ol', 'li', 'strong', 'a'}
    if not 880 <= words <= 1150: return f'so tu {words}'
    if links != [src]: return f'link {links}'
    if tags: return f'the {tags}'
    if not 50 <= len(m.get('title', '')) <= 75: return 'tieu de'
    if not m.get('slug') or not m.get('keyword'): return 'thieu slug/keyword'
    if BANNED.search(re.sub('<[^>]+>', ' ', h) + ' ' + m['title']): return 'tu cam ' + BANNED.search(re.sub('<[^>]+>', ' ', h) + ' ' + m['title']).group(0)
    return None


def clean(h):
    """Bỏ cụm 'theo bài gốc' (người đọc blog không biết 'bài gốc' là gì)."""
    def cap(mo): return mo.group(1) + mo.group(2).upper()
    h = re.sub(r'(?i)\b(theo (gợi ý|hướng dẫn|chia sẻ) (trong|của|từ) bài gốc|theo bài gốc|như bài gốc (nêu|chia sẻ)),\s*', '', h)
    h = re.sub(r'(<(?:p|li|h2|h3)>)(\w)', cap, h)
    h = re.sub(r'(?i)\s*\((theo|như) bài gốc\)', '', h)
    return h


def time_since_mod(d):
    return min(now.timestamp() - os.path.getmtime(os.path.join(d, f)) for f in ('post.html', 'meta.json'))


for plat in CFG.get('nen_tang', ['wp', 'wix']):
    due = D.datetime.fromisoformat(state[plat])
    if now < due: continue
    if not in_window(now):
        state[plat] = to_window(now).isoformat(); continue
    nxt = None
    for r, p, src in tasks:
        if p != plat or (plat, int(r)) in done: continue
        d = f'bai/{r}'
        if os.path.exists(d + '/NO_SOURCE.txt'): continue
        if plat in PLAN and (r not in PLAN[plat] or D.datetime.fromisoformat(PLAN[plat][r]) > now): continue
        if os.path.exists(d + '/post.html') and os.path.exists(d + '/meta.json'):
            bad = check(d, src)
            if bad: print(plat.upper(), 'SKIP_INVALID', r, bad); continue
            nxt = (int(r), src); break
    if not nxt:
        print(plat.upper(), 'NO_READY_CONTENT'); state[plat] = (now + D.timedelta(minutes=10)).isoformat(); continue
    row, src = nxt
    m = json.load(open(f'bai/{row}/meta.json')); html = clean(open(f'bai/{row}/post.html').read())
    res, err = (publish_wp if plat == 'wp' else publish_wix)(row, m, html)
    if err:
        print(plat.upper(), 'ERROR', row, err); state[plat] = (now + D.timedelta(minutes=20)).isoformat(); continue
    # (gap computed below; overridden by PLAN if present)
    res['live'] = http_ok(res['url'])
    log(dict(platform=plat, row=row, source=src, status='published', when=now.isoformat(timespec='seconds'), **res))
    g = next_gap(plat, now)
    state[plat] = to_window(now + D.timedelta(minutes=g)).isoformat() if g else '2099-01-01T00:00:00+07:00'
    if plat in PLAN:   # lịch cố định giãn đến Chủ nhật (Trang chốt 06/11)
        nxt_rows = [r for r, p, _ in tasks if p == plat and (plat, int(r)) not in done and r in PLAN[plat]]
        state[plat] = PLAN[plat][nxt_rows[0]] if nxt_rows else '2099-01-01T00:00:00+07:00'

json.dump(state, open('state.json', 'w'), indent=1)
left = {p: sum(1 for _, q, _ in tasks if q == p) - sum(1 for q, _ in done if q == p) for p in ('wp', 'wix')}
print('LEFT', left)
pend = [D.datetime.fromisoformat(state[p]) for p in ('wp', 'wix') if left[p] > 0]
print('WAKE_AT', min(pend).isoformat(timespec='minutes') if pend else None)

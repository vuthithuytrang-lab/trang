#!/usr/bin/env python3
"""Đăng bài 'GG Group - Tuấn' (dự án GP) lên Google Group techcombankvietnam qua Gmail API.
Usage: dang_ggr.py check <row> | send <row> | due [phut]   (due: gửi các bài đã tới giờ, rồi chờ gửi tiếp các bài tới giờ trong <phut> phút tới)
Ghi kết quả vào da-dang.jsonl. Không in chìa."""
import datetime, json, os, re, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__))
SK = '/home/user/trang/.claude/skills/share-bai-ggr'
ACC = os.path.join(SK, 'ggr-accounts.local.json')
G = 'techcombankvietnam@googlegroups.com'
LOG = os.path.join(HERE, 'da-dang.jsonl')
TZ = datetime.timezone(datetime.timedelta(hours=7))
CAM = re.compile(r'\b(duy nhất|(?<!Mẫu )(?<!Phụ lục )số 1(?![\d/])|hàng đầu|tốt nhất|cao nhất|rẻ nhất|lớn nhất|uy tín nhất|nhanh nhất|thấp nhất|hiệu quả nhất)\b', re.I)

def say(*a): print(datetime.datetime.now(TZ).strftime('%H:%M:%S'), *a, flush=True)
def plan(): return json.load(open(os.path.join(HERE, 'plan.json'), encoding='utf-8'))
def item(row): return next(x for x in plan() if str(x['row']) == str(row))
def done(): return {json.loads(l)['row'] for l in open(LOG)} if os.path.exists(LOG) else set()

def check(row):
    x = item(row); d = os.path.join(HERE, 'bai', str(row))
    h = open(os.path.join(d, 'ggr.html'), encoding='utf-8').read()
    meta = json.load(open(os.path.join(d, 'meta.json'), encoding='utf-8'))
    text = re.sub(r'<[^>]+>', ' ', h); words = len(text.split()); errs = []
    if not 900 <= words <= 1100: errs.append(f'so tu {words}')
    if re.findall(r'<a\s+href="([^"]+)"', h) != [x['url']]: errs.append('link sai')
    if set(re.findall(r'</?([a-z0-9]+)', h)) - {'p', 'h2', 'h3', 'ul', 'ol', 'li', 'strong', 'a'}: errs.append('the la')
    if CAM.search(text): errs.append('tu cam: ' + CAM.search(text).group(0))
    if re.search(r'<h[23][^>]*>[^<]*(kết luận|tóm lại|tổng kết|tóm tắt|lời kết)', h, re.I): errs.append('co ket luan')
    if not 55 <= len(meta['title']) <= 70: errs.append(f"tieu de {len(meta['title'])}")
    if meta['kw'].lower() not in meta['title'].lower(): errs.append('tieu de thieu kw')
    if 'checklist' in meta['title'].lower(): errs.append('tieu de co checklist')
    return x, meta, words, errs

def run(*cmd):
    return subprocess.run(list(cmd), capture_output=True, text=True, cwd=SK)

def token():
    acc = json.load(open(ACC))[G]
    with tempfile.TemporaryDirectory() as t:
        out = os.path.join(t, 'r.json')
        run('bash', 'scripts/ggr-http.sh', 'refresh-token', acc['client_id'], acc['client_secret'], acc['refresh_token'], out)
        r = run('node', 'scripts/ggr-json.js', 'save-refreshed-access-token', ACC, G, out)
        if r.returncode: raise SystemExit('refresh token loi')
    return json.load(open(ACC))[G]['access_token']

def send(row):
    x, meta, words, errs = check(row)
    if errs: return 0, {'error': errs}
    at = token()
    with tempfile.TemporaryDirectory() as t:
        pay, out, msg = (os.path.join(t, n) for n in ('p.json', 's.json', 'm.json'))
        run('node', 'scripts/ggr-json.js', 'build-mime-message', os.path.join(HERE, 'bai', str(row), 'ggr.html'), meta['title'], G, pay)
        r = run('bash', 'scripts/ggr-http.sh', 'gmail-send', at, pay, out)
        code = int(re.search(r'HTTP_STATUS:(\d+)', r.stdout).group(1))
        res = json.load(open(out))
        if code // 100 != 2 or 'id' not in res: return code, res
        run('bash', 'scripts/ggr-http.sh', 'gmail-get-message', at, res['id'], msg)
        mid = run('node', 'scripts/ggr-json.js', 'extract-message-id', msg).stdout.strip().splitlines()[-1]
        link = run('node', 'scripts/ggr-json.js', 'build-permalink', G, mid).stdout.strip().splitlines()[-1]
    now = datetime.datetime.now(TZ)
    rec = {'row': x['row'], 'gmail_id': res['id'], 'url': link, 'sent': now.isoformat(timespec='minutes'),
           'when': x['when'], 'title': meta['title'], 'words': words}
    open(LOG, 'a').write(json.dumps(rec, ensure_ascii=False) + '\n')
    return 200, rec

def due(minutes=0):
    end = datetime.datetime.now(TZ) + datetime.timedelta(minutes=minutes)
    while True:
        left = sorted([x for x in plan() if x['row'] not in done() and x['when']], key=lambda x: x['when'])
        if not left: say('XONG'); return
        ok = []
        for x in left:
            try: e = check(x['row'])[3]
            except Exception as ex: e = [type(ex).__name__]
            if e: say('CHUA SAN SANG', x['row'], e)
            else: ok.append(x)
        left = ok
        if not left: say('khong co bai san sang'); return
        x = left[0]; t = datetime.datetime.fromisoformat(x['when'])
        now = datetime.datetime.now(TZ)
        if t > end: say('cho', x['row'], x['when']); return
        if t > now: time.sleep(min((t - now).total_seconds(), 300)); continue
        code, r = send(x['row'])
        say('OK' if code == 200 else 'LOI', x['row'], code, (r.get('url') if code == 200 else str(r)[:250]))
        if code != 200: return
        time.sleep(20)

if __name__ == '__main__':
    if sys.argv[1] == 'check':
        x, meta, w, e = check(sys.argv[2]); print(x['row'], w, meta['title'], len(meta['title']), e or 'OK')
    elif sys.argv[1] == 'send': print(send(sys.argv[2]))
    else: due(int(sys.argv[2]) if len(sys.argv) > 2 else 0)

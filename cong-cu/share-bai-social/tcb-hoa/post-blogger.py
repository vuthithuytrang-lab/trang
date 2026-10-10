#!/usr/bin/env python3
"""Hẹn giờ / đăng 1 bài Hoa lên Blogger nganhangtechcombankvietnam.
Usage: post-blogger.py <row> <ISO-time-with-offset>
Tạo nháp rồi publish với publishDate (tương lai = hẹn giờ). Không in token.
Ghi da-dang-blogger.jsonl. Gặp 403/429 thì dừng hẳn (exit 3) để không bị khóa.
"""
import json, os, subprocess, sys, tempfile, datetime, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ACC = '/home/user/trang/.claude/skills/share-bai-blogger/blogger-accounts.local.json'
KEY = 'nganhangtechcombankvietnam.blogspot.com'
DEADLINE = datetime.datetime.fromisoformat('2026-10-11T17:00:00+07:00')
MIN_GAP = 30  # phút, chốt chặn giữa 2 bài bất kỳ trên blog
VN = datetime.timezone(datetime.timedelta(hours=7))


def curl(args, data=None, token=None, form=None):
    cmd = ['curl', '-s', '-m', '90', '-w', '\n%{http_code}']
    tmp = []
    if token:
        h = tempfile.NamedTemporaryFile('w', delete=False); h.write('Authorization: Bearer ' + token + '\n'); h.close()
        cmd += ['-H', '@' + h.name]; tmp.append(h.name)
    if data is not None:
        f = tempfile.NamedTemporaryFile('w', delete=False, suffix='.json'); json.dump(data, f, ensure_ascii=False); f.close()
        cmd += ['-H', 'Content-Type: application/json; charset=utf-8', '--data-binary', '@' + f.name]; tmp.append(f.name)
    if form is not None:
        f = tempfile.NamedTemporaryFile('w', delete=False); f.write(urllib.parse.urlencode(form)); f.close()
        cmd += ['--data-binary', '@' + f.name, '-H', 'Content-Type: application/x-www-form-urlencoded']; tmp.append(f.name)
    out = subprocess.run(cmd + args, capture_output=True, text=True).stdout
    for t in tmp: os.unlink(t)
    body, _, code = out.rpartition('\n')
    try:
        return int(code), json.loads(body) if body else {}
    except ValueError:
        return int(code or 0), {'raw': body[:300]}


def token():
    acc = json.load(open(ACC))[KEY]
    code, r = curl(['-X', 'POST', 'https://oauth2.googleapis.com/token'], form={
        'client_id': acc['client_id'], 'client_secret': acc['client_secret'],
        'refresh_token': acc['refresh_token'], 'grant_type': 'refresh_token'})
    if code != 200: sys.exit(json.dumps({'error': 'refresh_failed', 'code': code, 'detail': r.get('error')}))
    return r['access_token'], acc['blog_id']


def stop_if_limited(code, r, row, step):
    if code in (403, 429):
        print(json.dumps({'error': 'BI_GIOI_HAN', 'code': code, 'row': row, 'step': step,
                          'detail': (r.get('error') or {}).get('message') if isinstance(r.get('error'), dict) else r}))
        sys.exit(3)


def main():
    row, when = sys.argv[1], sys.argv[2]
    t = datetime.datetime.fromisoformat(when)
    if t > DEADLINE: sys.exit(json.dumps({'error': 'qua han chot 17h 11/10', 'row': row}))
    log = os.path.join(HERE, 'da-dang-blogger.jsonl')
    if os.path.exists(log) and any(json.loads(l)['row'] == int(row) for l in open(log)):
        sys.exit(json.dumps({'error': 'row da dang', 'row': row}))
    d = os.path.join(HERE, 'bai', row)
    if subprocess.run([sys.executable, '-I', os.path.join(HERE, 'kiem-tra.py'), d], capture_output=True).returncode:
        sys.exit(json.dumps({'error': 'bai chua qua kiem tra', 'row': row}))
    meta = json.load(open(os.path.join(d, 'meta.json'), encoding='utf-8'))
    tok, blog = token()
    api = f'https://www.googleapis.com/blogger/v3/blogs/{blog}/posts'
    # chốt chặn khoảng cách + chống trùng tiêu đề, dựa trên dữ liệu thật trên blog
    for st in ('live', 'scheduled', 'draft'):
        code, r = curl([api + f'?status={st}&maxResults=100&fetchBodies=false&fields=items(id,title,published,status)'], token=tok)
        stop_if_limited(code, r, row, 'list')
        for p in r.get('items', []):
            if p.get('title') == meta['title']:
                sys.exit(json.dumps({'error': 'da co bai cung tieu de', 'row': row, 'id': p['id'], 'status': p.get('status')}))
            if st != 'draft' and p.get('published'):
                gap = abs((datetime.datetime.fromisoformat(p['published']) - t).total_seconds()) / 60
                if gap < MIN_GAP:
                    sys.exit(json.dumps({'error': f'cach bai khac duoi {MIN_GAP} phut', 'row': row, 'phut': round(gap)}))
    content = open(os.path.join(d, 'wp-hoa.html'), encoding='utf-8').read()
    code, r = curl(['-X', 'POST', api + '/?isDraft=true'], data={'kind': 'blogger#post', 'title': meta['title'], 'content': content}, token=tok)
    stop_if_limited(code, r, row, 'draft')
    if code != 200 or not r.get('id'): sys.exit(json.dumps({'error': 'tao nhap loi', 'row': row, 'code': code, 'detail': str(r)[:300]}))
    pid = r['id']
    now = datetime.datetime.now(datetime.timezone.utc)
    q = '?publishDate=' + urllib.parse.quote(t.isoformat(), safe='') if t > now else ''
    code, r = curl(['-X', 'POST', f'{api}/{pid}/publish{q}'], token=tok)
    stop_if_limited(code, r, row, 'publish')
    if code != 200: sys.exit(json.dumps({'error': 'publish loi (bai dang o dang nhap)', 'row': row, 'id': pid, 'code': code, 'detail': str(r)[:300]}))
    dt = datetime.datetime.fromisoformat(r['published']).astimezone(VN)
    res = {'row': int(row), 'id': pid, 'status': r.get('status'), 'date': dt.isoformat(), 'url': r.get('url'),
           'ngay': f'{dt.day}/{dt.month}/{dt.year}'}
    with open(log, 'a', encoding='utf-8') as f: f.write(json.dumps(res, ensure_ascii=False) + '\n')
    print(json.dumps(res, ensure_ascii=False))


main()

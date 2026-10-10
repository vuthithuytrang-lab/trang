#!/usr/bin/env python3
"""Hẹn giờ 40 bài 'Blogger - Tuấn' lên techcombank2026.blogspot.com.
Dùng lại bài viết ở ../tcb-tuan-11-10/bai/<row>/ (trang WordPress cũ đã bị xóa nên không trùng).
Tạo từng bài cách nhau 8–12 phút (tránh chống spam của Blogger); gặp 403/429 thì chờ 2 tiếng rồi thử lại.
Đợt 10/10: tạo 20 bài cách 3–4,5 phút thì bị 403 ở bài 21 -> nhịp an toàn là >= 8 phút/bài.
Ghi kết quả vào da-dang.jsonl. Không in token."""
import json, os, random, subprocess, sys, tempfile, time, datetime, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
BAI = os.path.join(HERE, '..', 'tcb-tuan-11-10', 'bai')
ACC = '/home/user/trang/.claude/skills/share-bai-blogger/blogger-accounts.local.json'
KEY = 'techcombank2026.blogspot.com'
LOG = os.path.join(HERE, 'da-dang.jsonl')

def curl(args, data=None, token=None):
    cmd = ['curl', '-s', '-m', '60', '-w', '\n%{http_code}']
    tmp = []
    if token:
        h = tempfile.NamedTemporaryFile('w', delete=False); h.write('Authorization: Bearer ' + token + '\n'); h.close()
        cmd += ['-H', '@' + h.name]; tmp.append(h.name)
    if data is not None:
        f = tempfile.NamedTemporaryFile('w', delete=False, suffix='.json'); json.dump(data, f, ensure_ascii=False); f.close()
        cmd += ['-H', 'Content-Type: application/json; charset=utf-8', '--data-binary', '@' + f.name]; tmp.append(f.name)
    out = subprocess.run(cmd + args, capture_output=True, text=True).stdout
    for n in tmp: os.unlink(n)
    body, _, code = out.rpartition('\n')
    try: return int(code or 0), (json.loads(body) if body else {})
    except ValueError: return int(code or 0), {'raw': body[:300]}

def token():
    a = json.load(open(ACC))[KEY]
    code, r = curl(['-X', 'POST', 'https://oauth2.googleapis.com/token', '-d', 'client_id=' + a['client_id'],
                    '-d', 'client_secret=' + a['client_secret'], '-d', 'refresh_token=' + a['refresh_token'], '-d', 'grant_type=refresh_token'])
    if code != 200: raise SystemExit(f'refresh loi {code} {r.get("error")}')
    return r['access_token'], a['blog_id']

def say(*a): print(datetime.datetime.now().strftime('%H:%M:%S'), *a, flush=True)

def post_one(x):
    d = os.path.join(BAI, str(x['row']))
    html = open(os.path.join(d, 'wp.html'), encoding='utf-8').read()
    title = json.load(open(os.path.join(d, 'meta.json'), encoding='utf-8'))['title']
    tok, bid = token()
    base = f'https://www.googleapis.com/blogger/v3/blogs/{bid}/posts/'
    t = datetime.datetime.fromisoformat(x['when'])
    future = (t - datetime.datetime.now(datetime.timezone.utc)).total_seconds() > 120
    code, r = curl([base + '?isDraft=true'], {'title': title, 'content': html}, tok)
    if code != 200: return code, r
    pid = r['id']
    q = '?publishDate=' + urllib.parse.quote(t.isoformat()) if future else ''
    code, r = curl(['-X', 'POST', f'{base}{pid}/publish{q}'], None, tok)
    if code != 200: return code, {'draft_id': pid, **r}
    res = {'row': x['row'], 'tuan_row': x['tuan_row'], 'id': pid, 'url': r.get('url'), 'status': r.get('status'),
           'when': x['when'] if future else datetime.datetime.now().astimezone().isoformat(), 'published': r.get('published')}
    open(LOG, 'a').write(json.dumps(res, ensure_ascii=False) + '\n')
    return 200, res

HAN_CHOT = datetime.datetime.fromisoformat(os.environ.get('HAN_CHOT', '2026-10-11T18:28:00+07:00'))

def replan(plan, done):
    rest = [x for x in plan if x['row'] not in done]
    start = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    gap = (HAN_CHOT - start) / max(len(rest) - 1, 1)
    for i, x in enumerate(rest): x['when'] = (start + gap * i).astimezone(HAN_CHOT.tzinfo).replace(microsecond=0).isoformat()
    json.dump(plan, open(os.path.join(HERE, 'plan.json'), 'w'), ensure_ascii=False, indent=1)
    say('GIAN LAI', len(rest), 'bai, cach', int(gap.total_seconds() // 60), 'phut, tu', rest[0]['when'])

def main():
    plan = json.load(open(os.path.join(HERE, 'plan.json')))
    done = {json.loads(l)['row'] for l in open(LOG)} if os.path.exists(LOG) else set()
    for x in plan:
        if x['row'] in done: continue
        for attempt in range(6):
            if (datetime.datetime.fromisoformat(x['when']) - datetime.datetime.now(datetime.timezone.utc)).total_seconds() < 600:
                replan(plan, done)  # lỡ giờ (vd bị chặn lâu) -> giãn đều phần còn lại tới hạn chót, không dồn bài
            code, r = post_one(x)
            if code == 200:
                say('OK', x['stt'], x['row'], r['status'], r['when'], r['url']); done.add(x['row']); break
            say('LOI', x['stt'], x['row'], code, str(r)[:200])
            if 'draft_id' in r:  # nháp đã tạo nhưng chưa hẹn giờ được -> dừng hẳn để người xử lý
                raise SystemExit('dung: nhap ' + r['draft_id'] + ' chua hen gio')
            if code in (403, 429, 500, 503): time.sleep(int(os.environ.get('CHO_403', 7200))); continue
            raise SystemExit('dung: loi khong thu lai')
        else:
            raise SystemExit('dung: thu lai qua nhieu lan')
        time.sleep(random.randint(int(os.environ.get('GIAN_MIN', 480)), int(os.environ.get('GIAN_MAX', 720))))
    say('XONG')

if __name__ == '__main__': main()

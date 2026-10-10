#!/usr/bin/env python3
"""Đăng bài 'Webflow - Tuấn' lên techcombankvietnam.webflow.io (collection Blog Posts).
Webflow không có hẹn giờ qua API, nên: chuẩn bị trước mỗi bài thành NHÁP (đã có ảnh bìa),
đến giờ thì mới chuyển sang công khai và publish. Tiến trình phải chạy liên tục.
Usage: dang_webflow.py check <row> | run
Ghi kết quả vào da-dang.jsonl (bài đã lên) và nhap.jsonl (bài đã chuẩn bị). Không in chìa."""
import datetime, hashlib, json, os, random, re, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open('/home/user/trang/.claude/skills/share-bai-webflow/webflow-accounts.local.json'))['techcombankvietnam']
API = 'https://api.webflow.com/v2'
LOG, NHAP = os.path.join(HERE, 'da-dang.jsonl'), os.path.join(HERE, 'nhap.jsonl')
CAM = re.compile(r'\b(duy nhất|(?<!Mẫu )(?<!Phụ lục )số 1(?![\d/%])|hàng đầu|tốt nhất|cao nhất|rẻ nhất|lớn nhất|uy tín nhất|nhanh nhất|thấp nhất|hiệu quả nhất)\b', re.I)

def say(*a): print(datetime.datetime.now().strftime('%H:%M:%S'), *a, flush=True)

def call(method, path, data=None):
    with tempfile.NamedTemporaryFile('w', delete=False) as h:
        h.write(f"Authorization: Bearer {A['token']}\nContent-Type: application/json\naccept: application/json\n")
    cmd = ['curl', '-s', '-m', '90', '-w', '\n%{http_code}', '-X', method, '-H', '@' + h.name]
    if data is not None: cmd += ['--data-binary', json.dumps(data, ensure_ascii=False)]
    out = subprocess.run(cmd + [API + path], capture_output=True, text=True).stdout
    os.unlink(h.name)
    body, _, code = out.rpartition('\n')
    try: return int(code or 0), (json.loads(body) if body else {})
    except ValueError: return int(code or 0), {'raw': body[:300]}

def plan(): return json.load(open(os.path.join(HERE, 'plan.json')))
def jl(f): return [json.loads(l) for l in open(f)] if os.path.exists(f) else []

def check(row):
    x = next(x for x in plan() if str(x['row']) == str(row)); d = os.path.join(HERE, 'bai', str(row))
    h = open(os.path.join(d, 'webflow.html'), encoding='utf-8').read()
    meta = json.load(open(os.path.join(d, 'meta.json'), encoding='utf-8'))
    text = re.sub(r'<[^>]+>', ' ', h); words = len(text.split()); errs = []
    if not 900 <= words <= 1100: errs.append(f'so tu {words}')
    if re.findall(r'<a\s+href="([^"]+)"', h) != [x['url']]: errs.append('link sai')
    if set(re.findall(r'</?([a-z0-9]+)', h)) - {'p', 'h2', 'h3', 'ul', 'ol', 'li', 'strong', 'a'}: errs.append('the la')
    if CAM.search(text): errs.append('tu cam: ' + CAM.search(text).group(0))
    if re.search(r'<h[23][^>]*>[^<]*(kết luận|tóm lại|tổng kết|tóm tắt|lời kết)', h, re.I): errs.append('co ket luan')
    if not 55 <= len(meta['title']) <= 70: errs.append(f"tieu de {len(meta['title'])}")
    if x['kw'].lower() not in meta['title'].lower(): errs.append('tieu de thieu kw')
    if re.search(r'checklist|hiểu lầm|ngộ nhận|nhầm lẫn', meta['title'], re.I): errs.append('tieu de trung goc cu')
    if not meta.get('thumb'): errs.append('thieu thumb')
    return x, h, meta, words, errs

def upload_thumb(row, meta):
    png = os.path.join(tempfile.gettempdir(), f"{meta['slug']}.png")
    subprocess.run([sys.executable, os.path.join(HERE, 'thumb.py'), str(row), png], check=True)
    md5 = hashlib.md5(open(png, 'rb').read()).hexdigest()
    code, r = call('POST', f"/sites/{A['site_id']}/assets", {'fileName': os.path.basename(png), 'fileHash': md5})
    if code not in (200, 202): return None, f'asset {code} {str(r)[:150]}'
    form = sum((['-F', f'{k}={v}'] for k, v in r['uploadDetails'].items()), [])
    c = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', *form, '-F', f'file=@{png};type=image/png', r['uploadUrl']],
                       capture_output=True, text=True).stdout
    os.unlink(png)
    if not c.startswith('2'): return None, f'upload {c}'
    return {'fileId': r['id'], 'url': r['hostedUrl'], 'alt': meta['thumb']}, None

def prepare(row):
    x, h, meta, words, errs = check(row)
    if errs: return 0, {'error': errs}
    img, err = upload_thumb(row, meta)
    if err: return 0, {'error': err}
    summary = re.sub(r'<[^>]+>', '', h.splitlines()[0])[:250]
    fd = {'name': meta['title'], 'slug': meta['slug'], A['field_body']: h, A['field_image']: img, 'post-summary': summary}
    code, r = call('POST', f"/collections/{A['collection_id']}/items", {'isDraft': True, 'isArchived': False, 'fieldData': fd})
    if code not in (200, 202): return code, r
    res = {'row': x['row'], 'tuan_row': x['tuan_row'], 'id': r['id'], 'when': x['when'], 'words': words}
    open(NHAP, 'a').write(json.dumps(res, ensure_ascii=False) + '\n')
    return 200, res

def publish(n):
    code, r = call('PATCH', f"/collections/{A['collection_id']}/items/{n['id']}", {'isDraft': False})
    if code != 200: return code, r
    code, r = call('POST', f"/collections/{A['collection_id']}/items/publish", {'itemIds': [n['id']]})
    if code not in (200, 202): return code, r
    slug = json.load(open(os.path.join(HERE, 'bai', str(n['row']), 'meta.json'), encoding='utf-8'))['slug']
    res = {**n, 'url': f"https://{A['site_domain']}/blog/{slug}", 'published_at': datetime.datetime.now().astimezone().isoformat()}
    open(LOG, 'a').write(json.dumps(res, ensure_ascii=False) + '\n')
    return 200, res

def run():
    next_stage = 0  # thời điểm được tạo nháp tiếp theo (không chặn việc đăng bài đến giờ)
    while True:
        rows_done = {n['row'] for n in jl(LOG)}
        if len(rows_done) == len(plan()): say('XONG'); return
        now = datetime.datetime.now(datetime.timezone.utc)
        # 1) đến giờ thì publish bài đã chuẩn bị (chỉ khi trang mẫu Blog Posts đã gắn xong -> có file cho-phep-dang)
        for n in (jl(NHAP) if os.path.exists(os.path.join(HERE, 'cho-phep-dang')) else []):
            if n['row'] in rows_done or datetime.datetime.fromisoformat(n['when']) > now: continue
            code, r = publish(n)
            say('OK' if code == 200 else 'LOI', n['row'], n['when'], r.get('url') if code == 200 else str(r)[:200])
            time.sleep(30)
        # 2) chuẩn bị nháp cho bài sẵn sàng sắp tới (mỗi vòng 1 bài, cách nhau vài phút)
        ready = {int(l) for l in open(os.path.join(HERE, 'san-sang.txt')) if l.strip()} if os.path.exists(os.path.join(HERE, 'san-sang.txt')) else set()
        staged = {n['row'] for n in jl(NHAP)}
        todo = sorted((x for x in plan() if x['row'] in ready and x['row'] not in staged), key=lambda x: x['when'])
        if todo and time.time() >= next_stage:
            code, r = prepare(todo[0]['row'])
            say('NHAP' if code == 200 else 'LOI NHAP', todo[0]['row'], str(r)[:200])
            next_stage = time.time() + random.randint(480, 720)  # tạo nháp thưa ra 8–12 phút/bài
        time.sleep(30)

if __name__ == '__main__':
    if sys.argv[1] == 'check':
        x, _, meta, w, e = check(sys.argv[2]); print(x['row'], w, meta['title'], len(meta['title']), e or 'OK')
    else: run()

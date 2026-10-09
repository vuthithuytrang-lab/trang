#!/usr/bin/env python3
"""Hẹn giờ / đăng 1 bài Hoa lên WordPress nganhangtechcombankvn.
Usage: post-hoa.py <row> <ISO-time-with-offset>
In JSON {row,id,status,date,link,pretty}. Không in token. Ghi thêm vào da-dang.jsonl.
"""
import json, os, re, subprocess, sys, tempfile, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ACC = '/home/user/trang/.claude/skills/share-bai-wp/wp-accounts.local.json'
SITE = 'nganhangtechcombankvn.wordpress.com'
API = 'https://public-api.wordpress.com/rest/v1.1/sites/' + SITE


def curl(args, data=None):
    token = json.load(open(ACC))[SITE]['access_token']
    hdr = tempfile.NamedTemporaryFile('w', delete=False)
    hdr.write('Authorization: Bearer ' + token + '\n'); hdr.close()
    cmd = ['curl', '-s', '-m', '90', '-w', '\n%{http_code}', '-H', '@' + hdr.name]
    f = None
    if data is not None:
        f = tempfile.NamedTemporaryFile('w', delete=False, suffix='.json')
        json.dump(data, f, ensure_ascii=False); f.close()
        cmd += ['-H', 'Content-Type: application/json; charset=utf-8', '--data-binary', '@' + f.name]
    out = subprocess.run(cmd + args, capture_output=True, text=True).stdout
    os.unlink(hdr.name)
    if f: os.unlink(f.name)
    body, _, code = out.rpartition('\n')
    try:
        return int(code), json.loads(body) if body else {}
    except ValueError:
        return int(code or 0), {'raw': body[:300]}


def to_gutenberg(h):
    out = []
    for line in [l.strip() for l in h.splitlines() if l.strip()]:
        if line.startswith('<p'): out.append('<!-- wp:paragraph -->\n' + line + '\n<!-- /wp:paragraph -->')
        elif line.startswith('<h2'): out.append('<!-- wp:heading {"style":{"typography":{"fontSize":"26px"}}} -->\n' + line.replace('<h2>', '<h2 class="wp-block-heading" style="font-size:26px">') + '\n<!-- /wp:heading -->')
        elif line.startswith('<h3'): out.append('<!-- wp:heading {"level":3,"style":{"typography":{"fontSize":"21px"}}} -->\n' + line.replace('<h3>', '<h3 class="wp-block-heading" style="font-size:21px">') + '\n<!-- /wp:heading -->')
        elif line.startswith('<ul'): out.append('<!-- wp:list -->\n<ul class="wp-block-list">')
        elif line.startswith('<ol'): out.append('<!-- wp:list {"ordered":true} -->\n<ol class="wp-block-list">')
        elif line.startswith('</ul'): out.append('</ul>\n<!-- /wp:list -->')
        elif line.startswith('</ol'): out.append('</ol>\n<!-- /wp:list -->')
        elif line.startswith('<li'): out.append('<!-- wp:list-item -->\n' + line + '\n<!-- /wp:list-item -->')
        else: sys.exit(json.dumps({'error': 'dong la khong boc duoc', 'line': line[:80]}))
    return '\n\n'.join(out)


def main():
    row, when = sys.argv[1], sys.argv[2]
    d = os.path.join(HERE, 'bai', row)
    if subprocess.run([sys.executable, '-I', os.path.join(HERE, 'kiem-tra.py'), d]).returncode:
        sys.exit(json.dumps({'error': 'bai chua qua kiem tra', 'row': row}))
    meta = json.load(open(os.path.join(d, 'meta.json'), encoding='utf-8'))
    # không đăng trùng: đã có bài cùng slug trên site thì dừng
    code, r = curl([API + '/posts/slug:' + meta['slug'] + '?fields=ID,status,URL'])
    if code == 200 and r.get('ID'):
        sys.exit(json.dumps({'error': 'da co bai cung slug', 'row': row, 'id': r['ID'], 'status': r.get('status')}))
    # chốt chặn: mọi bài trên site phải cách nhau tối thiểu 55 phút, hạn chót 17h 11/10/2026
    t = datetime.datetime.fromisoformat(when)
    if t > datetime.datetime.fromisoformat('2026-10-11T17:00:00+07:00'):
        sys.exit(json.dumps({'error': 'qua han chot 17h 11/10', 'row': row}))
    code, r = curl([API + '/posts?status=publish,future&number=100&fields=ID,date,slug'])
    for p in [p for p in r.get('posts', []) if p.get('slug') != 'hello-world']:
        gap = abs((datetime.datetime.fromisoformat(p['date']) - t).total_seconds()) / 60
        if gap < 55:
            sys.exit(json.dumps({'error': 'cach bai khac duoi 55 phut', 'row': row, 'bai_gan': p['ID'], 'phut': round(gap)}))
    content = to_gutenberg(open(os.path.join(d, 'wp-hoa.html'), encoding='utf-8').read())
    future = datetime.datetime.fromisoformat(when) > datetime.datetime.now(datetime.timezone.utc)
    code, r = curl(['-X', 'POST', API + '/posts/new'], {
        'title': meta['title'], 'content': content, 'slug': meta['slug'], 'excerpt': meta.get('excerpt', ''),
        'status': 'future' if future else 'publish', 'date': when, 'format': 'standard'})
    if code not in (200, 201) or not r.get('ID'):
        sys.exit(json.dumps({'error': 'dang loi', 'row': row, 'code': code, 'detail': r.get('error') or r.get('message') or r.get('raw')}))
    # API trả giờ UTC; link đẹp + cột J theo giờ Việt Nam (múi giờ site)
    dt = datetime.datetime.fromisoformat(r['date']).astimezone(datetime.timezone(datetime.timedelta(hours=7)))
    pretty = f"https://{SITE}/{dt:%Y/%m/%d}/{r['slug']}/"
    res = {'row': int(row), 'id': r['ID'], 'status': r['status'], 'date': r['date'], 'link': r['URL'], 'pretty': pretty,
           'ngay': f'{dt.day}/{dt.month}/{dt.year}'}
    with open(os.path.join(HERE, 'da-dang.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(res, ensure_ascii=False) + '\n')
    print(json.dumps(res, ensure_ascii=False))


main()

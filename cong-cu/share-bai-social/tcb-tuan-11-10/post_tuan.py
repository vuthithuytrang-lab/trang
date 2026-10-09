#!/usr/bin/env python3
"""Soát + hẹn giờ 1 bài 'WordPress - Tuấn' lên techcombankvn2026.wordpress.com.
Usage: post_tuan.py check <row> | post <row>
Ghi kết quả vào da-dang.jsonl. Không in token."""
import json, os, re, subprocess, sys, tempfile, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = 'techcombankvn2026.wordpress.com'
ACC = '/home/user/trang/.claude/skills/share-bai-wp/wp-accounts.local.json'
CAM = re.compile(r'\b(duy nhất|(?<!Mẫu )(?<!Phụ lục )số 1(?![\d/])|hàng đầu|tốt nhất|cao nhất|rẻ nhất|lớn nhất|uy tín nhất|nhanh nhất|thấp nhất|hiệu quả nhất)\b', re.I)
KETLUAN = re.compile(r'<h[23][^>]*>[^<]*(kết luận|tóm lại|tổng kết|tóm tắt|lời kết)', re.I)
ALLOWED = {'p','h2','h3','ul','ol','li','strong','a'}

def plan(row):
    return next(x for x in json.load(open(os.path.join(HERE, 'plan.json'))) if str(x['row']) == str(row))

def check(row):
    x = plan(row); d = os.path.join(HERE, 'bai', str(row))
    html = open(os.path.join(d, 'wp.html'), encoding='utf-8').read()
    meta = json.load(open(os.path.join(d, 'meta.json'), encoding='utf-8'))
    text = re.sub(r'<[^>]+>', ' ', html); words = len(text.split())
    links = re.findall(r'<a\s+href="([^"]+)"', html)
    tags = set(re.findall(r'</?([a-z0-9]+)', html))
    errs = []
    if not 900 <= words <= 1100: errs.append(f'so tu {words}')
    if links != [x['url']]: errs.append(f'link {links}')
    if tags - ALLOWED: errs.append(f'the la {tags-ALLOWED}')
    if CAM.search(text): errs.append('tu cam: ' + CAM.search(text).group(0))
    if KETLUAN.search(html): errs.append('co phan ket luan')
    if not 55 <= len(meta['title']) <= 70: errs.append(f"tieu de {len(meta['title'])} ky tu")
    if x['kw'].lower() not in meta['title'].lower(): errs.append('tieu de thieu kw')
    if re.search(r'1800|@techcombank', text): errs.append('hotline/email')
    return x, html, meta, words, errs

def to_gutenberg(html):
    out = []
    for line in [l.strip() for l in html.splitlines() if l.strip()]:
        if line.startswith('<p'): out.append('<!-- wp:paragraph -->\n' + line + '\n<!-- /wp:paragraph -->')
        elif line.startswith('<h2'): out.append('<!-- wp:heading {"style":{"typography":{"fontSize":"26px"}}} -->\n' + line.replace('<h2>', '<h2 class="wp-block-heading" style="font-size:26px">') + '\n<!-- /wp:heading -->')
        elif line.startswith('<h3'): out.append('<!-- wp:heading {"level":3,"style":{"typography":{"fontSize":"21px"}}} -->\n' + line.replace('<h3>', '<h3 class="wp-block-heading" style="font-size:21px">') + '\n<!-- /wp:heading -->')
        elif line.startswith('<ul'): out.append('<!-- wp:list -->\n<ul class="wp-block-list">')
        elif line.startswith('<ol'): out.append('<!-- wp:list {"ordered":true} -->\n<ol class="wp-block-list">')
        elif line.startswith('</ul'): out.append('</ul>\n<!-- /wp:list -->')
        elif line.startswith('</ol'): out.append('</ol>\n<!-- /wp:list -->')
        elif line.startswith('<li'): out.append('<!-- wp:list-item -->\n' + line + '\n<!-- /wp:list-item -->')
        else: out.append(line)
    return '\n\n'.join(out)

def post(row):
    x, html, meta, words, errs = check(row)
    if errs: sys.exit(json.dumps({'row': x['row'], 'error': errs}, ensure_ascii=False))
    log = os.path.join(HERE, 'da-dang.jsonl')
    if os.path.exists(log) and any(json.loads(l)['row'] == x['row'] for l in open(log)):
        sys.exit(json.dumps({'row': x['row'], 'error': 'da dang roi'}))
    t = datetime.datetime.fromisoformat(x['when'])
    if (t - datetime.datetime.now(datetime.timezone.utc)).total_seconds() < 120:
        sys.exit(json.dumps({'row': x['row'], 'error': 'qua gio hen'}))
    tok = json.load(open(ACC))[SITE]['access_token']
    payload = {'title': meta['title'], 'content': to_gutenberg(html), 'slug': meta['slug'], 'status': 'future', 'date': x['when']}
    with tempfile.NamedTemporaryFile('w', delete=False) as h: h.write('Authorization: Bearer ' + tok + '\n')
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f: json.dump(payload, f, ensure_ascii=False)
    out = subprocess.run(['curl', '-s', '-m', '60', '-w', '\n%{http_code}', '-H', '@' + h.name, '-H', 'Content-Type: application/json; charset=utf-8',
                          '--data-binary', '@' + f.name, f'https://public-api.wordpress.com/rest/v1.1/sites/{SITE}/posts/new'], capture_output=True, text=True).stdout
    os.unlink(h.name); os.unlink(f.name)
    body, _, code = out.rpartition('\n'); r = json.loads(body)
    if code != '200' or r.get('status') != 'future': sys.exit(json.dumps({'row': x['row'], 'error': code, 'detail': str(r)[:300]}))
    url = f"https://{SITE}/{t:%Y/%m/%d}/{r['slug']}/"
    res = {'row': x['row'], 'tuan_row': x['tuan_row'], 'id': r['ID'], 'url': url, 'status': r['status'], 'when': x['when'], 'words': words}
    open(log, 'a').write(json.dumps(res, ensure_ascii=False) + '\n'); print(json.dumps(res, ensure_ascii=False))

if __name__ == '__main__':
    if sys.argv[1] == 'check':
        x, _, meta, w, e = check(sys.argv[2]); print(x['row'], w, meta['title'], len(meta['title']), e or 'OK')
    else: post(sys.argv[2])

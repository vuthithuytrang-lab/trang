#!/usr/bin/env python3
"""Đăng / hẹn giờ 1 bài lên Blogger hoặc WordPress.
Usage: post.py <blogger|wp> <row> <ISO-time-with-offset or 'now'>
In ra JSON {platform,row,url,status,id,when}. Không in token.
"""
import json, os, re, subprocess, sys, tempfile, datetime, urllib.parse

SKILLS = '/home/user/trang/.claude/skills'
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bai')
BLOG_KEY = 'nganhangtechcombankvn.blogspot.com'
WP_SITE = 'techcombankvietnam.wordpress.com'


def curl(args, data=None, token=None):
    hdr = None
    cmd = ['curl', '-s', '-m', '60', '-w', '\n%{http_code}']
    if token:
        hdr = tempfile.NamedTemporaryFile('w', delete=False)
        hdr.write('Authorization: Bearer ' + token + '\n'); hdr.close()
        cmd += ['-H', '@' + hdr.name]
    if data is not None:
        f = tempfile.NamedTemporaryFile('w', delete=False, suffix='.json')
        json.dump(data, f, ensure_ascii=False); f.close()
        cmd += ['-H', 'Content-Type: application/json; charset=utf-8', '--data-binary', '@' + f.name]
    out = subprocess.run(cmd + args, capture_output=True, text=True).stdout
    if hdr: os.unlink(hdr.name)
    if data is not None: os.unlink(f.name)
    body, _, code = out.rpartition('\n')
    try:
        return int(code), json.loads(body) if body else {}
    except ValueError:
        return int(code or 0), {'raw': body[:300]}


def blogger_token():
    p = os.path.join(SKILLS, 'share-bai-blogger/blogger-accounts.local.json')
    acc = json.load(open(p))[BLOG_KEY]
    code, r = curl(['-X', 'POST', 'https://oauth2.googleapis.com/token',
                    '-d', 'client_id=' + acc['client_id'], '-d', 'client_secret=' + acc['client_secret'],
                    '-d', 'refresh_token=' + acc['refresh_token'], '-d', 'grant_type=refresh_token'])
    if code != 200: sys.exit(json.dumps({'error': 'refresh_failed', 'code': code, 'detail': r.get('error')}))
    return r['access_token'], acc['blog_id']


def to_gutenberg(html):
    out = []
    for line in [l.strip() for l in html.splitlines() if l.strip()]:
        if line.startswith('<p'): out.append('<!-- wp:paragraph -->\n' + line + '\n<!-- /wp:paragraph -->')
        elif line.startswith('<h2'): out.append('<!-- wp:heading -->\n' + line.replace('<h2>', '<h2 class="wp-block-heading">') + '\n<!-- /wp:heading -->')
        elif line.startswith('<h3'): out.append('<!-- wp:heading {"level":3} -->\n' + line.replace('<h3>', '<h3 class="wp-block-heading">') + '\n<!-- /wp:heading -->')
        elif line.startswith('<ul'): out.append('<!-- wp:list -->\n<ul class="wp-block-list">')
        elif line.startswith('<ol'): out.append('<!-- wp:list {"ordered":true} -->\n<ol class="wp-block-list">')
        elif line.startswith('</ul'): out.append('</ul>\n<!-- /wp:list -->')
        elif line.startswith('</ol'): out.append('</ol>\n<!-- /wp:list -->')
        elif line.startswith('<li'): out.append('<!-- wp:list-item -->\n' + line + '\n<!-- /wp:list-item -->')
        else: out.append(line)
    return '\n\n'.join(out)


def main():
    plat, row, when = sys.argv[1], sys.argv[2], sys.argv[3]
    d = os.path.join(BASE, row)
    meta = json.load(open(os.path.join(d, 'meta.json')))
    now = datetime.datetime.now(datetime.timezone.utc)
    t = now if when == 'now' else datetime.datetime.fromisoformat(when)
    future = (t - now).total_seconds() > 120
    if plat == 'blogger':
        tok, bid = blogger_token()
        html = open(os.path.join(d, 'blogger.html')).read()
        url = f'https://www.googleapis.com/blogger/v3/blogs/{bid}/posts/'
        if len(sys.argv) > 4:
            code, r = 200, {'id': sys.argv[4]}
        else:
            code, r = curl([url + ('?isDraft=true' if future else '')], {'title': meta['title_blogger'], 'content': html}, tok)
        if code != 200: sys.exit(json.dumps({'error': 'create', 'code': code, 'detail': str(r)[:300]}))
        if future:
            code, r = curl(['-X', 'POST', f"{url}{r['id']}/publish?publishDate={urllib.parse.quote(t.isoformat())}"], None, tok)
            if code != 200: sys.exit(json.dumps({'error': 'schedule', 'code': code, 'detail': str(r)[:300]}))
        res = {'id': r['id'], 'url': r.get('url'), 'status': r.get('status')}
    else:
        p = os.path.join(SKILLS, 'share-bai-wp/wp-accounts.local.json')
        tok = json.load(open(p))[WP_SITE]['access_token']
        html = to_gutenberg(open(os.path.join(d, 'wp.html')).read())
        payload = {'title': meta['title_wp'], 'content': html, 'slug': meta['slug'],
                   'status': 'future' if future else 'publish'}
        if future: payload['date'] = t.isoformat()
        code, r = curl([f'https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}/posts/new'], payload, tok)
        if code != 200: sys.exit(json.dumps({'error': 'create', 'code': code, 'detail': str(r)[:300]}))
        res = {'id': r['ID'], 'url': r.get('URL'), 'status': r.get('status')}
    res.update(platform=plat, row=int(row), when=t.isoformat())
    print(json.dumps(res, ensure_ascii=False))


main()

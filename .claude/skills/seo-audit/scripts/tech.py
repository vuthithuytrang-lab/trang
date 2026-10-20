#!/usr/bin/env python3
"""Bước 6 — chỉ số kỹ thuật cấp trang cho trang mình và trang top của mỗi cụm."""
import argparse, json, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import clean, crawl_many, is_js_rendered

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data')
ap.add_argument('--topn', type=int, default=3, help='lấy trang đứng top N của mỗi từ khoá')
ap.add_argument('--workers', type=int, default=10)
a = ap.parse_args()
ME = json.load(open(f'{a.data}/meta.json'))['domain']
KW = json.load(open(f'{a.data}/kw.json'))
P = {clean(p['url']): p for p in json.load(open(f'{a.data}/pages.json'))}
urls = {u for u in P if ME in u}
for r in KW:
    for p, d, u in r['serp']:
        if p <= a.topn and d != ME and u in P: urls.add(u)
path = f'{a.data}/tech.json'
done = {clean(r['url']): r for r in (json.load(open(path)) if os.path.exists(path) else []) if not r.get('error')}
todo = sorted(urls - set(done))
print(f"{len(urls)} URL cần chỉ số kỹ thuật · {len(todo)} chưa có")
if todo:
    for r in crawl_many(todo, a.workers):
        if not r.get('error'): done[clean(r['url'])] = r
keep = ('url', 'ttfb', 'kb', 'imgs_all', 'noalt', 'h1n', 'h1', 'title', 'desc', 'canonical',
        'robots', 'og', 'scripts', 'inline', 'css', 'jumps')
out = []
for u, r in done.items():
    d = {k: r.get(k) for k in keep}
    d['imgs'] = r.get('imgs_all', 0)
    d['tlen'] = len(r.get('title') or ''); d['dlen'] = len(r.get('desc') or '')
    out.append(d)
json.dump(out, open(path, 'w'), ensure_ascii=False)
mine = [r for r in out if ME in r['url']]
riv = [r for r in out if ME not in r['url']]
if mine and riv:
    med = lambda g, k: st.median([x[k] for x in g])
    pc = lambda g, f: f"{sum(1 for x in g if f(x))*100//len(g)}%"
    print(f"\n{'Chỉ số':30s}{'mình':>10}{'đối thủ top':>14}")
    for lab, k in [('TTFB (ms)', 'ttfb'), ('Ảnh thiếu alt', 'noalt'), ('Độ dài title', 'tlen'),
                   ('Độ dài description', 'dlen'), ('Script ngoài', 'scripts'), ('CSS ngoài', 'css')]:
        print(f"{lab:30s}{med(mine,k):10.0f}{med(riv,k):14.0f}")
    for lab, f in [('Có đúng 1 H1', lambda x: x['h1n'] == 1),
                   ('Nhảy cấp heading', lambda x: x['jumps'] > 0),
                   ('Title trên 60 ký tự', lambda x: x['tlen'] > 60),
                   ('Có ảnh thiếu alt', lambda x: x['noalt'] > 0)]:
        print(f"{lab:30s}{pc(mine,f):>10}{pc(riv,f):>14}")

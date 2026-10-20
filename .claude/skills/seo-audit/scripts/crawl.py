#!/usr/bin/env python3
"""Bước 3 và 5 — crawl toàn bộ SERP. Xét TẤT CẢ đối thủ, không lọc top 3."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import SOCIAL, crawl_many, is_js_rendered

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data')
ap.add_argument('--depth', type=int, default=10, help='độ sâu SERP crawl, mặc định top 10')
ap.add_argument('--add', help='file JSON danh sách URL bổ sung (bước 5)')
ap.add_argument('--workers', type=int, default=10)
a = ap.parse_args()
KW = json.load(open(f'{a.data}/kw.json'))
ME = json.load(open(f'{a.data}/meta.json'))['domain']
path = f'{a.data}/pages.json'
done = {}
if os.path.exists(path):
    done = {p['url']: p for p in json.load(open(path)) if not p.get('error')}

urls = set()
for r in KW:
    for p, d, u in r['serp']:
        if p <= a.depth and d not in SOCIAL:
            urls.add(u)
    for p, u in r['allmine']:
        urls.add(u.split('?')[0])
if a.add:
    urls |= set(json.load(open(a.add)))
todo = sorted(urls - set(done))
print(f"{len(urls)} URL trong tập · {len(done)} đã có · {len(todo)} cần crawl")
if todo:
    res = crawl_many(todo, a.workers)
    for r in res:
        if not r.get('error'): done[r['url']] = r
    err = [r for r in res if r.get('error')]
    print(f"crawl xong · lỗi {len(err)}")
    for r in err[:10]: print("   ", r['url'][:80], r['error'][:50])
P = list(done.values())
json.dump(P, open(path, 'w'), ensure_ascii=False)
js = [p for p in P if is_js_rendered(p)]
mine = [p for p in P if ME in p['url']]
print(f"\nTổng {len(P)} trang đo được · của mình {len(mine)} · đối thủ {len(P)-len(mine)}")
print(f"CỔNG CHẶN: {len(js)} trang render JavaScript, loại khỏi mọi bảng so sánh")
for p in js[:8]: print(f"   {p['words']} từ · {p['kb']}KB · {p['url'][:80]}")

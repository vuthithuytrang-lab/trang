#!/usr/bin/env python3
"""Cổng chặn bắt buộc — kiểm tình trạng thật của mọi URL nội bộ trước khi kết luận.

Không đề xuất sửa một trang khi chưa biết trang đó còn sống hay không. Script phân loại
mọi URL của mình xuất hiện trong file check top và trong Search Console thành:
200 index được · 200 nhưng noindex · canonical trỏ nơi khác · 301/302 · 404/410 · 5xx · lỗi mạng.

    python3 scripts/verify_urls.py --data data

Kết quả ghi vào data/url_status.json, các script sau đọc lại để loại URL đã 301.
Xem references/verify.md.
"""
import argparse, collections, json, os, re, sys, warnings
warnings.filterwarnings('ignore')
import requests
import concurrent.futures as cf
sys.path.insert(0, os.path.dirname(__file__))
from lib import UA, clean

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data')
ap.add_argument('--min-imp', type=int, default=1,
                help='chỉ kiểm URL có từ N hiển thị GSC trở lên; URL trong file check top luôn kiểm')
ap.add_argument('--workers', type=int, default=10)
a = ap.parse_args()

ME = json.load(open(f'{a.data}/meta.json'))['domain']
KW = json.load(open(f'{a.data}/kw.json'))

# nguồn 1: mọi URL của mình từng xuất hiện trong file check top
urls = {clean(u) for r in KW for _, u in r['allmine']}
imp = collections.Counter()
# nguồn 2: mọi URL của mình có hiển thị trên Search Console
p_gsc = f'{a.data}/gsc_qp.json'
if os.path.exists(p_gsc):
    for r in json.load(open(p_gsc)):
        u = clean(r['keys'][1])
        if ME in u:
            imp[u] += r['impressions']
    urls |= {u for u, i in imp.items() if i >= a.min_imp}
urls = sorted(urls)


def check(u):
    out = {'url': u, 'imp': imp.get(u, 0)}
    try:
        r = requests.get(u, headers={'User-Agent': UA}, timeout=25, verify=False,
                         allow_redirects=False)
        out['status'] = r.status_code
        if r.status_code in (301, 302, 303, 307, 308):
            out['target'] = r.headers.get('Location', '')
            # đi hết chuỗi chuyển hướng, tối đa 5 chặng
            chain, cur = [], r
            for _ in range(5):
                loc = cur.headers.get('Location')
                if not loc: break
                nxt = requests.get(loc if loc.startswith('http') else u.split('/')[0] + '//' + u.split('/')[2] + loc,
                                   headers={'User-Agent': UA}, timeout=25, verify=False,
                                   allow_redirects=False)
                chain.append((nxt.url, nxt.status_code))
                if nxt.status_code < 300 or nxt.status_code >= 400: break
                cur = nxt
            out['chain'] = chain
            out['final'] = chain[-1][1] if chain else None
            return out
        if r.status_code == 200:
            body = requests.get(u, headers={'User-Agent': UA}, timeout=25, verify=False).text
            can = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', body)
            rob = re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)', body)
            out['canonical'] = can.group(1) if can else ''
            out['robots'] = rob.group(1) if rob else ''
            out['noindex'] = 'noindex' in (out['robots'] or '').lower()
            out['words'] = len(re.findall(r'\w+', re.sub(r'<[^>]+>', ' ', body), flags=re.UNICODE))
    except Exception as e:
        out['error'] = str(e)[:90]
    return out


print(f"kiểm {len(urls)} URL nội bộ (file check top + Search Console)")
res = []
with cf.ThreadPoolExecutor(a.workers) as ex:
    for r in ex.map(check, urls):
        res.append(r)
json.dump({r['url']: r for r in res}, open(f'{a.data}/url_status.json', 'w'), ensure_ascii=False)

def grp(f): return sorted([r for r in res if f(r)], key=lambda x: -x.get('imp', 0))
redir = grp(lambda r: r.get('status') in (301, 302, 303, 307, 308))
gone = grp(lambda r: r.get('status') in (404, 410))
err5 = grp(lambda r: isinstance(r.get('status'), int) and r['status'] >= 500)
neterr = grp(lambda r: 'error' in r)
noidx = grp(lambda r: r.get('noindex'))
xcan = grp(lambda r: r.get('canonical') and clean(r['canonical']) != clean(r['url']))
thin = grp(lambda r: r.get('status') == 200 and 0 < r.get('words', 999) < 300)
ok = [r for r in res if r.get('status') == 200 and not r.get('noindex')]

print(f"\n{'Tình trạng':38s}{'số URL':>8}   Ý nghĩa với báo cáo")
rows = [
    ('200, index được', len(ok), 'dùng bình thường'),
    ('301/302 đã chuyển hướng', len(redir), 'KHÔNG tính là ăn thịt từ khoá, không đề xuất sửa'),
    ('404/410 đã mất', len(gone), 'PHẢI xử lý trước: khôi phục hoặc 301 về trang thay thế'),
    ('5xx lỗi máy chủ', len(err5), 'kiểm lại hạ tầng trước khi kết luận gì về nội dung'),
    ('lỗi mạng khi kiểm', len(neterr), 'kiểm thủ công, không suy đoán'),
    ('200 nhưng noindex', len(noidx), 'không bao giờ lên top được, đừng đề xuất tối ưu nội dung'),
    ('canonical trỏ nơi khác', len(xcan), 'thứ hạng dồn về trang canonical, xét lại vai trò'),
    ('200 nhưng dưới 300 từ', len(thin), 'có thể render bằng JavaScript, xem cổng chặn 1'),
]
for lab, n, note in rows:
    print(f"{lab:38s}{n:>8}   {note}")

def dump(title, items, extra=lambda r: ''):
    if not items: return
    print(f"\n--- {title} ---")
    for r in items[:15]:
        print(f"   {r.get('imp',0):>7} hiển thị · {r['url'].replace('https://www.'+ME,'').replace('https://'+ME,'') or '/'}{extra(r)}")

dump('404 hoặc 410 — xử lý trước khi làm bất cứ việc gì khác', gone)
dump('5xx — lỗi máy chủ', err5)
dump('noindex — không thể lên top', noidx, lambda r: f"  [{r.get('robots','')}]")
dump('301/302 — loại khỏi phép đếm ăn thịt từ khoá', redir,
     lambda r: f"  → {r.get('target','')[:70]}" + (f"  (chặng cuối {r['final']})" if r.get('final') and r['final'] != 200 else ''))
dump('canonical trỏ nơi khác', xcan, lambda r: f"  → {r['canonical'][:70]}")
dump('dưới 300 từ', thin, lambda r: f"  ({r.get('words')} từ)")

bad = [r for r in redir if r.get('final') and r['final'] != 200]
if bad:
    print(f"\nCẢNH BÁO: {len(bad)} URL chuyển hướng tới đích không phải 200 — chuỗi hỏng, phải sửa.")
print("\nĐọc kỹ trước khi viết đề xuất: không đề xuất sửa nội dung cho URL 404, 5xx hay noindex;")
print("không tính URL đã 301 là ăn thịt từ khoá; URL có canonical khác thì xét vai trò trước.")

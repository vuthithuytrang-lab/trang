#!/usr/bin/env python3
"""Cổng chặn trước khi dựng báo cáo — không mục nào được thiếu vì lười quét.

Duyệt từng cụm, kiểm dữ liệu của từng mục, rồi chia chỗ thiếu làm hai loại:

  QUÉT BÙ ĐƯỢC   dữ liệu tồn tại ngoài kia, chỉ là chưa lấy về. Phải quét thêm.
                 Ví dụ: URL đối thủ trong SERP chưa crawl, tech.py chưa chạy cho
                 trang của mình, gsc_analysis.json còn theo bộ cụm cũ.
  KHÔNG CÓ THẬT  đã quét hết mà vẫn không có, vì thực tế là không có. Ví dụ:
                 domain của mình không nằm trong SERP đã đo của cụm đó.

Chỉ loại thứ hai mới được phép hiện dòng "không đủ dữ liệu" trong báo cáo. Loại thứ
nhất phải quét, không được ẩn và cũng không được ghi chú cho qua.

    python3 scripts/precheck.py --data data           # chỉ báo cáo
    python3 scripts/precheck.py --data data --fix     # tự chạy các lệnh quét bù

build_report.py gọi script này trước khi dựng và dừng lại nếu còn chỗ quét bù được.
"""
import argparse, collections, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import clean, is_js_rendered, SOCIAL

HERE = os.path.dirname(os.path.abspath(__file__))

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data')
ap.add_argument('--fix', action='store_true', help='tự chạy lệnh quét bù thay vì chỉ liệt kê')
ap.add_argument('--depth', type=int, default=10, help='độ sâu SERP cần có đủ dữ liệu')
ap.add_argument('--site', help='property GSC, dùng khi cần chạy lại gsc.py')
ap.add_argument('--quiet', action='store_true')
a = ap.parse_args()

D = a.data
def L(p, d=None):
    return json.load(open(f'{D}/{p}')) if os.path.exists(f'{D}/{p}') else d

META = L('meta.json') or sys.exit('thiếu data/meta.json — chạy parse_ranktracker.py trước')
ME = META['domain']
KW = L('kw.json') or []
CLU = (L('clusters.json') or {}).get('clusters') or []
PAGES = L('pages.json') or []
P = {clean(p['url']): p for p in PAGES}
TECH = {clean(t['url']): t for t in (L('tech.json') or [])}
UST = L('url_status.json') or {}
GSCA = L('gsc_analysis.json') or {}
QP = L('gsc_qp.json')
BYKW = {r['kw']: r for r in KW}

todo = collections.OrderedDict()   # nhãn -> dict(vì sao, lệnh, số lượng)
real = collections.Counter()       # mục -> số cụm thực sự không có dữ liệu


def need(key, why, cmd, n=1):
    e = todo.setdefault(key, dict(why=why, cmd=cmd, n=0))
    e['n'] += n


# ── 1. Bộ cụm đổi mà các bước sau chưa chạy lại ────────────────────────────────
CIDS = sorted((c.get('cid') or c['name']) for c in CLU)
if QP is None:
    need('gsc', 'chưa lấy Search Console — mục 15 sẽ trống ở mọi cụm',
         f"python3 {HERE}/gsc.py --site <property> --days 90 --data {D}")
elif not GSCA:
    need('gsc_analyze', 'có dữ liệu Search Console thô nhưng chưa tổng hợp theo cụm',
         f"python3 {HERE}/gsc_analyze.py --data {D}")
else:
    sig = (GSCA.get('sig') or {}).get('cids')
    bc = GSCA.get('by_cluster') or {}
    stale = sig != CIDS if sig else (len(set(bc) & set(CIDS)) < 0.8 * len(CIDS))
    if stale:
        need('gsc_analyze',
             f'gsc_analysis.json còn theo bộ cụm cũ ({len(bc)} cụm) trong khi clusters.json '
             f'có {len(CLU)} cụm — đã phân cụm lại mà quên chạy lại bước này',
             f"python3 {HERE}/gsc_analyze.py --data {D}")

# ── 2. URL trong SERP chưa crawl ───────────────────────────────────────────────
want_riv, want_mine = set(), set()
for r in KW:
    for pos, d, u in r.get('serp', []):
        if pos <= a.depth and d != ME and d not in SOCIAL:
            want_riv.add(clean(u))
    for _, u in r.get('allmine', []):
        want_mine.add(clean(u))
miss_riv = {u for u in want_riv if u not in P}
miss_mine = {u for u in want_mine if u not in P}
if miss_riv or miss_mine:
    _ex = f'{D}/extra_urls.json'
    json.dump(sorted(miss_riv | miss_mine), open(_ex, 'w'), ensure_ascii=False)
    if miss_riv:
        need('crawl_riv', f'{len(miss_riv)} URL đối thủ trong top {a.depth} chưa crawl — '
                          f'mục 2, 6, 16 sẽ thiếu đối chứng',
             f"python3 {HERE}/crawl.py --data {D} --add {_ex}", len(miss_riv))
    if miss_mine:
        need('crawl_mine', f'{len(miss_mine)} URL của mình đang xếp hạng nhưng chưa crawl — '
                           f'mục 3, 9, 12, 16, 17 sẽ thiếu',
             f"python3 {HERE}/crawl.py --data {D} --add {_ex}", len(miss_mine))

# ── 3. Chỉ số kỹ thuật thiếu cho trang đang xếp hạng ───────────────────────────
have_mine = {u for u in want_mine if u in P}
no_tech = {u for u in have_mine if u not in TECH}
if not TECH:
    need('tech', 'chưa chạy tech.py — mục 17 trống ở mọi cụm',
         f"python3 {HERE}/tech.py --data {D}")
elif no_tech:
    need('tech', f'{len(no_tech)} trang của mình chưa có chỉ số kỹ thuật — mục 17 thiếu',
         f"python3 {HERE}/tech.py --data {D}", len(no_tech))

# ── 4. Tình trạng URL chưa kiểm ────────────────────────────────────────────────
_ust = {clean(u) for u in UST}
no_st = {u for u in have_mine if u not in _ust}
if not UST:
    need('verify', 'chưa kiểm tình trạng URL — không được kết luận gì khi chưa biết '
                   'URL đang 200, 404, 301 hay noindex',
         f"python3 {HERE}/verify_urls.py --data {D}")
elif len(no_st) > 0.2 * max(len(have_mine), 1):
    need('verify', f'{len(no_st)}/{len(have_mine)} URL của mình chưa biết tình trạng',
         f"python3 {HERE}/verify_urls.py --data {D}", len(no_st))

# ── 5. Duyệt từng cụm: chỗ nào thiếu thật, chỗ nào do chưa quét ────────────────
per_cluster = []
for c in CLU:
    rows = [BYKW[k] for k in c['kws'] if k in BYKW]
    myu = {clean(u) for r in rows for _, u in r.get('allmine', [])}
    riv = {clean(u) for r in rows for pos, d, u in r.get('serp', [])
           if pos <= a.depth and d != ME and d not in SOCIAL}
    riv_have = {u for u in riv if u in P and not is_js_rendered(P[u])}
    riv_js = {u for u in riv if u in P and is_js_rendered(P[u])}
    riv_no = riv - set(P)
    gone = []
    if not myu:
        real['trangminh'] += 1; real['doithucontent'] += 1; real['tech2'] += 1
        gone.append('3·16·17 — mình không có mặt trong SERP đã đo của cụm này')
    elif not riv_have:
        if riv_no:
            gone.append(f'16 — {len(riv_no)} trang đối thủ chưa crawl')
        else:
            real['doithucontent'] += 1
            gone.append(f'16 — cả {len(riv_js)} trang đối thủ đều render JavaScript, bị loại')
    if gone and not a.quiet:
        per_cluster.append((c['name'], len(rows), gone))

# ── Chống lặp: quét bù hai lần vẫn không lấy được thì thôi, không chặn mãi ────
_rp = f'{D}/precheck_runs.json'
RUNS = L('precheck_runs.json') or {}
hard = {k: e for k, e in todo.items() if RUNS.get(k, 0) >= 2}
for k in hard:
    todo.pop(k)

# ── Báo cáo ───────────────────────────────────────────────────────────────────
print(f'Kiểm {len(CLU)} cụm · {len(KW)} từ khoá · {len(P)} trang đã crawl\n')
if todo:
    print('PHẢI QUÉT BÙ — dữ liệu có ngoài kia, chưa lấy về. Không được ẩn mục, phải quét:')
    for k, e in todo.items():
        print(f"   [{k}] {e['why']}")
        print(f"        {e['cmd']}")
    print()
else:
    print('Không còn gì để quét bù — mọi nguồn đã đầy đủ.\n')

if real:
    print('KHÔNG CÓ THẬT — đã quét hết, thực tế là không có. Mục vẫn hiện kèm lý do:')
    lab = {'trangminh': 'mục 3 trang của mình', 'doithucontent': 'mục 16 nội dung đối thủ',
           'tech2': 'mục 17 kỹ thuật'}
    for k, n in real.most_common():
        print(f'   {lab.get(k, k):32s}{n:3d} cụm')
    print()

if per_cluster and not a.quiet:
    print(f'Chi tiết {len(per_cluster)} cụm có mục trống:')
    for nm, n, gone in per_cluster[:25]:
        print(f'   {nm[:40]:40s} {n:3d} kw   {"; ".join(gone)}')
    if len(per_cluster) > 25:
        print(f'   ... còn {len(per_cluster)-25} cụm')
    print()

if hard:
    print('ĐÃ QUÉT BÙ 2 LẦN VẪN KHÔNG LẤY ĐƯỢC — nguồn chặn hoặc URL hỏng.')
    print('Không chặn nữa, nhưng phải ghi rõ trong báo cáo là thiếu vì lý do gì:')
    for k, e in hard.items():
        print(f"   [{k}] {e['why']}")
    print()

if a.fix and todo:
    print('--- CHẠY QUÉT BÙ ---')
    seen = set()
    for k, e in todo.items():
        cmd = e['cmd']
        if cmd in seen: continue
        seen.add(cmd)
        if '<property>' in cmd:
            if a.site:
                cmd = cmd.replace('<property>', a.site)
            else:
                print(f'   BỎ QUA {k}: cần --site để chạy {cmd}')
                continue
        print(f'   $ {cmd}', flush=True)
        rc = subprocess.call(cmd, shell=True)
        if rc != 0:
            print(f'   lệnh thoát mã {rc} — xử lý rồi chạy lại precheck')
    for k in todo: RUNS[k] = RUNS.get(k, 0) + 1
    json.dump(RUNS, open(_rp, 'w'))
    print('\nChạy lại precheck để xác nhận đã hết chỗ quét bù.')

sys.exit(2 if todo else 0)

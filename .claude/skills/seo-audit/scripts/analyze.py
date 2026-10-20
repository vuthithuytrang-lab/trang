#!/usr/bin/env python3
"""Bước 7 và 8 — đo khoảng cách, bốn phép đo cấu trúc, tính khả thi từ mục tiêu."""
import argparse, collections, json, os, re, statistics as st, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import SOCIAL, clean, dom, is_js_rendered, nrm, tier_pool, REF_RATES as REF

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data')
ap.add_argument('--goals', default='top10=85,top5=70,top3=50')
ap.add_argument('--exclude', help='file text: mỗi dòng một từ khoá lệch ý định, loại khỏi kho')
a = ap.parse_args()
KW = json.load(open(f'{a.data}/kw.json'))
META = json.load(open(f'{a.data}/meta.json'))
ME = META['domain']
P = {clean(p['url']): p for p in json.load(open(f'{a.data}/pages.json'))}
JS = {u for u, p in P.items() if is_js_rendered(p)}
CLU = json.load(open(f'{a.data}/clusters.json'))['clusters']
GOALS = dict((k, int(v)) for k, v in (x.split('=') for x in a.goals.split(',')))
BAD = set()
if a.exclude and os.path.exists(a.exclude):
    BAD = {l.strip() for l in open(a.exclude, encoding='utf-8') if l.strip()}

TOT = len(KW)
pos = {r['kw']: r['pos'] for r in KW}
def cnt(lo, hi): return sum(1 for r in KW if r['pos'] and lo <= r['pos'] <= hi)
cur = {'top3': cnt(1, 3), 'top5': cnt(1, 5), 'top10': cnt(1, 10)}
pool = {t: tier_pool(KW, t, BAD) for t in ('4-5', '6-10', '11-20', '21-50', '>50')}

print(f"=== MỤC TIÊU TRƯỚC, TÍNH NGƯỢC TỶ LỆ CẦN THIẾT ===")
print(f"{'Mốc':7s}{'hiện':>6}{'%':>7}{'mục tiêu':>10}{'cần thêm':>10}{'kho khả dụng':>14}{'tỷ lệ cần':>11}  đánh giá")
summary = {}
for mark in ('top3', 'top5', 'top10'):
    if mark not in GOALS: continue
    goal = round(TOT * GOALS[mark] / 100)
    need = goal - cur[mark]
    src = [t for t, *_ in REF[mark]]
    kho = sum(len(pool[t]) for t in src)
    rate = need / kho if kho else 9
    cap = sum(len(pool[t]) * r[3] for t in src for r in REF[mark] if r[0] == t)
    verdict = 'ĐẠT ĐƯỢC' if cap >= need else f'KHÔNG ĐẠT, thiếu {round(need-cap)} từ khoá'
    print(f"{mark:7s}{cur[mark]:6d}{cur[mark]*100/TOT:6.1f}%{goal:10d}{need:10d}{kho:14d}{rate*100:10.0f}%  {verdict}")
    summary[mark] = dict(cur=cur[mark], goal=goal, need=need, pool=kho, rate=round(rate, 3), cap=round(cap))
print("\n  Tỷ lệ cần so với ba mức tham chiếu (thận trọng / cơ sở / triệt để):")
for mark in ('top3', 'top5', 'top10'):
    if mark not in GOALS: continue
    for t, c1, c2, c3 in REF[mark]:
        print(f"   {mark:6s} từ tầng {t:6s} kho {len(pool[t]):3d} · mức {c1:.0%} / {c2:.0%} / {c3:.0%}")

print("\n=== BỐN PHÉP ĐO CẤU TRÚC ===")
root = blog = 0
for r in KW:
    for p, d, u in r['serp']:
        if p <= 3 and d != ME and d not in SOCIAL:
            (blog if re.search(r'/(blog|tin-tuc|kien-thuc|cam-nang|bai-viet|news)/', u) else root)
            if re.search(r'/(blog|tin-tuc|kien-thuc|cam-nang|bai-viet|news)/', u): blog += 1
            else: root += 1
byroot = [r['pos'] for r in KW if r['pos'] and r['url'] and '/blog/' not in r['url']]
byblog = [r['pos'] for r in KW if r['pos'] and r['url'] and '/blog/' in r['url']]
print(f"1. Trang dịch vụ so với blog")
print(f"   đối thủ: {root*100//max(root+blog,1)}% lượt top 3 nằm trên URL cấp gốc")
if byroot: print(f"   mình cấp gốc: {len(byroot)} kw · trung vị {st.median(byroot):.0f} · top3 {sum(1 for p in byroot if p<=3)*100//len(byroot)}%")
if byblog: print(f"   mình blog   : {len(byblog)} kw · trung vị {st.median(byblog):.0f} · top3 {sum(1 for p in byblog if p<=3)*100//len(byblog)}%")
myurls = {clean(u) for r in KW for p, u in r['allmine']}
u3 = {clean(u) for r in KW for p, u in r['allmine'] if p <= 3}
cover = sum(1 for r in KW if r['pos'])
print(f"2. Độ phân tán URL: {len(myurls)} URL cho {cover} kw = {cover/max(len(myurls),1):.1f} kw/URL · {len(u3)} URL có top3 = {cur['top3']/max(len(u3),1):.1f} kw top3/URL")
can = sum(1 for r in KW if r['nurl'] >= 2)
print(f"3. Ăn thịt từ khoá theo file check top: {can}/{TOT} = {can*100//TOT}%")
mine_p = [p for u, p in P.items() if ME in u]
t3p = set()
for r in KW:
    for p, d, u in r['serp']:
        if p <= 3 and d != ME and u in P and u not in JS: t3p.add(u)
ENT = {'Organization', 'LocalBusiness', 'PostalAddress', 'GeoCoordinates', 'ContactPoint', 'Place'}
f = lambda g: sum(1 for p in g if ENT & set(p['schemas'])) * 100 // max(len(g), 1)
print(f"4. Schema thực thể: mình {f(mine_p)}% · trang top3 {f([P[u] for u in t3p])}%")

print("\n=== NGƯỠNG LỌT TOP THEO CỤM ===")
print(f"{'Cụm':34s}{'kw':>4}{'top10':>7}{'từ':>7}{'ảnh':>6}{'ilink':>7}{'H2/H3':>8}")
res = {}
for c in CLU:
    ks = set(c['kws'])
    rows = [r for r in KW if r['kw'] in ks]
    E = {}
    for r in rows:
        for p, d, u in r['serp']:
            if p <= 10 and d != ME and u in P and u not in JS: E[u] = P[u]
    t10 = sum(1 for r in rows if r['pos'] and r['pos'] <= 10)
    if len(E) >= 5:
        med = lambda k: st.median([p[k] for p in E.values()])
        res[c['name']] = {k: med(k) for k in ('words', 'imgs_all', 'ilinks', 'h2', 'h3', 'kb')}
        print(f"{c['name'][:34]:34s}{len(rows):4d}{t10:7d}{med('words'):7.0f}{med('imgs_all'):6.0f}{med('ilinks'):7.0f}"
              f"{str(int(med('h2')))+'/'+str(int(med('h3'))):>8}")
    else:
        print(f"{c['name'][:34]:34s}{len(rows):4d}{t10:7d}   mẫu quá nhỏ, bỏ qua")
json.dump(dict(goals=summary, thresholds=res), open(f'{a.data}/analysis.json', 'w'), ensure_ascii=False)

print("\n=== CHỈ SỐ THEO TẦNG VỊ TRÍ — on-page có phân biệt được không ===")
T = collections.defaultdict(dict)
for r in KW:
    for p, d, u in r['serp']:
        if d == ME or u not in P or u in JS: continue
        t = '1-3' if p <= 3 else '4-5' if p <= 5 else '6-7' if p <= 7 else '8-10' if p <= 10 else None
        if t: T[t][u] = P[u]
tiers = ['1-3', '4-5', '6-7', '8-10']
print(f"{'Chỉ số':22s}" + ''.join(f"{t:>10}" for t in tiers))
for lab, k in [('Số từ', 'words'), ('Số ảnh', 'imgs_all'), ('Link nội bộ', 'ilinks'), ('H2', 'h2'), ('H3', 'h3')]:
    print(f"{lab:22s}" + ''.join(f"{st.median([p[k] for p in T[t].values()]) if T[t] else 0:10.0f}" for t in tiers))
print(f"{'(số trang)':22s}" + ''.join(f"{len(T[t]):10d}" for t in tiers))
print("\nNếu các dòng trên gần bằng nhau giữa tầng 1-3 và 8-10 thì on-page KHÔNG phải yếu tố")
print("quyết định thứ hạng trong top 10 — phải nói thẳng điều đó trong báo cáo.")

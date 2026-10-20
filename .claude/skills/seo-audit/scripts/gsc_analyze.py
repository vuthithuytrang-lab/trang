#!/usr/bin/env python3
"""Ăn thịt từ khoá thật + hiệu quả theo cụm, từ Search Console. Chạy sau verify_urls.py."""
import argparse, collections, json, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import clean, nrm

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data')
ap.add_argument('--min-imp', type=int, default=30)
a = ap.parse_args()
ME = json.load(open(f'{a.data}/meta.json'))['domain']
QP = json.load(open(f'{a.data}/gsc_qp.json'))
KW = json.load(open(f'{a.data}/kw.json'))
CLU = json.load(open(f'{a.data}/clusters.json'))['clusters']
status = {}
if os.path.exists(f'{a.data}/url_status.json'):
    status = json.load(open(f'{a.data}/url_status.json'))
else:
    print("CẢNH BÁO: chưa chạy verify_urls.py — kết quả có thể tính nhầm URL đã 301")
REDIR = {clean(u) for u, v in status.items() if v.get('status') in (301, 302, 308)}

byq = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0.0]))
for r in QP:
    p = clean(r['keys'][1])
    if p in REDIR: continue
    d = byq[nrm(r['keys'][0])][p]
    d[0] += r['impressions']; d[1] += r['clicks']; d[2] += r['position'] * r['impressions']
for q in byq:
    for p, d in byq[q].items():
        if d[0]: d[2] /= d[0]

kwset = {nrm(r['kw']): r for r in KW}
can = wrong = 0
detail = {}
for q, v in byq.items():
    if q not in kwset: continue
    s = sorted(v.items(), key=lambda x: -x[1][0])
    iscan = len(s) >= 2 and s[0][1][0] >= a.min_imp and s[1][1][0] >= 0.2 * s[0][1][0]
    if iscan: can += 1
    big = [x for x in s if x[1][0] >= 100]
    w = None
    if len(big) >= 2:
        bi, bp = big[0], min(big, key=lambda x: x[1][2])
        if bp[0] != bi[0] and bi[1][2] - bp[1][2] >= 5:
            wrong += 1
            w = (bi[0], round(bi[1][2], 1), bp[0], round(bp[1][2], 1), bi[1][0])
    detail[q] = dict(urls=[(p, d[0], d[1], round(d[2], 1)) for p, d in s[:6]], can=iscan, wrong=w)
print(f"Từ khoá trong bộ theo dõi có dữ liệu GSC: {len(detail)}/{len(KW)}")
print(f"Bị ăn thịt (URL#2 >= 20% hiển thị của URL#1): {can} = {can*100//max(len(detail),1)}%")
print(f"Google ưu tiên URL kém hơn >= 5 bậc: {wrong}")

eater = collections.Counter(); eimp = collections.Counter()
for q, d in detail.items():
    if not d['can']: continue
    for p, i, c, pos in d['urls'][1:4]:
        eater[p] += 1; eimp[p] += i
print(f"\nURL chen vào nhiều từ khoá nhất:")
for p, n in eater.most_common(10):
    print(f"   {n:4d} kw · {eimp[p]:7,d} hiển thị   {p}")

crawled = {clean(p['url']) for p in json.load(open(f'{a.data}/pages.json'))}
newu = [(p, i) for p, i in eimp.most_common() if p not in crawled]
if newu:
    json.dump([p for p, i in newu], open(f'{a.data}/extra_urls.json', 'w'))
    print(f"\n{len(newu)} URL đang tranh chấp mà chưa crawl — chạy:")
    print(f"   python3 crawl.py --data {a.data} --add {a.data}/extra_urls.json")
    for p, i in newu[:10]: print(f"   {i:7,d} hiển thị   {p}")

out = {}
for c in CLU:
    ks = {nrm(k) for k in c['kws']}
    rows = [d for q, d in detail.items() if q in ks]
    imp = sum(u[1] for d in rows for u in d['urls'])
    clk = sum(u[2] for d in rows for u in d['urls'])
    poss = [st.median([u[3] for u in d['urls']]) for d in rows if d['urls']]
    serp = [r['pos'] for r in KW if r['kw'] in set(c['kws']) and r['pos']]
    out[c.get('cid') or c['name']] = dict(name=c['name'], imp=imp, clicks=clk, ctr=round(clk * 100 / max(imp, 1), 3),
                          can=sum(1 for d in rows if d['can']), nkw=len(c['kws']),
                          gsc_pos=round(st.median(poss), 1) if poss else None,
                          serp_pos=round(st.median(serp), 1) if serp else None)
# chữ ký bộ cụm: build_report đối chiếu để bắt trường hợp phân cụm lại mà quên chạy lại bước này
_sig = dict(n=len(CLU), cids=sorted((c.get('cid') or c['name']) for c in CLU))
json.dump(dict(by_cluster=out, detail=detail, sig=_sig),
          open(f'{a.data}/gsc_analysis.json', 'w'), ensure_ascii=False)
print(f"\n{'Cụm':34s}{'kw':>4}{'ăn thịt':>9}{'hiển thị':>11}{'click':>7}{'CTR':>8}{'vt file':>9}{'vt GSC':>8}")
for n, d in sorted(out.items(), key=lambda x: -x[1]['imp']):
    print(f"{n[:34]:34s}{d['nkw']:4d}{d['can']:9d}{d['imp']:11,d}{d['clicks']:7d}{d['ctr']:7.2f}%{str(d['serp_pos']):>9}{str(d['gsc_pos']):>8}")
print("\nNhắc: cột vt file là thứ hạng thật. Cột vt GSC là vị trí trung bình có trọng số")
print("theo hiển thị, gộp mọi thiết bị và tỉnh thành — thấp hơn là bình thường, không dùng")
print("để phủ nhận thứ hạng đo được.")

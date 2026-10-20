#!/usr/bin/env python3
"""Bước 2 — phân cụm theo SERP, thuật toán centroid. Xem references/clustering.md."""
import argparse, collections, json, os, sys, unicodedata
sys.path.insert(0, os.path.dirname(__file__))
from lib import SOCIAL, slugify

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data')
ap.add_argument('--min-shared', type=int, default=4)
ap.add_argument('--merge-small', type=int, default=3)
ap.add_argument('--merge-cluster', type=float, default=0.7)
ap.add_argument('--depth', type=int, default=10)
a = ap.parse_args()
KW = json.load(open(f'{a.data}/kw.json'))
META = json.load(open(f'{a.data}/meta.json'))
ME = META['domain']

S = {r['kw']: {u for p, d, u in r['serp']
               if p <= a.depth and d not in SOCIAL and d != ME} for r in KW}
rest = [r['kw'] for r in KW]
groups = []
while rest:
    deg = {k: sum(1 for k2 in rest if k2 != k and len(S[k] & S[k2]) >= a.min_shared) for k in rest}
    seed = max(rest, key=lambda k: (deg[k], -len(k)))
    g = [seed] + [k for k in rest if k != seed and len(S[seed] & S[k]) >= a.min_shared]
    groups.append({'seed': seed, 'kws': g})
    rest = [k for k in rest if k not in set(g)]

big = [g for g in groups if len(g['kws']) >= 3]
small = [g for g in groups if len(g['kws']) < 3]
for g in small:
    best, bs = None, 0
    for G in big:
        ov = max((len(S[k] & S[G['seed']]) for k in g['kws']), default=0)
        if ov > bs: bs, best = ov, G
    if best and bs >= a.merge_small:
        best['kws'] += g['kws']; g['merged'] = True
# Không bỏ sót từ khoá nào: cụm nhỏ không gộp được thì đứng riêng thành cụm của chính nó,
# kể cả cụm chỉ có một từ khoá. Không còn khái niệm "từ khoá đơn lẻ".
big += [g for g in small if not g.get('merged')]
left = []

changed = True
while changed:
    changed = False
    for i in range(len(big)):
        for j in range(i + 1, len(big)):
            x, y = S[big[i]['seed']], S[big[j]['seed']]
            if x and y and len(x & y) / min(len(x), len(y)) >= a.merge_cluster:
                big[i]['kws'] += big[j]['kws']; big.pop(j); changed = True; break
        if changed: break
big.sort(key=lambda g: -len(g['kws']))

allg = collections.Counter()
for r in KW:
    w = unicodedata.normalize('NFC', r['kw']).lower().split()
    for n in (4, 3, 2):
        for i in range(len(w) - n + 1): allg[' '.join(w[i:i + n])] += 1

def suggest(kws):
    if len(kws) == 1:
        return kws[0]
    c = collections.Counter()
    for k in kws:
        w = unicodedata.normalize('NFC', k).lower().split()
        seen = set()
        for n in (4, 3, 2):
            for i in range(len(w) - n + 1):
                g = ' '.join(w[i:i + n])
                if g not in seen: seen.add(g); c[g] += 1
    best, bs = None, 0
    for g, n in c.items():
        if n < len(kws) * 0.5: continue
        sc = (n / len(kws)) * (n / allg[g]) * (1 + 0.35 * len(g.split()))
        if sc > bs: bs, best = sc, g
    return best or min(kws, key=len)

pos = {r['kw']: r['pos'] for r in KW}
out = []
_used = {}
for g in big:
    ks = g['kws']
    nm = suggest(ks)
    sl = slugify(nm) or 'cum'
    # slug phải duy nhất, nếu không file báo cáo của cụm này sẽ ghi đè cụm kia
    if sl in _used:
        _used[sl] += 1
        sl = f'{sl}-{_used[sl]}'
    else:
        _used[sl] = 1
    # cid là khoá nối giữa các bước, suy từ slug nên duy nhất và KHÔNG đổi khi
    # agent đặt lại tên cụm. Mọi file sinh sau đều tra theo cid, không tra theo name.
    out.append(dict(cid=sl, name=nm, name_auto=True, seed=g['seed'], kws=ks, slug=sl))
json.dump(dict(clusters=out, orphan=left), open(f'{a.data}/clusters.json', 'w'), ensure_ascii=False)
_tot = sum(len(g['kws']) for g in out)
assert _tot == len(KW), f'THIẾU từ khoá: {_tot}/{len(KW)} — mọi từ khoá phải nằm trong một cụm'
_sz = collections.Counter(len(g['kws']) for g in out)
print(f"{len(out)} cụm · {_tot}/{len(KW)} từ khoá — không bỏ sót từ khoá nào")
print(f"   cụm >=5 kw: {sum(v for k, v in _sz.items() if k >= 5)} · "
      f"2–4 kw: {sum(v for k, v in _sz.items() if 2 <= k <= 4)} · 1 kw: {_sz.get(1, 0)}\n")
print(f"{'#':>3} {'Tên gợi ý':38s}{'kw':>4}{'top10':>7}{'top3':>6}  hạt giống")
for i, g in enumerate(out, 1):
    ks = g['kws']
    t3 = sum(1 for k in ks if pos[k] and pos[k] <= 3)
    t10 = sum(1 for k in ks if pos[k] and pos[k] <= 10)
    print(f"{i:>3} {g['name'][:38]:38s}{len(ks):4d}{t10:7d}{t3:6d}  {g['seed'][:40]}")
_dup = [n for n, c in collections.Counter(g['name'] for g in out).items() if c > 1]
if _dup:
    print(f"\n{len(_dup)} tên gợi ý bị trùng giữa các cụm — bắt buộc đặt lại tên khác nhau:")
    for n in _dup[:8]: print(f"   {n}")
print("\nBẮT BUỘC: đọc lại danh sách và đặt tên tiếng Việt có nghĩa cho từng cụm,")
print("ghi đè trường name trong data/clusters.json rồi mới chạy bước sau.")

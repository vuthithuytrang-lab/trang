#!/usr/bin/env python3
"""Bước 1 — đọc file check top rank tracker. Chấp nhận cả top 10 lẫn top 100."""
import argparse, csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import dom, clean, SOCIAL

ap = argparse.ArgumentParser()
ap.add_argument('--csv', required=True)
ap.add_argument('--domain', required=True)
ap.add_argument('--out', default='data')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
ME = a.domain.lower().replace('www.', '')

rows = [r for r in csv.reader(open(os.path.expanduser(a.csv), encoding='utf-8-sig')) if r]
hdr = next((r for r in rows[:5] if r and r[0].strip() == 'Keyword'), None)
if not hdr:
    sys.exit('Không tìm thấy dòng tiêu đề có cột Keyword')
days = [c for c in hdr if re.fullmatch(r'\d{4}-\d{2}-\d{2}', c.strip())]
if not days:
    sys.exit('Không tìm thấy cột ngày dạng YYYY-MM-DD')

serp, cur = {}, None
for r in rows[rows.index(hdr) + 1:]:
    if len(r) < 3 or r[0].strip() == 'Keyword':
        continue
    if r[0].strip():
        cur = r[0].strip()
    if cur is None:
        continue
    serp.setdefault(cur, {d: {} for d in days})
    for di, d in enumerate(days):
        pi, ui = 1 + di * 3, 2 + di * 3
        if ui >= len(r):
            continue
        p, u = r[pi].strip(), r[ui].strip()
        if p.isdigit() and u.startswith('http'):
            serp[cur][d][int(p)] = u

first, last = days[0], days[-1]
depth = max((max(v[last].keys()) for v in serp.values() if v[last]), default=10)
out = []
for kw, dv in serp.items():
    s, s0 = dv[last], dv[first]
    mine = [(p, u) for p, u in sorted(s.items()) if dom(u) == ME]
    mine0 = [(p, u) for p, u in sorted(s0.items()) if dom(u) == ME]
    out.append(dict(
        kw=kw, pos=mine[0][0] if mine else None, url=mine[0][1] if mine else None,
        pos0=mine0[0][0] if mine0 else None, nurl=len(mine), allmine=mine,
        serp=[(p, dom(u), clean(u)) for p, u in sorted(s.items())],
        top10=[(p, dom(u), clean(u)) for p, u in sorted(s.items()) if p <= 10],
        depth=len(s)))
json.dump(out, open(f'{a.out}/kw.json', 'w'), ensure_ascii=False)
json.dump(dict(domain=ME, days=days, first=first, last=last, depth=depth,
               n_kw=len(out)), open(f'{a.out}/meta.json', 'w'), ensure_ascii=False)

n10 = sum(1 for r in out if r['pos'] and r['pos'] <= 10)
n5 = sum(1 for r in out if r['pos'] and r['pos'] <= 5)
n3 = sum(1 for r in out if r['pos'] and r['pos'] <= 3)
print(f"{len(out)} từ khoá · độ sâu SERP top {depth} · mốc {first} → {last}")
print(f"{a.domain}: top3 {n3} ({n3*100//len(out)}%) · top5 {n5} ({n5*100//len(out)}%) · top10 {n10} ({n10*100//len(out)}%)")
if not n10 and not any(r['pos'] for r in out):
    print("CẢNH BÁO: không tìm thấy domain trong file. Kiểm tra lại tham số --domain")

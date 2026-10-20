#!/usr/bin/env python3
"""Bước 4 — Search Console. Tự dò credential theo GSC_CREDENTIALS_FILE / GSC_CREDENTIALS_DIR."""
import argparse, datetime as dt, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ap = argparse.ArgumentParser()
ap.add_argument('--site', required=True, help='property GSC, ví dụ https://www.abc.com/')
ap.add_argument('--days', type=int, default=90)
ap.add_argument('--end', help='YYYY-MM-DD, mặc định hôm qua')
ap.add_argument('--data', default='data')
ap.add_argument('--cred', help='đường dẫn credential, bỏ trống thì tự dò')
a = ap.parse_args()

from auth import credential_candidates, load_credentials
from googleapiclient.discovery import build

def find_cred(site):
    if a.cred: return a.cred
    for p in credential_candidates():
        try:
            svc = build('searchconsole', 'v1', credentials=load_credentials(p), cache_discovery=False)
            sites = [s['siteUrl'] for s in svc.sites().list().execute().get('siteEntry', [])]
        except Exception:
            continue
        if site in sites:
            print(f"dùng credential: {os.path.basename(p)}")
            return p
    sys.exit(f"Không credential nào có quyền với {site}. Đặt GSC_CREDENTIALS_DIR hoặc "
             f"GSC_CREDENTIALS_FILE trỏ tới credential có quyền (xác thực bằng /seo-analyst), hoặc truyền --cred.")

cred = find_cred(a.site)
svc = build('searchconsole', 'v1', credentials=load_credentials(cred), cache_discovery=False)
end = dt.date.fromisoformat(a.end) if a.end else dt.date.today() - dt.timedelta(days=3)
start = end - dt.timedelta(days=a.days - 1)

def query(dims, limit=100000):
    rows, sr = [], 0
    while True:
        r = svc.searchanalytics().query(siteUrl=a.site, body={
            'startDate': str(start), 'endDate': str(end), 'dimensions': dims,
            'rowLimit': 25000, 'startRow': sr}).execute().get('rows', [])
        rows += r
        if len(r) < 25000 or len(rows) >= limit: break
        sr += 25000
    return rows

os.makedirs(a.data, exist_ok=True)
qp = query(['query', 'page'])
pg = query(['page'])
json.dump(qp, open(f'{a.data}/gsc_qp.json', 'w'), ensure_ascii=False)
json.dump(pg, open(f'{a.data}/gsc_page.json', 'w'), ensure_ascii=False)
json.dump(dict(site=a.site, start=str(start), end=str(end)), open(f'{a.data}/gsc_meta.json', 'w'))
print(f"{start} → {end} · {len(qp)} dòng query×page · {len(pg)} trang")
print(f"clicks {sum(r['clicks'] for r in pg):,} · impressions {sum(r['impressions'] for r in pg):,}")
print("\nBƯỚC TIẾP THEO BẮT BUỘC: chạy verify_urls.py trước khi tính ăn thịt từ khoá.")

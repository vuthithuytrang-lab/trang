"""Lấy giá ca cao thế giới từ API công khai của trang sản phẩm ICE (ice.com).
NY = ICE US Cocoa Futures (productId 578, hubId 727, USD/tấn); London = ICE Europe London Cocoa (15246/17450, GBP/tấn).
Mỗi kỳ hạn: giá khớp gần nhất (lastPrice, lastTime GMT) + giá chốt phiên trước (ngày gần nhất trong lịch sử ngày, trước ngày của lastTime).
Cách chạy: python3 -I lay_gia_ice.py <file-ra.json>"""
import json, sys, urllib.request, datetime
BASE = 'https://www.ice.com/marketdata/api/productguide/charting/'
SAN = {'newyork': (578, 727, 'https://www.ice.com/products/7/Cocoa-Futures/data'),
       'london': (15246, 17450, 'https://www.ice.com/products/37089076/London-Cocoa-Futures/data')}
def get(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=60))
kq = {'lay_luc_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), 'san': {}}
for ten, (p, h, trang) in SAN.items():
    rows = []
    for c in get(f'{BASE}contract-data?productId={p}&hubId={h}&mode=2'):
        hist = get(f'{BASE}data/historical?marketId={c["marketId"]}&historicalSpan=1').get('bars', [])
        last_day = None
        if c.get('lastTime'):
            last_day = datetime.datetime.strptime(c['lastTime'][:10], '%m/%d/%Y').date()
        prev = None
        for d, v in reversed(hist):
            dd = datetime.datetime.strptime(d, '%a %b %d %H:%M:%S %Y').date()
            if last_day is None or dd < last_day:
                prev = (dd.isoformat(), v); break
        r = {'ky_han': c['marketStrip'], 'gia': c['lastPrice'], 'luc': c['lastTime'], 'pct': c['change'],
             'chot_truoc_ngay': prev[0] if prev else None, 'chot_truoc': prev[1] if prev else None,
             'lich_su_cuoi': hist[-3:]}
        if r['gia'] is not None and r['chot_truoc'] is not None:
            r['thay_doi'] = round(r['gia'] - r['chot_truoc'], 2)
        rows.append(r)
    kq['san'][ten] = {'trang': trang, 'api': f'{BASE}contract-data?productId={p}&hubId={h}&mode=2', 'ky_han': rows}
json.dump(kq, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
for ten, s in kq['san'].items():
    print(ten)
    for r in s['ky_han']:
        print(' ', r['ky_han'], r['gia'], r['luc'], 'chốt trước', r['chot_truoc_ngay'], r['chot_truoc'], 'đổi', r.get('thay_doi'), 'pct', round(r['pct'] or 0, 3))

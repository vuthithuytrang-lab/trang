#!/usr/bin/env python3
"""Kiểm tra sức khỏe các trang trước mỗi lượt đăng.
Cách chạy: python3 check_sites.py <thư mục dự án>
- Mở trang chủ từng nền tảng trong du-an.json.
- Nền tảng nào trả 410 / 404 / 451, hoặc không trả 200 mà báo "suspended" → coi là BỊ KHÓA:
  đặt lịch nền tảng đó trong state.json thành 2099 (dừng hẳn) và in BLOCKED <nền tảng>.
In OK <nền tảng> nếu bình thường. Không in chìa."""
import json, os, subprocess, sys

PROJ = os.path.abspath(sys.argv[1]); os.chdir(PROJ)
cfg = json.load(open('du-an.json'))
state = json.load(open('state.json')) if os.path.exists('state.json') else {}
homes = {'wp': 'https://' + cfg.get('wordpress', {}).get('site', '') + '/',
         'wix': cfg.get('wix', {}).get('trang_chu', '')}
changed = False
for plat in cfg.get('nen_tang', []):
    url = homes.get(plat)
    if not url or url == 'https:///':
        print('SKIP', plat, '(chưa khai báo trang chủ)'); continue
    out = subprocess.run(['curl', '-s', '-L', '-m', '40', '-w', '\n%{http_code}', url], capture_output=True, text=True).stdout
    body, _, code = out.rpartition('\n')
    # Dựa vào mã trả về; chữ "suspended" chỉ xét khi trang không trả 200 (mã JS của Wix có sẵn chữ này)
    blocked = code in ('410', '404', '451') or (code != '200' and 'suspended' in body.lower())
    if blocked:
        print('BLOCKED', plat, code, url)
        state[plat] = '2099-01-01T00:00:00+07:00'; changed = True
    else:
        print('OK', plat, code)
if changed:
    json.dump(state, open('state.json', 'w'), indent=1)

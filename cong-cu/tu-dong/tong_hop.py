#!/usr/bin/env python3
"""Gom kết quả chay.sh của các bài thành thư mục xuất: <mã>.html + trang-thai.json (Apps Script đọc file này).
Dùng: python3 tong_hop.py <thư mục ket-qua> <thư mục xuất>"""
import datetime, json, os, re, shutil, sys

kq, ra = sys.argv[1], sys.argv[2]
os.makedirs(ra, exist_ok=True)
luc = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
tt = {}
for f in sorted(os.listdir(kq)):
    if not f.endswith('.log'):
        continue
    ma = f[:-4]
    log = open(os.path.join(kq, f), encoding='utf-8', errors='replace').read()
    ten = re.search(r'^bai1 (.+?): \d+ bảng lãi suất', log, re.M)
    ngay = re.search(r'^XONG \S+ ngày (\S+)', log, re.M)
    html = os.path.join(kq, ma, 'bai.html')
    ok = bool(ngay and ten and os.path.exists(html))
    duyet = [l.strip() for l in log.splitlines()
             if re.search(r'cần duyệt:|LỖI:|KHÔNG ĐỌC ĐƯỢC|KHÔNG đọc được', l)]
    duyet = list(dict.fromkeys(re.sub(r'^\s*(cần duyệt:\s*)', '', l) for l in duyet))
    tt[ma] = {'ok': ok, 'luc': luc, 'ngay': ngay.group(1) if ngay else '', 'ten': ten.group(1) if ten else '',
              'can_duyet': '\n'.join(duyet)[:1500], 'loi': '' if ok else (log.strip().splitlines() or ['?'])[-1][:200]}
    if ok:
        shutil.copy(html, os.path.join(ra, ma + '.html'))
json.dump(tt, open(os.path.join(ra, 'trang-thai.json'), 'w'), ensure_ascii=False, indent=1)
for ma, v in tt.items():
    print(('✔' if v['ok'] else '✘'), ma, v['ten'] or v['loi'])

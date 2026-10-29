#!/usr/bin/env python3
"""Gom kết quả chay.sh của các bài vào thư mục xuất: <mã>.html + trang-thai.json (Apps Script đọc file này).
Bài không chạy lần này giữ nguyên kết quả cũ trong thư mục xuất. "_yeu_cau" = mã phiếu Drive vừa xử lý, "_ntfy" = mốc yêu cầu trang công khai.
Dùng: python3 tong_hop.py <thư mục ket-qua> <thư mục xuất> [mã phiếu]"""
import datetime, json, os, re, shutil, sys

kq, ra = sys.argv[1], sys.argv[2]
os.makedirs(ra, exist_ok=True)
luc = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
p_tt = os.path.join(ra, 'trang-thai.json')
tt = json.load(open(p_tt)) if os.path.exists(p_tt) else {}
if len(sys.argv) > 3:   # nt-… = yêu cầu từ trang công khai (ntfy), còn lại = phiếu Drive
    tt['_ntfy' if sys.argv[3].startswith('nt-') else '_yeu_cau'] = sys.argv[3]
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
json.dump(tt, open(p_tt, 'w'), ensure_ascii=False, indent=1)
for ma, v in tt.items():
    if ma.startswith('_'):
        continue
    print(('✔' if v['ok'] else '✘'), ma, v['ten'] or v['loi'])

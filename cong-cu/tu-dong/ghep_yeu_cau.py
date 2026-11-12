"""Ghép số cho 1 yêu cầu HTML: python3 -I ghep_yeu_cau.py <mã bài> <mã yêu cầu> <file html gửi lên>
Đọc ket-qua/<mã>.log + ket-qua/<mã>/bai.html (chay.sh vừa chạy) → ket-qua/h-<mã yêu cầu>.html + .json (app đọc)."""
import datetime, json, os, re, subprocess, sys

ma, id_, vao = sys.argv[1:4]
D = os.path.dirname(os.path.abspath(__file__))
kq = {'ma': ma, 'luc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'), 'ok': False}
log = open(f'ket-qua/{ma}.log', encoding='utf-8', errors='replace').read() if os.path.exists(f'ket-qua/{ma}.log') else ''
m = re.search(r'^XONG \S+ ngày (\S+)', log, re.M)
kq['ngay'] = m.group(1) if m else ''
kq['can_duyet'] = '\n'.join(dict.fromkeys(re.sub(r'^\s*cần duyệt:\s*', '', l).strip() for l in log.splitlines()
                             if re.search(r'cần duyệt:|LỖI:|KHÔNG ĐỌC ĐƯỢC', l)))[:3000]
if not os.path.exists(vao) or os.path.getsize(vao) < 50:
    kq['loi'] = 'Không đọc được HTML gửi lên (rỗng hoặc hỏng).'
elif not m or not os.path.exists(f'ket-qua/{ma}/bai.html'):
    kq['loi'] = 'Công thức chưa chạy xong: ' + ((log.strip().splitlines() or ['?'])[-1][:200])
else:
    r = subprocess.run(['python3', '-I', os.path.join(D, 'ghep_html.py'), vao, f'ket-qua/{ma}/bai.html',
                        f'ket-qua/h-{id_}.html', 'ghep.json'], capture_output=True, text=True)
    print(r.stdout, r.stderr)
    if r.returncode == 0:
        kq.update(json.load(open('ghep.json', encoding='utf-8')), ok=True)
    else:
        kq['loi'] = 'Lỗi khi ghép số vào HTML: ' + r.stderr.strip()[-200:]
json.dump(kq, open(f'ket-qua/h-{id_}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('yêu cầu HTML', id_, 'xong' if kq['ok'] else 'lỗi: ' + kq.get('loi', ''))

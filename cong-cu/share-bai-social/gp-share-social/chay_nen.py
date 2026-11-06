#!/usr/bin/env python3
"""Vòng đăng Wix chạy nền, KHÔNG tốn token AI.
- Chờ đến giờ trong state.json (lịch wix_plan.json), nhưng luôn cách bài trước >= 120 phút và chỉ 07:00–23:00.
- Trước mỗi lượt: trang Wix trả 410/404/451 -> ghi BLOCKED.txt rồi dừng hẳn.
- Mỗi lượt chạy step.py, ghi log vào chay_nen.log. Hết lịch (2099) -> thoát.
AI chỉ thức dậy 1 lần/tối để ghi link vào sheet."""
import json, os, subprocess, time, datetime as D
os.chdir(os.path.dirname(os.path.abspath(__file__)))
VN = D.timezone(D.timedelta(hours=7))
HOME = 'https://trangjena3.wixsite.com/techcombankvietnam'
def log(*a):
    with open('chay_nen.log', 'a') as f: f.write(D.datetime.now(VN).strftime('%d/%m %H:%M ') + ' '.join(map(str, a)) + '\n')
def last_post():
    t = None
    for l in open('posted.jsonl'):
        r = json.loads(l)
        if r.get('platform') == 'wix': t = D.datetime.fromisoformat(r['when'])
    return t
log('START pid', os.getpid())
while True:
    st = json.load(open('state.json')).get('wix', '2099')
    if st.startswith('2099'): log('HET LICH'); break
    target = D.datetime.fromisoformat(st)
    lp = last_post()
    if lp: target = max(target, lp + D.timedelta(minutes=120))
    if target.astimezone(VN).hour >= 23: target = (target.astimezone(VN) + D.timedelta(days=1)).replace(hour=7, minute=5, second=0)
    elif target.astimezone(VN).hour < 7: target = target.astimezone(VN).replace(hour=7, minute=5, second=0)
    while D.datetime.now(VN) < target: time.sleep(min(60, max(1, (target - D.datetime.now(VN)).total_seconds())))
    code = subprocess.run(['curl', '-s', '-o', '/dev/null', '-L', '-m', '40', '-w', '%{http_code}', HOME], capture_output=True, text=True).stdout
    if code in ('410', '404', '451'):
        open('BLOCKED.txt', 'w').write(code); log('BLOCKED', code); break
    out = subprocess.run(['python3', 'step.py'], capture_output=True, text=True, timeout=1800)
    for l in (out.stdout + out.stderr).splitlines():
        if l.startswith(('PUBLISHED', 'WAKE_AT', 'LEFT')) or 'ERR' in l or 'Traceback' in l: log(l[:300])
    if 'Traceback' in out.stderr: log('LOI step.py -> dung'); break
    time.sleep(30)

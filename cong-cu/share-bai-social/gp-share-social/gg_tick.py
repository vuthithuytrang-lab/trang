#!/usr/bin/env python3
"""Lượt đăng bù Google Group: chỉ 07:00–23:00, cách bài trước ≥ 13 phút (Trang yêu cầu xong trước 23h 08/11), đăng bài đầu tiên đến giờ trong gg_plan.json."""
import json, subprocess, datetime as D, sys
VN = D.timezone(D.timedelta(hours=7)); now = D.datetime.now(VN)
plan = json.load(open('gg_plan.json'))
done = {json.loads(l)['main_row'] for l in open('gg_posted.jsonl')}
last = max(D.datetime.fromisoformat(json.loads(l)['when']) for l in open('gg_posted.jsonl'))
left = [p for p in plan if p['main'] not in done]
nxt = lambda: (left[0]['at'] if left else None)
if not left: print('GG_HET'); sys.exit()
if not (7 <= now.hour < 23): print('GG_NGOAI_GIO'); print('GG_WAKE_AT', nxt()); sys.exit()
if (now - last).total_seconds() < 720 or D.datetime.fromisoformat(left[0]['at']) > now: print('GG_CHUA_DEN_GIO'); print('GG_WAKE_AT', nxt()); sys.exit()
import os
while left and not os.path.exists(f"bai/{left[0]['main']}/post.html") and os.path.exists(f"bai/{left[0]['main']}/NO_SOURCE.txt"): print('GG_BO_QUA_KHONG_NGUON', left.pop(0)['row'])
if not left: print('GG_HET'); sys.exit()
if not os.path.exists(f"bai/{left[0]['main']}/post.html"): print('GG_CHO_BAI_VIET', left[0]['row']); sys.exit()
p = left.pop(0)
out = subprocess.run(['python3', 'gg_post.py', str(p['main'] + 4)], capture_output=True, text=True)
line = next((l for l in out.stdout.splitlines() if l.startswith('PUBLISHED')), None)
if not line: print('GG_LOI', out.stderr[-400:]); sys.exit()
rec = json.loads(line[10:]); rec['row'] = p['row']; rec['slot'] = 'GG Group - Trang'
L = open('gg_posted.jsonl').read().splitlines(); L[-1] = json.dumps(rec, ensure_ascii=False); open('gg_posted.jsonl', 'w').write('\n'.join(L) + '\n')
print('GG_PUBLISHED', json.dumps(rec, ensure_ascii=False)); print('GG_LEFT', len(left)); print('GG_WAKE_AT', nxt())

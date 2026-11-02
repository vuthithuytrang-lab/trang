#!/usr/bin/env python3
"""Đợt 2 (2/11): 96 bài mới (28–123) + bài 5, 7, 8. Bỏ Mastodon (bị khóa).
Wix/Webflow/Blogger/GG luân phiên 15 phút một lượt; WordPress giữ ~5 tiếng một bài."""
import json, os, random
from datetime import datetime, timedelta, timezone
HERE = os.path.dirname(os.path.abspath(__file__))
VN = timezone(timedelta(hours=7)); random.seed(211)
QUEUE = [5, 7, 8] + list(range(28, 124))
lich = json.load(open(os.path.join(HERE, "lich.json")))
done = {(r["so"], r["nen"]) for r in map(json.loads, open(os.path.join(HERE, "da-dang.jsonl"))) if r.get("ok")}
# giữ các lượt đã đăng + WordPress 24–27 đã hẹn; bỏ các lượt cũ của bài 5, 7, 8
keep = [e for e in lich if (e["so"], e["nen"]) in done or (e["nen"] == "wp" and 24 <= e["so"] <= 27)]
fixed_wp = sorted(datetime.fromisoformat(e["gio"]) for e in keep if e["nen"] == "wp" and (e["so"], "wp") not in done)
# hàng đợi riêng từng nền, lệch nhau vài bài để cùng một bài không lên 4 nơi trong 1 tiếng
q = {n: QUEUE[o:] + QUEUE[:o] for n, o in (("wix", 0), ("wf", 2), ("bl", 4), ("gg", 6))}
rot, wpq = ["wix", "wf", "bl", "gg"], list(QUEUE)
t = datetime(2026, 11, 2, 12, 0, tzinfo=VN); last_wp = fixed_wp[-1]; nxt_wp = last_wp + timedelta(minutes=305)
new, k = [], 0
while any(q.values()):
    if fixed_wp and fixed_wp[0] <= t + timedelta(minutes=14):
        t = max(t, fixed_wp.pop(0) + timedelta(minutes=15)); continue
    if not fixed_wp and wpq and nxt_wp <= t:
        new.append({"so": wpq.pop(0), "nen": "wp", "gio": t.strftime("%Y-%m-%dT%H:%M+07:00")})
        nxt_wp = t + timedelta(minutes=random.randint(300, 310)); t += timedelta(minutes=15); continue
    n = rot[k % 4]; k += 1
    if q[n]:
        new.append({"so": q[n].pop(0), "nen": n, "gio": t.strftime("%Y-%m-%dT%H:%M+07:00")})
        t += timedelta(minutes=random.randint(14, 16))
while wpq:  # phần WordPress còn lại sau thứ 6: vẫn 5 tiếng một bài
    t = max(t, nxt_wp); new.append({"so": wpq.pop(0), "nen": "wp", "gio": t.strftime("%Y-%m-%dT%H:%M+07:00")})
    nxt_wp = t + timedelta(minutes=random.randint(300, 310)); t = nxt_wp
out = sorted(keep + new, key=lambda e: e["gio"])
json.dump(out, open(os.path.join(HERE, "lich.json"), "w"), ensure_ascii=False, indent=1)
rot_new = [e for e in new if e["nen"] != "wp"]
print("lượt mới:", len(new), "| luân phiên xong lúc", rot_new[-1]["gio"], "| WP đến hết 6/11:", sum(1 for e in new if e["nen"] == "wp" and e["gio"] < "2026-11-07"), "| WP cuối", new[-1]["gio"])

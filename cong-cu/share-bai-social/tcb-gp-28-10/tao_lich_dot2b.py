#!/usr/bin/env python3
"""4/11 (sửa lần 3: Trang cần xong HẾT, kể cả WordPress, trước 23h thứ 6 → WordPress ~33 phút/bài): máy chủ dừng từ trưa 2/11 nên lịch bị trễ. Trang yêu cầu dồn lại để thứ 6 (6/11) xong hết.
Giữ nguyên thứ tự cũ của từng nền; Wix/Webflow/Blogger/GG luân phiên 7–9 phút một lượt; WordPress ~1 tiếng một bài."""
import json, os, random
from datetime import datetime, timedelta, timezone
HERE = os.path.dirname(os.path.abspath(__file__))
VN = timezone(timedelta(hours=7)); random.seed(411)
lich = json.load(open(os.path.join(HERE, "lich.json")))
done = {(r["so"], r["nen"]) for r in map(json.loads, open(os.path.join(HERE, "da-dang.jsonl"))) if r.get("ok")}
keep = [e for e in lich if (e["so"], e["nen"]) in done]
pend = sorted((e for e in lich if (e["so"], e["nen"]) not in done), key=lambda e: e["gio"])
rot = [e for e in pend if e["nen"] != "wp"]; wpq = [e for e in pend if e["nen"] == "wp"]
t = datetime.now(VN).replace(second=0, microsecond=0) + timedelta(minutes=3); nxt_wp = t; new = []
while rot:
    if wpq and nxt_wp <= t:
        e = wpq.pop(0); new.append({**e, "gio": t.strftime("%Y-%m-%dT%H:%M+07:00")})
        nxt_wp = t + timedelta(minutes=random.randint(29, 32)); t += timedelta(minutes=6); continue
    e = rot.pop(0); new.append({**e, "gio": t.strftime("%Y-%m-%dT%H:%M+07:00")})
    t += timedelta(minutes=random.choice([6, 6, 7]))
while wpq:
    t = max(t, nxt_wp); e = wpq.pop(0); new.append({**e, "gio": t.strftime("%Y-%m-%dT%H:%M+07:00")})
    nxt_wp = t + timedelta(minutes=random.randint(29, 32))
json.dump(sorted(keep + new, key=lambda e: e["gio"]), open(os.path.join(HERE, "lich.json"), "w"), ensure_ascii=False, indent=1)
r = [e for e in new if e["nen"] != "wp"]
print("luân phiên:", len(r), "lượt, xong lúc", r[-1]["gio"], "| WP đến hết 6/11:", sum(1 for e in new if e["nen"] == "wp" and e["gio"] < "2026-11-07"), "/", sum(1 for e in new if e["nen"] == "wp"), "| WP cuối", [e for e in new if e["nen"] == "wp"][-1]["gio"])

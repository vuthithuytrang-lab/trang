#!/usr/bin/env python3
"""In các ô D:E cần ghi vào sheet cho những lượt đã đăng mà chưa ghi (theo da-ghi-sheet.json). --xong để đánh dấu đã ghi."""
import json, os, sys
from datetime import datetime
HERE = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(HERE, "da-ghi-sheet.json")
OFF = {"wp": 0, "wix": 1, "ma": 2, "wf": 3, "bl": 4, "gg": 5}
ghi = set(map(tuple, json.load(open(F)))) if os.path.exists(F) else set()
moi = {}
for r in map(json.loads, open(os.path.join(HERE, "da-dang.jsonl"))):
    if r.get("ok") and (r["so"], r["nen"]) not in ghi and r["luc"] >= "2026-11-04": moi[(r["so"], r["nen"])] = r
if "--xong" in sys.argv:
    json.dump(sorted(ghi | set(moi)), open(F, "w")); print("đã đánh dấu", len(moi))
else:
    for (so, n), r in sorted(moi.items(), key=lambda x: x[1]["luc"]):
        d = datetime.fromisoformat(r["luc"])
        print(json.dumps({"range": f"'Share social GP'!D{9 + 6 * (so - 1) + OFF[n]}:E{9 + 6 * (so - 1) + OFF[n]}", "values": [[r["link"], f"{d:%H:%M %d/%m/%Y}"]]}, ensure_ascii=False))

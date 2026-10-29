#!/usr/bin/env python3
"""Chờ đến giờ của lượt kế tiếp trong lich.json rồi đăng (dùng làm đồng hồ hẹn giờ chính xác)."""
import json, os, subprocess, sys, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
done = {(r["so"], r["nen"]) for r in map(json.loads, open(os.path.join(HERE, "da-dang.jsonl"))) if r.get("ok")}
nxt = next(e for e in json.load(open(os.path.join(HERE, "lich.json"))) if (e["so"], e["nen"]) not in done)
cho = (datetime.fromisoformat(nxt["gio"]) - datetime.now(timezone.utc)).total_seconds()
print("lượt kế:", nxt, "chờ", int(cho), "giây", flush=True)
if cho > 6600: sys.exit("còn quá xa, chưa chờ")
time.sleep(max(0, cho) + 20)
for c in ("check", "dang"):
    p = subprocess.run([sys.executable, os.path.join(HERE, "dang.py"), c, str(nxt["so"]), nxt["nen"]], capture_output=True, text=True)
    print(p.stdout[-1500:], p.stderr[-800:], flush=True)
    if p.returncode or "LỖI" in p.stdout: break

#!/usr/bin/env python3
"""Đăng liên tục các lượt đến hạn trong lich.json trong khoảng ~110 phút rồi thoát (để phiên ghi sheet + commit + chạy lại)."""
import json, os, subprocess, sys, time
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.abspath(__file__)); het = time.time() + 110 * 60
while True:
    done = {(r["so"], r["nen"]) for r in map(json.loads, open(os.path.join(HERE, "da-dang.jsonl"))) if r.get("ok")}
    nxt = next((e for e in json.load(open(os.path.join(HERE, "lich.json"))) if (e["so"], e["nen"]) not in done), None)
    if not nxt: print("hết lịch", flush=True); break
    cho = (datetime.fromisoformat(nxt["gio"]) - datetime.now(timezone.utc)).total_seconds()
    if time.time() + max(cho, 0) > het: print("lượt kế ngoài khung giờ:", nxt, flush=True); break
    p = subprocess.run([sys.executable, os.path.join(HERE, "cho_dang.py")], capture_output=True, text=True)
    out = p.stdout.strip().splitlines(); print(out[0] if out else "", "|", (out[-1] if out else "")[:300], flush=True)
    done2 = {(r["so"], r["nen"]) for r in map(json.loads, open(os.path.join(HERE, "da-dang.jsonl"))) if r.get("ok")}
    if (nxt["so"], nxt["nen"]) not in done2: print("LỖI ở lượt", nxt, p.stdout[-800:], p.stderr[-400:], flush=True); break

#!/usr/bin/env python3
"""In các dòng 'Wix - Tuấn' cần ghi sheet: row | link | 'HH:MM dd/mm/yyyy'."""
import datetime, json, os
H = os.path.dirname(os.path.abspath(__file__))
done = {l.strip() for l in open(os.path.join(H, 'da-ghi-sheet.txt'))} if os.path.exists(os.path.join(H, 'da-ghi-sheet.txt')) else set()
for x in map(json.loads, open(os.path.join(H, 'da-dang.jsonl'))):
    if str(x['row']) in done: continue
    slug = json.load(open(os.path.join(H, 'bai', str(x['row']), 'meta.json')))['slug']
    t = datetime.datetime.fromisoformat(x['when'])
    print(f"{x['row']} | https://accyenthang2.wixsite.com/techcombankvietnam/post/{slug} | {t:%H:%M %d/%m/%Y}")

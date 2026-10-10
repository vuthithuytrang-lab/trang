#!/usr/bin/env python3
"""In ra các dòng sheet còn phải ghi (bài đã hẹn giờ/đã lên nhưng chưa có trong da-ghi-sheet.txt).
Mỗi dòng: <nền tảng> <row> | <dòng sheet> | <nhãn cột H> | <link> | <ngày d/m/yyyy>"""
import datetime, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
done = {tuple(l.split()) for l in open(os.path.join(HERE, 'da-ghi-sheet.txt')) if l.strip()}
NEN = [('blogger', 'tcb-tuan-blogger', 'Blogger - Tuấn', 0), ('wix', 'tcb-tuan-wix', 'Wix - Tuấn', 1), ('webflow', 'tcb-tuan-webflow', 'Webflow - Tuấn', 2)]
for key, d, label, off in NEN:
    f = os.path.join(HERE, d, 'da-dang.jsonl')
    if not os.path.exists(f): continue
    for x in map(json.loads, open(f)):
        if (key, str(x['row'])) in done: continue
        url = x['url']
        if key == 'wix': url = 'https://accyenthang2.wixsite.com/techcombankvietnam/post/' + json.load(open(os.path.join(HERE, d, 'bai', str(x['row']), 'meta.json')))['slug']
        t = datetime.datetime.fromisoformat(x.get('published_at') or x['when']).astimezone(datetime.timezone(datetime.timedelta(hours=7)))
        print(f"{key} {x['row']} | {x['tuan_row'] + off} | {label} | {url} | {t.day}/{t.month}/{t.year}")

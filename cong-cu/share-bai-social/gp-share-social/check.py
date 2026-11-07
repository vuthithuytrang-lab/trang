#!/usr/bin/env python3
"""Soát 1 bài: python3 check.py <dòng>. In OK hoặc lỗi."""
import json, re, sys
r = sys.argv[1]; d = f'bai/{r}'
h = open(d + '/post.html').read(); m = json.load(open(d + '/meta.json'))
BAN = re.compile(r'(?<!chậm )(?<!sớm )(?<!mới )(?<!thứ )\b(duy nhất|số 1|hàng đầu|tốt nhất|rẻ nhất|cao nhất|thấp nhất|lớn nhất)\b', re.I)
txt = re.sub('<[^>]+>', ' ', h); words = len(txt.split()); links = re.findall(r'href="([^"]+)"', h)
tags = set(re.findall(r'</?([a-z0-9]+)', h)) - {'p', 'h2', 'h3', 'ul', 'ol', 'li', 'strong', 'a'}
err = []
if not 880 <= words <= 1150: err.append(f'so tu {words}')
if links != [m.get('source')]: err.append(f'link {links}')
if tags: err.append(f'the {tags}')
if not 50 <= len(m.get('title', '')) <= 75: err.append(f'tieu de {len(m.get("title",""))} ky tu')
for k in ('slug', 'keyword', 'source', 'title'):
    if not m.get(k): err.append('thieu ' + k)
if BAN.search(txt + ' ' + m.get('title', '')): err.append('tu cam ' + BAN.search(txt + ' ' + m['title']).group(0))
if 'bài gốc' in txt.lower(): err.append('co cum "bai goc"')
print('OK' if not err else 'LOI: ' + '; '.join(err), words)

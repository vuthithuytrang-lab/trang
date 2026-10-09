#!/usr/bin/env python3
"""Soát 1 bài Hoa theo quy tắc TCB (HUONG-DAN-TCB.md phần C + luật riêng đợt Hoa).
Usage: python3 kiem-tra.py <thu-muc-bai>   (thư mục có wp-hoa.html + meta.json)
In OK hoặc danh sách lỗi; thoát 1 nếu có lỗi.
"""
import json, os, re, sys, html

d = sys.argv[1]
body = open(os.path.join(d, 'wp-hoa.html'), encoding='utf-8').read()
meta = json.load(open(os.path.join(d, 'meta.json'), encoding='utf-8'))
kw, src, title = meta['kw'].lower(), meta['url'], meta['title']
err = []

text = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<!--.*?-->', ' ', body, flags=re.S)))
words = len(text.split())
if not 900 <= words <= 1100: err.append(f'so tu {words} (can 900-1100)')
if not 55 <= len(title) <= 70: err.append(f'tieu de {len(title)} ky tu (can 55-70)')
if kw not in title.lower(): err.append('tieu de thieu tu khoa')

links = re.findall(r'<a\s[^>]*href="([^"]+)"', body)
if links != [src]: err.append(f'link sai: {links}')
first_p = re.search(r'<p>(.*?)</p>', body, re.S)
if not first_p or src not in first_p.group(1): err.append('link khong nam o doan mo dau')
elif kw not in html.unescape(re.sub(r'<[^>]+>', '', first_p.group(1))).lower(): err.append('doan mo dau thieu tu khoa')
n = text.lower().count(kw)
if not 3 <= n <= 7: err.append(f'tu khoa xuat hien {n} lan')

tags = set(re.findall(r'<\s*/?\s*([a-zA-Z0-9]+)', body))
bad = tags - {'p', 'h2', 'h3', 'ul', 'ol', 'li', 'strong', 'a'}
if bad: err.append(f'the khong cho phep: {bad}')
if 'style=' in body or '<!--' in body: err.append('khong de style/comment trong ban nhap (script dang tu them)')

low = text.lower()
for w in ['tốt nhất', 'duy nhất', 'số 1', 'số một', 'hàng đầu', 'lớn nhất', 'cao nhất', 'rẻ nhất', 'nhanh nhất', 'uy tín nhất']:
    if w in low: err.append(f'tu cam: {w}')
if re.search(r'1800\s?\d{3,4}|@techcombank|hotline', low): err.append('co hotline/email')
heads = [html.unescape(re.sub(r'<[^>]+>', '', h)).strip().lower() for h in re.findall(r'<h[23]>(.*?)</h[23]>', body, re.S)]
if heads and re.match(r'(kết luận|tóm lại|tổng kết|lời kết|tóm tắt)', heads[-1]): err.append('con muc tom tat cuoi bai')
last_p = re.findall(r'<p>(.*?)</p>', body, re.S)[-1].lower()
if re.match(r'\s*(tóm lại|nhìn chung|tổng kết|kết luận|nói tóm lại|như vậy)', last_p): err.append('doan cuoi la tom tat')
if 'tham khảo' not in low or 'thời điểm' not in low: err.append('thieu cau luu y tham khao')

print('OK' if not err else 'LOI: ' + '; '.join(err), f'({words} tu, tieu de {len(title)} ky tu)')
sys.exit(1 if err else 0)

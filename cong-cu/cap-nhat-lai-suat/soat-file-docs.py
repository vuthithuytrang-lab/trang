#!/usr/bin/env python3
"""So file Google Docs (bản xuất HTML từ Drive) với bản dựng tam/bai-viet.min.html: từng ô bảng, ô tô vàng, chữ ngoài bảng.
Chạy: python3 soat-file-docs.py <đường-dẫn-kết-quả-download_file_content.json>"""
import json, base64, re, html, sys, difflib
d = json.load(open(sys.argv[1]))
try:
    g = base64.b64decode(d['content']).decode('utf-8')
except Exception:
    g = d['content']
open('tam/google-export.html', 'w').write(g)
mau = open('tam/bai-viet.min.html').read()

def o_bang(h):
    out = []
    for tb in re.findall(r'<table.*?</table>', h, re.S):
        for tr in re.findall(r'<tr.*?</tr>', tb, re.S):
            out.append([(re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', td))).replace('\xa0', ' ').strip(),
                         bool(re.search(r'background-color:#ffff00', td))) for td in re.findall(r'<td.*?</td>', tr, re.S)])
    return out

def chu(h):
    h = re.sub(r'<table.*?</table>|<style.*?</style>', '', h, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).replace('\xa0', ' ').strip()

G, M = o_bang(g), o_bang(mau)
sai = [(i, a, b) for i, (a, b) in enumerate(zip(G, M)) if a != b]
print('Số ảnh:', len(re.findall(r'<img', g)), '| số dòng bảng:', len(G), '/', len(M), '| dòng lệch:', len(sai))
for x in sai[:10]:
    print('  LỆCH', x)
print('Ô tô vàng trong bảng:', sum(y for r in G for _, y in r), '/', sum(y for r in M for _, y in r))
print('Chữ tô vàng ngoài bảng:', re.findall(r'background-color:#ffff00[^>]*>([^<]+)<', re.sub(r'<table.*?</table>', '', g, flags=re.S)))
sm = difflib.SequenceMatcher(None, chu(g), chu(mau))
print('Chữ ngoài bảng giống nhau:', round(sm.ratio() * 100, 2), '%')
for op in sm.get_opcodes():
    if op[0] != 'equal':
        print('  KHÁC', op[0], repr(chu(g)[op[1]:op[2]][:80]), '->', repr(chu(mau)[op[3]:op[4]][:80]))

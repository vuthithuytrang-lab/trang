# Chuyển HTML → danh sách khối giống cách Google Docs nhập (cho mô phỏng): python3 khoi.py < html > json
import sys, json
from bs4 import BeautifulSoup
s = BeautifulSoup(sys.stdin.read(), 'lxml')
out = []
def runs(el):
    text, links = '', []
    for node in el.descendants:
        if isinstance(node, str) and not node.find_parent(['script', 'style']):
            if node.find_parent('table') and el.name != 'table': continue
            a = node.find_parent('a'); t = str(node).replace('\n', ' ')
            if a is not None and a.get('href'): links.append([len(text), len(text) + len(t), a['href']])
            text += t
    return text, links
for el in s.body.find_all(['p', 'h2', 'h3', 'h4', 'li', 'table']):
    if el.find_parent(['table']) or (el.name == 'p' and el.find_parent('li')) or (el.name == 'li' and el.find(['li'])): continue
    t, l = runs(el)
    out.append({'type': 'TABLE' if el.name == 'table' else ('LIST_ITEM' if el.name == 'li' else 'PARAGRAPH'),
                'heading': el.name in ('h2', 'h3', 'h4'), 'text': t, 'links': l})
print(json.dumps(out, ensure_ascii=False))

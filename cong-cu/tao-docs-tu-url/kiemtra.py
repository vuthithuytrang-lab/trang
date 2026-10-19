# kiemtra.py <thư mục lô>/ — soát cuối mỗi lô trước khi tải lên Drive, và soạn sẵn nội dung cột E
# - mỗi anchor trong sheet (F-G + mọi cặp N) phải là CHỮ NGUYÊN VĂN của 1 link trỏ đúng URL
# - anchor phải được tô vàng; phần chèn mới không nằm trong 25% đầu thân bài
# In ra JSON: {row: {"ok": bool, "loi": [...], "ghichu_E": "..."}}
import json, sys, re
from bs4 import BeautifulSoup
D = sys.argv[1]
rows = {f"r{r['row']}": r for r in json.load(open(D + 'rows.json', encoding='utf-8'))}
plan = json.load(open(D + 'plan.json', encoding='utf-8'))
YEL = 'background-color:#ffff00'
CACH = {'tygia': 'cột I', 'phrase': 'gắn câu có sẵn', 'sentence': 'viết thêm 1 câu', 'xemthem': 'xem thêm',
        'doanmoi': 'đoạn mới', 'chuyenlink': 'chuyển link cũ sang đúng anchor', 'dacolink': 'có sẵn link đúng anchor'}

def slug(u): return u.split('?')[0].rstrip('/').split('/')[-1]
def norm(x): return re.sub(r'\s+', ' ', x.replace('\xa0', ' ')).strip()

out = {}
for rid, r in rows.items():
    loi = []
    try:
        s = BeautifulSoup(open(f'{D}final/{rid}.html', encoding='utf-8').read(), 'lxml')
    except FileNotFoundError:
        out[r['row']] = dict(ok=False, loi=['chưa có file final'], ghichu_E=''); continue
    can = [(r['F'], r['G'])] + [tuple(p) for p in r['pairs']]
    links = s.find_all('a')
    for a, u in can:
        hit = [x for x in links if norm(x.get_text('')).lower() == norm(a).lower() and slug(x.get('href', '')) == slug(u)]
        if not hit: loi.append(f'thiếu/sai anchor: {a}')
        elif not any(x.find('span', style=YEL) for x in hit): loi.append(f'chưa tô vàng: {a}')
    # 25% đầu: tính trên thân bài (sau meta), bỏ các dòng ghi chú đỏ
    body = [b for b in s.body.find_all(['p', 'h2', 'h3', 'h4', 'li', 'table'])
            if not b.find_parent(['li', 'table']) and not b.find('span', style='color:#ff0000')][6:]
    tot = sum(len(b.get_text()) for b in body) or 1; acc = 0
    ops = {o['anchor']: o for o in plan.get(rid, [])}
    for b in body:
        for x in b.find_all('a'):
            o = ops.get(norm(x.get_text('')))
            if o and o['t'] not in ('tygia', 'dacolink') and x.find('span', style=YEL) and acc * 100 / tot < 25:
                loi.append(f'nằm trong 25% đầu: {o["anchor"]}')
        acc += len(b.get_text())
    moi = [f"{o['anchor']} ({CACH[o['t']]})" for o in plan.get(rid, []) if o['t'] not in ('chuyenlink', 'dacolink')]
    cl = [f"{o['anchor']} ({CACH[o['t']]})" for o in plan.get(rid, []) if o['t'] in ('chuyenlink', 'dacolink')]
    n = len(can); du = n - sum(1 for l in loi if l.startswith('thiếu'))
    e = f'Đủ {du}/{n} anchor (đúng nguyên văn sheet).\nĐã chèn mới ({len(moi)}): ' + '; '.join(moi) + '.'
    if cl: e += f'\nLink có sẵn ({len(cl)}): ' + '; '.join(cl) + '.'
    thieu = [l.split(': ', 1)[1] for l in loi if l.startswith('thiếu')]
    e += '\nThiếu: ' + ('; '.join(thieu) if thieu else 'không') + '.'
    out[r['row']] = dict(ok=not loi, loi=loi, ghichu_E=e)
print(json.dumps(out, ensure_ascii=False, indent=1))

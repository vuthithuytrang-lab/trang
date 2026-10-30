import sys, json, re, html as H, html as html_mod, urllib.parse
from bs4 import BeautifulSoup, NavigableString

def unwrap(h):
    if h.startswith('https://www.google.com/url'):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(h).query)
        h = q.get('q', [h])[0]
    return h

def norm(u):
    u = (u or '').strip()
    p = urllib.parse.urlparse(u)
    return (p.netloc.replace('www.', '') + p.path.rstrip('/')).lower(), p.query

def class_styles(soup):
    css = ''.join(s.get_text() for s in soup.find_all('style'))
    st = {}
    for m in re.finditer(r'\.([\w-]+)\{([^}]*)\}', css):
        b = 'font-weight:700' in m.group(2); i = 'font-style:italic' in m.group(2)
        st[m.group(1)] = (b, i)
    return st

def fmt(span, st):
    b = i = False
    for c in span.get('class', []):
        bb, ii = st.get(c, (False, False)); b |= bb; i |= ii
    s = span.get('style', '')
    b |= 'font-weight:700' in s; i |= 'font-style:italic' in s
    return b, i

def render(block, st):
    # gom các mảnh (text, b, i, href)
    pieces = []
    def walk(node, b, i, href):
        for ch in node.children:
            if isinstance(ch, NavigableString):
                t = str(ch)
                if t: pieces.append((t, b, i, href))
            elif ch.name == 'br':
                pieces.append(('<br>', b, i, href))
            elif ch.name == 'img':
                continue
            else:
                nb, ni = b, i
                if ch.name == 'span': fb, fi = fmt(ch, st); nb |= fb; ni |= fi
                if ch.name in ('b', 'strong'): nb = True
                if ch.name in ('i', 'em'): ni = True
                nh = href
                if ch.name == 'a' and ch.get('href'): nh = unwrap(ch['href'])
                walk(ch, nb, ni, nh)
    walk(block, False, False, None)
    for k, p in enumerate(pieces):
        if '[Nội dung gốc' in p[0]:
            pre = p[0].split('[Nội dung gốc')[0]
            pieces = pieces[:k] + ([(pre,) + p[1:]] if pre.strip() else [])
            while pieces and (pieces[-1][0] == '<br>' or not pieces[-1][0].strip()): pieces.pop()
            break
    # gộp mảnh theo link, rồi theo định dạng
    out = []
    def esc(t): return '<br>' if t == '<br>' else H.escape(t.replace('\xa0', ' '), quote=False).replace('>', '&gt;')
    def styled(t, b, i):
        if not t.strip(): return t
        if b: t = f'<b>{t}</b>'
        if i: t = f'<i>{t}</i>'
        return t
    k = 0
    while k < len(pieces):
        href = pieces[k][3]
        grp = []
        while k < len(pieces) and pieces[k][3] == href:
            grp.append(pieces[k]); k += 1
        segs = []
        for t, b, i, _ in grp:
            if segs and segs[-1][1:] == (b, i): segs[-1][0] += esc(t)
            else: segs.append([esc(t), b, i])
        inner = ''.join(styled(t, b, i) for t, b, i in segs)
        if href:
            inner = f'<a href="{H.escape(href)}" target="_blank" rel="noopener noreferrer">{inner}</a>'
        out.append(inner)
    s = ''.join(out)
    s = re.sub(r'</b><b>|</i><i>', '', s)
    return re.sub(r'\s+', ' ', s).strip()

def short(t, n=80):
    t = re.sub(r'\s+', ' ', t.replace('\xa0', ' ')).strip()
    return t if len(t) <= n else t[:n].rstrip() + '...'

def section(head):
    if not head: return 'phần mở bài'
    m = re.match(r'\s*(\d+(?:\.\d+)*)', head)
    if m: return 'mục ' + m.group(1)
    return 'phần "' + short(head, 40) + '"'

def process(path, targets):
    soup = BeautifulSoup(open(path, encoding='utf-8').read(), 'html.parser')
    st = class_styles(soup)
    blocks = [b for b in soup.body.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
              if not (b.name == 'p' and b.find_parent('li'))]
    items = []
    for b in blocks:
        t = b.get_text().replace('\xa0', ' ').strip()
        items.append(dict(el=b, text=t, head=b.name.startswith('h') and not t.startswith('[')))
    tmap = {}
    for a, u in targets:
        tmap.setdefault(norm(u)[0], []).append(a)
    for it in items:
        it['hit'] = any(norm(unwrap(a.get('href', '')))[0] in tmap for a in it['el'].find_all('a'))
    found = {}; results = []; curhead = None; title_seen = False
    for idx, it in enumerate(items):
        if it['head']:
            if it['el'].name in ('h2', 'h3', 'h4'): curhead = it['text']
            continue
        if it['text'].startswith('[Nội dung gốc'): continue
        hits = []
        for a in it['el'].find_all('a'):
            key = norm(unwrap(a.get('href', '')))[0]
            if key in tmap:
                anc = a.get_text().strip()
                hits.append((anc, key))
        if not hits: continue
        nxt = next((x for x in items[idx+1:] if x['text']), None)
        prvs = [x for x in reversed(items[:idx]) if x['text'] and not x['text'].startswith('[Nội dung gốc')]
        newmark = bool(prvs) and re.match(r'^\[Đề xuất', prvs[0]['text'])
        if newmark: prvs = [x for x in prvs if not x['text'].startswith('[')]
        prv = prvs[0] if prvs else None
        if '[Nội dung gốc' in it['text']:
            orig = re.sub(r'^.*?\[Nội dung gốc trước khi chèn:\s*', '', it['text'], flags=re.S).rstrip(']').strip()
            mode = ('THAY', orig)
        elif nxt and nxt['text'].startswith('[Nội dung gốc'):
            orig = re.sub(r'^\[Nội dung gốc trước khi chèn:\s*', '', nxt['text']).rstrip(']').strip()
            mode = ('THAY', orig)
        else:
            mode = ('THÊM', prv['text'] if prv else '')
            isref = re.search(r'tham khảo|xem thêm|>>>', it['text'], re.I)
            for x in ([] if isref else items[idx+1:idx+16]):
                if x['head'] or x.get('hit'): break
                if x['text'].startswith('[Nội dung gốc'):
                    orig = re.sub(r'^\[Nội dung gốc trước khi chèn:\s*', '', x['text']).rstrip(']').strip()
                    mode = ('THAY1', orig); break
        intable = it['el'].find_parent('td') is not None
        if mode[0] == 'THÊM' and not newmark and not re.search(r'tham khảo|xem thêm|&gt;&gt;&gt;|>>>', it['text'], re.I):
            # file Docs không ghi nội dung gốc cho đoạn này
            mode = ('KIEMTRA', prv['text'] if prv else '')
        for anc, key in hits: found.setdefault(key, anc)
        tag = 'li' if it['el'].name == 'li' else 'p'
        body = render(it['el'], st)
        out_html = f'<li>{body}</li>' if tag == 'li' else f'<p style="text-align: justify;">{body}</p>'
        results.append(dict(intable=intable, cur=it['text'], mode=mode, sec=section(curhead), html=out_html, anchors=[h[0] for h in hits]))
    missing = [a for a, u in targets if norm(u)[0] not in found]
    return results, missing

def build_cell(results, missing):
    parts = []
    for n, r in enumerate(results, 1):
        ancs = ', '.join(dict.fromkeys(r['anchors']))
        where = r['sec'] + (', trong bảng' if r['intable'] else '')
        r['sec'] = where
        if r['mode'][0] == 'KIEMTRA':
            c = f'<!-- Link {n} ({ancs}): KIỂM TRA - file Docs không ghi nội dung gốc cho đoạn này. Nếu đoạn đã có trên web thì THAY đoạn "{short(r["cur"])}"; nếu chưa có thì THÊM ngay sau đoạn "{short(r["mode"][1])}" ({r["sec"]}) -->'
        elif r['mode'][0] == 'THAY1':
            c = f'<!-- Link {n} ({ancs}): SỬA dòng "{short(r["cur"])}" trong cụm có nội dung gốc "{short(r["mode"][1], 60)}" ({r["sec"]}), thay bằng dòng dưới -->'
        elif r['mode'][0] == 'THAY':
            c = f'<!-- Link {n} ({ancs}): THAY đoạn "{short(r["mode"][1])}" ({r["sec"]}) bằng đoạn dưới -->'
        else:
            c = f'<!-- Link {n} ({ancs}): THÊM dòng mới ngay sau đoạn "{short(r["mode"][1])}" ({r["sec"]}) -->'
        parts.append(c.replace('--', '-').replace('<!-', '<!--').replace('->', '-->') if False else c + '\n' + r['html'])
    s = '\n\n'.join(parts)
    if missing:
        s += ('\n\n' if s else '') + '<!-- CHƯA TÌM THẤY trong file Docs: ' + '; '.join(missing) + ' -->'
    return s

if __name__ == '__main__':
    # python3 tao_html.py <viec_can_lam.json> <thu_muc_html> <thu_muc_ra>
    import os, unicodedata
    jobs = json.load(open(sys.argv[1], encoding='utf-8'))
    hdir, odir = sys.argv[2], sys.argv[3]
    os.makedirs(odir, exist_ok=True)
    cells = {}
    for o in jobs:
        p = os.path.join(hdir, f"{o['row']}.html")
        if not os.path.exists(p):
            print('THIEU FILE DOCS', o['row']); continue
        raw = html_mod.unescape(open(p, encoding='utf-8').read())
        slug = o['url'].rstrip('/').split('/')[-1]
        tg = [tuple(x) for x in o['pairs']] + ([(o['I'], o['J'])] if o.get('J') else [])
        if slug not in raw:
            cells[o['row']] = f'<!-- CHƯA TẠO HTML: link FILE BLOG ở cột K không mở ra file Docs của bài {slug}. Cần kiểm tra lại link file Docs. -->'
        else:
            r, m = process(p, tg)
            c = build_cell(r, m)
            if o.get('note'):
                c = f'<!-- Chị Lộc duyệt: "{o["note"]}" -->\n\n' + c
            cells[o['row']] = c
        cells[o['row']] = unicodedata.normalize('NFC', cells[o['row']])
        print(o['row'], len(cells[o['row']]), 'ky tu')
    json.dump({str(k): v for k, v in cells.items()}, open(os.path.join(odir, 'cells.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    # chia lô ghi: mỗi lô <= 12000 ký tự, các dòng gần nhau
    col = jobs[0]['html_col'] if jobs else 'Z'
    ks = sorted(cells); groups = []; cur = []; size = 0
    for k in ks:
        if cur and (k - cur[-1] > 12 or size + len(cells[k]) > 12000):
            groups.append(cur); cur = []; size = 0
        cur.append(k); size += len(cells[k])
    if cur: groups.append(cur)
    sheet = jobs[0]['sheet'] if jobs else ''
    for i, g in enumerate(groups):
        vals = [[cells[r]] if r in cells else [None] for r in range(g[0], g[-1] + 1)]
        json.dump({'range': f"'{sheet}'!{col}{g[0]}:{col}{g[-1]}", 'values': vals},
                  open(os.path.join(odir, f'lo_{i:02d}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('so lo ghi:', len(groups))

# them-html.py <thư mục>/ — thêm dòng "HTML: ->" vào từng đề xuất cột Blog, đúng kiểu HTML web AIG
# (đoạn gốc giữ đậm/nghiêng, chỉ thay câu đề xuất). Ra file <thư mục>/ab-html.json.
import json, re, html, unicodedata, sys
from bs4 import BeautifulSoup, NavigableString
D = sys.argv[1] if len(sys.argv) > 1 else './'   # thư mục chứa a1..a4 (report.json, rows.json, raw-goc/)
AT = ' target="_blank" rel="noopener"'
def nfc(s): return unicodedata.normalize('NFC', s.replace('\xa0', ' '))
def link(url, a, bold): x = f'<a href="{url}"{AT}>{html.escape(a, quote=False)}</a>'; return f'<strong>{x}</strong>' if bold else x
def render_text(t, anchor, url, bold):
    t = nfc(t).strip(); k = t.find(anchor)
    if k < 0: return html.escape(t, quote=False), False
    return html.escape(t[:k], quote=False) + link(url, anchor, bold) + html.escape(t[k + len(anchor):], quote=False), True
def p_moi(y, anchor, url):
    if y.startswith('>>>'):
        body, ok = render_text(y[3:].strip(), anchor, url, True)
        return f'<p style="text-align: justify;"><em>&gt;&gt;&gt; {body}</em></p>', ok
    body, ok = render_text(y, anchor, url, False)
    return f'<p style="text-align: justify;">{body}</p>', ok
def chars(p):
    out = []
    for node in p.descendants:
        if isinstance(node, NavigableString) and node.parent.name not in ('script', 'style'):
            chain = []; q = node.parent
            while q is not None and q is not p: chain.insert(0, q); q = q.parent
            for c in nfc(str(node)): out.append((c, tuple(chain)))
    return out
def open_tag(t):
    at = ''.join(f' {k}="{html.escape(" ".join(v) if isinstance(v, list) else v)}"' for k, v in t.attrs.items())
    return f'<{t.name}{at}>'
def render_runs(cs):
    s, cur = '', ()
    def close(n):
        nonlocal s
        for t in reversed(cur[n:]): s += f'</{t.name}>'
    for c, ch in cs:
        if ch != cur:
            n = 0
            while n < min(len(ch), len(cur)) and ch[n] is cur[n]: n += 1
            close(n); 
            for t in ch[n:]: s += open_tag(t)
            cur = ch
        s += html.escape(c, quote=False)
    close(0); return s
def norm_map(cs):
    t, idx, prev_sp = '', [], False
    for i, (c, _) in enumerate(cs):
        if c.isspace():
            if prev_sp: continue
            c = ' '; prev_sp = True
        else: prev_sp = False
        t += c; idx.append(i)
    return t, idx
def sua_doan(soup, x, y, anchor, url):
    xn = re.sub(r'\s+', ' ', nfc(x)).strip().rstrip('…')
    for p in soup.select('section.main_content_post p, section.main_content_post li'):
        cs = chars(p); t, idx = norm_map(cs); k = t.find(xn)
        if k < 0: continue
        s, e = idx[k], idx[k + len(xn) - 1] + 1
        pstyle = open_tag(p).replace('<li', '<p') if p.name == 'p' else '<p style="text-align: justify;">'
        if y.startswith('>>>') and len(re.sub(r'\W', '', t)) - len(re.sub(r'\W', '', xn)) < 5:
            return p_moi(y, anchor, url)
        mid, ok = render_text(y, anchor, url, False)
        return pstyle + render_runs(cs[:s]) + mid + render_runs(cs[e:]) + '</p>', ok
    return None, False
def giu_cau_sua_link(soup, x, url):
    xn = re.sub(r'\s+', ' ', nfc(x)).strip()
    slug = url.rstrip('/').split('/')[-1]
    for p in soup.select('section.main_content_post p, section.main_content_post li'):
        if xn[:60] in re.sub(r'\s+', ' ', nfc(p.get_text())):
            for a in p.find_all('a', href=True):
                if slug in a['href']: a['href'] = url
            return str(p).replace('<li', '<p', 1).replace('</li>', '</p>'), True
    return None, False
def dam_bao_link(h, url):
    # link tới trang đích: luôn mở tab mới, bỏ nofollow nếu có (dofollow)
    def sua(m):
        a = m.group(0)
        if url.rstrip('/') not in a: return a
        a = re.sub(r'\s+rel="([^"]*)"', lambda r: ' rel="' + ' '.join(x for x in r.group(1).split() if x != 'nofollow' and x != 'ugc' and x != 'sponsored') + '"', a)
        a = a.replace(' rel=""', '')
        if 'target=' not in a: a = a[:-1] + ' target="_blank">'
        if 'rel=' not in a: a = a[:-1] + ' rel="noopener">'
        return a
    return re.sub(r'<a\b[^>]*>', sua, h)
tong = loi = 0; ket = {}
for b in ['a1', 'a2', 'a3', 'a4']:
    rep = json.load(open(D + b + '/report.json')); rows = {str(r['row']): r for r in json.load(open(D + b + '/rows.json'))}
    for row, v in rep.items():
        r = rows[row]; urls = {n: (a, u) for n, (a, u) in zip(r['so'], r['pairs'])}
        soup = BeautifulSoup(open(f'{D}{b}/raw-goc/r{row}.html', encoding='utf-8').read(), 'lxml')
        khoi = v['AB'].split('\n\n'); moi = []
        for k in khoi:
            m = re.match(r'Anchor (\d+): ([^\n]+)\nTrước khi chèn: ([^\n]+)\nĐề xuất: ([^\n]+)(.*)$', k, re.S)
            if not m: moi.append(k); continue
            n, anc, x, y, rest = int(m[1]), m[2].strip(), m[3].strip(), m[4].strip(), m[5]
            anchor, url = urls[n]; tong += 1
            if re.match(r'(?i)giữ nguyên câu', y): h, ok = giu_cau_sua_link(soup, x, url)
            elif x.startswith('(dòng mới)'): h, ok = p_moi(y, anchor, url)
            else: h, ok = sua_doan(soup, x, y, anchor, url)
            if not h or not ok: loi += 1; print('CHƯA DỰNG ĐƯỢC', row, n, x[:60]); h = h or p_moi(y, anchor, url)[0]
            h = dam_bao_link(h, url)
            moi.append(f'Anchor {n}: {anc}\nTrước khi chèn: {x}\nĐề xuất: {y}\nYêu cầu link: dofollow (không gắn nofollow), mở tab mới (target="_blank")\nHTML: ->\n{h}{rest}')
        ket[row] = {'AB': '\n\n'.join(moi), 'B': r['B']}
json.dump(ket, open(D + 'ab-html.json', 'w'), ensure_ascii=False, indent=0)
print('đề xuất', tong, 'lỗi', loi)

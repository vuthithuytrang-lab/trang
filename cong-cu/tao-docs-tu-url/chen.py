# Chèn internal link vào bản HTML của bài (out/<id>.html) theo kế hoạch plan.json -> final/<id>.html
# Mọi chữ mới/đổi tô nền vàng; ngay sau đoạn có thay đổi thêm 1 dòng ghi chú đỏ nghiêng.
import json, sys, re, difflib, html, copy
from bs4 import BeautifulSoup
sys.path.insert(0, sys.argv[1]); from blocks import load
SP = sys.argv[1]
YEL = 'background-color:#ffff00'
def esc(x): return html.escape(x, quote=False)
def hl(x): return f'<span style="{YEL}">{esc(x)}</span>'
def link(url, inner): return f'<a href="{html.escape(url)}">{inner}</a>'
def note(txt):
    return BeautifulSoup(f'<p style="text-align:justify;"><i><span style="color:#ff0000">{esc(txt)}</span></i></p>', 'lxml').p
def norm(x): return re.sub(r'\s+', ' ', x.replace('\xa0', ' ')).strip()

def diff_render(before, after, anchor, url, bold=()):
    """Dựng HTML cho câu sau khi chèn: từ mới/đổi tô vàng, anchor gắn link, giữ in đậm các cụm trong `bold`."""
    TOK = r'[^\s.,;:!?]+|[.,;:!?]+'
    bw = re.findall(TOK, before)
    am = list(re.finditer(TOK, after)); aw = [m.group(0) for m in am]
    changed = [False]*len(aw)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, bw, aw, autojunk=False).get_opcodes():
        if op != 'equal':
            for j in range(j1, j2): changed[j] = True
    # gộp các vùng đổi cách nhau <= 3 từ giống nhau, để phần tô vàng liền mạch, dễ đọc
    idx = [j for j, c in enumerate(changed) if c]
    for a, b in zip(idx, idx[1:]):
        if 1 < b - a <= 4:
            for j in range(a, b): changed[j] = True
    a0 = after.index(anchor); a1 = a0 + len(anchor)
    marks = [False]*len(after)
    for j, m in enumerate(am):
        if changed[j]:
            end = am[j+1].start() if j+1 < len(am) and changed[j+1] else m.end()
            for k in range(m.start(), end): marks[k] = True
    for k in range(a0, a1): marks[k] = True   # anchor luôn tô vàng, kể cả khi chữ không đổi
    bmask = [False]*len(after)
    for b in bold:
        i = after.find(b)
        if i >= 0:
            for k in range(i, i+len(b)): bmask[k] = True
    # cắt thành đoạn theo (mark, bold, in-anchor)
    out, k = [], 0
    while k < len(after):
        key = (marks[k], bmask[k], a0 <= k < a1)
        e = k
        while e < len(after) and (marks[e], bmask[e], a0 <= e < a1) == key: e += 1
        seg = esc(after[k:e])
        if key[0]: seg = f'<span style="{YEL}">{seg}</span>'
        if key[1]: seg = f'<b>{seg}</b>'
        out.append((key[2], seg)); k = e
    res, inlink = '', False
    for isA, seg in out:
        if isA and not inlink: res += f'<a href="{html.escape(url)}">'; inlink = True
        if not isA and inlink: res += '</a>'; inlink = False
        res += seg
    if inlink: res += '</a>'
    return res

def wrap_phrase(block, phrase, url):
    """Gắn link + tô vàng vào đúng cụm có sẵn (khớp nguyên cụm, không nằm trong link cũ)."""
    for s in block.find_all(string=True):
        if s.find_parent('a'): continue
        m = re.search(r'(?<![\wÀ-ỹ])' + re.escape(phrase) + r'(?![\wÀ-ỹ])', s)
        if m:
            new = esc(s[:m.start()]) + link(url, hl(m.group(0))) + esc(s[m.end():])
            s.replace_with(BeautifulSoup(f'<x>{new}</x>', 'lxml').x)
            for x in block.find_all('x'): x.unwrap()
            return True
    return False

def block_end(b):
    """Chỗ chèn đoạn mới sau b: nếu b là gạch đầu dòng thì chèn sau cả danh sách."""
    while b.name == 'li' or (b.parent is not None and b.parent.name in ('ul', 'ol')):
        b = b.parent
    return b

def run(rid, ops):
    s, bl = load(f'{SP}out/{rid}.html')
    orig = [copy.copy(b) for b in bl]
    after_blocks = []   # (block, note_text) — chèn ghi chú sau
    log = []
    for op in ops:
        b = bl[op['i']]
        before_txt = norm(orig[op['i']].get_text(''))
        if op['t'] in ('tygia', 'vietlai'):   # vietlai: viết lại nhẹ 1 câu có sẵn để anchor nằm tự nhiên trong câu
            # câu gốc ở cột I có thể chỉ là một phần của đoạn / gạch đầu dòng (VD sau nhãn in đậm)
            bt, at = norm(op['before']).rstrip('.'), norm(op['after'])
            # chỉ viết lại phần tử NHỎ NHẤT chứa câu gốc (1 ô bảng, 1 gạch đầu dòng con) để giữ nguyên cấu trúc bảng/danh sách
            cands = [x for x in [b] + b.find_all(['p', 'li', 'td', 'th']) if bt in norm(x.get_text(''))]
            if cands:
                small = min(cands, key=lambda x: len(x.get_text('')))
                if small is not b:
                    path = [y for y in b.find_all(True)].index(small)
                    b = small; orig_b = [y for y in orig[op['i']].find_all(True)][path]
                    before_txt = norm(orig_b.get_text(''))
                else: orig_b = orig[op['i']]
            else: orig_b = orig[op['i']]
            k = before_txt.find(bt)
            if k < 0:
                log.append(dict(op=op, ok=False, why='không khớp câu gốc')); continue
            tail = before_txt[k+len(bt):]
            if tail.startswith('.') and at.endswith('.'): tail = tail[1:]
            full_after = before_txt[:k] + at + tail
            bold = op.get('bold') or [x.get_text('') for x in orig_b.find_all('b') if norm(x.get_text(''))]
            inner = diff_render(before_txt, full_after, op['anchor'], op['url'], [norm(x) for x in bold])
            if op['after'].lstrip().startswith('>>>'): inner = f'<b><i>{inner}</i></b>'
            old_links = [(x.get_text(''), x.get('href', '')) for x in orig_b.find_all('a') if x.get('href')]
            b.clear(); b.append(BeautifulSoup(f'<x>{inner}</x>', 'lxml').x); b.x.unwrap()
            # giữ lại link cũ của đoạn (viết lại câu không được làm mất link có sẵn)
            for t, h in old_links:
                t = t.strip().rstrip('.:;, ')   # bỏ dấu câu/khoảng trắng dính vào chữ của link cũ
                if not t: continue
                for st in b.find_all(string=True):
                    if st.find_parent('a') or t not in st: continue
                    k = st.find(t); par = st.parent
                    new_html = esc(st[:k]) + f'<a href="{html.escape(h)}">{esc(t)}</a>' + esc(st[k+len(t):])
                    st.replace_with(BeautifulSoup(f'<x>{new_html}</x>', 'lxml').x)
                    for x in b.find_all('x'): x.unwrap()
                    break
                else:
                    log.append(dict(op=op, ok=False, why=f'link cũ "{t}" không còn chữ để gắn lại'))
            after_blocks.append((b, f'[Nội dung gốc trước khi chèn: {before_txt}]'))
        elif op['t'] == 'phrase':
            ok = wrap_phrase(b, op['anchor'], op['url'])
            if not ok: log.append(dict(op=op, ok=False, why='không thấy cụm')); continue
            after_blocks.append((b, f'[Nội dung gốc trước khi chèn: {before_txt}]'))
        elif op['t'] == 'sentence':
            sent = op['sentence']; a0 = sent.index(op['anchor'])
            inner = esc(' ') + hl(sent[:a0]) + link(op['url'], hl(op['anchor'])) + hl(sent[a0+len(op['anchor']):])
            # mục danh sách bọc chữ trong <p>: viết thêm câu vào trong <p>, không để chữ trôi ra ngoài (Docs dính liền 2 câu)
            kids = [x for x in b.children if getattr(x, 'name', None) or str(x).strip()]
            tb = kids[-1] if b.name == 'li' and kids and getattr(kids[-1], 'name', None) == 'p' else b
            tb.append(BeautifulSoup(f'<x>{inner}</x>', 'lxml').x); tb.x.unwrap()
            after_blocks.append((tb, f'[Nội dung gốc trước khi chèn: {before_txt}]'))
        elif op['t'] == 'xemthem':
            sent = op['sentence']; a0 = sent.index(op['anchor'])
            inner = hl(sent[:a0]) + link(op['url'], hl(op['anchor'])) + hl(sent[a0+len(op['anchor']):])
            p = BeautifulSoup(f'<p style="text-align:justify;"><b><i>{inner}</i></b></p>', 'lxml').p
            # Mẫu Trang duyệt 19/10/2026: ghi chú đỏ nằm TRÊN câu viết thêm, cách 1 dòng trống
            block_end(b).insert_after(p)
            p.insert_before(note('[Đề xuất viết thêm đoạn mới]'))
            p.insert_before(BeautifulSoup('<p></p>', 'lxml').p)
        elif op['t'] == 'doanmoi':
            # đoạn văn mới (chữ thường), ghi chú đỏ đặt trên, cách 1 dòng trống
            sent = op['sentence']; a0 = sent.index(op['anchor'])
            inner = hl(sent[:a0]) + link(op['url'], hl(op['anchor'])) + hl(sent[a0+len(op['anchor']):])
            p = BeautifulSoup(f'<p style="text-align:justify;">{inner}</p>', 'lxml').p
            block_end(b).insert_after(p)
            p.insert_before(note('[Đề xuất viết thêm đoạn mới]'))
            p.insert_before(BeautifulSoup('<p></p>', 'lxml').p)
        elif op['t'] == 'chuyenlink':
            # bài có sẵn link tới URL đích nhưng sai anchor: bỏ link khỏi cụm cũ, gắn vào ĐÚNG anchor của sheet
            hit = [x for x in b.find_all('a') if x.get('href', '').split('?')[0].rstrip('/').endswith(op['slug'])]
            if not hit:
                log.append(dict(op=op, ok=False, why='không thấy link có sẵn')); continue
            olds = []
            for a in hit:
                olds.append(a.get_text(''))
                a.replace_with(BeautifulSoup(f'<x>{hl(a.get_text(""))}</x>', 'lxml').x)
            for x in b.find_all('x'): x.unwrap()
            if op.get('sentence'):
                sent = op['sentence']; a0 = sent.index(op['anchor'])
                inner = esc(' ') + hl(sent[:a0]) + link(op['url'], hl(op['anchor'])) + hl(sent[a0+len(op['anchor']):])
                b.append(BeautifulSoup(f'<x>{inner}</x>', 'lxml').x); b.x.unwrap()
            else:
                # cụm anchor có sẵn trong đoạn (có thể vừa được tô vàng ở bước trên)
                if not wrap_phrase(b, op['anchor'], op['url']):
                    log.append(dict(op=op, ok=False, why='không thấy cụm anchor')); continue
            after_blocks.append((b, f'[Nội dung gốc trước khi chèn: {before_txt}] (link cũ gắn trên cụm "{"; ".join(olds)}" đã chuyển sang đúng anchor "{op["anchor"]}")'))
        elif op['t'] == 'dacolink':
            # bài gốc đã có link đúng URL đích: giữ nguyên, chỉ ghi chú để người duyệt thấy đủ anchor
            hit = [x for x in b.find_all('a') if x.get('href', '').split('?')[0].rstrip('/').endswith(op['slug'])]
            if not hit:
                log.append(dict(op=op, ok=False, why='không thấy link có sẵn')); continue
            # Trang yêu cầu 19/10/2026: link có sẵn giữ nguyên nhưng vẫn tô vàng để người duyệt thấy
            for a in hit:
                for t in list(a.find_all(string=True)):
                    t.replace_with(BeautifulSoup(f'<x>{hl(str(t))}</x>', 'lxml').x)
                for x in a.find_all('x'): x.unwrap()
            after_blocks.append((b, f'[Anchor "{op["anchor"]}": bài gốc đã có sẵn link đúng URL đích tại đoạn này, giữ nguyên, không chèn thêm]'))
        log.append(dict(op=op, ok=True))
    for b, t in after_blocks:
        if b.name == 'li':   # gạch đầu dòng: ghi chú xuống dòng ngay trong cùng gạch, không chen vào giữa danh sách
            b.append(BeautifulSoup('<br/>', 'lxml').br); b.append(note(t).i)
        else:
            b.insert_after(note(t))
    # Google Docs tự biến đoạn chữ giữa 2 dấu $ (VD "NT$; ... NT$") thành công thức toán → bọc riêng từng dấu $
    for st in list(s.find_all(string=lambda t: '$' in t)):
        if st.find_parent(['script', 'style']) or (st.parent.name == 'span' and st == '$'): continue
        st.replace_with(BeautifulSoup('<x>' + esc(str(st)).replace('$', '<span style="font-family:Arial">$</span>') + '</x>', 'lxml').x)
    for x in s.find_all('x'): x.unwrap()
    # phông Arial của Docs thiếu chữ chỉ số dưới "ₘ" (hiện ô vuông) → đổi sang chữ m dạng chỉ số dưới
    for st in list(s.find_all(string=lambda t: 'ₘ' in t)):
        st.replace_with(BeautifulSoup('<x>' + esc(str(st)).replace('ₘ', '<sub>m</sub>') + '</x>', 'lxml').x)
    for x in s.find_all('x'): x.unwrap()
    open(f'{SP}final/{rid}.html', 'w', encoding='utf-8').write(str(s))
    return log

plan = json.load(open(f'{SP}plan.json', encoding='utf-8'))
res = {rid: run(rid, ops) for rid, ops in plan.items()}
for rid, lg in res.items():
    for l in lg: print(rid, l['op']['t'], l['op']['anchor'], 'OK' if l['ok'] else 'LỖI: ' + l['why'])

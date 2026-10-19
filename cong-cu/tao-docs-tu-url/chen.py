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
    # gộp các vùng đổi cách nhau <= 2 từ giống nhau, để phần tô vàng liền mạch, dễ đọc
    idx = [j for j, c in enumerate(changed) if c]
    for a, b in zip(idx, idx[1:]):
        if 1 < b - a <= 3:
            for j in range(a, b): changed[j] = True
    a0 = after.index(anchor); a1 = a0 + len(anchor)
    marks = [False]*len(after)
    for j, m in enumerate(am):
        if changed[j]:
            end = am[j+1].start() if j+1 < len(am) and changed[j+1] else m.end()
            for k in range(m.start(), end): marks[k] = True
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

def run(rid, ops):
    s, bl = load(f'{SP}out/{rid}.html')
    orig = [copy.copy(b) for b in bl]
    after_blocks = []   # (block, note_text) — chèn ghi chú sau
    log = []
    for op in ops:
        b = bl[op['i']]
        before_txt = norm(orig[op['i']].get_text(''))
        if op['t'] == 'tygia':
            if norm(op['before']).rstrip('.') != before_txt.rstrip('.'):  # bỏ qua khác biệt dấu chấm cuối câu
                log.append(dict(op=op, ok=False, why='không khớp câu gốc')); continue
            inner = diff_render(before_txt, norm(op['after']), op['anchor'], op['url'], op.get('bold', ()))
            if op['after'].lstrip().startswith('>>>'): inner = f'<b><i>{inner}</i></b>'
            b.clear(); b.append(BeautifulSoup(f'<x>{inner}</x>', 'lxml').x); b.x.unwrap()
            after_blocks.append((b, f'[Trước khi chèn: {before_txt}]'))
        elif op['t'] == 'phrase':
            ok = wrap_phrase(b, op['anchor'], op['url'])
            if not ok: log.append(dict(op=op, ok=False, why='không thấy cụm')); continue
            after_blocks.append((b, f'[Trước khi chèn: {before_txt}]'))
        elif op['t'] == 'sentence':
            sent = op['sentence']; a0 = sent.index(op['anchor'])
            inner = esc(' ') + hl(sent[:a0]) + link(op['url'], hl(op['anchor'])) + hl(sent[a0+len(op['anchor']):])
            b.append(BeautifulSoup(f'<x>{inner}</x>', 'lxml').x); b.x.unwrap()
            after_blocks.append((b, f'[Trước khi chèn: {before_txt}]'))
        elif op['t'] == 'xemthem':
            sent = op['sentence']; a0 = sent.index(op['anchor'])
            inner = hl(sent[:a0]) + link(op['url'], hl(op['anchor'])) + hl(sent[a0+len(op['anchor']):])
            p = BeautifulSoup(f'<p style="text-align:justify;"><b><i>{inner}</i></b></p>', 'lxml').p
            # Mẫu Trang duyệt 19/10/2026: ghi chú đỏ nằm TRÊN câu viết thêm, cách 1 dòng trống
            b.insert_after(p)
            p.insert_before(note('[Đề xuất viết thêm đoạn mới]'))
            p.insert_before(BeautifulSoup('<p></p>', 'lxml').p)
        log.append(dict(op=op, ok=True))
    for b, t in after_blocks:
        b.insert_after(note(t))
    open(f'{SP}final/{rid}.html', 'w', encoding='utf-8').write(str(s))
    return log

plan = json.load(open(f'{SP}plan.json', encoding='utf-8'))
res = {rid: run(rid, ops) for rid, ops in plan.items()}
for rid, lg in res.items():
    for l in lg: print(rid, l['op']['t'], l['op']['anchor'], 'OK' if l['ok'] else 'LỖI: ' + l['why'])

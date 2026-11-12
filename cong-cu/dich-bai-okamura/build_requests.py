"""Dựng tab bản dịch kiểu "bảng 2 cột: trái bản Việt | phải bản Anh" trong Google Doc.

Bước 1 (tạo khung):  python3 build_requests.py frame --title "EN" > frame.json
    -> gửi update_doc. Lấy tabId mới trong phản hồi (addDocumentTab).
    Gửi tiếp: python3 build_requests.py table --tab TAB_ID   (xoay ngang trang + chèn bảng 1x2)
Bước 2 (đổ nội dung): đọc lại doc (read_doc) rồi
    python3 build_requests.py fill DOC.json EN.txt --tab TAB_ID --src-tab t.0 --out reqs.json [--chunk 60]
    -> in ra các file reqs_1.json, reqs_2.json ... gửi update_doc lần lượt, ĐÚNG THỨ TỰ.

EN.txt: mỗi dòng "SỐ: nội dung" — SỐ là số đầu dòng do dump_doc.py in ra cho bản Việt.
Ký hiệu trong nội dung: **đậm**  _nghiêng_  [chữ](link)  [IMG kix.id]  (chỗ đặt ảnh).
Dòng thiếu / để trống = bỏ đoạn đó ở bản Anh (dùng để xoá dòng trống thừa).

Luật checklist tự áp cho bản Anh:
  - link okamura.com.vn/vi/... -> okamura.com.vn/...
  - heading không in đậm
  - đoạn căn giữa (chú thích ảnh): in nghiêng toàn bộ, có dấu chấm cuối
  - "etc." / "etc" -> "..."
  - giãn dòng 1.5, cách đoạn trên/dưới 10pt
"""
import argparse, json, re, sys

LINK_STYLE = {"underline": True,
              "foregroundColor": {"color": {"rgbColor": {"red": 0.06666667, "green": 0.33333334, "blue": 0.8}}}}
MAX_IMG_W = 330
TS_FIELDS = "bold,italic,underline,strikethrough,link,foregroundColor,backgroundColor,fontSize,baselineOffset"
PS_KEYS = ["namedStyleType", "alignment", "lineSpacing", "spaceAbove", "spaceBelow",
           "indentStart", "indentFirstLine", "spacingMode"]


def load(p):
    d = json.load(open(p))
    if isinstance(d, dict) and 'content' in d:
        d = d['content'] if isinstance(d['content'], dict) else json.loads(d['content'])
    return d


def fix_link(url):
    return re.sub(r'(okamura\.com\.vn)/vi(/|$)', r'\1/', url)


# ---------- đọc bản Việt thành khối ----------
def vn_blocks(content, objs):
    out = []
    for el in content:
        if 'paragraph' in el:
            p = el['paragraph']; ps = p.get('paragraphStyle', {})
            runs = []
            for e in p['elements']:
                if 'textRun' in e:
                    t = e['textRun']['content'].replace('\n', '')
                    if t:
                        runs.append({'t': t, 's': e['textRun'].get('textStyle', {})})
                elif 'inlineObjectElement' in e:
                    oid = e['inlineObjectElement']['inlineObjectId']
                    emb = objs[oid]['inlineObjectProperties']['embeddedObject']
                    runs.append({'img': oid, 'uri': emb['imageProperties']['contentUri'], 'size': emb.get('size')})
            out.append({'type': 'p', 'key': el['startIndex'], 'ps': ps,
                        'bullet': 'bullet' in p, 'runs': runs})
        elif 'table' in el:
            tb = el['table']
            out.append({'type': 'table', 'rows': [[vn_blocks(c['content'], objs) for c in r['tableCells']]
                                                  for r in tb['tableRows']]})
    return out


# ---------- đọc markup bản Anh ----------
TOK = re.compile(r'\[IMG ([^\]\s]+)[^\]]*\]|\[([^\]]*)\]\(([^)]+)\)|\*\*|_')


def parse_markup(s):
    runs, bold, ital = [], False, False
    pos = 0
    def add(t, link=None):
        if t:
            st = {}
            if bold: st['bold'] = True
            if ital: st['italic'] = True
            if link:
                st['link'] = {'url': fix_link(link)}; st.update(LINK_STYLE)
            runs.append({'t': t, 's': st})
    for m in TOK.finditer(s):
        add(s[pos:m.start()])
        if m.group(1):
            runs.append({'img': m.group(1)})
        elif m.group(3):
            add(m.group(2), m.group(3))
        elif m.group(0) == '**':
            bold = not bold
        else:
            ital = not ital
        pos = m.end()
    add(s[pos:])
    # gộp run liền nhau cùng kiểu
    merged = []
    for r in runs:
        if merged and 't' in r and 't' in merged[-1] and merged[-1]['s'] == r['s']:
            merged[-1]['t'] += r['t']
        else:
            merged.append(r)
    return merged


def en_rules(runs, ps):
    named = ps.get('namedStyleType', 'NORMAL_TEXT')
    for r in runs:
        if 't' in r:
            r['t'] = re.sub(r'\s*,?\s*\betc\b\.?', '...', r['t'])
    if named.startswith('HEADING') or named == 'TITLE':
        for r in runs:
            if 't' in r: r['s'].pop('bold', None)
    elif ps.get('alignment') == 'CENTER' and any('t' in r and r['t'].strip() for r in runs):
        for r in runs:
            if 't' in r: r['s']['italic'] = True
        last = [r for r in runs if 't' in r][-1]
        stripped = last['t'].rstrip()
        if stripped and stripped[-1] not in '.!?':
            last['t'] = stripped + '.'
        else:
            last['t'] = stripped
    return runs


def en_blocks(vn, tr, objs_uri):
    out = []
    for b in vn:
        if b['type'] == 'table':
            out.append({'type': 'table', 'rows': [[en_blocks(c, tr, objs_uri) for c in row] for row in b['rows']]})
            continue
        s = tr.get(b['key'])
        if s is None or not s.strip():
            continue
        runs = parse_markup(s.strip())
        for r in runs:
            if 'img' in r:
                r['uri'], r['size'] = objs_uri[r['img']]
        ps = dict(b['ps'])
        ps['lineSpacing'] = 150
        ps['spaceAbove'] = {'magnitude': 10, 'unit': 'PT'}
        ps['spaceBelow'] = {'magnitude': 10, 'unit': 'PT'}
        out.append({'type': 'p', 'key': b['key'], 'ps': ps, 'bullet': b['bullet'], 'runs': en_rules(runs, ps)})
    return out


# ---------- sinh request ----------
def clean_ts(s):
    keep = {k: v for k, v in s.items() if k in ('bold', 'italic', 'underline', 'strikethrough', 'link',
                                                'foregroundColor', 'backgroundColor', 'fontSize', 'baselineOffset')}
    if keep.get('baselineOffset') == 'NONE': keep.pop('baselineOffset')
    for k in ('bold', 'italic', 'underline', 'strikethrough'):
        if keep.get(k) is False: keep.pop(k)
    return keep


def ps_sig(b):
    ps = {k: b['ps'][k] for k in PS_KEYS if k in b['ps']}
    for k in ('indentStart', 'indentFirstLine', 'spaceAbove', 'spaceBelow'):
        if k in ps and not ps[k].get('magnitude'): ps.pop(k)
    if b['bullet']:
        ps.pop('indentStart', None); ps.pop('indentFirstLine', None)
    return json.dumps(ps, sort_keys=True), ps


class Gen:
    def __init__(self, tab):
        self.tab = tab; self.reqs = []

    def loc(self, i):
        return {'index': i, 'tabId': self.tab}

    def rng(self, a, b):
        return {'startIndex': a, 'endIndex': b, 'tabId': self.tab}

    def segment(self, P, paras):
        """Chèn 1 dãy đoạn (không có bảng) vào vị trí P, trong đoạn trống sẵn có."""
        texts, offs, o = [], [], 0
        for b in paras:
            t = ''.join(r.get('t', '') for r in b['runs'])
            texts.append(t); offs.append(o); o += len(t) + 1
        full = '\n'.join(texts)
        R = self.reqs
        if full:
            R.append({'insertText': {'text': full, 'location': self.loc(P)}})
            R.append({'updateTextStyle': {'textStyle': {}, 'fields': TS_FIELDS, 'range': self.rng(P, P + len(full))}})
        end = P + len(full) + 1
        R.append({'deleteParagraphBullets': {'range': self.rng(P, end)}})
        # kiểu đoạn: 1 lệnh kiểu nền cho cả đoạn, rồi chỉ sửa các đoạn khác nền
        sigs = [ps_sig(b) for b in paras]
        from collections import Counter
        base = Counter(x[0] for x in sigs).most_common(1)[0][0]
        def ps_req(i, j):
            ps = sigs[i][1]
            fields = [k for k in PS_KEYS if not (paras[i]['bullet'] and k in ('indentStart', 'indentFirstLine'))]
            R.append({'updateParagraphStyle': {'paragraphStyle': ps, 'fields': ','.join(fields),
                                               'range': self.rng(P + offs[i], P + offs[j] + len(texts[j]) + 1)}})
        bi = next(i for i, x in enumerate(sigs) if x[0] == base)
        ps_req_base = sigs[bi][1]
        fields = [k for k in PS_KEYS if not (paras[bi]['bullet'] and k in ('indentStart', 'indentFirstLine'))]
        R.append({'updateParagraphStyle': {'paragraphStyle': ps_req_base, 'fields': ','.join(fields),
                                           'range': self.rng(P, end)}})
        i = 0
        while i < len(paras):
            if sigs[i][0] == base:
                i += 1; continue
            j = i
            while j + 1 < len(paras) and sigs[j + 1][0] == sigs[i][0]: j += 1
            ps_req(i, j)
            i = j + 1
        # gạch đầu dòng
        i = 0
        while i < len(paras):
            if paras[i]['bullet']:
                j = i
                while j + 1 < len(paras) and paras[j + 1]['bullet']: j += 1
                R.append({'createParagraphBullets': {'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE',
                                                     'range': self.rng(P + offs[i], P + offs[j] + len(texts[j]))}})
                i = j + 1
            else:
                i += 1
        # kiểu chữ
        imgs = []
        for b, off in zip(paras, offs):
            c = P + off
            for r in b['runs']:
                if 'img' in r:
                    imgs.append((c, r)); continue
                st = clean_ts(r['s'])
                if st:
                    R.append({'updateTextStyle': {'textStyle': st, 'fields': ','.join(st.keys()),
                                                  'range': self.rng(c, c + len(r['t']))}})
                c += len(r['t'])
        # ảnh: chèn từ cuối lên để không lệch vị trí
        for c, r in sorted(imgs, key=lambda x: -x[0]):
            req = {'uri': r['uri'], 'location': self.loc(c)}
            if r.get('size') and 'width' in r['size'] and 'height' in r['size']:
                w, h = r['size']['width']['magnitude'], r['size']['height']['magnitude']
                k = min(1.0, MAX_IMG_W / w)  # ô bảng chỉ rộng ~1/2 trang ngang
                req['objectSize'] = {'width': {'magnitude': round(w * k, 1), 'unit': 'PT'},
                                     'height': {'magnitude': round(h * k, 1), 'unit': 'PT'}}
            R.append({'insertInlineImage': req})

    def cell(self, P, blocks):
        """Đổ nội dung 1 ô (ô đang trống, đoạn trống ở P). Làm ngược từ cuối lên."""
        segs, tables, cur = [], [], []
        for b in blocks:
            if b['type'] == 'table':
                segs.append(cur); tables.append(b); cur = []
            else:
                cur.append(b)
        segs.append(cur)
        for k in range(len(segs) - 1, -1, -1):
            if segs[k]:
                self.segment(P, segs[k])
            if k > 0:
                tb = tables[k - 1]; rows, cols = len(tb['rows']), len(tb['rows'][0])
                self.reqs.append({'insertTable': {'rows': rows, 'columns': cols, 'location': self.loc(P)}})
                T = P + 1
                cells, idx = [], T
                for r in range(rows):
                    idx += 1
                    for c in range(cols):
                        idx += 1  # vị trí bắt đầu ô
                        cells.append((idx + 1, tb['rows'][r][c]))  # đoạn trống trong ô
                        idx += 1
                for cp, cb in reversed(cells):
                    self.cell(cp, cb)


def read_tr(path):
    tr = {}
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^\s*(\d+):\s?(.*)$', line.rstrip('\n'))
        if m: tr[int(m.group(1))] = m.group(2)
    return tr


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    f = sp.add_parser('frame'); f.add_argument('--title', default='Bản dịch EN')
    t = sp.add_parser('table'); t.add_argument('--tab', required=True)
    g = sp.add_parser('fill')
    g.add_argument('doc'); g.add_argument('en')
    g.add_argument('--tab', required=True); g.add_argument('--src-tab', default='t.0')
    g.add_argument('--out', required=True); g.add_argument('--chunk', type=int, default=0)
    g.add_argument('--cells', help='"5,7" = vị trí 2 ô của bảng khung vừa tạo ở tab mới (bỏ qua bước đọc lại)')
    a = ap.parse_args()

    if a.cmd == 'frame':
        print(json.dumps({'requests': [{'addDocumentTab': {'tabProperties': {'title': a.title}}}]}, ensure_ascii=False)); return
    if a.cmd == 'table':
        print(json.dumps({'requests': [
            {'updateDocumentStyle': {'documentStyle': {'flipPageOrientation': True}, 'fields': 'flipPageOrientation', 'tabId': a.tab}},
            {'insertTable': {'rows': 1, 'columns': 2, 'location': {'index': 1, 'tabId': a.tab}}}]})); return

    d = load(a.doc)
    def all_tabs(ts):
        for x in ts:
            yield x; yield from all_tabs(x.get('childTabs', []))
    tabs = {x['tabProperties']['tabId']: x['documentTab'] for x in all_tabs(d['tabs'])}
    src = tabs[a.src_tab]
    objs = src.get('inlineObjects', {})
    vn = vn_blocks(src['body']['content'], objs)
    uri = {k: (v['inlineObjectProperties']['embeddedObject']['imageProperties']['contentUri'],
               v['inlineObjectProperties']['embeddedObject'].get('size')) for k, v in objs.items()}
    tr = read_tr(a.en)
    # kiểm tra khóa
    keys = set()
    def collect(bs):
        for b in bs:
            if b['type'] == 'p': keys.add(b['key'])
            else:
                for row in b['rows']:
                    for c in row: collect(c)
    collect(vn)
    bad = [k for k in tr if k not in keys]
    if bad: sys.exit(f'Số dòng không khớp bản Việt: {bad}')
    for k, s in tr.items():
        for oid in re.findall(r'\[IMG ([^\]\s]+)', s):
            if oid not in uri: sys.exit(f'Ảnh {oid} (dòng {k}) không có trong bản Việt')
    en = en_blocks(vn, tr, uri)
    if a.cells:
        L, R = map(int, a.cells.split(','))
    else:
        dst = tabs[a.tab]
        tbl = [e for e in dst['body']['content'] if 'table' in e]
        if not tbl: sys.exit('Tab đích chưa có bảng khung')
        cells = tbl[0]['table']['tableRows'][0]['tableCells']
        L, R = cells[0]['content'][0]['startIndex'], cells[1]['content'][0]['startIndex']
        if any(len(c['content']) > 1 or c['endIndex'] - c['startIndex'] > 2 for c in cells):
            sys.exit('Bảng khung không trống — dừng để tránh ghi đè')
    gen = Gen(a.tab)
    gen.cell(R, en)   # ô phải trước (vị trí lớn hơn)
    gen.cell(L, vn)
    reqs = gen.reqs
    n = a.chunk or len(reqs)
    parts = [reqs[i:i + n] for i in range(0, len(reqs), n)]
    base = a.out[:-5] if a.out.endswith('.json') else a.out
    for i, p in enumerate(parts, 1):
        json.dump({'requests': p}, open(f'{base}_{i}.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print(f'{len(reqs)} requests -> {len(parts)} file: {base}_1..{len(parts)}.json  (ô trái={L}, ô phải={R})')


if __name__ == '__main__':
    main()

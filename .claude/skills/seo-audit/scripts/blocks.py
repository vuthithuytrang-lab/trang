# -*- coding: utf-8 -*-
"""Các khối HTML của báo cáo từng cụm — mục 2 và mục 8 đến 17.

Mọi hàm nhận CTX (dict dữ liệu đã nạp) thay vì đọc file trực tiếp, nên tái dùng được
cho bất kỳ dự án nào. build_report.py nạp dữ liệu một lần rồi gọi các hàm ở đây.

CTX gồm: me (domain), pages (dict url→trang), perkw (dict kw→so sánh), tech (dict url→kỹ thuật),
gsc (dict theo cụm), js (set url render JS), sh (hàm rút gọn url).
"""
import collections, html, re, statistics as st, unicodedata


def esc(s): return html.escape(str(s), quote=False)
def num(v): return format(int(v), ',').replace(',', '.')


LABEL = {'top3': 'top 3', 'top5': 'top 5', 'top10': 'top 10'}

LAB = {'keep': ('GIỮ', 't-keep'), 'fix': ('SỬA', 't-fix'), 'new': ('MỚI', 't-new'),
       'gap': ('GAP SERP', 't-gap'), 'brand': ('BRAND', 't-brand')}

STOP = set(('và của cho các những một là có với tại trong khi để về từ như hay nhất '
            'mới nên bạn được sẽ đó này gì').split())
NAMEISH = re.compile(r'(dự án|công trình|chi nhánh|khách hàng|anh |chị |mr|ms)', re.I)
PROJECT = re.compile(r'(office|tower|building|quận\s*\d|q\.\s*\d|tp\.|–|—)', re.I)

KEYS = [('báo giá|chi phí|giá |đơn giá|dự toán', 'Bảng giá / chi phí'),
        ('quy trình|các bước', 'Quy trình làm việc'),
        (r'mẫu |top \d|\d+\+', 'Bộ mẫu / danh sách mẫu'),
        ('vì sao|tại sao|lý do|cam kết|năng lực|kinh nghiệm', 'Vì sao chọn đơn vị'),
        ('dự án|công trình đã|thực tế', 'Dự án thực tế'),
        ('phong cách', 'Phong cách thiết kế'),
        ('tiêu chuẩn|nguyên tắc|lưu ý|kinh nghiệm thiết kế', 'Tiêu chuẩn / lưu ý'),
        ('xu hướng', 'Xu hướng'),
        ('câu hỏi|faq|hỏi đáp|thắc mắc', 'FAQ'),
        ('liên hệ|tư vấn|hotline|nhận báo giá', 'Liên hệ / CTA'),
        ('là gì|khái niệm|định nghĩa', 'Định nghĩa / là gì'),
        ('vật liệu|nội thất sử dụng|chất liệu', 'Vật liệu'),
        (r'diện tích|m2|\dm²', 'Theo diện tích'),
        ('bố trí|không gian|khu vực|phòng ', 'Bố trí không gian'),
        ('thời gian|tiến độ|bảo hành', 'Tiến độ / bảo hành')]


def is_project(h):
    if NAMEISH.search(h):
        return True
    caps = len(re.findall(r'\b[A-ZĐ][a-zà-ỹ]{2,}', h))
    return bool(PROJECT.search(h)) and caps >= 1


def toks(s):
    s = unicodedata.normalize('NFC', s).lower()
    s = re.sub(r'^\s*\d+[\.\)]\s*', '', s)
    s = re.sub(r'[^\w\s]', ' ', s)
    return {w for w in s.split() if w not in STOP and len(w) > 1}


def sim(a, b):
    return len(a & b) / min(len(a), len(b)) if a and b else 0



def _card(idv, title, icon, inner):
    return ('\n<div class="card" id="' + idv + '">\n'
            '  <h2><i class="fa-solid ' + icon + '"></i> ' + title + '</h2>\n  ' + inner + '\n</div>\n')


def _empty(idv, title, icon, msg):
    """Mục không đủ dữ liệu vẫn phải hiện, kèm lý do — không được ẩn đi."""
    return _card(idv, title, icon,
                 '<div class="note"><i class="fa-solid fa-circle-info"></i>' + msg + '</div>')


# ── Mục 2: mổ xẻ đối thủ ─────────────────────────────────────────────────────

def _sections(p):
    """Các nhóm mục nội dung một trang thật sự có, nhận diện từ heading đã crawl."""
    got = set()
    for hh in p['headings']:
        n = _norm(hh)
        for pat, lab in KEYS:
            if re.search(pat, n):
                got.add(lab)
    return got


def _auto_rival_note(ctx, p, cohort, held, topn):
    """Mạnh — yếu — chỗ chen vào, sinh từ số đo được. Không có số thì không viết dòng đó."""
    med = lambda k: st.median([x[k] for x in cohort]) if cohort else None
    strong, weak = [], []
    for lab, k in (('số từ', 'words'), ('số ảnh', 'imgs_all'), ('link nội bộ', 'ilinks')):
        m = med(k)
        if m is None:
            continue
        v = p[k]
        (strong if v >= m else weak).append(f'{lab} {v} so với trung vị {m:.0f} của nhóm top {topn}')
    if p['faq_schema']:
        strong.append('có FAQPage schema')
    elif any(x.get('faq_schema') for x in cohort):
        weak.append('không có FAQPage schema trong khi trang khác cùng nhóm có')
    if p['datemod'][:10]:
        strong.append(f'nội dung ghi ngày cập nhật {p["datemod"][:10]}')
    else:
        weak.append('không có dateModified nên không biết lần cập nhật gần nhất')
    mh2 = med('h2')
    if mh2 is not None:
        (strong if p['h2'] >= mh2 else weak).append(
            f'{p["h2"]} H2 / {p["h3"]} H3 so với trung vị {mh2:.0f} H2 của nhóm')
    mine_sec = _sections(p)
    others = collections.Counter()
    for x in cohort:
        if x['url'] == p['url']:
            continue
        for lab in _sections(x):
            others[lab] += 1
    miss = [lab for lab, c in others.most_common() if c >= 2 and lab not in mine_sec]
    chen = []
    if miss:
        chen.append('thiếu mục ' + ', '.join(f'<b>{esc(x)}</b>' for x in miss[:4])
                    + f' trong khi ít nhất 2 trang cùng nhóm top {topn} đều có')
    weak_pos = [f'"{esc(k)}" ({pp})' for k, pp in held if pp >= 2][:5]
    if weak_pos:
        chen.append('đang đứng sau vị trí 1 ở ' + ', '.join(weak_pos)
                    + ' — đây là các từ khoá vượt được mà không cần hạ trang số 1')
    if not chen:
        chen.append(f'không tìm ra khe hở đo được: trang này có đủ các nhóm mục nội dung mà nhóm top {topn} '
                    'có, và đang giữ vị trí 1 ở mọi từ khoá đo được của cụm')
    return ('; '.join(strong) or 'không chỉ số nào vượt trung vị nhóm',
            '; '.join(weak) or 'không chỉ số nào dưới trung vị nhóm',
            '. '.join(chen))


def rival_block(ctx, rows, notes=None, topn=3):
    """notes: {domain: (mạnh, yếu, chỗ chen vào)} do agent viết, ghi đè bản tự động từng domain."""
    P, sh, ME = ctx['pages'], ctx['sh'], ctx['me']
    dm, urls, best = collections.Counter(), collections.defaultdict(collections.Counter), {}
    held = collections.defaultdict(list)
    for r in rows:
        pk = ctx['perkw'].get(r['kw'])
        if not pk: continue
        for x in pk['riv']:
            if x['pos'] > topn: continue
            u = x['url'].split('?')[0]
            dm[x['dom']] += 1; urls[x['dom']][u] += 1
            held[x['dom']].append((r['kw'], x['pos']))
            best[x['dom']] = min(best.get(x['dom'], 99), x['pos'])
    if not dm: return ''
    notes = notes or {}

    def row(p, dom_, k, bp, me=False):
        faq = 'schema' if p['faq_schema'] else ('hiển thị' if p['faq_render'] else 'không')
        return ('<tr' + (' class="me"' if me else '') + '><td>' +
                (esc(dom_) if me else '<b>' + esc(dom_) + '</b>') + '</td>'
                '<td class="mono small">' + esc(sh(p['url'])) + '</td>'
                '<td class="num">' + k + '</td><td class="num">' + bp + '</td>'
                '<td class="num">' + str(p['words']) + '</td>'
                '<td class="num small">' + f"{p['imgs_all']} ({p['lazy']}/{p['srcset']}/{p['webp']})" + '</td>'
                '<td class="num">' + str(p['kb']) + '</td>'
                '<td class="num">' + f"{p['h2']}/{p['h3']}" + '</td>'
                '<td class="num">' + str(p['ilinks']) + '</td>'
                '<td class="num small">' + faq + '</td>'
                '<td class="num small">' + esc(p['datemod'][:10] or '—') + '</td></tr>')

    tb = ['<div class="tblwrap"><table><thead><tr><th>Domain</th><th>Trang đang xếp hạng</th>'
          f'<th class="num">Top {topn} ở<br>bao nhiêu kw</th><th class="num">Hạng<br>tốt nhất</th>'
          '<th class="num">Số từ</th><th class="num">Ảnh<br>(lazy/srcset/webp)</th><th class="num">KB</th>'
          '<th class="num">H2/H3</th><th class="num">Link<br>nội bộ</th><th class="num">FAQ</th>'
          '<th class="num">Cập nhật</th></tr></thead><tbody>']
    mine = [u for u, _ in collections.Counter(r['url'].split('?')[0] for r in rows if r['url']).most_common(2)]
    for u in mine:
        if u in P: tb.append(row(P[u], ME, '—', '—', me=True))
    for d, k in dm.most_common(6):
        u = urls[d].most_common(1)[0][0]
        if u in P: tb.append(row(P[u], d, str(k), str(best[d])))
    tb.append('</tbody></table></div>')

    cohort = [P[urls[d].most_common(1)[0][0]] for d, _ in dm.most_common(6)
              if urls[d].most_common(1)[0][0] in P and urls[d].most_common(1)[0][0] not in ctx['js']]
    cards = []
    for d, k in dm.most_common(6):
        u = urls[d].most_common(1)[0][0]
        p = P.get(u)
        if not p or u in ctx['js']: continue
        m, w, ch = notes[d] if d in notes else _auto_rival_note(ctx, p, cohort, held[d], topn)
        cards.append('<div class="rival"><div class="rh"><span class="rname">' + esc(d) + '</span>'
                     f'<span class="rstat">top {topn} ở {k} từ khoá · hạng tốt nhất {best[d]} · '
                     f'{p["words"]} từ · {p["imgs_all"]} ảnh · {p["ilinks"]} link nội bộ</span></div>'
                     '<p class="rtitle">Title: <span class="mono">' + esc(p['title'][:130]) + '</span></p>'
                     '<dl><dt class="m">Mạnh ở</dt><dd>' + m + '</dd>'
                     '<dt class="w">Yếu ở</dt><dd>' + w + '</dd>'
                     '<dt class="a">Chỗ chen vào</dt><dd>' + ch + '</dd></dl></div>')
    return ('\n<div class="card" id="doithu">\n'
            f'  <h2><i class="fa-solid fa-users-viewfinder"></i> 2. Mổ xẻ đối thủ đang chiếm top {topn}</h2>\n'
            f'  <p style="color:var(--text-2)">Các trang <b>thực sự đang đứng top {topn}</b> của những từ khoá '
            'trong cụm, lấy từ file check top. Mọi chỉ số đo trực tiếp từ HTML thô. Dòng nền xanh là trang của mình.</p>\n  '
            + '\n'.join(tb) + '\n  ' + '\n'.join(cards) + '\n</div>\n')


# ── Mục 8: ngưỡng lọt top và đối chiếu mục nội dung ──────────────────────────

def threshold_block(ctx, rows, myurls, mark='top10'):
    lo, hi = {'top10': (1, 10), 'top5': (1, 5), 'top3': (1, 3)}[mark]
    P = ctx['pages']
    E = {}
    for r in rows:
        pk = ctx['perkw'].get(r['kw'])
        if not pk: continue
        for x in pk['riv']:
            if lo <= x['pos'] <= hi: E[x['url']] = x
    E = list(E.values())
    if len(E) < 5: return ''  # mốc này không đủ mẫu; build_report vẫn dựng card mục 8
    med = lambda k: st.median([x[k] for x in E])
    m = P.get(myurls[0][0]) if myurls else None
    if not m: return ''
    specs = [('Số từ nội dung chính', med('words'), m['words'], True),
             ('Số ảnh', med('imgs'), m['imgs_all'], True),
             ('Link nội bộ', med('ilinks'), m['ilinks'], True),
             ('Số H2', med('h2'), m['h2'], True),
             ('Số H3', med('h3'), m['h3'], True),
             ('Dung lượng HTML (KB)', med('kb'), m['kb'], False)]
    h = ['<div class="tblwrap"><table><thead><tr><th>Chỉ số</th>'
         f'<th class="num">Ngưỡng lọt {LABEL.get(mark, mark)}<br><span class="small">trung vị toàn bộ {len(E)} trang đang ở vị trí {lo}–{hi}</span></th>'
         '<th class="num">Trang chủ lực của mình</th><th>Đã đạt chưa</th></tr></thead><tbody>']
    for lab, tgt, val, up in specs:
        ok = (val >= tgt) if up else (val <= tgt)
        d = abs(val - tgt)
        if up:
            note = f'Đạt, trên ngưỡng {d:.0f}' if ok else f'<b>Dưới ngưỡng {d:.0f}</b>'
            cls = 'top' if ok else 'zero'
        elif ok:
            note, cls = f'Nhẹ hơn ngưỡng {d:.0f}KB', 'top'
        elif d <= 30:
            note, cls = f'Nặng hơn ngưỡng {d:.0f}KB, không đáng ngại', ''
        else:
            note, cls = f'<b>Nặng hơn ngưỡng {d:.0f}KB</b>', 'zero'
        h.append(f'<tr><td>{esc(lab)}</td><td class="num">{tgt:.0f}</td>'
                 f'<td class="num {cls}">{val:.0f}</td><td class="small">{note}</td></tr>')
    return '\n'.join(h) + '</tbody></table></div>'


def gap_block(ctx, rows, myurls, topn=14):
    P, JS = ctx['pages'], ctx['js']
    urls = collections.Counter()
    for r in rows:
        pk = ctx['perkw'].get(r['kw'])
        if not pk: continue
        for x in pk['riv']: urls[x['url'].split('?')[0]] += 1
    top = [u for u, _ in urls.most_common(topn) if u in P and u not in JS]
    cnt, mine = collections.Counter(), set()
    for u in top:
        seen = set()
        for hh in P[u]['headings']:
            n = _norm(hh)
            for pat, lab in KEYS:
                if re.search(pat, n) and lab not in seen:
                    seen.add(lab); cnt[lab] += 1
    for u, _ in myurls[:2]:
        if u in P:
            for hh in P[u]['headings']:
                n = _norm(hh)
                for pat, lab in KEYS:
                    if re.search(pat, n): mine.add(lab)
    out = ['<div class="tblwrap"><table><thead><tr><th>Nhóm mục nội dung</th>'
           f'<th class="num">Bao nhiêu trong {len(top)} trang top có</th>'
           '<th class="num">Trang mình</th><th>Kết luận</th></tr></thead><tbody>']
    miss = 0
    for lab, k in cnt.most_common():
        if k < max(2, len(top) // 3): continue
        has = lab in mine
        if not has: miss += 1
        out.append(f'<tr><td>{esc(lab)}</td><td class="num">{k}/{len(top)}</td>'
                   f'<td class="num {"top" if has else "zero"}">{"có" if has else "không"}</td>'
                   f'<td class="small">{"Đang có, giữ" if has else "<b>Thiếu — bổ sung</b>"}</td></tr>')
    return '\n'.join(out) + '</tbody></table></div>', miss, len(top)


def _norm(h):
    h = unicodedata.normalize('NFC', h).lower()
    h = re.sub(r'^\s*\d+[\.\)]\s*', '', h)
    h = re.sub(r'[^\w\s]', ' ', h)
    return re.sub(r'\s+', ' ', h).strip()


# ── Mục 9 đến 14: phần định tính do agent viết, các hàm dưới chỉ dựng bảng ───

def meta_table(det):
    h = ['<div class="tblwrap"><table><thead><tr><th style="width:13%">Thành phần</th>'
         '<th style="width:29%">Hiện tại</th><th style="width:26%">Đề xuất</th>'
         '<th>Lý do, kèm số đo được</th></tr></thead><tbody>']
    for a, b, c, d in det['meta']:
        h.append(f'<tr><td><b>{esc(a)}</b></td><td class="small">{esc(b)}</td>'
                 f'<td class="small"><b>{esc(c)}</b></td><td class="small">{d}</td></tr>')
    return '\n'.join(h) + '</tbody></table></div>'


def outline_block(det):
    """Mục 10 — outline dạng thẻ, mỗi H2 một khối có viền màu theo nhãn, H3 xếp thành hàng
    kèm huy hiệu vị trí bên phải."""
    CLS = {'keep': 'ok', 'fix': 'wa', 'new': 'nw', 'gap': 'gp', 'brand': 'br'}
    out = ['<div class="outline">']
    for kind, title, desc, subs in det['outline']:
        lab, cls = LAB[kind]
        sub = ''
        if subs:
            rows = []
            for sk, sname, snote in subs:
                pos = str(snote or '')
                m = re.search(r'(ngo[àa]i top 100|\d+)\s*$', pos)
                badge = m.group(1) if m else pos
                badge = 'ngoài top 100' if 'ngo' in badge else (f'vị trí {badge}' if badge else '')
                rows.append(f'<div class="ol-sub"><span class="ol-kw">{esc(sname)}</span>'
                            f'<span class="ol-pos">{esc(badge)}</span></div>')
            sub = ('<div class="ol-subs"><div class="ol-subs-h">Từ khoá nhắm trong mục này</div>'
                   + ''.join(rows) + '</div>')
        out.append(f'<div class="ol-item ol-{CLS.get(kind, "ok")}">'
                   f'<div class="ol-head"><span class="tag {cls}">{lab}</span>'
                   f'<span class="ol-title">{esc(title)}</span></div>'
                   f'<div class="ol-meta">{desc}</div>{sub}</div>')
    out.append('</div>')
    return '\n'.join(out)


def faq_table(det):
    h = ['<div class="tblwrap"><table><thead><tr><th style="width:33%">Câu hỏi</th>'
         '<th style="width:37%">Hướng trả lời</th><th>Vì sao đưa vào, kèm số</th></tr></thead><tbody>']
    for q, a, s in det['faq']:
        h.append(f'<tr><td><b>{esc(q)}</b></td><td class="small">{esc(a)}</td>'
                 f'<td class="small">{esc(s)}</td></tr>')
    return '\n'.join(h) + '</tbody></table></div>'


def media_block(det):
    h = ['<div class="tblwrap"><table><thead><tr><th>Hạng mục</th><th class="num">Hiện tại</th>'
         '<th>Đối thủ tốt nhất trong cụm</th><th class="num">Mục tiêu</th></tr></thead><tbody>']
    for a, b, c, d in det['media']:
        h.append(f'<tr><td>{esc(a)}</td><td class="num">{esc(b)}</td>'
                 f'<td class="small">{esc(c)}</td><td class="num"><b>{esc(d)}</b></td></tr>')
    alt = '\n'.join(f'File : {esc(f)}\nAlt  : {esc(x)}' for f, x in det.get('alt', []))
    return ('\n'.join(h) + '</tbody></table></div>'
            + (f'<p style="color:var(--text-2);margin:14px 0 6px">Quy ước đặt tên file và alt text:</p>'
               f'<pre>{alt}</pre>' if alt else ''))


def schema_table(det):
    h = ['<div class="tblwrap"><table><thead><tr><th style="width:18%">Loại</th>'
         '<th style="width:24%">Trạng thái hiện tại</th><th>Việc cần làm</th></tr></thead><tbody>']
    for a, b, c in det['schema']:
        h.append(f'<tr><td><b>{esc(a)}</b></td><td class="small">{esc(b)}</td>'
                 f'<td class="small">{esc(c)}</td></tr>')
    return '\n'.join(h) + '</tbody></table></div>'


def checklist_table(det):
    h = ['<div class="tblwrap"><table><thead><tr><th class="num">Đợt</th><th style="width:38%">Việc</th>'
         '<th>Vì sao ưu tiên, kèm số đo được</th><th class="num">Công sức</th></tr></thead><tbody>']
    for a, b, c, d in det['checklist']:
        h.append(f'<tr><td class="num"><b>{esc(a)}</b></td><td>{b}</td>'
                 f'<td class="small">{c}</td><td class="num small">{esc(d)}</td></tr>')
    note = (f'<div class="note"><i class="fa-solid fa-circle-info"></i>{det["checklist_note"]}</div>'
            if det.get('checklist_note') else '')
    return '\n'.join(h) + '</tbody></table></div>' + note


# ── Mục 15: Search Console ───────────────────────────────────────────────────

def gsc_block(ctx, cluster_name, cid=None):
    _g = ctx.get('gsc') or {}
    d = (_g.get(cid) if cid else None) or _g.get(cluster_name)
    if not d:
        return _empty('gsc', '15. Đối chiếu Search Console', 'fa-chart-line',
                      'Chưa có dữ liệu Search Console cho cụm này. Chạy <span class="mono">'
                      'scripts/gsc.py</span> rồi <span class="mono">scripts/gsc_analyze.py</span>. '
                      'Nếu đã chạy thì kiểm tên cụm trong gsc_analysis.json có khớp clusters.json không '
                      '— đổi tên cụm sau khi chạy gsc_analyze thì phải chạy lại.')
    gap = (d['gsc_pos'] - d['serp_pos']) if (d.get('gsc_pos') and d.get('serp_pos')) else None
    note = ''
    if gap and gap > 3:
        note = ('<div class="note"><i class="fa-solid fa-circle-info"></i>'
                '<b>Hai con số này đo hai thứ khác nhau, không mâu thuẫn.</b> Vị trí trung vị <b>'
                + str(d['serp_pos']) + '</b> là thứ hạng thật đo tại một điểm — số dùng để theo dõi tiến độ. '
                'Con số <b>' + str(d['gsc_pos']) + '</b> của Search Console là vị trí trung bình có trọng số '
                'theo lượt hiển thị, gộp mọi thiết bị và tỉnh thành, nên luôn thấp hơn.</div>')
    return ('\n<div class="card" id="gsc">\n'
            '  <h2><i class="fa-solid fa-chart-line"></i> 15. Đối chiếu Search Console</h2>\n'
            '  <div class="metagrid" style="margin-bottom:16px">\n'
            f'    <div class="metabox"><div class="k">Hiển thị</div><div class="v">{num(d["imp"])}</div></div>\n'
            f'    <div class="metabox"><div class="k">Click</div><div class="v">{d["clicks"]}</div></div>\n'
            f'    <div class="metabox"><div class="k">Tỷ lệ nhấp</div><div class="v">{d["ctr"]}%</div></div>\n'
            f'    <div class="metabox"><div class="k">Từ khoá bị ăn thịt</div>'
            f'<div class="v">{d["can"]}/{d["nkw"]} theo dữ liệu thật</div></div>\n  </div>\n  ' + note + '\n</div>\n')


# ── Mục 16: đối chiếu nội dung với đối thủ ───────────────────────────────────

def content_block(ctx, rows, myurls, topn=3):
    P, JS, sh = ctx['pages'], ctx['js'], ctx['sh']
    cnt = collections.Counter()
    for r in rows:
        pk = ctx['perkw'].get(r['kw'])
        if not pk: continue
        for x in pk['riv']:
            if x['pos'] <= topn: cnt[x['url'].split('?')[0]] += 1
    top = [u for u, _ in cnt.most_common(8) if u in P and u not in JS][:3]
    myu = [u for u, _ in myurls[:2] if u in P]
    if not top or not myu:
        return _empty('doithucontent', '16. Đối chiếu nội dung với đối thủ', 'fa-file-circle-check',
                      ('Chưa có trang nào của mình trong cụm để đối chiếu. '
                       if not myu else 'Không crawl được trang đối thủ nào trong cụm. ')
                      + 'Xem mục 2 để biết đối thủ đang chiếm top là ai.')
    myh = [toks(h) for u in myu for h in P[u]['headings']]
    blocks = []
    for u in top:
        p = P[u]
        items = []
        for h in [h for h in p['headings'] if len(toks(h)) >= 2][:22]:
            if is_project(h):
                tag = '<span class="tag t-brand">tên dự án của họ</span>'
            else:
                has = max((sim(toks(h), m) for m in myh), default=0) >= 0.5
                tag = ('<span class="tag t-keep">mình đã có</span>' if has
                       else '<span class="tag t-gap">mình chưa có</span>')
            items.append(f'<tr><td>{esc(h[:110])}</td><td class="num">{tag}</td></tr>')
        blocks.append(f'<div class="h2block"><div class="title">{esc(u.split("/")[2])}'
                      f'<span class="rstat" style="font-weight:400"> — {p["words"]} từ · {p["imgs_all"]} ảnh · '
                      f'{p["h2"]} H2 / {p["h3"]} H3 · top {topn} ở {cnt[u]} từ khoá</span></div>'
                      f'<div class="meta mono">{esc(sh(u))}</div>'
                      f'<div class="tblwrap"><table><thead><tr><th>Mục nội dung của họ</th>'
                      f'<th class="num">Đối chiếu</th></tr></thead><tbody>{"".join(items)}</tbody></table></div></div>')
    groups = []
    for u in top:
        for h in P[u]['headings']:
            t = toks(h)
            if len(t) < 2 or is_project(h): continue
            placed = False
            for g in groups:
                if sim(g['t'], t) >= 0.55:
                    g['t'] |= t; g['ex'].append(h); g['dom'].add(u); placed = True; break
            if not placed: groups.append({'t': t, 'ex': [h], 'dom': {u}})
    miss = sorted([g for g in groups if len(g['dom']) >= 2
                   and max((sim(g['t'], m) for m in myh), default=0) < 0.5],
                  key=lambda g: -len(g['dom']))
    rows_ = ''.join(f'<tr><td>{esc(g["ex"][0][:100])}</td><td class="num">{len(g["dom"])}/{len(top)}</td>'
                    f'<td class="small">{esc(", ".join(sorted(d.split("/")[2] for d in g["dom"])))}</td></tr>'
                    for g in miss[:12])
    tail = (f'<div class="tblwrap"><table><thead><tr><th>Mục nội dung</th>'
            f'<th class="num">Số đối thủ có</th><th>Là những trang nào</th></tr></thead>'
            f'<tbody>{rows_}</tbody></table></div>') if rows_ else \
        ('<div class="note ok"><i class="fa-solid fa-circle-check"></i>Không có mục nội dung nào '
         'xuất hiện ở từ hai đối thủ trở lên mà trang mình còn thiếu.</div>')
    return ('\n<div class="card" id="doithucontent">\n'
            '  <h2><i class="fa-solid fa-file-circle-check"></i> 16. Đối chiếu nội dung với đối thủ</h2>\n'
            '  <p style="color:var(--text-2)">Trích toàn bộ mục nội dung thật của các trang đang đứng đầu cụm, '
            'đối chiếu với trang chủ lực của mình. Danh sách để người viết bài dùng trực tiếp.</p>\n'
            + '\n'.join(blocks) +
            '\n  <h3 style="margin-top:22px">Mục nhiều đối thủ cùng có mà mình chưa có</h3>\n  '
            + tail + '\n</div>\n')


# ── Mục 17: rà soát kỹ thuật cấp trang ───────────────────────────────────────

def tech_block(ctx, rows, myurls, topn=3):
    TECH, sh = ctx.get('tech') or {}, ctx['sh']
    myu = [u for u, _ in myurls[:3] if u in TECH]
    riv = set()
    for r in rows:
        pk = ctx['perkw'].get(r['kw'])
        if not pk: continue
        for x in pk['riv']:
            if x['pos'] <= topn and x['url'].split('?')[0] in TECH:
                riv.add(x['url'].split('?')[0])
    if not myu or not riv:
        return _empty('tech2', '17. Rà soát kỹ thuật cấp trang', 'fa-wrench',
                      ('Chưa có trang nào của mình trong cụm nên không có gì để rà. '
                       if not myu else 'Chưa có chỉ số kỹ thuật của đối thủ trong cụm — '
                                       'chạy scripts/tech.py để bổ sung.'))
    R = [TECH[u] for u in riv]
    med = lambda k: st.median([r[k] for r in R])
    specs = [('TTFB tải HTML (ms)', 'ttfb', 'low'), ('Ảnh thiếu alt', 'noalt', 'low'),
             ('Số H1', 'h1n', 'one'), ('Độ dài title', 'tlen', 'range'),
             ('Độ dài description', 'dlen', 'range'), ('Heading nhảy cấp', 'jumps', 'low'),
             ('Script ngoài', 'scripts', 'low'), ('File CSS ngoài', 'css', 'low'),
             ('Thẻ og:', 'og', 'high')]
    head = ''.join(f'<th class="num mecol">{esc(sh(u))[:34]}</th>' for u in myu)
    body = []
    for lab, k, rule in specs:
        cells = ''
        for u in myu:
            v = TECH[u][k]
            ok = (v <= med(k)) if rule == 'low' else (v >= med(k)) if rule == 'high' else \
                 (v == 1) if rule == 'one' else ((30 <= v <= 60) if k == 'tlen' else (120 <= v <= 160))
            cells += f'<td class="num {"top" if ok else "zero"}">{v}</td>'
        body.append(f'<tr><td>{esc(lab)}</td>{cells}<td class="num">{med(k):.0f}</td></tr>')
    fixes = []
    for u in myu:
        t, f = TECH[u], []
        if t['noalt'] > 0: f.append(f"{t['noalt']}/{t['imgs']} ảnh thiếu alt")
        if t['tlen'] > 60: f.append(f"title {t['tlen']} ký tự, sẽ bị cắt trên kết quả tìm kiếm")
        if t['h1n'] != 1: f.append(f"{t['h1n']} thẻ H1")
        if t['jumps'] > 0: f.append(f"{t['jumps']} chỗ nhảy cấp heading")
        if not t.get('canonical'): f.append('thiếu canonical')
        if t['dlen'] == 0: f.append('thiếu description')
        if f: fixes.append(f'<li><span class="mono">{esc(sh(u))}</span> — {esc("; ".join(f))}</li>')
    tail = ('<h3 style="margin-top:20px">Lỗi kỹ thuật cụ thể cần sửa</h3>'
            '<ul style="color:var(--text-2);padding-left:20px">' + ''.join(fixes) + '</ul>') if fixes else ''
    return ('\n<div class="card" id="tech2">\n'
            '  <h2><i class="fa-solid fa-wrench"></i> 17. Rà soát kỹ thuật cấp trang</h2>\n'
            '  <p style="color:var(--text-2)">Đo trực tiếp từ HTML thô. Cột cuối là trung vị các trang '
            'đang đứng đầu cụm. Ô nền xanh là đạt, ô nền đỏ là cần sửa.</p>\n'
            '  <div class="tblwrap"><table><thead><tr><th>Chỉ số</th>' + head +
            '<th class="num">Trung vị đối thủ</th></tr></thead><tbody>' + ''.join(body) +
            '</tbody></table></div>\n  ' + tail + '\n</div>\n')


# ── Mục 3: các trang của mình đang phục vụ cụm ───────────────────────────────

def mypages_block(ctx, rows, myurls):
    P, sh = ctx['pages'], ctx['sh']
    st_ = ctx.get('url_status') or {}
    ix = ctx.get('index_status') or {}
    if not myurls:
        return _empty('trangminh', '3. Các trang của mình đang phục vụ cụm', 'fa-file-lines',
                      '<b>Chưa có trang nào của mình xếp hạng cho cụm này.</b> Đây là cụm chưa có '
                      'trang đích — xem outline ở mục 10 để biết cần dựng trang thế nào, và mục 16 '
                      'để biết các trang đang top của cụm có những nội dung gì.')
    o = ['<div class="tblwrap"><table><thead><tr><th>URL</th><th class="num">Số kw<br>đang gánh</th>'
         '<th class="num">Vị trí<br>tốt nhất</th><th class="num">Số từ</th><th class="num">Ảnh</th>'
         '<th class="num">H2/H3</th><th class="num">Link<br>nội bộ</th><th class="num">Cập nhật</th>'
         '<th>Tình trạng</th></tr></thead><tbody>']
    for u, k in myurls[:10]:
        p = P.get(u)
        best = min([r['pos'] for r in rows if r['url'] and r['url'].split('?')[0] == u and r['pos']] or [0]) or '—'
        s = st_.get(u, {}) or {}
        i = ix.get(u, {}) or {}
        flag = []
        if s.get('status') and s['status'] != 200: flag.append(f"HTTP {s['status']}")
        if s.get('noindex'): flag.append('noindex')
        if i.get('verdict') and i['verdict'] != 'PASS': flag.append(i.get('coverageState', 'chưa index'))
        if i.get('googleCanonical') and i.get('userCanonical') \
                and i['googleCanonical'].rstrip('/') != i['userCanonical'].rstrip('/'):
            flag.append('Google gộp về ' + sh(i['googleCanonical']))
        tag = ('<span class="down">' + '; '.join(flag) + '</span>') if flag else '<span class="up">bình thường</span>'
        o.append(f'<tr><td class="mono small">{esc(sh(u))}</td><td class="num">{k}</td>'
                 f'<td class="num">{best}</td>'
                 + (f'<td class="num">{p["words"]}</td><td class="num">{p["imgs_all"]}</td>'
                    f'<td class="num">{p["h2"]}/{p["h3"]}</td><td class="num">{p["ilinks"]}</td>'
                    f'<td class="num small">{esc(p["datemod"][:10] or "—")}</td>' if p
                    else '<td class="num">—</td>' * 5)
                 + f'<td class="small">{tag}</td></tr>')
    o.append('</tbody></table></div>')
    note = ''
    if len(myurls) >= 2:
        note = ('<div class="note warn"><i class="fa-solid fa-triangle-exclamation"></i>'
                f'<b>{len(myurls)} URL cùng phục vụ cụm này.</b> Chỉ một trang được làm trang đích. '
                'Các trang còn lại phải đổi vai hoặc gộp — xem mục ăn thịt từ khoá.</div>')
    return ('\n<div class="card" id="trangminh">\n'
            '  <h2><i class="fa-solid fa-file-lines"></i> 3. Các trang của mình đang phục vụ cụm</h2>\n  '
            + '\n'.join(o) + '\n  ' + note + '\n</div>\n')


# ── Mục 6: ma trận mật độ cụm từ ─────────────────────────────────────────────

def density_block(ctx, rows, myurls, topn=4, maxterms=12):
    """Ma trận: cụm từ × trang. Cụm từ lấy từ chính từ khoá của cụm, ưu tiên kw nhiều hiển thị
    và các biến thể đảo trật tự. Trang gồm 2 trang của mình và top đối thủ."""
    P, sh, JS = ctx['pages'], ctx['sh'], ctx['js']
    cnt = collections.Counter()
    for r in rows:
        pk = ctx['perkw'].get(r['kw'])
        if not pk: continue
        for x in pk['riv']:
            if x['pos'] <= 10: cnt[x['url'].split('?')[0]] += 1
    riv = [u for u, _ in cnt.most_common(10) if u in P and u not in JS][:topn]
    mine = [u for u, _ in myurls[:2] if u in P]
    cols = [(sh(u), P[u], True) for u in mine] + [(u.split('/')[2].replace('www.', ''), P[u], False) for u in riv]
    if not cols:
        return _card('matdo', '6. Ma trận mật độ cụm từ', 'fa-table-cells',
                     '<div class="note"><i class="fa-solid fa-circle-info"></i>'
                     'Không dựng được ma trận: không có trang nào của mình trong cụm và không crawl được '
                     'trang đối thủ nào. Kiểm tra lại bước crawl.</div>'
                     + kwdens_block(ctx, rows))

    # Chọn cụm từ để đo: n-gram thành phần xuất hiện ở nhiều từ khoá của cụm, không lấy
    # nguyên văn từ khoá đuôi dài — cụm dài gần như luôn bằng 0 nên bảng vô dụng.
    kws = [r['kw'] for r in rows]
    gram = collections.Counter()
    for k in kws:
        w = unicodedata.normalize('NFC', k).lower().split()
        seen_ = set()
        # tiếng Việt nhiều âm tiết: "thiết kế nội thất ngân hàng" đã 6 tiếng, cắt ở 5 là mất nghĩa
        for n in (8, 7, 6, 5, 4, 3, 2):
            for i in range(len(w) - n + 1):
                g = ' '.join(w[i:i + n])
                if g not in seen_:
                    seen_.add(g); gram[g] += 1
    # Chỉ giữ n-gram tối đại: nếu có cụm dài hơn chứa nó mà cùng số từ khoá thì cụm ngắn
    # là lát cắt vô nghĩa ("thiết kế nội thất ngân" so với "thiết kế nội thất ngân hàng").
    _min = max(2, len(kws) * 0.25)
    _cand = {g: c for g, c in gram.items() if c >= _min}
    _byc = collections.defaultdict(list)
    for g, c in _cand.items(): _byc[c].append(g)
    gram = {g: c for c, gs in _byc.items() for g in gs
            if not any(g != p and g in p for p in gs)}
    picked = []
    for g, c in sorted(gram.items(), key=lambda x: (-x[1], -len(x[0].split()))):
        if c < _min: continue
        # Chỉ loại khi cụm này chồng với cụm đã chọn VÀ cùng số từ khoá — khi đó nó không
        # mang thêm thông tin. Cụm dài phổ biến ít hơn vẫn giữ, vì đó mới là cụm có nghĩa.
        _gw = g.split()
        _skip = False
        for p, pc in picked:
            if pc != c: continue
            if g in p or p in g:
                _skip = True; break
            _pw = p.split()
            # cùng số từ khoá và chồng nhau phần lớn: chỉ là hai lát cắt của một cụm
            if len(set(_gw) & set(_pw)) >= 0.7 * min(len(_gw), len(_pw)):
                _skip = True; break
        if _skip: continue
        picked.append((g, c))
        if len(picked) >= maxterms - 3: break
    # thêm vài từ khoá ngắn nhất của cụm, thường là truy vấn gốc
    for k in sorted(kws, key=len)[:3]:
        t = nrm_term(k)
        if not any(t == p for p, _ in picked): picked.append((t, None))
    terms = [(g, c) for g, c in picked][:maxterms]
    if not terms:
        return _card('matdo', '6. Ma trận mật độ cụm từ', 'fa-table-cells',
                     '<div class="note"><i class="fa-solid fa-circle-info"></i>'
                     f'Cụm chỉ có {len(rows)} từ khoá nên không rút được cụm từ chung cho ma trận. '
                     'Bảng dưới đo mật độ theo từng từ khoá, chi tiết hơn.</div>'
                     + kwdens_block(ctx, rows))

    def dens(p, t):
        return len(re.findall(re.escape(unicodedata.normalize('NFC', t).lower()), p['text']))

    head = ''.join(f'<th class="num{" mecol" if me else ""}">{esc(c)[:26]}</th>' for c, _, me in cols)
    body = []
    for t, nkw in terms:
        vals = [dens(p, t) for _, p, _ in cols]
        mx = max(vals) if vals else 0
        cells = ''
        for v in vals:
            cls = 'num top' if v == mx and mx > 0 else ('num zero' if v == 0 else 'num')
            cells += f'<td class="{cls}">{v}</td>'
        body.append(f'<tr><td>{esc(t)}</td><td class="num">{nkw if nkw else "—"}</td>{cells}</tr>')
    for lab, k in (('Số từ nội dung chính', 'words'), ('Số ảnh', 'imgs_all'),
                   ('H2 / H3', None), ('Link nội bộ', 'ilinks'), ('HTML (KB)', 'kb')):
        if k is None:
            cells = ''.join(f'<td class="num">{p["h2"]}/{p["h3"]}</td>' for _, p, _ in cols)
        else:
            cells = ''.join(f'<td class="num">{p[k]}</td>' for _, p, _ in cols)
        body.append(f'<tr class="sumrow"><td>{lab}</td><td class="num">—</td>{cells}</tr>')

    zero = [t for t, _ in terms if all(dens(p, t) == 0 for _, p, me in cols if me)]
    _mine_cols = [c for c in cols if c[2]]
    lose = [t for t, _ in terms
            if mine and max((dens(p, t) for _, p, me in cols if me), default=0)
            < max((dens(p, t) for _, p, me in cols if not me), default=0)]
    notes = []
    if zero:
        notes.append('<div class="note gap"><i class="fa-solid fa-circle-exclamation"></i>'
                     f'<b>{len(zero)} cụm từ khoá không xuất hiện lần nào</b> trên trang của mình: '
                     + ', '.join(f'"{esc(t)}"' for t in zero[:6])
                     + '. Đây là nguyên nhân trực tiếp nhất, sửa được ngay bằng cách đưa cụm vào '
                       'heading và đoạn mở đầu.</div>')
    if lose:
        notes.append('<div class="note warn"><i class="fa-solid fa-triangle-exclamation"></i>'
                     f'<b>{len(lose)} cụm mình nhắc ít hơn đối thủ đang đứng trên</b>: '
                     + ', '.join(f'"{esc(t)}"' for t in lose[:6]) + '.</div>')
    if not zero and not lose:
        notes.append('<div class="note ok"><i class="fa-solid fa-circle-check"></i>'
                     'Không cụm nào bị bỏ trống hay thua đối thủ về mật độ. Nguyên nhân chưa lên top '
                     'nằm ngoài mật độ từ khoá — đọc tiếp mục ăn thịt từ khoá và rà soát kỹ thuật.</div>')
    return ('\n<div class="card" id="matdo">\n'
            '  <h2><i class="fa-solid fa-table-cells"></i> 6. Ma trận mật độ cụm từ</h2>\n'
            '  <p style="color:var(--text-2)">Số lần cụm từ xuất hiện trong nội dung chính, đo cùng một '
            'cách cho mọi trang. Ô nền xanh là giá trị cao nhất hàng, ô nền đỏ là không xuất hiện lần nào. '
            'Cột nền xanh nhạt là trang của mình.</p>\n'
            '  <div class="tblwrap"><table><thead><tr><th style="width:26%">Cụm từ</th>'
            f'<th class="num">Có trong<br>bao nhiêu kw<br><span class="small">trên {len(rows)} kw</span></th>'
            + head + '</tr></thead><tbody>'
            + ''.join(body) + '</tbody></table></div>\n  ' + '\n  '.join(notes)
            + '\n  ' + kwdens_block(ctx, rows) + '\n</div>\n')


def kwdens_rows(ctx, rows, mark_cut=3):
    """Mật độ của từng từ khoá: trang mình so với các trang đang đứng top của chính từ khoá đó.

    Trả (danh sách dòng, ngưỡng bao trùm). Ngưỡng bao trùm lấy MAX trên toàn bộ từ khoá của
    trung vị nhóm top — trung vị bên trong một từ khoá để một trang lệch không kéo lệch cả
    bảng, rồi max giữa các từ khoá vì trang phải phủ được từ khoá khó nhất trong cụm.
    """
    out = []
    for r in sorted(rows, key=lambda x: (x['pos'] or 999, x['kw'])):
        pk = ctx['perkw'].get(r['kw'])
        if not pk:
            continue
        riv = [x for x in pk['riv'] if x['pos'] <= mark_cut]
        if not riv:
            continue
        med = st.median([x['dens'] for x in riv])
        hi = max(riv, key=lambda x: x['dens'])
        medw = st.median([x['words'] for x in riv])
        my = pk.get('my')
        out.append(dict(kw=r['kw'], pos=r['pos'], n=len(riv),
                        my=(my['dens'] if my else None), med=med,
                        hi=hi['dens'], hidom=hi['dom'],
                        myw=(my['words'] if my else None), medw=medw,
                        # cả nhóm top không nhắc nguyên văn lần nào: truy vấn này Google không
                        # đòi khớp nguyên văn, không được tính vào ngưỡng bao trùm
                        dead=(med == 0 and hi['dens'] == 0)))
    if not out:
        return [], None
    live = [x for x in out if not x['dead']]
    topw = max(out, key=lambda x: x['medw'])
    top = max(live, key=lambda x: x['med']) if live else None
    return out, dict(dens=(top['med'] if top else None), dens_kw=(top['kw'] if top else None),
                     hi=max(x['hi'] for x in out), words=topw['medw'], words_kw=topw['kw'],
                     n=len(out), nlive=len(live))


def kwdens_block(ctx, rows, mark_cut=3):
    """Bảng mật độ theo từng từ khoá, dòng cuối là ngưỡng bao trùm cả cụm."""
    data, cover = kwdens_rows(ctx, rows, mark_cut)
    if not data:
        return ('<h3 style="margin-top:24px">Mật độ theo từng từ khoá</h3>'
                '<div class="note"><i class="fa-solid fa-circle-info"></i>'
                f'Chưa crawl được trang nào đang đứng top {mark_cut} của các từ khoá trong cụm nên không '
                'đo được mật độ theo từng từ khoá. Chạy <span class="mono">scripts/precheck.py --fix</span>.'
                '</div>')
    o = ['<div class="tblwrap"><table><thead><tr><th style="width:28%">Từ khoá</th>'
         '<th class="num">Vị trí</th><th class="num mecol">Mật độ<br>trang mình</th>'
         f'<th class="num">Trung vị<br>top {mark_cut}</th><th class="num">Cao nhất top {mark_cut}</th>'
         '<th class="num">Còn thiếu</th><th class="num">Số từ mình<br>/ trung vị top</th>'
         '</tr></thead><tbody>']
    nlow = 0
    for d in data:
        if d['dead']:
            myc = (f'<td class="num">{d["my"]}</td>' if d['my'] is not None
                   else '<td class="num small">chưa có trang</td>')
            gap = ('<td class="small">không trang top nào nhắc nguyên văn</td>')
        elif d['my'] is None:
            myc, gap = ('<td class="num zero">chưa có trang</td>',
                        '<td class="num zero">—</td>')
        else:
            short = max(0, d['med'] - d['my'])
            if short > 0:
                nlow += 1
            myc = f'<td class="num {"zero" if short else "top"}">{d["my"]}</td>'
            gap = (f'<td class="num zero"><b>thiếu {short:.0f}</b></td>' if short
                   else '<td class="num top">đạt</td>')
        w = (f'{d["myw"]} / {d["medw"]:.0f}' if d['myw'] else f'— / {d["medw"]:.0f}')
        cls = 'r3' if d['pos'] and d['pos'] <= 3 else 'r10' if d['pos'] and d['pos'] <= 10 else \
              'r20' if d['pos'] and d['pos'] <= 20 else 'r50' if d['pos'] and d['pos'] <= 50 else 'rx'
        hic = (f'{d["hi"]} · <span class="small">{esc(d["hidom"])}</span>' if d['hi'] else '0')
        o.append(f'<tr class="{cls}"><td>{esc(d["kw"])}</td><td class="num">{d["pos"] or "—"}</td>'
                 + myc + f'<td class="num">{d["med"]:.0f}</td><td class="num">{hic}</td>'
                 + gap + f'<td class="num small">{w}</td></tr>')
    dens_cell = (f'<b>{cover["dens"]:.0f}</b>' if cover['dens'] is not None else '—')
    o.append('<tr class="sumrow"><td><b>NGƯỠNG BAO TRÙM CẢ CỤM</b></td><td class="num">—</td>'
             f'<td class="num">—</td><td class="num">{dens_cell}</td>'
             f'<td class="num"><b>{cover["hi"]}</b></td><td class="num">—</td>'
             f'<td class="num"><b>{cover["words"]:.0f}</b></td></tr>')
    o.append('</tbody></table></div>')
    return ('<h3 style="margin-top:24px">Mật độ theo từng từ khoá</h3>'
            f'<p style="color:var(--text-2)">Mỗi dòng so trang của mình với các trang đang thật sự đứng '
            f'top {mark_cut} của <b>chính từ khoá đó</b>, không phải trung bình cả cụm. Mật độ là số lần '
            'cụm từ khoá xuất hiện trong nội dung chính, đo cùng một cách cho mọi trang.</p>'
            + ''.join(o)
            + '<div class="note gap"><i class="fa-solid fa-bullseye"></i>'
            + (f'<b>Để một URL phủ được cả {cover["n"]} từ khoá của cụm</b> thì phải đạt mức của từ khoá '
               f'khó nhất, không phải mức trung bình: mật độ <b>{cover["dens"]:.0f} lần</b> '
               f'(từ khoá đẩy ngưỡng: "{esc(cover["dens_kw"])}") và độ dài <b>{cover["words"]:.0f} từ</b> '
               f'(từ khoá đẩy ngưỡng: "{esc(cover["words_kw"])}"). Ngưỡng lấy max trên các từ khoá của '
               f'trung vị nhóm top {mark_cut} từng từ khoá. Trang cao nhất đo được nhắc '
               f'<b>{cover["hi"]} lần</b> — đó là trần thực tế đang có người làm được.'
               if cover['dens'] is not None else
               f'<b>Không từ khoá nào của cụm được nhóm top {mark_cut} nhắc nguyên văn.</b> Google không '
               'đòi khớp nguyên văn cho các truy vấn này, nên không có ngưỡng mật độ để đặt ra. Ngưỡng '
               f'còn lại là độ dài <b>{cover["words"]:.0f} từ</b> (từ khoá đẩy ngưỡng: '
               f'"{esc(cover["words_kw"])}"). Cụm từ cần nhắc xem ở ma trận phía trên.')
            + (f' Hiện <b>{nlow}/{cover["nlive"]} từ khoá đo được</b> có mật độ dưới trung vị nhóm '
               f'top {mark_cut}.' if nlow else '')
            + (f' {len(data) - cover["nlive"]}/{cover["n"]} từ khoá không trang top nào nhắc nguyên văn, '
               'đã loại khỏi phép tính ngưỡng.' if cover['nlive'] < cover['n'] else '') + '</div>')


def clustergap_block(ctx, rows, goals, cut):
    """Khoảng cách của riêng nhóm tới mục tiêu, kèm danh sách từ khoá ứng viên rẻ nhất."""
    n = len(rows)
    if not goals:
        return ''
    band = lambda lo, hi: [r for r in rows if r['pos'] and lo <= r['pos'] <= hi]
    tiers = [('4–5', band(4, 5)), ('6–10', band(6, 10)), ('11–20', band(11, 20)),
             ('21–50', band(21, 50)),
             ('>50', [r for r in rows if not r['pos'] or r['pos'] > 50])]
    lines = []
    for m in sorted(goals, key=lambda x: cut[x]):
        c = sum(1 for r in rows if r['pos'] and r['pos'] <= cut[m])
        goal = -(-n * goals[m] // 100)
        need = max(0, goal - c)
        cls, txt = ('keep', f'<b>Đã đạt</b> — {c}/{n} = {c * 100 // max(n, 1)}%, mục tiêu {goals[m]}%.') \
            if not need else \
            ('must', f'Đang {c}/{n} = {c * 100 // max(n, 1)}%, mục tiêu {goals[m]}% tức {goal} từ khoá. '
                     f'<b>Cần thêm {need} từ khoá.</b>')
        lines.append(f'<div class="rolebar {cls}"><div class="rk">Mốc top {cut[m]}</div>'
                     f'<div class="rv">{txt}</div></div>')
    cand = ''
    for lab, lst in tiers:
        if not lst or lab == '>50':
            continue
        kws = ' · '.join(f'{esc(r["kw"])} ({r["pos"]})' for r in sorted(lst, key=lambda x: x['pos'])[:8])
        cand += (f'<tr><td>{lab}</td><td class="num">{len(lst)}</td>'
                 f'<td class="small">{kws}{" …" if len(lst) > 8 else ""}</td></tr>')
    out50 = [r for r in rows if not r['pos'] or r['pos'] > 50]
    if out50:
        cand += (f'<tr><td>&gt;50</td><td class="num">{len(out50)}</td>'
                 '<td class="small">Xa mốc nhất, để sau cùng.</td></tr>')
    return ('\n<div class="card" id="gapnhom">\n'
            '  <h2><i class="fa-solid fa-bullseye-arrow"></i> Khoảng cách của nhóm tới mục tiêu</h2>\n  '
            + ''.join(lines) +
            '\n  <h3 style="margin-top:18px">Từ khoá ứng viên, xếp theo mức rẻ</h3>\n'
            '  <p style="color:var(--text-2)">Vị trí càng gần mốc thì đẩy vào càng rẻ. Đánh theo thứ tự '
            'từ trên xuống, không rải đều.</p>\n'
            '  <div class="tblwrap"><table><thead><tr><th style="width:12%">Tầng vị trí</th>'
            '<th class="num">Số kw</th><th>Từ khoá, kèm vị trí hiện tại</th></tr></thead><tbody>'
            + cand + '</tbody></table></div>\n</div>\n')


def nrm_term(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', s)).strip().lower()


def gap_missing(ctx, rows, myurls, topn=14):
    """Trả về [(tên mục, số trang top có, tổng trang xét)] cho các mục mình còn thiếu."""
    P, JS = ctx['pages'], ctx['js']
    urls = collections.Counter()
    for r in rows:
        pk = ctx['perkw'].get(r['kw'])
        if not pk: continue
        for x in pk['riv']: urls[x['url'].split('?')[0]] += 1
    top = [u for u, _ in urls.most_common(topn) if u in P and u not in JS]
    cnt, mine = collections.Counter(), set()
    for u in top:
        seen = set()
        for hh in P[u]['headings']:
            n = _norm(hh)
            for pat, lab in KEYS:
                if re.search(pat, n) and lab not in seen:
                    seen.add(lab); cnt[lab] += 1
    for u, _ in myurls[:2]:
        if u in P:
            for hh in P[u]['headings']:
                n = _norm(hh)
                for pat, lab in KEYS:
                    if re.search(pat, n): mine.add(lab)
    return [(lab, k, len(top)) for lab, k in cnt.most_common()
            if k >= max(2, len(top) // 3) and lab not in mine]


# ── Mục 4, 5, 7: mạnh — yếu — việc cần làm, sinh tự động từ số đã đo ─────────

def _bench(ctx, rows, myurls, mark='top10'):
    """Trả (chỉ số của mình, ngưỡng trung vị nhóm top, số trang lấy mẫu)."""
    lo, hi = {'top10': (1, 10), 'top5': (1, 5), 'top3': (1, 3)}[mark]
    E = {}
    for r in rows:
        pk = ctx['perkw'].get(r['kw'])
        if not pk:
            continue
        for x in pk['riv']:
            if lo <= x['pos'] <= hi:
                E[x['url']] = x
    E = list(E.values())
    m = ctx['pages'].get(myurls[0][0]) if myurls else None
    if len(E) < 5 or not m:
        return None, None, len(E)
    med = lambda k: st.median([x[k] for x in E])
    mine = dict(words=m['words'], imgs=m['imgs_all'], ilinks=m['ilinks'], h2=m['h2'],
                h3=m['h3'], faq=int(bool(m['faq_schema'])), schema=len(m['schemas']))
    tgt = dict(words=med('words'), imgs=med('imgs'), ilinks=med('ilinks'), h2=med('h2'),
               h3=med('h3'), faq=st.median([int(bool(x.get('faq'))) for x in E]),
               schema=None)
    return mine, tgt, len(E)


_LABELS = [('words', 'Số từ nội dung chính'), ('imgs', 'Số ảnh'), ('ilinks', 'Link nội bộ'),
           ('h2', 'Số thẻ H2'), ('h3', 'Số thẻ H3')]


def strength_block(ctx, rows, myurls):
    mine, tgt, n = _bench(ctx, rows, myurls)
    if not mine:
        return _empty('manh', '4. Điểm mạnh đang có', 'fa-thumbs-up',
                      'Chưa có trang nào của mình xếp hạng cho cụm này, hoặc nhóm top chưa đủ 5 trang '
                      'đo được để lập ngưỡng so sánh. Không có điểm mạnh nào để giữ.')
    good = [(lab, mine[k], tgt[k]) for k, lab in _LABELS if tgt[k] and mine[k] >= tgt[k]]
    t3 = sum(1 for r in rows if r['pos'] and r['pos'] <= 3)
    t10 = sum(1 for r in rows if r['pos'] and r['pos'] <= 10)
    o = []
    if t10:
        o.append(f'<li>Đang giữ <b>{t10}/{len(rows)}</b> từ khoá trong top 10'
                 + (f', trong đó <b>{t3}</b> ở top 3' if t3 else '') + '.</li>')
    for lab, v, t in good:
        o.append(f'<li><b>{lab}</b>: {v:.0f} — đã vượt ngưỡng {t:.0f} của nhóm top 10 '
                 f'(trung vị {n} trang).</li>')
    if not o:
        return _empty('manh', '4. Điểm mạnh đang có', 'fa-thumbs-up',
                      'Không chỉ số nào của trang chủ lực đạt ngưỡng nhóm top 10. '
                      'Xem mục 5 để biết thiếu ở đâu.')
    return ('\n<div class="card" id="manh"><h2><i class="fa-solid fa-thumbs-up"></i> '
            '4. Điểm mạnh đang có</h2><ul>' + ''.join(o) + '</ul>'
            '<p style="color:var(--text-3);font-size:13px">Giữ nguyên các mục này khi sửa trang. '
            'Mọi thay đổi lên phần đang thắng đều là rủi ro thuần.</p></div>\n')


_TECHSPECS = [('On-page', 'Độ dài title', 'tlen', 'near'),
              ('On-page', 'Độ dài description', 'dlen', 'near'),
              ('On-page', 'Số thẻ H1', 'h1n', 'one'),
              ('On-page', 'Ảnh thiếu alt', 'noalt', 'low'),
              ('On-page', 'Chỗ nhảy cấp heading', 'jumps', 'low'),
              ('Kỹ thuật', 'TTFB tải HTML (ms)', 'ttfb', 'low'),
              ('Kỹ thuật', 'Script ngoài', 'scripts', 'low'),
              ('Kỹ thuật', 'File CSS ngoài', 'css', 'low'),
              ('Kỹ thuật', 'Dung lượng HTML (KB)', 'kb', 'low')]


def _tech_gaps(ctx, rows, myurls, topn=3):
    """Điểm yếu lớp on-page và kỹ thuật, đo từ tech.json của trang mình so với trang top."""
    TECH = ctx.get('tech') or {}
    myu = [u for u, _ in myurls[:1] if u in TECH]
    riv = set()
    for r in rows:
        pk = ctx['perkw'].get(r['kw'])
        if not pk: continue
        for x in pk['riv']:
            u = x['url'].split('?')[0]
            if x['pos'] <= topn and u in TECH:
                riv.add(u)
    if not myu or len(riv) < 2:
        return []
    t, R = TECH[myu[0]], [TECH[u] for u in riv]
    out = []
    for layer, lab, k, rule in _TECHSPECS:
        if k not in t or t[k] is None:
            continue
        vals = [x[k] for x in R if x.get(k) is not None]
        if not vals:
            continue
        med = st.median(vals)
        v = t[k]
        if rule == 'low' and v > med:
            out.append(((v - med) / max(med, 1), layer, lab, v, med, f'cao hơn trung vị {v - med:.0f}'))
        elif rule == 'one' and v != 1:
            out.append((1.0, layer, lab, v, 1, 'phải đúng 1 thẻ H1'))
        elif rule == 'near' and abs(v - med) / max(med, 1) >= 0.25:
            out.append((abs(v - med) / max(med, 1), layer, lab, v, med,
                        'ngắn hơn' if v < med else 'dài hơn'))
    return out


def weakness_block(ctx, rows, myurls, topn=3):
    mine, tgt, n = _bench(ctx, rows, myurls)
    tech = _tech_gaps(ctx, rows, myurls, topn)
    if not mine and not tech:
        return _empty('yeu', '5. Điểm yếu xếp theo mức tác động', 'fa-triangle-exclamation',
                      'Chưa có trang nào của mình xếp hạng cho cụm này nên không đo được khoảng cách '
                      'ở cấp trang. Việc cần làm là dựng trang đích — xem mục 10.')
    bad = []
    if mine:
        for k, lab in _LABELS:
            if tgt[k] and mine[k] < tgt[k]:
                gap = tgt[k] - mine[k]
                bad.append((gap / max(tgt[k], 1), 'Nội dung', lab, mine[k], tgt[k],
                            f'thiếu {gap:.0f}'))
    bad += tech
    bad.sort(key=lambda x: -x[0])
    if not bad:
        return _empty('yeu', '5. Điểm yếu xếp theo mức tác động', 'fa-triangle-exclamation',
                      'Trang chủ lực đã đạt hoặc vượt mọi ngưỡng đo được ở cả ba lớp nội dung, on-page '
                      'và kỹ thuật. Khoảng cách còn lại không nằm ở on-page — xem mục 15 và 17.')
    LCLS = {'Nội dung': 't-new', 'On-page': 't-fix', 'Kỹ thuật': 't-gap'}
    o = ['<div class="tblwrap"><table><thead><tr><th>Lớp</th><th>Điểm yếu</th>'
         '<th class="num">Của mình</th>'
         f'<th class="num">Mức của nhóm top<br><span class="small">trung vị các trang đang đứng đầu</span></th>'
         '<th class="num">Chênh</th><th>Mức tác động</th></tr></thead><tbody>']
    for ratio, layer, lab, v, t, why in bad:
        lvl = 'Cao' if ratio >= 0.4 else ('Trung bình' if ratio >= 0.15 else 'Thấp')
        cls = 'zero' if ratio >= 0.4 else ''
        o.append(f'<tr><td><span class="tag {LCLS.get(layer, "t-keep")}">{layer}</span></td>'
                 f'<td>{esc(lab)}</td><td class="num {cls}">{v:.0f}</td>'
                 f'<td class="num">{t:.0f}</td><td class="num">{esc(why)}</td>'
                 f'<td>{lvl} — lệch {ratio*100:.0f}% so với mức nhóm top</td></tr>')
    o.append('</tbody></table></div>')
    miss = ''
    if not tech:
        miss = ('<div class="note"><i class="fa-solid fa-circle-info"></i>'
                'Chưa đủ dữ liệu kỹ thuật để so lớp on-page và kỹ thuật: cần chỉ số của trang mình và '
                'ít nhất 2 trang đối thủ. Chạy <span class="mono">scripts/tech.py</span>.</div>')
    return ('\n<div class="card" id="yeu"><h2><i class="fa-solid fa-triangle-exclamation"></i> '
            '5. Điểm yếu xếp theo mức tác động</h2>'
            '<p style="color:var(--text-2)">Gộp cả ba lớp vào một bảng để thấy cái nào nặng nhất: '
            'nội dung, on-page, kỹ thuật. Chi tiết từng lớp ở mục 6, 9 và 17.</p>'
            + ''.join(o) + miss
            + '<p style="color:var(--text-3);font-size:13px">Xếp theo tỷ lệ lệch so với mức nhóm top, '
              'không theo số tuyệt đối — thiếu 20 ảnh trên nền 30 nặng hơn thiếu 200 từ trên nền 2.000.</p></div>\n')


def todo_block(ctx, rows, myurls, det, tgt_url, verd, goals=None):
    n = len(rows)
    o = []
    lab = {'GIỮ': 'Giữ URL chốt và gộp phần còn lại về đó',
           'TỐI ƯU': 'Tối ưu trang đã có, không viết trang mới',
           'KHÔI PHỤC': 'Khôi phục URL đang 404 hoặc 301 sang trang thay thế',
           'TẠO MỚI': 'Dựng trang mới cho cụm'}.get(verd, verd)
    o.append(f'<li><b>{esc(lab)}</b> — <span class="mono small">{esc(ctx["sh"](tgt_url))}</span></li>')
    for m, cut in (('top5', 5), ('top10', 10)):
        if not goals or m not in goals:
            continue
        cur = sum(1 for r in rows if r['pos'] and r['pos'] <= cut)
        need = max(0, -(-n * goals[m] // 100) - cur)
        o.append(f'<li>Mốc top {cut}: đang {cur}/{n}, '
                 + (f'<b>cần thêm {need} từ khoá</b>.' if need else '<b>đã đạt</b>, chỉ cần giữ.') + '</li>')
    for it in (det.get('checklist') or [])[:6]:
        if len(it) >= 2:
            o.append(f'<li>Đợt {esc(it[0])}: {esc(it[1])}</li>')
    return ('\n<div class="card" id="tomtat"><h2><i class="fa-solid fa-list-ol"></i> '
            '7. Tóm tắt việc cần làm</h2><ol>' + ''.join(o) + '</ol>'
            '<p style="color:var(--text-3);font-size:13px">Chi tiết từng việc ở mục 9 đến 14. '
            'Thứ tự trong danh sách này là thứ tự thực hiện.</p></div>\n')

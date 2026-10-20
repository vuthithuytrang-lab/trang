# -*- coding: utf-8 -*-
"""Sinh tự động sáu mục định tính từ dữ liệu đã đo: meta, outline, FAQ, ảnh, schema, checklist.

Lý do tồn tại: một dự án có thể có hàng chục cụm. Bắt agent viết tay sáu mục cho từng cụm
là bất khả thi, và thực tế dẫn tới báo cáo bị cắt mất mục. Ở đây mọi mục đều có bản tự động
làm mức sàn, dựng từ số đo được — không bịa. content.py chỉ để ghi đè hoặc bổ sung phần
cần phán đoán của người.

Mọi con số trong bản tự động đều truy được về pages.json, kw.json, tech.json hoặc gsc.
"""
import collections, re, statistics as st, unicodedata


def _n(s): return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', str(s))).strip().lower()


def _dens(p, t): return len(re.findall(re.escape(_n(t)), p['text']))


def _terms(rows, maxterms=10):
    """Cụm từ thành phần của cụm — cùng thuật toán với ma trận mật độ ở blocks.py."""
    kws = [r['kw'] for r in rows]
    gram = collections.Counter()
    for k in kws:
        w = _n(k).split()
        seen = set()
        for n in (8, 7, 6, 5, 4, 3, 2):
            for i in range(len(w) - n + 1):
                g = ' '.join(w[i:i + n])
                if g not in seen:
                    seen.add(g); gram[g] += 1
    lo = max(2, len(kws) * 0.25)
    cand = {g: c for g, c in gram.items() if c >= lo}
    byc = collections.defaultdict(list)
    for g, c in cand.items(): byc[c].append(g)
    gram = {g: c for c, gs in byc.items() for g in gs if not any(g != p and g in p for p in gs)}
    out = []
    for g, c in sorted(gram.items(), key=lambda x: (-x[1], -len(x[0].split()))):
        gw = set(g.split())
        if any(pc == c and (g in p or p in g or
                            len(gw & set(p.split())) >= 0.7 * min(len(gw), len(p.split())))
               for p, pc in out):
            continue
        out.append((g, c))
        if len(out) >= maxterms: break
    return out


def _rivals(ctx, rows, topn=10, take=6):
    """Trang đối thủ đang top của cụm. Nguồn chính là perkw; perkw chỉ có dữ liệu cho từ khoá
    mà mình cũng xếp hạng, nên cụm chưa có trang đích sẽ rỗng — khi đó đọc thẳng SERP trong kw.json."""
    P, JS = ctx['pages'], ctx['js']
    me = ctx.get('me') or ''
    cnt = collections.Counter()
    for r in rows:
        pk = ctx['perkw'].get(r['kw'])
        if not pk: continue
        for x in pk['riv']:
            if x['pos'] <= topn: cnt[x['url'].split('?')[0]] += 1
    out = [P[u] for u, _ in cnt.most_common(20) if u in P and u not in JS][:take]
    if out:
        return out
    cnt = collections.Counter()
    for r in rows:
        for s in (r.get('top10') or r.get('serp') or []):
            if isinstance(s, (list, tuple)) and len(s) >= 3:
                pos, dom, url = s[0], s[1], s[2]
            elif isinstance(s, dict):
                pos, dom, url = s.get('pos'), s.get('domain', ''), s.get('url', '')
            else:
                continue
            if not url or (pos or 999) > topn: continue
            if me and (me in str(dom) or me in url): continue
            cnt[url.split('?')[0]] += 1
    return [P[u] for u, _ in cnt.most_common(30) if u in P and u not in JS][:take]


def auto_meta(ctx, rows, myurls):
    P, sh = ctx['pages'], ctx['sh']
    mine = [P[u] for u, _ in myurls[:1] if u in P]
    if not mine: return []
    m = mine[0]
    terms = _terms(rows)
    riv = _rivals(ctx, rows)
    out = []

    t = m.get('title') or ''
    miss = [g for g, _ in terms[:4] if _n(g) not in _n(t)]
    tl = len(t)
    why = []
    if miss: why.append('thiếu cụm ' + ', '.join(f'"{x}"' for x in miss[:3]))
    if tl > 60: why.append(f'dài {tl} ký tự nên bị cắt trên kết quả tìm kiếm')
    if tl < 30: why.append(f'chỉ {tl} ký tự, còn chỗ để thêm cụm')
    rt = [r['title'] for r in riv[:2] if r.get('title')]
    if rt: why.append('đối thủ đang đứng trên dùng: ' + ' · '.join(f'"{x[:60]}"' for x in rt))
    out.append(('Title', f'{t} ({tl} ký tự)',
                ('Thêm ' + ', '.join(f'"{x}"' for x in miss[:2]) + ', giữ dưới 60 ký tự')
                if miss else 'Giữ nguyên, đã chứa các cụm chính',
                '; '.join(why) if why else 'Đã chứa cụm chính và đúng độ dài'))

    d = m.get('desc') or ''
    dl = len(d)
    dmiss = [g for g, _ in terms[:3] if _n(g) not in _n(d)]
    out.append(('Meta description', (f'{d[:130]} ({dl} ký tự)' if d else 'KHÔNG CÓ'),
                'Viết 150–160 ký tự, chứa ' + ', '.join(f'"{x}"' for x in dmiss[:2])
                if (dmiss or not 120 <= dl <= 165) else 'Giữ nguyên',
                (f'Độ dài {dl}, ngoài khoảng 120–165 nên dễ bị viết lại. ' if not 120 <= dl <= 165 else '')
                + ('Thiếu cụm ' + ', '.join(f'"{x}"' for x in dmiss[:3]) if dmiss else '')))

    h1 = m.get('h1') or ''
    h1miss = [g for g, _ in terms[:3] if _n(g) not in _n(h1)]
    out.append(('H1', h1 or 'KHÔNG CÓ',
                'Đưa cụm ' + ', '.join(f'"{x}"' for x in h1miss[:2]) + ' vào H1'
                if h1miss else 'Giữ nguyên',
                'H1 phải chứa cụm chính của cụm từ khoá. '
                + ('Đang thiếu: ' + ', '.join(h1miss[:3]) if h1miss else 'Đang đủ.')))

    u = m['url']
    slugmiss = [g for g, _ in terms[:2]
                if not all(w in _n(u) for w in _n(g).split()[:3])]
    out.append(('URL', sh(u),
                'Giữ nguyên' if not slugmiss else 'Cân nhắc, chỉ đổi khi thật cần và phải 301',
                'Slug đã chứa cụm chính.' if not slugmiss
                else f'Slug chưa chứa {slugmiss[0]}. Đổi slug làm mất tín hiệu đang có, '
                     'chỉ đổi khi trang còn yếu và có 301 đầy đủ.'))

    dm = (m.get('datemod') or '')[:10]
    rdm = sorted([r['datemod'][:10] for r in riv if r.get('datemod')], reverse=True)[:2]
    out.append(('dateModified', dm or 'KHÔNG KHAI', 'Cập nhật sau mỗi đợt sửa nội dung',
                ('Đối thủ đang đứng trên cập nhật ' + ', '.join(rdm) + '.') if rdm
                else 'Đối thủ trong cụm không khai dateModified.'))
    return out


def _hnorm(h):
    """Chuẩn hoá một heading để gom nhóm: bỏ dấu, bỏ số thứ tự, bỏ từ dừng."""
    s = unicodedata.normalize('NFD', str(h).lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('đ', 'd')
    s = re.sub(r'^\s*[0-9ivx]+[\.\)]?\s*', '', s)
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    stop = {'cua', 'va', 'la', 'cac', 'nhung', 'cho', 'voi', 'khi', 'ban', 'gi', 'nao',
            've', 'tren', 'trong', 'mot', 'nhat', 'nay', 'hay', 'de', 'duoc', 'co', 'khong',
            'tim', 'hieu', 'tai', 'sao', 'the', 'ra', 'sau', 'truoc', 'moi', 'ai', 'nen'}
    return [w for w in s.split() if w not in stop and len(w) > 1]


MODEL_RE = re.compile(r'([A-Za-z]{2,}[-\s]?\d{2,}[A-Za-z0-9\-]*)|(\b\d{3,4}[A-Za-z]{1,3}\b)')
BRANDS = ('hafele', 'bosch', 'junger', 'lorca', 'chefs', 'eurosun', 'spelier', 'sunhouse',
          'electrolux', 'malloca', 'canzy', 'faster', 'kaff', 'teka', 'cata', 'binova',
          'giovani', 'napoliz', 'dmestik', 'texgio', 'latino', 'elmich', 'comfee', 'panasonic',
          'sharp', 'toshiba', 'mitsubishi', 'siemens', 'bluestone', 'rangdong', 'nagakawa',
          'locknlock', 'ferroli', 'eurokera', 'schott', 'hitachi', 'daikin')


def _is_product_heading(t):
    """Heading là một mục sản phẩm cụ thể của đối thủ, không phải chủ đề — loại khỏi outline."""
    low = _n(t)
    if MODEL_RE.search(t):
        return True
    if sum(1 for b in BRANDS if b in low) >= 1 and len(low.split()) <= 9:
        return True
    return False


def _strip_num(t):
    return re.sub(r'^\s*[0-9IVXivx]+\s*[\.\)\-–]\s*', '', str(t)).strip()


def _hgroups(riv, minpages=2):
    """Gom heading của các trang top thành nhóm chủ đề. Trả về list (tên đại diện, số trang có, ví dụ)."""
    items = []
    for p in riv:
        seen = set()
        for h in (p.get('headings') or []):
            t = _strip_num(h)
            if not (6 <= len(t) <= 110):
                continue
            if _is_product_heading(t):
                continue
            w = _hnorm(t)
            if len(w) < 2:
                continue
            sig = frozenset(w)
            if sig in seen:
                continue
            seen.add(sig)
            items.append((sig, t, p['url'].split('/')[2]))
    groups = []
    for sig, title, dom in items:
        hit = None
        for g in groups:
            inter = len(sig & g['sig'])
            if inter >= 2 and inter >= 0.6 * min(len(sig), len(g['sig'])):
                hit = g
                break
        if hit:
            hit['sig'] |= sig
            hit['titles'].append(title)
            hit['doms'].add(dom)
        else:
            groups.append({'sig': set(sig), 'titles': [title], 'doms': {dom}})
    out = []
    for g in groups:
        if len(g['doms']) < minpages:
            continue
        rep = collections.Counter(g['titles']).most_common(1)[0][0]
        out.append((rep, len(g['doms']), sorted(g['doms'])[:3], g['titles']))
    out.sort(key=lambda x: -x[1])
    return out


def _facts(*pairs):
    """Hàng chip số liệu đặt dưới câu dẫn của mỗi mục outline."""
    ch = ''.join(f'<span class="ol-fact"><i>{k}</i>{v}</span>' for k, v in pairs if v)
    return f'<div class="ol-facts">{ch}</div>' if ch else ''


def _outline_newpage(rows, riv, terms):
    """Cụm chưa có trang đích — dựng outline cho trang MỚI hoàn toàn, khung lấy từ heading
    thật của các trang đang top."""
    if not riv:
        return [('new', 'Chưa dựng được outline',
                 'Cụm chưa có trang đích của mình VÀ chưa crawl được trang đối thủ nào trong '
                 'top 10. Cần crawl bổ sung trước khi dựng outline.', [])]
    rwords = st.median([r['words'] for r in riv])
    rimgs = st.median([r['imgs_all'] for r in riv])
    out = [('new', 'TRANG MỚI — cụm chưa có trang đích',
            'Toàn bộ outline dưới đây là MỚI. Khung dựng từ heading thật của '
            f'{len(riv)} trang đang top trong cụm, xếp theo số trang top có mục đó. '
            'Số liệu đối thủ bên dưới là mức sàn để trang mới cạnh tranh được.'
            + _facts(('Độ dài mục tiêu', f'{int(rwords * 1.1):,} từ'),
                     ('Ảnh mục tiêu', f'{int(rimgs):,}'),
                     ('Đối thủ trung vị', f'{rwords:.0f} từ · {rimgs:.0f} ảnh'),
                     ('Trang top đã đo', f'{len(riv)}')), [])]
    used = set()

    def kws_for(words, take=5):
        ws = set(words)
        if not ws:
            return []
        hit = []
        for r in rows:
            if r['kw'] in used:
                continue
            kw = set(_hnorm(r['kw']))
            if not kw:
                continue
            inter = len(ws & kw)
            if inter >= 2 and inter >= 0.5 * len(kw):
                hit.append((inter / len(kw), r.get('pos'), r['kw']))
        hit.sort(key=lambda x: (-x[0], x[1] is None, x[1] or 999))
        res = [(p, k) for _, p, k in hit[:take]]
        used.update(k for _, k in res)
        return res

    nriv = max(1, len(riv))
    order = 0
    for rep, npages, doms, _titles in _hgroups(riv, minpages=2)[:12]:
        order += 1
        gw = _hnorm(rep)
        subs = [('new', kw, f'nhắm từ khoá này, vị trí hiện tại '
                            f'{pos if pos else "ngoài top 100"}')
                for pos, kw in kws_for(gw)]
        out.append(('new', f'H2 {order}. {rep}',
                    'Mục này có trên trang top của cụm. Viết mới theo đúng ý định của các '
                    'trang đang xếp hạng.'
                    + _facts(('Đối thủ có mục này', f'{npages}/{nriv} trang top ({", ".join(doms)})'),
                             ('Độ dài', '350–500 từ'), ('Ảnh', '2–3')), subs))
    for g, nkw in terms[:4]:
        best = max([(_dens(r, g), r) for r in riv], key=lambda x: x[0], default=(0, None))
        rv, rp = best
        if rp is None or rv < 5:
            continue
        order += 1
        out.append(('new', f'H2 {order}. Khối nội dung dùng cụm "{g}"',
                    'Dựng một mục riêng cho cụm từ này, đặt cụm vào heading và đoạn mở đầu.'
                    + _facts(('Mật độ mục tiêu', f'{max(6, rv // 2)}–{rv} lần'),
                             ('Đối thủ cao nhất', f'{rp["url"].split("/")[2]} {rv} lần'),
                             ('Có trong', f'{nkw} từ khoá của cụm'),
                             ('Độ dài', '350–500 từ')),
                    [('new', kw, f'vị trí hiện tại {pos if pos else "ngoài top 100"}')
                     for pos, kw in kws_for(_hnorm(g))]))
    qs = [r for r in rows if any(q in _n(r['kw']) for q in QWORD)]
    if qs:
        order += 1
        out.append(('gap', f'H2 {order}. Câu hỏi thường gặp',
                    'Dựng mục hỏi đáp hiển thị thật trong HTML rồi mới khai FAQPage schema.'
                    + _facts(('Từ khoá dạng câu hỏi', f'{len(qs)}/{len(rows)} của cụm'),
                             ('Độ dài', '300–500 từ')),
                    [('gap', r['kw'], f'vị trí hiện tại {r.get("pos") or "ngoài top 100"}')
                     for r in qs[:6]]))
    order += 1
    out.append(('brand', f'H2 {order}. Giải pháp của thương hiệu cho nhu cầu này',
                'Đặt sau phần trả lời hết ý định tìm kiếm. Nêu đúng dòng sản phẩm liên quan '
                'tới chủ đề của cụm, kèm liên kết tới trang danh mục tương ứng.'
                + _facts(('Độ dài', '150–250 từ'), ('Ảnh', '1–2 ảnh sản phẩm thật')), []))
    return out


def auto_outline(ctx, rows, myurls, missing_sections=None):
    """Outline đầy đủ đáp ứng SERP, gắn nhãn GIỮ / SỬA / MỚI / GAP SERP / BRAND.

    Khung outline lấy từ heading thật của các trang đang top trong cụm, gom thành nhóm chủ đề
    rồi xếp theo số trang top có mục đó. Mỗi mục kèm mật độ hiện tại → mục tiêu (từ ma trận
    mật độ), độ dài, số ảnh và lý do có số của đối thủ.
    """
    P = ctx['pages']
    mine = [P[u] for u, _ in myurls[:1] if u in P]
    terms = _terms(rows)
    riv = _rivals(ctx, rows)
    if not mine:
        return _outline_newpage(rows, riv, terms)
    m = mine[0]
    myh = [_hnorm(h) for h in (m.get('headings') or [])]
    myset = [set(w) for w in myh if len(w) >= 2]
    rwords = st.median([r['words'] for r in riv]) if riv else 0
    rimgs = st.median([r['imgs_all'] for r in riv]) if riv else 0
    out = []

    out.append(('keep',
                f'Khung hiện tại: {m["h2"]} H2 / {m["h3"]} H3 · {m["words"]} từ · '
                f'{m["imgs_all"]} ảnh · {m["ilinks"]} link nội bộ',
                'GIỮ khung. Các mục dưới đây dựng từ heading thật của '
                f'{len(riv)} trang đang top trong cụm, xếp theo số trang top có mục đó.'
                + _facts(('Số từ', f'{m["words"]:,} → {max(m["words"], int(rwords * 1.15)):,}' if rwords else f'{m["words"]:,}'),
                         ('Đối thủ trung vị', f'{rwords:.0f} từ · {rimgs:.0f} ảnh' if rwords else ''),
                         ('Ảnh', f'{m["imgs_all"]}'),
                         ('Link nội bộ', f'{m["ilinks"]}')), []))

    used_kw = set()

    def kws_for(words, take=5):
        """Từ khoá của cụm khớp riêng chủ đề này. Mỗi từ khoá chỉ gán cho đúng một mục."""
        ws = set(words)
        if not ws:
            return []
        hit = []
        for r in rows:
            if r['kw'] in used_kw:
                continue
            kw = set(_hnorm(r['kw']))
            if not kw:
                continue
            inter = len(ws & kw)
            if inter >= 2 and inter >= 0.5 * len(kw):
                hit.append((inter / len(kw), r.get('pos'), r['kw']))
        hit.sort(key=lambda x: (-x[0], x[1] is None, x[1] or 999))
        out = [(p, k) for _, p, k in hit[:take]]
        used_kw.update(k for _, k in out)
        return out

    groups = _hgroups(riv, minpages=2)
    nriv = max(1, len(riv))
    order = 0
    for rep, npages, doms, titles in groups[:14]:
        gw = _hnorm(rep)
        mine_has = any(len(set(gw) & s) >= 2 and len(set(gw) & s) >= 0.6 * min(len(gw), len(s))
                       for s in myset)
        order += 1
        subs = []
        for pos, kw in kws_for(gw):
            subs.append(('keep' if mine_has else 'new', kw,
                         f'nhắm từ khoá này, vị trí hiện tại {pos if pos else "ngoài top 100"}'))
        dens = _dens(m, ' '.join(gw[:3])) if len(gw) >= 2 else 0
        best = max([(_dens(r, ' '.join(gw[:3])), r) for r in riv], key=lambda x: x[0],
                   default=(0, None)) if len(gw) >= 2 else (0, None)
        dtxt = ''
        if best[1] is not None and best[0] > 0:
            dtxt = (f'Mật độ cụm "{" ".join(gw[:3])}": hiện <b>{dens} lần</b>, '
                    f'{best[1]["url"].split("/")[2]} nhắc <b>{best[0]} lần</b>. '
                    f'Mục tiêu {max(3, int(best[0] * 0.8))}–{best[0]} lần. ')
        dens_chip = (f'{dens} → {max(3, int(best[0] * 0.8))}–{best[0]} lần'
                     if (best[1] is not None and best[0] > 0) else '')
        who = f'{npages}/{nriv} trang top ({", ".join(doms)})'
        if mine_has:
            out.append(('keep', f'H2 {order}. {rep}',
                        'Trang đã có mục này. Rà lại xem đã trả lời đủ ý chưa, '
                        'bổ sung nếu còn thiếu số liệu cụ thể.'
                        + _facts(('Đối thủ có mục này', who),
                                 (f'Mật độ "{" ".join(gw[:3])}"', dens_chip),
                                 ('Bổ sung', '150–250 từ')), subs))
        else:
            out.append(('new', f'H2 {order}. {rep}',
                        'Trang mình chưa có mục này. Viết mới, đặt sau các mục đã có '
                        'cùng nhóm chủ đề.'
                        + _facts(('Đối thủ có mục này', who),
                                 (f'Mật độ "{" ".join(gw[:3])}"', dens_chip),
                                 ('Độ dài', '350–500 từ'),
                                 ('Ảnh', '2–3 ảnh hoặc bảng số liệu')), subs))

    for g, nkw in terms:
        my = _dens(m, g)
        best = max([(_dens(r, g), r) for r in riv], key=lambda x: x[0], default=(0, None))
        rv, rp = best
        if rp is None:
            continue
        if my == 0 and rv >= 5:
            order += 1
            out.append(('new', f'H2 {order}. Khối nội dung dùng cụm "{g}"',
                        'Cụm này chưa xuất hiện lần nào trên trang. Đặt vào heading và đoạn mở đầu '
                        'của mục mới.'
                        + _facts(('Mật độ', f'0 → {max(6, rv // 2)}–{rv} lần'),
                                 ('Đối thủ cao nhất', f'{rp["url"].split("/")[2]} {rv} lần'),
                                 ('Có trong', f'{nkw} từ khoá của cụm'),
                                 ('Độ dài', '350–500 từ')),
                        [('new', kw, f'vị trí hiện tại {pos if pos else "ngoài top 100"}')
                         for pos, kw in kws_for(_hnorm(g))]))
        elif rv > my * 1.5 and rv >= 8:
            order += 1
            out.append(('fix', f'H2 {order}. Mở rộng phần nói về "{g}"',
                        'Bổ sung vào mục đã có, không tạo mục mới.'
                        + _facts(('Mật độ', f'{my} → {int(rv * 0.8)}–{rv} lần'),
                                 ('Đối thủ cao nhất', f'{rp["url"].split("/")[2]} {rv} lần'),
                                 ('Có trong', f'{nkw} từ khoá của cụm'),
                                 ('Bổ sung', '250–400 từ')),
                        [('fix', kw, f'vị trí hiện tại {pos if pos else "ngoài top 100"}')
                         for pos, kw in kws_for(_hnorm(g))[:4]]))

    if missing_sections:
        for lab, k, n in missing_sections[:6]:
            order += 1
            out.append(('gap', f'H2 {order}. Mục "{lab}"',
                        'Mục này có trên trang top của cụm nhưng trang mình chưa có.'
                        + _facts(('Đối thủ có mục này', f'{k}/{n} trang top'),
                                 ('Độ dài', '300–500 từ')), []))

    qs = [r for r in rows if any(q in _n(r['kw']) for q in QWORD)]
    if qs:
        order += 1
        out.append(('gap', f'H2 {order}. Câu hỏi thường gặp',
                    'Dựng mục hỏi đáp hiển thị thật trong HTML rồi mới khai FAQPage schema. '
                    'Bộ câu hỏi cụ thể ở mục 11.'
                    + _facts(('Từ khoá dạng câu hỏi', f'{len(qs)}/{len(rows)} của cụm'),
                             ('Độ dài', '300–500 từ')),
                    [('gap', r['kw'], f'vị trí hiện tại {r.get("pos") or "ngoài top 100"}')
                     for r in sorted(qs, key=lambda x: (x.get('pos') is None, x.get('pos') or 999))[:6]]))

    order += 1
    out.append(('brand', f'H2 {order}. Giải pháp của thương hiệu cho nhu cầu này',
                'Chỗ chèn sản phẩm một cách tự nhiên, đặt sau phần trả lời hết ý định tìm kiếm '
                'chứ không đặt lên đầu. Nêu đúng dòng sản phẩm liên quan tới chủ đề của cụm, '
                'kèm liên kết tới trang danh mục hoặc trang sản phẩm tương ứng.'
                + _facts(('Độ dài', '150–250 từ'), ('Ảnh', '1–2 ảnh sản phẩm thật')), []))

    if not any(o[0] in ('new', 'fix', 'gap') for o in out):
        out.append(('keep', 'Không có khoảng trống nội dung đo được',
                    'Mật độ mọi cụm đều ngang hoặc hơn đối thủ và không thiếu mục nào so với '
                    'các trang đang top. Nguyên nhân chưa lên top nằm ngoài nội dung — đọc mục '
                    'ăn thịt từ khoá và rà soát kỹ thuật.', []))
    return out


QWORD = ('là gì', 'bao nhiêu', 'như thế nào', 'thế nào', 'ở đâu', 'khi nào', 'có nên',
         'tại sao', 'vì sao', 'cách ', 'quy trình', 'mất bao lâu', 'giá', 'chi phí')


def auto_faq(ctx, rows, n=8):
    out = []
    for r in sorted(rows, key=lambda x: (x['pos'] or 999)):
        k = r['kw']
        if any(q in _n(k) for q in QWORD):
            out.append((k[0].upper() + k[1:] + '?', 'Trả lời trực tiếp trong 2–3 câu đầu, '
                        'dùng đúng cụm từ khoá.',
                        f'Chính là từ khoá đang ở vị trí {r["pos"] or "ngoài top"}'))
        if len(out) >= n // 2: break
    terms = _terms(rows, 6)
    tails = ('trọn gói', 'theo yêu cầu', 'chuyên nghiệp', 'giá rẻ', 'uy tín', 'cao cấp')
    for g, nkw in terms:
        if len(out) >= n: break
        t = next((x for x in tails if any(x in _n(r['kw']) for r in rows)), None)
        q = (f'{g[0].upper()}{g[1:]} {t} gồm những gì?' if t else f'{g[0].upper()}{g[1:]} là gì?')
        if not any(_n(q) == _n(x[0]) for x in out):
            out.append((q, 'Liệt kê đủ hạng mục, mỗi ý một câu.',
                        f'Cụm có trong {nkw} từ khoá của cụm'))
    for r in rows:
        if len(out) >= n: break
        k = r['kw']
        if not any(_n(k) in _n(x[0]) for x in out):
            out.append((k[0].upper() + k[1:] + '?', 'Trả lời ngắn, dẫn về mục tương ứng trong bài.',
                        f'Từ khoá đang ở vị trí {r["pos"] or "ngoài top"}'))
    return out[:n]


def auto_media(ctx, rows, myurls):
    P = ctx['pages']
    mine = [P[u] for u, _ in myurls[:1] if u in P]
    if not mine: return [], []
    m = mine[0]
    riv = _rivals(ctx, rows)
    if not riv: return [], []
    best = lambda k: max(riv, key=lambda r: r[k])
    out = []
    for lab, k in (('Ảnh nội dung', 'imgs_all'), ('Ảnh lazy-load', 'lazy'),
                   ('Ảnh có srcset', 'srcset'), ('Ảnh WebP', 'webp'), ('Link nội bộ', 'ilinks')):
        b = best(k)
        tgt = ('Toàn bộ' if k in ('lazy', 'srcset', 'webp')
               else f'{max(m[k], int(b[k] * 0.8))}–{max(m[k] + 10, b[k])}')
        out.append((lab, str(m[k]), f'{b["url"].split("/")[2]} {b[k]}', tgt))
    bk = min(riv, key=lambda r: r['kb'])
    out.append(('Dung lượng HTML', f'{m["kb"]}KB', f'{bk["url"].split("/")[2]} {bk["kb"]}KB',
                f'Dưới {max(m["kb"], int(st.median([r["kb"] for r in riv])))}KB'))
    terms = _terms(rows, 3)
    alt = [(re.sub(r'[^a-z0-9]+', '-', _n_ascii(g)) + f'-0{i+1}.webp',
            g[0].upper() + g[1:] + ' — ảnh minh hoạ thực tế')
           for i, (g, _) in enumerate(terms)]
    return out, alt


def _n_ascii(s):
    s = unicodedata.normalize('NFD', _n(s))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('đ', 'd')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


ENT = ('Organization', 'LocalBusiness', 'PostalAddress', 'GeoCoordinates', 'ContactPoint')


def auto_schema(ctx, rows, myurls):
    P = ctx['pages']
    mine = [P[u] for u, _ in myurls[:1] if u in P]
    if not mine: return []
    m = mine[0]
    riv = _rivals(ctx, rows)
    has = set(m.get('schemas') or [])
    out = []
    rc = collections.Counter()
    for r in riv:
        for s_ in set(r.get('schemas') or []): rc[s_] += 1
    faq_riv = sum(1 for r in riv if r.get('faq_render'))
    out.append(('FAQPage', 'Đã khai' if m.get('faq_schema') else
                ('Có khối hỏi đáp nhưng chưa khai schema' if m.get('faq_render') else 'Chưa có'),
                f'{faq_riv}/{len(riv)} trang top của cụm có khối hỏi đáp hiển thị. '
                'Render thật ra HTML trước, khai schema sau.'))
    ent_riv = sum(1 for r in riv if set(r.get('schemas') or []) & set(ENT))
    out.append(('Organization / LocalBusiness',
                'Đã có' if has & set(ENT) else 'Chưa có trên trang này',
                f'{ent_riv}/{len(riv)} trang top của cụm có schema doanh nghiệp. '
                'Khai một lần ở cấp template, hiệu lực toàn site.'))
    for s_, lab in (('Article', 'Article / BlogPosting'), ('BreadcrumbList', 'BreadcrumbList'),
                    ('ItemList', 'ItemList'), ('AggregateRating', 'AggregateRating')):
        n = rc.get(s_, 0)
        if s_ in has:
            out.append((lab, 'Đã có', 'Giữ' + (f'. {n}/{len(riv)} đối thủ top cũng có.' if n else '')))
        elif n >= max(1, len(riv) // 3):
            out.append((lab, 'Chưa có', f'{n}/{len(riv)} trang top của cụm có. '
                        + ('Chỉ khai khi có đánh giá thật hiển thị trên trang.'
                           if s_ == 'AggregateRating' else 'Cân nhắc bổ sung.')))
    return out


def auto_checklist(ctx, rows, myurls, meta, outline, media, schema):
    P = ctx['pages']
    out = []
    nurl = len(myurls)
    if nurl >= 2:
        out.append(('1', f'Phân vai {nurl} URL đang cùng phục vụ cụm, chọn một trang đích duy nhất',
                    f'{sum(1 for r in rows if r["nurl"] >= 2)}/{len(rows)} từ khoá của cụm có từ '
                    f'2 URL nội bộ cùng xuất hiện. Đây là lực cản trước mọi việc nội dung.', 'Trung bình'))
    tfix = [o for o in outline if o[0] in ('new', 'fix')]
    if tfix:
        out.append(('2', f'Bổ sung {len(tfix)} khối nội dung theo outline ở mục 10',
                    'Mỗi khối có cụm từ và mật độ mục tiêu ghi sẵn, lấy từ ma trận mật độ ở mục 6.',
                    'Trung bình' if len(tfix) <= 3 else 'Cao'))
    tmeta = [m for m in meta if m[0] in ('Title', 'H1') and not str(m[2]).startswith('Giữ')]
    if tmeta:
        out.append(('2', 'Sửa ' + ' và '.join(m[0] for m in tmeta) + ' theo mục 9',
                    'Cách rẻ nhất để đưa cụm còn thiếu vào tín hiệu mạnh nhất của trang.', 'Thấp'))
    tm = [m for m in media if m[0] in ('Ảnh WebP', 'Ảnh lazy-load', 'Ảnh có srcset')
          and str(m[1]).isdigit() and int(m[1]) == 0]
    if tm:
        out.append(('3', 'Xử lý ' + ', '.join(m[0].lower() for m in tm),
                    'Đang bằng 0 trong khi đối thủ trong cụm đã có.', 'Thấp'))
    if any(s[0] == 'FAQPage' and s[1] != 'Đã khai' for s in schema):
        out.append(('3', 'Render khối hỏi đáp rồi khai FAQPage schema',
                    'Bộ câu hỏi đã có ở mục 11. Render thật trước, khai schema sau.', 'Thấp'))
    gap = [o for o in outline if o[0] == 'gap']
    if gap:
        out.append(('4', f'Thêm {len(gap)} mục mà nhiều trang top có còn mình chưa có',
                    'Danh sách ở mục 8 và mục 16.', 'Trung bình'))
    if not out:
        out.append(('1', 'Giữ nguyên nội dung',
                    'Không đo được khoảng trống nào so với các trang đang đứng trên. '
                    'Việc cần làm nằm ngoài trang: liên kết, thẩm quyền, tín hiệu thực thể.', '—'))
    return out


def checklist_note(rows):
    """Số từ khoá hưởng lợi từ danh sách việc — mọi việc đều ở cấp trang chốt nên cùng một
    tập từ khoá hưởng lợi. Viết một lần dưới bảng thay vì lặp lại ở từng dòng."""
    nk = len(rows)
    nlow = sum(1 for r in rows if not r['pos'] or r['pos'] > 10)
    near = sum(1 for r in rows if r['pos'] and 11 <= r['pos'] <= 20)
    return (f'Toàn bộ việc trong bảng dồn vào URL chốt của cụm nên cùng ảnh hưởng <b>{nk} từ khoá</b>, '
            f'trong đó <b>{nlow} chưa vào top 10</b>'
            + (f' và <b>{near} đang ở tầng 11–20</b> — nhóm trả kết quả sớm nhất.' if near else '.'))


def build(ctx, rows, myurls, missing_sections=None):
    """Trả về dict sáu mục, dùng làm mức sàn cho báo cáo."""
    meta = auto_meta(ctx, rows, myurls)
    outline = auto_outline(ctx, rows, myurls, missing_sections)
    media, alt = auto_media(ctx, rows, myurls)
    schema = auto_schema(ctx, rows, myurls)
    faq = auto_faq(ctx, rows)
    return dict(meta=meta, outline=outline, faq=faq, media=media, alt=alt, schema=schema,
                checklist=auto_checklist(ctx, rows, myurls, meta, outline, media, schema),
                checklist_note=checklist_note(rows), _auto=True)

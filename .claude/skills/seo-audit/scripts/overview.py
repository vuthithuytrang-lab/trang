# -*- coding: utf-8 -*-
"""Các khối của file tổng hợp — sinh tự động, không phụ thuộc content.py.

Mọi con số ở đây truy được về đúng ba nguồn đã chứng thực:
  kw.json          file check top — thứ hạng thật, toàn bộ SERP
  gsc_*.json       Search Console — hiển thị, click, URL nội bộ tranh nhau
  pages/tech.json  HTML đã crawl, đã loại trang render JavaScript
  url_status / index_status — tình trạng thật và trạng thái lập chỉ mục của URL nội bộ

Không khối nào được phép in văn bản mẫu hay số điền tạm. Thiếu nguồn thì in thẳng
là thiếu nguồn nào và chạy lệnh gì để có.
"""
import collections, statistics as st

from blocks import esc, num, _empty
from lib import REF_RATES, tier_pool

TIER_ORDER = ['4-5', '6-10', '11-20', '21-50', '>50']
LVL = {'top3': 'top 3', 'top5': 'top 5', 'top10': 'top 10'}


def _pct(a, b):
    return (a * 100 // b) if b else 0


def _med(vals):
    return st.median(vals) if vals else None


def _need(n, goal_pct, cur):
    """Số từ khoá còn thiếu để nhóm n từ khoá đạt goal_pct phần trăm."""
    return max(0, -(-n * goal_pct // 100) - cur)


def _link(fn, name):
    return '<a href="' + fn + '">' + esc(name) + '</a>' if fn else esc(name)


def _pools(ov, mark):
    """Kho từ khoá theo tầng nguồn của một mốc, kèm ba mức chuyển đổi tham chiếu."""
    out = []
    for tier, lo_r, base_r, hi_r in REF_RATES[mark]:
        out.append((tier, len(tier_pool(ov['kw'], tier)), lo_r, base_r, hi_r))
    return out


def _cnt(ov, cut):
    return sum(1 for r in ov['kw'] if r['pos'] and r['pos'] <= cut)


def _main_mark(ov):
    """Mốc dùng để chẩn đoán và xếp ưu tiên: mốc rộng nhất trong mục tiêu đã đặt."""
    if not ov['marks']:
        return None
    return max(ov['marks'], key=lambda m: ov['cut'][m])


# ── D1. Phán quyết mục tiêu ──────────────────────────────────────────────────

def verdict_block(ov):
    if not ov['goals']:
        return _empty('phanquyet', 'Phán quyết mục tiêu', 'fa-gavel',
                      'Chưa đặt mục tiêu nên không tính được khoảng cách. Truyền '
                      '<span class="mono">--goals "top10=65,top5=50,top3=30"</span> khi dựng báo cáo.')
    tot = ov['tot']
    rows, bars = [], []
    for m in sorted(ov['marks'], key=lambda x: ov['cut'][x]):
        g = ov['goals'][m]
        cur, cut = _cnt(ov, ov['cut'][m]), ov['cut'][m]
        goal = round(tot * g / 100)
        need = max(0, goal - cur)
        pools = _pools(ov, m)
        kho = sum(p[1] for p in pools)
        cap = sum(p[1] * p[4] for p in pools)
        base = sum(p[1] * p[3] for p in pools)
        rate = (need / kho) if kho else None
        if need == 0:
            verd, cls, tag = 'ĐÃ ĐẠT', 'keep', f'Đang {cur}/{tot} = {_pct(cur, tot)}%, trên mục tiêu {g}%.'
        elif cap >= need:
            verd, cls = 'ĐẠT ĐƯỢC', 'keep'
            tag = (f'Cần thêm <b>{need}</b> từ khoá. Kho ở các tầng dưới mốc còn <b>{kho}</b> từ khoá; '
                   f'kể cả chỉ đạt mức chuyển đổi cơ sở cũng thu về khoảng <b>{base:.0f}</b>.')
        else:
            verd, cls = 'KHÔNG ĐẠT', 'must'
            tag = (f'Cần thêm <b>{need}</b> từ khoá nhưng đẩy hết kho <b>{kho}</b> từ khoá ở mức triệt để '
                   f'cũng chỉ được khoảng <b>{cap:.0f}</b> — <b>thiếu {round(need - cap)} từ khoá</b>. '
                   'Mục tiêu này không đạt được bằng on-page trong phạm vi bộ từ khoá đang theo dõi.')
        rows.append(f'<tr><td><b>Top {cut}</b></td><td class="num">{cur}</td>'
                    f'<td class="num">{_pct(cur, tot)}%</td><td class="num">{g}%</td>'
                    f'<td class="num">{goal}</td>'
                    f'<td class="num"><b class="warnnum">{need}</b></td><td class="num">{kho}</td>'
                    f'<td class="num">{f"{rate*100:.0f}%" if rate is not None else "—"}</td>'
                    f'<td class="num">{base:.0f}</td><td class="num">{cap:.0f}</td>'
                    f'<td><span class="sev {"s-lo" if verd != "KHÔNG ĐẠT" else "s-cr"}">{verd}</span></td></tr>')
        bars.append(f'<div class="rolebar {cls}"><div class="rk">Mốc top {cut} · mục tiêu {g}%</div>'
                    f'<div class="rv"><b>{verd}</b></div><div class="rn">{tag}</div></div>')
    ref = []
    for m in sorted(ov['marks'], key=lambda x: ov['cut'][x]):
        for tier, n_, lo_r, base_r, hi_r in _pools(ov, m):
            ref.append(f'<tr><td>Top {ov["cut"][m]}</td><td>từ tầng {esc(tier)}</td>'
                       f'<td class="num">{n_}</td><td class="num">{lo_r:.0%}</td>'
                       f'<td class="num">{base_r:.0%}</td><td class="num">{hi_r:.0%}</td></tr>')
    return ('\n<div class="card" id="phanquyet">\n'
            '  <h2><i class="fa-solid fa-gavel"></i> 1. Phán quyết mục tiêu</h2>\n'
            f'  <p style="color:var(--text-2)">Tính trên đúng {tot} từ khoá đang theo dõi, thứ hạng lấy từ '
            'file check top. Mục tiêu đặt trước, tỷ lệ cần thiết tính ngược ra, rồi mới đối chiếu với ba mức '
            'chuyển đổi tham chiếu để xem tỷ lệ đó có thực tế không.</p>\n'
            '  <div class="tblwrap"><table><thead><tr><th>Mốc</th><th class="num">Hiện có</th>'
            '<th class="num">%</th><th class="num">Mục tiêu</th><th class="num">Cần đạt<br>số kw</th>'
            '<th class="num">Cần thêm</th><th class="num">Kho<br>khả dụng</th>'
            '<th class="num">Tỷ lệ<br>cần thiết</th><th class="num">Kỳ vọng<br>mức cơ sở</th>'
            '<th class="num">Trần<br>mức triệt để</th><th>Phán quyết</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>\n  ' + ''.join(bars) +
            '\n  <h3 style="margin-top:20px">Kho từ khoá và mức chuyển đổi tham chiếu</h3>\n'
            '  <div class="tblwrap"><table><thead><tr><th>Mốc</th><th>Tầng nguồn</th>'
            '<th class="num">Số kw trong kho</th><th class="num">Thận trọng</th>'
            '<th class="num">Cơ sở</th><th class="num">Triệt để</th></tr></thead><tbody>'
            + ''.join(ref) + '</tbody></table></div>\n'
            '  <div class="note"><i class="fa-solid fa-circle-info"></i>Cột kỳ vọng và trần là <b>ước tính</b>, '
            'lấy kho từ khoá thật nhân với ba mức chuyển đổi ở <span class="mono">references/metrics.md</span> mục 5. '
            'Số kw và tầng vị trí là số đo được; hệ số chuyển đổi là mức tham chiếu, không phải số đo của dự án này.'
            '</div>\n</div>\n')


# ── D2. Đối thủ trên toàn bộ bộ từ khoá ──────────────────────────────────────

def rivals_block(ov):
    ME, KW = ov['me'], ov['kw']
    cut = ov['cut'][_main_mark(ov)] if ov['marks'] else 10
    top10, top3, urls, poss = (collections.Counter(), collections.Counter(),
                               collections.defaultdict(set), collections.defaultdict(list))
    block = collections.Counter()
    social = ov['social']
    for r in KW:
        mine_ok = r['pos'] and r['pos'] <= cut
        seen, seen3 = set(), set()
        for p, d, u in r['serp']:
            if d in social:
                continue
            if p <= 10:
                if d not in seen:
                    top10[d] += 1
                    seen.add(d)
                urls[d].add(u)
                poss[d].append(p)
            if p <= 3 and d not in seen3:
                top3[d] += 1
                seen3.add(d)
            if p <= cut and not mine_ok and d != ME:
                block[d] += 1
    if not top10:
        return _empty('doithu', 'Đối thủ trên toàn bộ bộ từ khoá', 'fa-users-viewfinder',
                      'Không đọc được SERP nào từ file check top. Chạy lại '
                      '<span class="mono">scripts/parse_ranktracker.py</span>.')
    order = [d for d, _ in top10.most_common(14)]
    if ME in top10 and ME not in order:
        order.append(ME)
    rows = []
    for d in order:
        nu = len(urls[d])
        me = (d == ME)
        rows.append('<tr>'
                    f'<td class="{"top" if me else ""}">{"<b>" + esc(d) + " — trang của mình</b>" if me else esc(d)}</td>'
                    f'<td class="num">{top10[d]}</td><td class="num">{_pct(top10[d], ov["tot"])}%</td>'
                    f'<td class="num">{top3[d]}</td>'
                    f'<td class="num">{_med(poss[d]):.0f}</td><td class="num">{nu}</td>'
                    f'<td class="num">{top10[d] / nu:.1f}</td>'
                    f'<td class="num">{"—" if me else block[d]}</td></tr>')
    lead = [d for d in order if d != ME][:3]
    mine_kwu = top10[ME] / len(urls[ME]) if ME in top10 and urls[ME] else None
    lead_kwu = _med([top10[d] / len(urls[d]) for d in lead]) if lead else None
    note = ''
    if mine_kwu and lead_kwu:
        note = ('<div class="note"><i class="fa-solid fa-circle-info"></i>'
                f'<b>Độ phân tán URL.</b> Ba đối thủ dẫn đầu gánh trung vị <b>{lead_kwu:.1f}</b> từ khoá trên '
                f'mỗi URL, mình <b>{mine_kwu:.1f}</b>. '
                + ('Mình đang chia nhỏ cùng một chủ đề ra quá nhiều URL — đó là gốc của phần lớn '
                   'trường hợp ăn thịt từ khoá bên dưới.' if mine_kwu < lead_kwu * 0.7 else
                   'Mức phân tán của mình không lệch xa nhóm dẫn đầu.') + '</div>')
    return ('\n<div class="card" id="doithu">\n'
            '  <h2><i class="fa-solid fa-users-viewfinder"></i> 2. Đối thủ trên toàn bộ bộ từ khoá</h2>\n'
            f'  <p style="color:var(--text-2)">Đếm trên toàn bộ SERP của {ov["tot"]} từ khoá trong file check top, '
            'đã loại mạng xã hội và sàn thương mại điện tử. Cột cuối trả lời thẳng: muốn đạt mục tiêu '
            f'top {cut} thì phải giành chỗ của ai.</p>\n'
            '  <div class="tblwrap"><table><thead><tr><th>Domain</th>'
            '<th class="num">kw có mặt<br>top 10</th><th class="num">% bộ<br>từ khoá</th>'
            '<th class="num">kw<br>top 3</th><th class="num">Vị trí<br>trung vị</th>'
            '<th class="num">Số URL<br>dùng</th><th class="num">kw/URL</th>'
            f'<th class="num">Đang chiếm chỗ<br>của mình ở top {cut}</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>\n  ' + note + '\n</div>\n')


# ── D3. Ma trận nguyên nhân ──────────────────────────────────────────────────

CAUSE = [
    ('KHÔI PHỤC', 's-cr', 'URL đang 404, 410 hoặc lỗi máy chủ',
     'Khôi phục nội dung hoặc 301 về trang thay thế. Không viết đề xuất nội dung cho URL đã chết.'),
    ('CHƯA INDEX', 's-cr', 'Google chưa lập chỉ mục trang',
     'Đưa vào chỉ mục trước: sửa liên kết nội bộ, gửi lại sitemap, xử lý nguyên nhân trong coverageState. '
     'Tối ưu nội dung lúc này chưa có tác dụng.'),
    ('GOOGLE ĐÃ GỘP', 's-hi', 'googleCanonical khác userCanonical',
     'Google đã tự chọn trang đại diện. Xác nhận nó chọn đúng trang; nếu sai thì sửa tín hiệu để đổi lựa chọn.'),
    ('ĂN THỊT', 's-hi', 'Từ hai URL nội bộ cùng nhận thứ hạng hoặc hiển thị',
     'Phân vai dứt khoát: một URL chốt, phần còn lại cắt nội dung trùng, đổi anchor link nội bộ, 301 nếu cần.'),
    ('CHƯA CÓ TRANG', 's-hi', 'Không URL nội bộ nào xếp hạng và không URL nào nhận hiển thị',
     'Dựng trang đích mới — xem outline trong file của nhóm tương ứng.'),
    ('CHƯA LỌT TOP', 's-hi', 'Trang đã tồn tại và có hiển thị trên Search Console nhưng chưa vào '
                             'độ sâu SERP đã đo',
     'Tối ưu trang đã có, không viết trang mới. URL cụ thể nằm ở mục 6 và trong file của nhóm.'),
    ('LỆCH Ý ĐỊNH', 's-md', 'SERP là loại trang khác hẳn trang của mình',
     'Cân nhắc loại khỏi kho tính mục tiêu, hoặc dựng đúng loại trang mà SERP đang thưởng.'),
    ('NỘI DUNG MỎNG', 's-md', 'Trang có thật nhưng dưới ngưỡng nhóm top 10 của chính từ khoá đó',
     'Bổ sung nội dung theo outline và ma trận mật độ trong file của nhóm.'),
    ('NGOÀI ON-PAGE', 's-lo', 'On-page đã đạt ngưỡng nhóm top 10 mà vẫn ngoài mốc',
     'On-page không còn là chỗ nghẽn. Các yếu tố còn lại chưa đo trong lần chạy này.'),
    ('CHƯA ĐỦ DỮ LIỆU', 's-lo', 'Chưa crawl được trang của mình hoặc dưới 3 trang đối thủ đo được',
     'Chạy scripts/precheck.py --fix để quét bù rồi dựng lại báo cáo.'),
]


def _label_kw(ov, r):
    """Gán đúng một nhãn nguyên nhân cho một từ khoá chưa đạt mốc. Dừng ở nhánh khớp đầu tiên."""
    ME, code, ix = ov['me'], ov['code'], ov['index_status']
    q = ov['nrm'](r['kw'])
    mine = [ov['clean'](u) for _p, u in r['allmine']]
    gsc_urls = [(u, i) for u, i in (ov['byq'].get(q) or {}).items() if ME in u]
    gsc_urls.sort(key=lambda x: -x[1])
    known = mine + [u for u, i in gsc_urls if i >= 10]
    dead = [u for u in known if code.get(u) in (404, 410) or (code.get(u) or 0) >= 500]
    if dead:
        return 'KHÔI PHỤC', dead[0]
    lead = mine[0] if mine else (gsc_urls[0][0] if gsc_urls else None)
    if lead:
        i = ix.get(lead) or {}
        if i.get('verdict') and i['verdict'] != 'PASS':
            return 'CHƯA INDEX', lead
        gc, uc = i.get('googleCanonical'), i.get('userCanonical')
        if gc and uc and gc.rstrip('/') != uc.rstrip('/'):
            return 'GOOGLE ĐÃ GỘP', lead
    det = (ov['gsc_detail'] or {}).get(q) or {}
    if r['nurl'] >= 2 or det.get('can'):
        return 'ĂN THỊT', lead
    if not known:
        return 'CHƯA CÓ TRANG', None
    if not mine:
        # có trang, có hiển thị, nhưng không URL nào lọt vào độ sâu SERP đã đo
        return 'CHƯA LỌT TOP', lead
    pk = ov['perkw'].get(r['kw']) or {}
    riv = [x for x in (pk.get('riv') or []) if x['pos'] <= 10]
    if not pk.get('my') or len(riv) < 3:
        return 'CHƯA ĐỦ DỮ LIỆU', lead
    sell = ov['sell']
    share = sum(1 for x in riv if x['url'].split('?')[0] in sell) / len(riv)
    if len(riv) >= 5:
        mine_sell = lead in sell
        if share >= 0.6 and not mine_sell:
            return 'LỆCH Ý ĐỊNH', lead
        if share <= 0.2 and mine_sell:
            return 'LỆCH Ý ĐỊNH', lead
    if pk['my']['words'] < st.median([x['words'] for x in riv]):
        return 'NỘI DUNG MỎNG', lead
    return 'NGOÀI ON-PAGE', lead


def cause_block(ov):
    m = _main_mark(ov)
    if not m:
        return ''
    cut = ov['cut'][m]
    fail = [r for r in ov['kw'] if not r['pos'] or r['pos'] > cut]
    if not fail:
        return ('\n<div class="card" id="nguyennhan"><h2><i class="fa-solid fa-stethoscope"></i> '
                f'3. Vấn đề đang khiến chưa đạt mục tiêu</h2><div class="note ok">'
                f'<i class="fa-solid fa-circle-check"></i>Toàn bộ {ov["tot"]} từ khoá đã nằm trong '
                f'top {cut}. Không còn từ khoá nào để chẩn đoán ở mốc này.</div></div>\n')
    band = lambda r: ('11–20' if r['pos'] and r['pos'] <= 20 else
                      '21–50' if r['pos'] and r['pos'] <= 50 else '>50')
    agg = collections.defaultdict(lambda: {'n': 0, '11–20': 0, '21–50': 0, '>50': 0, 'kw': []})
    for r in fail:
        lab, _u = _label_kw(ov, r)
        d = agg[lab]
        d['n'] += 1
        d[band(r)] += 1
        if len(d['kw']) < 4:
            d['kw'].append(r['kw'])
    rows = []
    for lab, cls, why, todo in CAUSE:
        d = agg.get(lab)
        if not d:
            continue
        rows.append(f'<tr><td><span class="sev {cls}">{lab}</span></td>'
                    f'<td class="num"><b>{d["n"]}</b></td><td class="num">{_pct(d["n"], len(fail))}%</td>'
                    f'<td class="num">{d["11–20"]}</td><td class="num">{d["21–50"]}</td>'
                    f'<td class="num">{d[">50"]}</td>'
                    f'<td class="small">{esc(why)}</td><td class="small">{esc(todo)}</td>'
                    f'<td class="small mono">{esc(" · ".join(d["kw"]))}</td></tr>')
    goal = ov['goals'].get(m)
    need = max(0, round(ov['tot'] * goal / 100) - _cnt(ov, cut)) if goal else 0
    near = agg and sorted(((d['11–20'], lab) for lab, d in agg.items()), reverse=True)[0]
    note = ''
    if need and near and near[0]:
        note = ('<div class="note warn"><i class="fa-solid fa-triangle-exclamation"></i>'
                f'Còn thiếu <b>{need}</b> từ khoá để đạt mốc top {cut}. Nhãn <b>{esc(near[1])}</b> đang giữ '
                f'<b>{near[0]}</b> từ khoá ở tầng 11–20 — đây là chỗ trả từ khoá nhanh nhất vì khoảng cách '
                'vị trí ngắn nhất.</div>')
    return ('\n<div class="card" id="nguyennhan">\n'
            '  <h2><i class="fa-solid fa-stethoscope"></i> 3. Vấn đề đang khiến chưa đạt mục tiêu</h2>\n'
            f'  <p style="color:var(--text-2)">Chẩn đoán <b>{len(fail)}</b> từ khoá chưa vào top {cut}. '
            'Mỗi từ khoá được gán đúng một nhãn, xét theo thứ tự ưu tiên từ trên xuống — trang chết thì '
            'không xét tiếp nội dung, chưa index thì không xét tiếp mật độ. Tổng các dòng bằng đúng số '
            'từ khoá chưa đạt, không từ khoá nào bị bỏ ra ngoài.</p>\n'
            '  <div class="tblwrap"><table><thead><tr><th>Nhãn</th><th class="num">Số kw</th>'
            '<th class="num">%</th><th class="num">11–20</th><th class="num">21–50</th>'
            '<th class="num">&gt;50</th><th>Căn cứ nhận nhãn</th><th>Việc cần làm</th>'
            '<th>Ví dụ từ khoá</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>\n  ' + note + '\n</div>\n')


# ── D4. Ưu tiên nhóm: nhóm nào dễ lên ────────────────────────────────────────

def priority_block(ov):
    m = _main_mark(ov)
    if not m or not ov['gap']:
        return ''
    cut, g = ov['cut'][m], ov['goals'][m]
    tier_key = {'top10': ('b11', 'b21', 'b50'), 'top5': ('b6', 'b11', 'b21'),
                'top3': ('b45', 'b6', 'b11')}[m]
    refs = REF_RATES[m]
    items = []
    for gg in ov['gap']:
        need = _need(gg['n'], g, gg['cnt'].get(m, 0))
        exp = sum(gg.get(k, 0) * refs[i][2] for i, k in enumerate(tier_key))
        pool = sum(gg.get(k, 0) for k in tier_key)
        items.append(dict(g=gg, need=need, exp=exp, pool=pool,
                          ratio=(exp / need) if need else None))
    todo = [x for x in items if x['need'] > 0]
    done = [x for x in items if x['need'] == 0]
    todo.sort(key=lambda x: (-(x['ratio'] or 0), x['need']))
    glob_need = max(0, round(ov['tot'] * g / 100) - _cnt(ov, cut))
    rows, run, cutoff = [], 0.0, None
    for i, x in enumerate(todo, 1):
        gain = min(x['need'], x['exp'])
        run += gain
        if cutoff is None and glob_need and run >= glob_need:
            cutoff = i
        r = x['ratio'] or 0
        lvl = ('RẤT DỄ', 's-lo') if r >= 2 else ('DỄ', 's-lo') if r >= 1.2 else \
              ('VỪA', 's-md') if r >= 0.8 else ('KHÓ', 's-cr')
        nm = _link(x['g']['fn'], x['g']['name'])
        tr = '<tr class="cutrow">' if cutoff == i else '<tr>'
        rows.append(tr +
                    f'<td class="num">{i}</td><td>{nm}</td><td class="num">{x["g"]["n"]}</td>'
                    f'<td class="num">{x["g"]["cnt"].get(m, 0)}</td>'
                    f'<td class="num"><b class="warnnum">{x["need"]}</b></td>'
                    f'<td class="num">{x["pool"]}</td><td class="num">{x["exp"]:.1f}</td>'
                    f'<td class="num">{r:.1f}×</td>'
                    f'<td><span class="sev {lvl[1]}">{lvl[0]}</span></td>'
                    f'<td><span class="tag {ov["vt"].get(x["g"]["verd"], "t-keep")}">{x["g"]["verd"]}</span></td>'
                    f'<td class="num">{run:.0f}</td></tr>')
    tail = ''
    if done:
        tail = (f'<div class="note ok"><i class="fa-solid fa-circle-check"></i>'
                f'<b>{len(done)} nhóm đã đạt mốc top {cut}</b> ở mức mục tiêu {g}%, tổng '
                f'{sum(x["g"]["n"] for x in done)} từ khoá. Các nhóm này chỉ cần giữ, không nằm trong '
                'danh sách thi công.</div>')
    cutnote = ''
    if cutoff:
        cutnote = ('<div class="note"><i class="fa-solid fa-flag-checkered"></i>'
                   f'<b>Làm hết {cutoff} nhóm đầu bảng là đủ mốc top {cut} cho toàn dự án.</b> '
                   f'Toàn bộ cần thêm {glob_need} từ khoá; cộng dồn dư địa kỳ vọng của {cutoff} nhóm này '
                   'đã vượt con số đó. Đường kẻ đậm là chỗ cắt.</div>')
    elif glob_need:
        cutnote = ('<div class="note warn"><i class="fa-solid fa-triangle-exclamation"></i>'
                   f'<b>Làm hết mọi nhóm vẫn chưa đủ mốc top {cut}.</b> Toàn bộ cần thêm {glob_need} từ khoá, '
                   f'cộng dồn dư địa kỳ vọng của tất cả {len(todo)} nhóm chỉ được {run:.0f}. '
                   'Phần thiếu không lấp được bằng on-page trong phạm vi bộ từ khoá đang theo dõi.</div>')
    return ('\n<div class="card" id="uutien">\n'
            '  <h2><i class="fa-solid fa-ranking-star"></i> 4. Nhóm nào dễ lên, làm nhóm nào trước</h2>\n'
            f'  <p style="color:var(--text-2)">Xếp theo tỷ lệ <b>dư địa kỳ vọng / cần thêm</b> ở mốc top {cut}. '
            'Dư địa kỳ vọng là số từ khoá trong kho của chính nhóm đó nhân với mức chuyển đổi cơ sở theo tầng '
            'vị trí — nhóm có nhiều từ khoá đang đứng sát mốc thì lên rẻ hơn nhóm phải kéo từ ngoài 50. '
            'Cột cuối cộng dồn từ trên xuống.</p>\n'
            '  <div class="tblwrap"><table><thead><tr><th class="num">#</th><th>Nhóm từ khoá</th>'
            f'<th class="num">Số kw</th><th class="num">Đang<br>top {cut}</th><th class="num">Cần thêm</th>'
            '<th class="num">Kho<br>tầng dưới</th><th class="num">Dư địa<br>kỳ vọng</th>'
            '<th class="num">Tỷ lệ</th><th>Mức độ</th><th>Loại việc</th>'
            '<th class="num">Cộng dồn</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>\n  ' + cutnote + tail + '\n</div>\n')


# ── D5. Khoảng cách on-page trên toàn bộ dự án ───────────────────────────────

_SPECS = [('Số từ nội dung chính', 'words'), ('Số ảnh', 'imgs'), ('Link nội bộ', 'ilinks'),
          ('Số H2', 'h2'), ('Số H3', 'h3'), ('Dung lượng HTML (KB)', 'kb')]


def _tier_pages(ov, lo, hi):
    """Trang đối thủ đang ở dải vị trí lo–hi, gộp toàn dự án, mỗi URL tính một lần."""
    out = {}
    for r in ov['kw']:
        pk = ov['perkw'].get(r['kw'])
        if not pk:
            continue
        for x in pk['riv']:
            if lo <= x['pos'] <= hi:
                out[x['url'].split('?')[0]] = x
    return list(out.values())


def onpage_gap_block(ov):
    t3, t410 = _tier_pages(ov, 1, 3), _tier_pages(ov, 4, 10)
    mine = {}
    for r in ov['kw']:
        pk = ov['perkw'].get(r['kw'])
        if pk and pk.get('my') and r.get('url'):
            mine[ov['clean'](r['url'])] = pk['my']
    mine = list(mine.values())
    if len(t3) < 5 or not mine:
        return _empty('gaponpage', 'Khoảng cách on-page trên toàn bộ dự án', 'fa-arrows-left-right-to-line',
                      'Chưa đủ mẫu: cần ít nhất 5 trang đối thủ ở top 3 đo được và một trang của mình '
                      'đang xếp hạng. Chạy <span class="mono">scripts/precheck.py --fix</span> để quét bù.')
    rows = []
    for lab, k in _SPECS:
        a, b, c = _med([x[k] for x in mine]), _med([x[k] for x in t3]), _med([x[k] for x in t410])
        d = a - b
        lower_better = (k == 'kb')
        ok = (d >= 0) if not lower_better else (d <= 0)
        rows.append(f'<tr><td>{esc(lab)}</td><td class="num {"top" if ok else "zero"}">{a:.0f}</td>'
                    f'<td class="num">{b:.0f}</td><td class="num">{c:.0f}</td>'
                    f'<td class="num">{"+" if d > 0 else ""}{d:.0f}</td></tr>')
    faq = lambda g: _pct(sum(1 for x in g if x.get('faq')), len(g))
    rows.append(f'<tr><td>Có FAQ schema</td><td class="num">{faq(mine)}%</td>'
                f'<td class="num">{faq(t3)}%</td><td class="num">{faq(t410)}%</td>'
                f'<td class="num">{faq(mine) - faq(t3):+d}</td></tr>')
    reach = 0
    per = []
    for cname, rws in ov['rows_by_cluster'].items():
        E, my = {}, None
        for r in rws:
            pk = ov['perkw'].get(r['kw'])
            if not pk:
                continue
            if pk.get('my') and my is None:
                my = pk['my']
            for x in pk['riv']:
                if x['pos'] <= 10:
                    E[x['url']] = x
        if len(E) >= 5 and my:
            thr = st.median([x['words'] for x in E.values()])
            per.append((cname, my['words'] >= thr))
            reach += 1 if my['words'] >= thr else 0
    pnote = ''
    if per:
        pnote = ('<div class="note"><i class="fa-solid fa-circle-info"></i>'
                 f'<b>{reach}/{len(per)} nhóm</b> có trang chủ lực đạt hoặc vượt ngưỡng số từ của nhóm top 10 '
                 f'trong chính nhóm đó. {len(per) - reach} nhóm còn dưới ngưỡng — chi tiết ở mục 8 của từng '
                 'file nhóm.</div>')
    return ('\n<div class="card" id="gaponpage">\n'
            '  <h2><i class="fa-solid fa-arrows-left-right-to-line"></i> '
            '5. Khoảng cách on-page trên toàn bộ dự án</h2>\n'
            f'  <p style="color:var(--text-2)">Trung vị đo trực tiếp từ HTML thô, đã loại trang render '
            f'JavaScript. Cột của mình lấy {len(mine)} trang đang xếp hạng, top 1–3 lấy {len(t3)} trang, '
            f'top 4–10 lấy {len(t410)} trang, mỗi URL tính một lần dù xếp hạng cho nhiều từ khoá.</p>\n'
            '  <div class="tblwrap"><table><thead><tr><th>Chỉ số</th>'
            '<th class="num">Trang của mình</th><th class="num">Top 1–3</th><th class="num">Top 4–10</th>'
            '<th class="num">Chênh so<br>với top 1–3</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>\n  ' + pnote + '\n</div>\n')


# ── D6. Danh sách việc cấp dự án ─────────────────────────────────────────────

_VORDER = ['TẠO MỚI', 'KHÔI PHỤC', 'TỐI ƯU', 'GIỮ']


def worklist_block(ov):
    if not ov['gap']:
        return ''
    m = _main_mark(ov)
    g = ov['goals'].get(m) if m else None
    by = collections.defaultdict(list)
    for gg in ov['gap']:
        by[gg['verd']].append(gg)
    cards = []
    for v in _VORDER:
        lst = by.get(v)
        if not lst:
            continue
        lst.sort(key=lambda x: -x['n'])
        need = sum(_need(x['n'], g, x['cnt'].get(m, 0)) for x in lst) if g else 0
        rows = ''.join(
            f'<tr><td>{_link(x["fn"], x["name"])}</td>'
            f'<td class="num">{x["n"]}</td>'
            f'<td class="num">{x["cnt"].get(m, 0) if m else "—"}</td>'
            f'<td class="num">{_need(x["n"], g, x["cnt"].get(m, 0)) if g else "—"}</td>'
            f'<td class="mono small">{esc(ov["sh"](x["tgt"]))}</td></tr>' for x in lst)
        cards.append(f'<h3 style="margin-top:18px"><span class="tag {ov["vt"].get(v, "t-keep")}">{v}</span> '
                     f'{len(lst)} nhóm · {sum(x["n"] for x in lst)} từ khoá'
                     + (f' · cần thêm {need} từ khoá' if g and need else '') + '</h3>'
                     '<div class="tblwrap"><table><thead><tr><th>Nhóm</th><th class="num">Số kw</th>'
                     f'<th class="num">Đang top {ov["cut"][m] if m else ""}</th>'
                     '<th class="num">Cần thêm</th><th>URL chốt</th></tr></thead><tbody>'
                     + rows + '</tbody></table></div>')
    return ('\n<div class="card" id="vieclam">\n'
            '  <h2><i class="fa-solid fa-list-check"></i> 6. Danh sách việc cấp dự án</h2>\n'
            '  <p style="color:var(--text-2)">Gom theo loại việc của URL chốt từng nhóm. URL chốt chọn theo '
            'thứ tự: đang xếp hạng thì giữ, chưa xếp hạng nhưng đã có hiển thị thì tối ưu, đang 404 mà còn '
            'hiển thị thì khôi phục, chỉ khi không còn trang nào phục vụ chủ đề mới tạo mới.</p>\n  '
            + ''.join(cards) + '\n</div>\n')


# ── Ghép toàn bộ ─────────────────────────────────────────────────────────────

def render(ov):
    parts = [('phanquyet', '1. Phán quyết mục tiêu', verdict_block(ov)),
             ('doithu', '2. Đối thủ trên toàn bộ bộ từ khoá', rivals_block(ov)),
             ('nguyennhan', '3. Vấn đề đang khiến chưa đạt mục tiêu', cause_block(ov)),
             ('uutien', '4. Nhóm nào dễ lên, làm nhóm nào trước', priority_block(ov)),
             ('gaponpage', '5. Khoảng cách on-page trên toàn bộ dự án', onpage_gap_block(ov)),
             ('vieclam', '6. Danh sách việc cấp dự án', worklist_block(ov))]
    toc = ''.join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t, h in parts if h)
    toc += '<li><a href="#gapnhom">7. Khoảng cách tới mục tiêu theo từng nhóm</a></li>'
    return ('<div class="toc"><b>Nội dung tài liệu</b><ol>' + toc + '</ol></div>'
            + ''.join(h for _i, _t, h in parts if h))

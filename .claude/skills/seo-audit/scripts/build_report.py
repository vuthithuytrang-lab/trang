#!/usr/bin/env python3
"""Bước 9 — dựng khung báo cáo HTML. Phần định tính do agent viết vào content.py."""
import argparse, collections, html, json, os, re, statistics as st, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import clean, dom, is_js_rendered, nrm, project_dir, slugify, SOCIAL
import blocks as B
import autocontent as AC
import overview as OV

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data')
ap.add_argument('--prefix', help='tiền tố tên file, mặc định lấy từ meta')
ap.add_argument('--out', help='thư mục xuất, mặc định ~/html/<dự án>/')
ap.add_argument('--project', help='tên thư mục dự án, mặc định lấy từ prefix hoặc domain')
ap.add_argument('--content', help='file python chứa dict C phần định tính từng cụm')
ap.add_argument('--min-file', type=int, default=1,
                help='số từ khoá tối thiểu để cụm có file riêng. Mặc định 1: mọi cụm đều có file, '
                     'kể cả cụm một từ khoá. Đặt cao hơn nếu muốn gọn')
ap.add_argument('--force', action='store_true',
                help='dựng báo cáo dù precheck báo còn chỗ quét bù. Chỉ dùng khi biết rõ '
                     'vì sao không quét được, và phải ghi lý do vào báo cáo')
ap.add_argument('--skip-precheck', action='store_true')
ap.add_argument('--goals', default='top5=30,top10=70',
                help='mốc mục tiêu, quyết định cột nào hiện trong bảng. VD top5=30,top10=70')
a = ap.parse_args()

# Cổng chặn: file gợi ý phải đủ mục. Thiếu vì chưa quét thì đi quét, không ẩn mục.
if not a.skip_precheck:
    import subprocess
    _pc = subprocess.call([sys.executable, os.path.join(os.path.dirname(__file__), 'precheck.py'),
                           '--data', a.data, '--quiet'])
    if _pc == 2 and not a.force:
        print('\nDỪNG — còn dữ liệu quét bù được. Chạy các lệnh trên rồi dựng lại.')
        print(f'  python3 {os.path.join(os.path.dirname(__file__), "precheck.py")} '
              f'--data {a.data} --fix     # tự chạy')
        print('Biết rõ vì sao không quét được thì thêm --force và ghi lý do vào báo cáo.')
        sys.exit(2)
    if _pc == 2 and a.force:
        print('\n--force: dựng báo cáo dù còn chỗ quét bù. Phải ghi rõ lý do trong báo cáo.\n')
META = json.load(open(f'{a.data}/meta.json')); ME = META['domain']
PRE = a.prefix or META['domain'].split('.')[0].split('-')[0][:6]
OUT = project_dir(a.out, ME, a.project or a.prefix)
_FA_LOCAL = os.path.expanduser(os.environ.get('FA_CSS_PATH', ''))
FA = (os.path.relpath(_FA_LOCAL, OUT) if _FA_LOCAL and os.path.exists(_FA_LOCAL)
      else 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css')
KW = json.load(open(f'{a.data}/kw.json'))
P = {clean(p['url']): p for p in json.load(open(f'{a.data}/pages.json'))}
JS = {u for u, p in P.items() if is_js_rendered(p)}
CLU = json.load(open(f'{a.data}/clusters.json'))['clusters']
GOALS = {}
for _x in a.goals.split(','):
    if '=' in _x:
        _k, _v = _x.split('='); GOALS[_k.strip()] = int(_v)
MARKS = [m for m in ('top3', 'top5', 'top10') if m in GOALS] or ['top5', 'top10']
CUT = {'top3': 3, 'top5': 5, 'top10': 10}
def _load(p, d=None):
    return json.load(open(p)) if os.path.exists(p) else d
GSC = _load(f'{a.data}/gsc_analysis.json')
QP_ = _load(f'{a.data}/gsc_qp.json') or []
UST = _load(f'{a.data}/url_status.json') or {}
_CODE = {clean(u): v.get('status') for u, v in UST.items()}
for _u, _p in P.items():
    _CODE.setdefault(_u, _p.get('code'))
_BYQ = collections.defaultdict(collections.Counter)
for _r in QP_:
    _BYQ[nrm(_r['keys'][0])][clean(_r['keys'][1])] += _r['impressions']
_HOME = {f'https://{ME}', f'https://{ME}/', f'https://www.{ME}', f'https://www.{ME}/'}
_PRICE = re.compile(r'(\d[\d.,]{4,}\s*(?:₫|đ\b|vnđ|vnd)|giá bán|thêm vào giỏ|mua ngay|liên hệ báo giá|giỏ hàng)', re.I)
_SELL = {u for u, pg in P.items() if len(_PRICE.findall(pg.get('text', ''))) >= 3}


_BASE_CACHE = {}
def _url_base():
    """Suy tiền tố đường dẫn từ chính URL nội bộ đã đo, không hard-code."""
    if 'v' in _BASE_CACHE: return _BASE_CACHE['v']
    import collections
    pref = collections.Counter()
    for u in list(_CODE.keys()):
        m = re.match(r'https?://[^/]+(/[^/]+)/', u)
        if m: pref[m.group(1)] += 1
    _BASE_CACHE['v'] = (pref.most_common(1)[0][0] + '/') if pref else '/'
    return _BASE_CACHE['v']

def _commercial(rows):
    sh_ = []
    for r in rows:
        riv = [clean(u) for pp, d, u in r['serp'] if pp <= 10 and d != ME and d not in SOCIAL and clean(u) in P]
        if len(riv) >= 5:
            sh_.append(sum(1 for u in riv if u in _SELL) / len(riv))
    return (sum(sh_) / len(sh_)) if sh_ else 0


def pick_target(c, rows):
    rank, best = collections.Counter(), {}
    for r in rows:
        for u in {clean(x) for _p, x in r['allmine']}:
            if u in _HOME:
                continue
            rank[u] += 1
            best[u] = min([best.get(u, 999)] + [_p for _p, x in r['allmine'] if clean(x) == u])
    gsc = collections.Counter()
    for r in rows:
        for u, i in _BYQ.get(nrm(r['kw']), {}).items():
            if u not in _HOME:
                gsc[u] += i
    if rank:
        u = max(rank, key=lambda x: (rank[x], -best[x], gsc[x]))
        extra = len({clean(r['url']) for r in rows if r['url'] and clean(r['url']) != u})
        why = f'đang xếp hạng {rank[u]}/{len(rows)} từ khoá của cụm, vị trí tốt nhất {best[u]}'
        if extra:
            why += f'. Gộp {extra} URL nội bộ còn lại về đây rồi 301'
        return u, 'GIỮ', why
    live = {u: i for u, i in gsc.items() if _CODE.get(u) != 404 and i >= 10}
    if live:
        u = max(live, key=lambda x: live[x])
        return u, 'TỐI ƯU', f'trang đã tồn tại và nhận {live[u]:,} hiển thị nhưng chưa lọt top 99 — tối ưu trang này, không viết trang mới'
    dead = {u: i for u, i in gsc.items() if _CODE.get(u) == 404}
    if dead:
        u = max(dead, key=lambda x: dead[x])
        return u, 'KHÔI PHỤC', f'URL đang trả 404 nhưng còn {dead[u]:,} hiển thị — khôi phục nội dung hoặc 301'
    _cm = _commercial(rows) >= 0.6
    base = _url_base()
    tail = slugify(c['name'], maxwords=7)
    return f'https://{ME}{base}{tail}', 'TẠO MỚI', 'đã đối chiếu toàn bộ trang có hiển thị trên Search Console, chưa trang nào phục vụ cụm này'
PERKW = {r['kw']: r for r in (_load(f'{a.data}/perkw.json') or [])}
TECH = {clean(r['url']): r for r in (_load(f'{a.data}/tech.json') or []) if not r.get('error')}
CSS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'report.css'), encoding='utf-8').read()
CON = {}
if a.content and os.path.exists(a.content):
    ns = {}
    exec(open(a.content, encoding='utf-8').read(), ns)
    CON = ns.get('C', {})

def esc(s): return html.escape(str(s), quote=False)
def _key(x): return re.sub(r'\s+', ' ', str(x)).strip().lower()
CONN = {_key(k): v for k, v in CON.items() if not str(k).startswith('__')}
_USED = set()
def sh(u): return u.replace(f'https://www.{ME}', '').replace(f'https://{ME}', '').replace('https://', '') or '/'
CTX = dict(me=ME, pages=P, perkw=PERKW, tech=TECH, js=JS, sh=sh,
           url_status=_load(f'{a.data}/url_status.json') or {},
           index_status=_load(f'{a.data}/index_status.json') or {},
           gsc=(GSC or {}).get('by_cluster'))
pos = {r['kw']: r for r in KW}

def kw_table(rows):
    o = ['<div class="tblwrap"><table><thead><tr><th style="width:30%">Từ khoá</th>'
         f'<th class="num">{META["first"][5:]}</th><th class="num">{META["last"][5:]}</th>'
         '<th class="num">Thay đổi</th><th class="num">URL nội bộ<br>cùng ra</th>'
         '<th>URL đang xếp hạng</th><th>Top 3 đối thủ</th></tr></thead><tbody>']
    for r in sorted(rows, key=lambda x: (x['pos'] or 999, x['kw'])):
        d = (r['pos0'] or 101) - (r['pos'] or 101)
        dc = f'<span class="up">+{d}</span>' if d > 0 else (f'<span class="down">{d}</span>' if d < 0 else '<span class="flat">0</span>')
        cls = 'r3' if r['pos'] and r['pos'] <= 3 else 'r10' if r['pos'] and r['pos'] <= 10 else \
              'r20' if r['pos'] and r['pos'] <= 20 else 'r50' if r['pos'] and r['pos'] <= 50 else 'rx'
        t3 = ' · '.join(x[1] for x in r['serp'][:3] if x[1] != ME) or '—'
        nu = r['nurl']
        nus = f'<b class="warnnum">{nu}</b>' if nu >= 3 else (f'<span class="midnum">{nu}</span>' if nu == 2 else str(nu))
        o.append(f'<tr class="{cls}"><td>{esc(r["kw"])}</td><td class="num">{r["pos0"] or "—"}</td>'
                 f'<td class="num"><b>{r["pos"] or "—"}</b></td><td class="num">{dc}</td>'
                 f'<td class="num">{nus}</td><td class="mono">{esc(sh(r["url"]) if r["url"] else "—")}</td>'
                 f'<td class="mono small">{esc(t3)}</td></tr>')
    return '\n'.join(o) + '</tbody></table></div>'

def page(title, body, crumb=''):
    return (f'<!DOCTYPE html>\n<html lang="vi">\n<head>\n<meta charset="UTF-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'<title>{esc(title)}</title>\n'
            f'<link rel="stylesheet" href="{FA}">\n'
            f'<style>\n{CSS}\n</style>\n</head>\n<body>\n<div class="wrap">\n{crumb}{body}\n</div>\n</body>\n</html>')

_VT = {'GIỮ': 't-keep', 'TỐI ƯU': 't-fix', 'KHÔI PHỤC': 't-gap', 'TẠO MỚI': 't-new'}
TOT = len(KW)
n = lambda lo, hi: sum(1 for r in KW if r['pos'] and lo <= r['pos'] <= hi)
files = []
GAP = []
_ROWS = {c['name']: [pos[k] for k in c['kws'] if k in pos] for c in CLU}
_TGT = {c['name']: pick_target(c, _ROWS[c['name']]) for c in CLU}
_TGTOWNER = {}
for _cn, (_u, _v, _w) in _TGT.items():
    _TGTOWNER.setdefault(clean(_u), []).append(_cn)
_URLCL = collections.defaultdict(set)
_URLKW = collections.defaultdict(collections.Counter)
for _cn, _rs in _ROWS.items():
    for _r in _rs:
        for _u in {clean(x) for _p, x in _r['allmine']}:
            _URLCL[_u].add(_cn)
            _URLKW[_u][_cn] += 1


def cannib_block(cname, rows, tgt, verd):
    """URL nội bộ đang tranh nhau trong cụm và hướng xử lý từng URL."""
    tgt = clean(tgt)
    info = {}
    for r in rows:
        for u in {clean(x) for _p, x in r['allmine']}:
            d = info.setdefault(u, {'kw': 0, 'best': 999, 'imp': 0})
            d['kw'] += 1
            d['best'] = min([d['best']] + [_p for _p, x in r['allmine'] if clean(x) == u])
    for r in rows:
        for u, i in _BYQ.get(nrm(r['kw']), {}).items():
            if u in _HOME:
                continue
            if u in info or i >= 100:
                info.setdefault(u, {'kw': 0, 'best': 999, 'imp': 0})['imp'] += i
    info.pop(tgt, None)
    if not info:
        return ''
    rowsh = []
    for u, d in sorted(info.items(), key=lambda x: (-x[1]['kw'], -x[1]['imp'])):
        other = sorted(_URLCL.get(u, set()) - {cname})
        owner = [x for x in _TGTOWNER.get(u, []) if x != cname]
        if owner:
            here = _URLKW[u].get(cname, 0)
            o1 = max(owner, key=lambda x: _URLKW[u].get(x, 0))
            there = _URLKW[u].get(o1, 0)
            if here > there:
                act, cls = ('XEM LẠI PHÂN VAI', 't-gap')
                note = ('URL này phục vụ <b>' + str(here) + ' từ khoá của cụm đang xem</b> '
                        'nhưng lại đang được chọn làm URL chốt của cụm <b>' + esc(o1) + '</b> '
                        '(chỉ ' + str(there) + ' từ khoá). Chốt lại: để URL này thuộc về cụm đang xem, '
                        'còn cụm kia trỏ về URL chốt của nó.')
            else:
                act, cls = ('KHÔNG 301', 't-brand')
                note = ('Đang là URL chốt của cụm <b>' + esc(o1) + '</b> và phục vụ '
                        + str(there) + ' từ khoá ở đó, nhiều hơn ' + str(here) + ' từ khoá ở cụm này. '
                        'Giữ nguyên URL. Cắt phần nội dung trùng ra khỏi trang rồi trỏ link nội bộ '
                        'sang URL chốt của cụm này.')
        elif other:
            act, cls = ('KIỂM TRƯỚC', 't-fix')
            _oth = ', '.join(f'{x} ({_URLKW[u].get(x, 0)} kw)' for x in
                             sorted(other, key=lambda x: -_URLKW[u].get(x, 0))[:3])
            note = ('Còn đang xếp hạng ở cụm <b>' + esc(_oth) + ('…' if len(other) > 3 else '')
                    + '</b>, trong khi ở cụm này giữ ' + str(d['kw']) + ' từ khoá. '
                    'Chỉ 301 sau khi xác nhận các cụm kia đã có URL chốt khác thay thế được.')
        elif _CODE.get(u) == 404:
            act, cls = ('ĐÃ 404', 't-gap')
            note = 'URL đã chết nhưng còn nhận hiển thị. 301 thẳng về URL chốt.'
        else:
            act, cls = ('301', 't-new')
            note = ('Chuyển phần nội dung riêng sang URL chốt trước, rồi 301. '
                    'Không xoá thẳng: trang này đang giữ '
                    + (f"{d['kw']} từ khoá của cụm" if d['kw'] else f"{d['imp']:,} hiển thị") + '.')
        rowsh.append(f'<tr><td class="mono small">{esc(sh(u))}</td>'
                     f'<td class="num">{d["kw"] or "—"}</td>'
                     f'<td class="num">{d["best"] if d["best"] < 999 else "—"}</td>'
                     f'<td class="num">{d["imp"]:,}</td>'
                     f'<td><span class="tag {cls}">{act}</span></td>'
                     f'<td class="small">{note}</td></tr>')
    n301 = sum(1 for h in rowsh if '>301<' in h or 'ĐÃ 404' in h)
    keep = sum(1 for h in rowsh if 'KHÔNG 301' in h)
    warn = sum(1 for h in rowsh if 'KIỂM TRƯỚC' in h)
    revi = sum(1 for h in rowsh if 'XEM LẠI PHÂN VAI' in h)
    head = (f'<p style="color:var(--text-2)">Ngoài URL chốt, còn <b>{len(rowsh)} URL nội bộ</b> '
            f'đang cùng nhận thứ hạng hoặc hiển thị cho từ khoá của cụm. '
            f'Đề xuất: <b>{n301} URL gộp rồi 301</b>')
    if warn:
        head += f', <b>{warn} URL phải kiểm trước</b>'
    if keep:
        head += f', <b>{keep} URL giữ nguyên</b> vì đang là URL chốt của cụm khác'
    if revi:
        head += f', <b>{revi} URL cần chốt lại phân vai</b>'
    head += '.</p>'
    return ('\n<div class="card" id="trunglap"><h2><i class="fa-solid fa-code-branch"></i> '
            'Xử lý URL trùng lặp đang ăn thịt từ khoá</h2>' + head
            + '<div class="tblwrap"><table><thead><tr><th>URL nội bộ</th>'
            '<th class="num">kw của cụm</th><th class="num">Vị trí tốt nhất</th>'
            '<th class="num">Hiển thị 90 ngày</th><th>Xử lý</th><th>Cách làm</th>'
            '</tr></thead><tbody>' + ''.join(rowsh) + '</tbody></table></div>'
            '<div class="note"><i class="fa-solid fa-triangle-exclamation"></i>'
            'Chuyển nội dung trước, 301 sau. 301 khi chưa gộp nội dung thì mất luôn phần từ khoá '
            'mà trang cũ đang giữ. Sau khi 301, cập nhật link nội bộ đang trỏ vào URL cũ.</div></div>\n')


for c in CLU:
    rows = _ROWS[c['name']]
    _tgt, _verd, _why = _TGT[c['name']]
    t3 = sum(1 for r in rows if r['pos'] and r['pos'] <= 3)
    t5 = sum(1 for r in rows if r['pos'] and r['pos'] <= 5)
    t10 = sum(1 for r in rows if r['pos'] and r['pos'] <= 10)
    g = GSC['by_cluster'].get(c['name'], {}) if GSC else {}
    myurls = collections.Counter(clean(r['url']) for r in rows if r['url']).most_common(6)
    _man = CONN.get(_key(c['name']))
    _man = _man if isinstance(_man, dict) else None
    if _man: _USED.add(_key(c['name']))
    # Bản tự động là mức sàn, luôn có đủ sáu mục. content.py ghi đè từng khoá nếu có.
    _missing_sec = []
    try:
        _gh, _nm, _nt = B.gap_block(CTX, rows, myurls)
        _missing_sec = [(lab, k, n) for lab, k, n in B.gap_missing(CTX, rows, myurls)]
    except Exception:
        _missing_sec = []
    det = AC.build(CTX, rows, myurls, _missing_sec)
    if _man:
        det.update({k: v for k, v in _man.items() if v})
        det['_auto'] = False
    thr_parts = []
    for _mk, _lbl in [(m, f'Ngưỡng lọt {m.replace("top", "top ")}') for m in MARKS]:
        _t = B.threshold_block(CTX, rows, myurls, mark=_mk)
        if _t:
            thr_parts.append(f'<h3 style="margin-top:18px">{_lbl}</h3>' + _t)
    thr = ''.join(thr_parts)
    gap_html, n_miss, n_top = B.gap_block(CTX, rows, myurls)
    parts = [B.rival_block(CTX, rows, (det or {}).get('rivals')),
             B.mypages_block(CTX, rows, myurls),
             B.strength_block(CTX, rows, myurls),
             B.weakness_block(CTX, rows, myurls),
             B.density_block(CTX, rows, myurls),
             B.todo_block(CTX, rows, myurls, det, _tgt, _verd, GOALS)]
    if thr or gap_html:
        parts.append('\n<div class="card" id="nguong">\n'
                     '  <h2><i class="fa-solid fa-ruler-horizontal"></i> 8. Ngưỡng lọt top và đối chiếu mục nội dung</h2>\n'
                     '  <p style="color:var(--text-2)">Ngưỡng lấy trên toàn bộ các trang đang nằm trong mốc: '
                     'top 3 lấy vị trí 1–3, top 5 lấy 1–5, top 10 lấy 1–10. Mốc nào dưới 5 trang thì không hiện.</p>\n  ' + thr +
                     f'\n  <h3 style="margin-top:22px">Đối chiếu mục nội dung với {n_top} trang top</h3>\n'
                     f'  <p style="color:var(--text-2)">Có <b>{n_miss} nhóm mục</b> nhiều trang top có mà mình chưa có.</p>\n  '
                     + gap_html + '\n</div>\n')
    if det:
        for num_, icon, title, fn in [(9, 'fa-tags', 'Lớp meta: title, H1, description, URL', B.meta_table),
                                      (10, 'fa-list-tree', 'Outline: giữ gì, sửa gì, thêm gì', B.outline_block),
                                      (11, 'fa-circle-question', 'Bộ FAQ — bắt buộc hiển thị thật', B.faq_table),
                                      (12, 'fa-images', 'Ảnh và tối ưu tải', B.media_block),
                                      (13, 'fa-code', 'Structured data cần sửa', B.schema_table),
                                      (14, 'fa-list-check', 'Checklist triển khai theo đợt', B.checklist_table)]:
            key = {9: 'meta', 10: 'outline', 11: 'faq', 12: 'media',
                   13: 'schema', 14: 'checklist'}[num_]
            if key not in det: continue
            parts.append(f'\n<div class="card" id="{key}">\n  <h2><i class="fa-solid {icon}"></i> '
                         f'{num_}. {title}</h2>\n  ' + fn(det) + '\n</div>\n')
    parts += [B.gsc_block(CTX, c['name'], c.get('cid') or c.get('slug')), B.content_block(CTX, rows, myurls), B.tech_block(CTX, rows, myurls)]
    extra = ''.join(p for p in parts if p)
    body = (f'<div class="head"><h1>{esc(c["name"])}</h1>'
            f'<p class="sub">{len(rows)} từ khoá · thứ hạng đo ngày {META["last"]} từ file check top '
            f'(độ sâu top {META["depth"]}) · số liệu nội dung từ crawl HTML thô</p>'
            f'<div class="metagrid">'
            + ''.join(
                f'<div class="metabox"><div class="k">{_m.replace("top", "Top ")}'
                + (f' · mục tiêu {GOALS[_m]}%' if _m in GOALS else '')
                + f'</div><div class="v">{_c}/{len(rows)} = {_c*100//max(len(rows),1)}%'
                + ((' · <b class="warnnum">cần thêm '
                    + str(max(0, -(-len(rows) * GOALS[_m] // 100) - _c)) + '</b>')
                   if _m in GOALS and max(0, -(-len(rows) * GOALS[_m] // 100) - _c) else
                   (' · <b>đã đạt</b>' if _m in GOALS else ''))
                + '</div></div>'
                for _m, _c in ((_m, sum(1 for r in rows if r['pos'] and r['pos'] <= CUT[_m])) for _m in MARKS))
            +
            f'<div class="metabox"><div class="k">Bị tranh chấp nội bộ</div><div class="v">'
            f'{sum(1 for r in rows if r["nurl"]>=2)}/{len(rows)} theo file check top</div></div>'
            f'<div class="metabox"><div class="k">Hiển thị 90 ngày</div><div class="v">'
            f'{g.get("imp","—")} · {g.get("clicks","—")} click</div></div></div></div>'
            + B.clustergap_block(CTX, rows, GOALS, CUT)
            + f'<div class="card" id="urlchot"><h2><i class="fa-solid fa-location-crosshairs"></i> '
            f'URL chốt của cụm</h2><div class="issue"><div class="ihead">'
            f'<span class="tag {_VT.get(_verd, "t-keep")}">{_verd}</span>'
            f'<span class="iname mono">{esc(sh(_tgt))}</span></div>'
            f'<div class="ibody">{esc(_why)}. Mọi việc tối ưu của cụm dồn vào đúng URL này; '
            f'không tạo thêm trang thứ hai cho cùng cụm.</div></div></div>'
            + cannib_block(c['name'], rows, _tgt, _verd)
            + f'<div class="card"><h2><i class="fa-solid fa-key"></i> 1. Danh sách đầy đủ từ khoá</h2>{kw_table(rows)}</div>'
            + extra)
    fn = f'{PRE}-{c["slug"]}.html' if len(rows) >= a.min_file else None
    if fn:
        open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(
            page(f'{c["name"]} — {ME}', body,
                 f'<p class="crumb"><a href="{PRE}-tong-hop.html">Tổng hợp {TOT} từ khoá</a> › {esc(c["name"])}</p>'))
    _mu = collections.Counter(sh(r['url']) for r in rows if r['url']).most_common()
    _lead = (_mu[0][0] + (f' + {len(_mu)-1} URL khác' if len(_mu) > 1 else '')) if _mu else '—'
    if fn:
        files.append(fn)
    _band = lambda lo, hi: sum(1 for r in rows if r['pos'] and lo <= r['pos'] <= hi)
    GAP.append(dict(fn=fn, name=c['name'], n=len(rows),
                    cnt={m: sum(1 for r in rows if r['pos'] and r['pos'] <= CUT[m]) for m in MARKS},
                    b45=_band(4, 5), b6=_band(6, 10), b11=_band(11, 20), b21=_band(21, 50),
                    b50=sum(1 for r in rows if not r['pos'] or r['pos'] > 50),
                    url=_lead, tgt=_tgt, verd=_verd, why=_why))

# Mọi từ khoá đều nằm trong một cụm — cluster_serp.py bảo đảm bằng assert.
_orph = json.load(open(f'{a.data}/clusters.json')).get('orphan') or []
if _orph:
    print(f'CẢNH BÁO: {len(_orph)} từ khoá không thuộc cụm nào. Chạy lại cluster_serp.py '
          f'bản mới — mọi từ khoá phải được phân cụm.')


# Dữ liệu cho file tổng hợp — gom một lần, mọi khối trong overview.py đọc từ đây.
OVCTX = dict(me=ME, kw=KW, tot=TOT, goals=GOALS, marks=MARKS, cut=CUT, pages=P, perkw=PERKW,
             tech=TECH, js=JS, sh=sh, clean=clean, nrm=nrm, social=SOCIAL, vt=_VT,
             url_status=UST, index_status=_load(f'{a.data}/index_status.json') or {},
             gsc_detail=(GSC or {}).get('detail') or {}, byq=_BYQ, code=_CODE, sell=_SELL,
             gap=GAP, clusters=CLU, rows_by_cluster=_ROWS, meta=META)


def _gap_table():
    if not GAP or not GOALS:
        return ''
    rows_ = sorted(GAP, key=lambda g: -sum(max(0, -(-g['n'] * GOALS[m] // 100) - g['cnt'][m]) for m in MARKS if m in GOALS))
    hdr = ''.join(f'<th class="num">Top {CUT[m]}</th><th class="num">%</th>'
                  f'<th class="num">Cần thêm<br><span class="small">để đạt {GOALS[m]}%</span></th>'
                  for m in MARKS if m in GOALS)
    o = ['<div class="card" id="gapnhom"><h2><i class="fa-solid fa-bullseye-arrow"></i> '
         '7. Khoảng cách tới mục tiêu theo từng nhóm từ khoá</h2>',
         f'<p style="color:var(--text-2)">Toàn bộ {TOT} từ khoá được chia thành {len(CLU)} cụm theo SERP, '
         f'không bỏ sót từ khoá nào. Cột <b>cần thêm</b> là số từ khoá '
         'phải đẩy vào mốc đó để chính nhóm này đạt mục tiêu. Cột kho là nguồn để lấy: '
         'vị trí càng gần thì chuyển đổi càng rẻ.</p>',
         '<div class="tblwrap"><table><thead><tr><th>Nhóm từ khoá</th><th class="num">Số kw</th>'
         + hdr + '<th class="num">6–10</th><th class="num">11–20</th><th class="num">21–50</th>'
         '<th class="num">&gt;50</th><th>URL chốt đề xuất</th></tr></thead><tbody>']
    tot_need = {m: 0 for m in MARKS}
    for g in rows_:
        cells = ''
        for m in MARKS:
            if m not in GOALS:
                continue
            c_, pc = g['cnt'][m], g['cnt'][m] * 100 // max(g['n'], 1)
            need = max(0, -(-g['n'] * GOALS[m] // 100) - c_)
            tot_need[m] += need
            cls = 'top' if pc >= GOALS[m] else 'zero'
            nd = '<b>0</b>' if need == 0 else f'<b class="warnnum">{need}</b>'
            cells += f'<td class="num">{c_}</td><td class="num {cls}">{pc}%</td><td class="num">{nd}</td>'
        nm = (f'<a href="{g["fn"]}">{esc(g["name"])}</a>' if g['fn'] else esc(g['name']))
        o.append(f'<tr><td>{nm}</td><td class="num">{g["n"]}</td>{cells}'
                 f'<td class="num">{g["b6"]}</td><td class="num">{g["b11"]}</td>'
                 f'<td class="num">{g["b21"]}</td><td class="num">{g["b50"]}</td>'
                 + f'<td><span class="tag {_VT.get(g["verd"], "t-keep")}">{g["verd"]}</span> '
                 + f'<span class="mono small">{esc(sh(g["tgt"]))}</span>'
                 + f'<div class="small" style="color:var(--text-3)">{esc(g["why"])}</div></td></tr>')
    tcells = ''
    for m in MARKS:
        if m not in GOALS:
            continue
        c_ = n(1, CUT[m])
        tcells += (f'<td class="num"><b>{c_}</b></td><td class="num"><b>{c_*100//TOT}%</b></td>'
                   f'<td class="num"><b>{tot_need[m]}</b></td>')
    o.append(f'<tr style="background:var(--surface-2)"><td><b>Cộng toàn bộ</b></td>'
             f'<td class="num"><b>{TOT}</b></td>{tcells}'
             f'<td class="num"><b>{sum(g["b6"] for g in GAP)}</b></td>'
             f'<td class="num"><b>{sum(g["b11"] for g in GAP)}</b></td>'
             f'<td class="num"><b>{sum(g["b21"] for g in GAP)}</b></td>'
             f'<td class="num"><b>{sum(g["b50"] for g in GAP)}</b></td><td></td></tr>')
    o.append('</tbody></table></div>')
    note = []
    for m in MARKS:
        if m not in GOALS:
            continue
        glob_need = max(0, round(TOT * GOALS[m] / 100) - n(1, CUT[m]))
        note.append(f'mốc top {CUT[m]}: cộng dồn từng nhóm cần <b>{tot_need[m]}</b> từ khoá, '
                    f'trong khi tính trên toàn bộ chỉ cần <b>{glob_need}</b>')
    o.append('<div class="note"><i class="fa-solid fa-circle-info"></i><b>Hai con số này khác nhau và đều đúng.</b> '
             + ' · '.join(note) + '. Cộng dồn từng nhóm luôn cao hơn vì nhóm đã vượt mục tiêu không bù được cho nhóm '
             'chưa đạt. Dùng con số toàn bộ để cam kết, dùng con số từng nhóm để giao việc.</div>')
    o.append('</div>')
    return ''.join(o)



body = (f'<div class="head"><h1>Đánh giá dự án — {esc(ME)}</h1>'
        f'<p class="sub">{TOT} từ khoá · thứ hạng ngày {META["last"]}, độ sâu top {META["depth"]} · '
        f'{len(P)} trang đo được, trong đó {len(JS)} trang render JavaScript đã loại khỏi bảng so sánh</p>'
        f'<div class="metagrid">'
        + ''.join(
            f'<div class="metabox"><div class="k">{_m.replace("top", "Top ")}'
            + (f' · mục tiêu {GOALS[_m]}%' if _m in GOALS else '')
            + f'</div><div class="v">{n(1, CUT[_m])} = {n(1, CUT[_m])*100//TOT}%'
            + (f' · thiếu {max(0, round(TOT*GOALS[_m]/100) - n(1, CUT[_m]))} kw' if _m in GOALS else '')
            + '</div></div>' for _m in MARKS)
        +
        f'<div class="metabox"><div class="k">Số cụm</div><div class="v">{len(CLU)}</div></div></div></div>'
        + OV.render(OVCTX) + _gap_table() + CON.get('__tong_hop__', ''))
open(os.path.join(OUT, f'{PRE}-tong-hop.html'), 'w', encoding='utf-8').write(page(f'Đánh giá dự án — {ME}', body))
print(f"{len(files)+1} file tại {OUT}:")
print(f"   {PRE}-tong-hop.html")
for g in GAP:
    mark = '  ' if g['fn'] else '  (chỉ vào bảng) '
    print(f"   {(g['fn'] or '—'):44s} {g['n']:3d} kw ·{mark}"
          + " · ".join(f"{m} {g['cnt'][m]:3d}" for m in MARKS) + f" · {g['name']}")
_unused = [k for k in CONN if k not in _USED]
if _unused:
    print(f"\nCẢNH BÁO: {len(_unused)} cụm trong content.py không khớp tên cụm nào trong "
          f"clusters.json nên bị bỏ qua hoàn toàn:")
    for k in _unused[:10]: print(f"   {k}")
    print("   Tên cụm phải khớp trường name trong data/clusters.json.")

_KEYS = [('meta', '9 · Lớp meta'), ('outline', '10 · Outline'), ('faq', '11 · FAQ'),
         ('media', '12 · Ảnh'), ('schema', '13 · Structured data'), ('checklist', '14 · Checklist'),
         ('rivals', '2 · Mổ xẻ đối thủ, phần nhận định')]
_miss = collections.Counter()
_nodet = []
for c in CLU:
    d = CONN.get(_key(c['name']))
    if not isinstance(d, dict):
        _nodet.append(c['name']); continue
    for k, lab in _KEYS:
        if k not in d: _miss[lab] += 1
print(f"\n=== PHẦN ĐỊNH TÍNH ===")
print(f"{len(CLU)-len(_nodet)}/{len(CLU)} cụm có phần viết tay bổ sung trong content.py.")
print(f"{len(_nodet)} cụm dùng bản tự động — vẫn đủ 14 mục, mọi số đều đo được, nhưng chưa có "
      f"nhận định của người: mổ xẻ đối thủ, điểm mạnh, điểm yếu.")
print("Bản tự động là MỨC SÀN, không phải bản giao. Với các cụm quan trọng nhất, viết thêm vào")
print("content.py để ghi đè: rivals (nhận định đối thủ), và tinh chỉnh meta/outline/faq nếu cần.")
print("Xem mẫu ở assets/content.example.py, yêu cầu chi tiết ở references/output.md.")

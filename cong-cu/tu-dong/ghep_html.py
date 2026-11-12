"""Ghép số / ngày mới vào ĐÚNG file HTML người dùng gửi (Trang yêu cầu 12/11/2026).

Trang dán HTML của bài (vd bài giá vàng lấy từ CMS) → máy chạy công thức như thường (đọc bài trên web + nguồn giá,
ra bản tô vàng) → bước này so CHỮ của HTML gửi lên với CHỮ của bản mới, tìm các chỗ chỉ khác số / ngày / chữ chiều
(tăng ↔ giảm…) rồi thay đúng các chữ đó ngay trong HTML gửi lên. Thẻ, thuộc tính, khoảng trắng, cấu trúc giữ nguyên
từng ký tự; không thêm tô vàng (HTML mới dán thẳng lên web được). Đoạn nào HTML gửi lên khác bài trên web quá nhiều
(không chỉ là số) thì KHÔNG đụng, ghi vào danh sách "bỏ qua" để người duyệt xem.

Dùng: python3 -I ghep_html.py <html gửi lên> <bai.html bản mới> <html ra> <báo cáo .json>
"""
import difflib
import html
import json
import re
import sys

TOKEN = re.compile(r'&#?\w+;|\d+(?:[.,/:]\d+)*|[^\W\d_]+|[^\w\s]', re.U)
SO = re.compile(r'^\d+(?:[.,/:]\d+)*$')
# chữ được phép đổi cùng với số (chiều tăng/giảm, dấu, ký hiệu mũi tên…)
CHU_DOI = {'tăng', 'giảm', 'đi', 'ngang', 'không', 'đổi', 'nhẹ', 'mạnh', 'lên', 'xuống', 'ổn', 'định', 'giữ', 'nguyên',
           '+', '-', '–', '−', '%', '▲', '▼', '➖', '↑', '↓', '(', ')', ',', '.', '/', 'tháng', 'ngày', 'năm', 'kỳ', 'hạn'}
VANG = re.compile(r'<span[^>]*background-color:\s*#ffff00[^>]*>(.*?)</span>', re.S | re.I)


def bo_vang(h):
    """Bỏ các thẻ tô vàng của bản mới (giữ chữ bên trong), lặp vì có thẻ lồng."""
    while True:
        h2 = VANG.sub(r'\1', h)
        if h2 == h:
            return h
        h = h2


def ma_token(t):
    """Khóa so sánh: giải mã &nbsp;…, bỏ khoảng trắng; rỗng = bỏ qua khi so."""
    return html.unescape(t).strip().lower()


def tach(h, bo_the_ngoai=False):
    """HTML -> danh sách token chữ [(khóa, đoạn, đầu, cuối)] (đoạn = chỉ số phần chữ giữa các thẻ)."""
    if bo_the_ngoai:
        h = re.sub(r'<(script|style|head)\b.*?</\1>', ' ', h, flags=re.S | re.I)
    phan = re.split(r'(<[^>]*>)', h)
    tok = []
    for i, p in enumerate(phan):
        if p.startswith('<'):
            continue
        for m in TOKEN.finditer(p):
            k = ma_token(m.group(0))
            if k:
                tok.append((k, i, m.start(), m.end()))
    return phan, tok


NGAY = re.compile(r'^(\d{1,2})/(\d{1,2})/(\d{4})$')


def doi_duoc(cu, moi):
    """Một cụm khác nhau (khác độ dài) có phải chỉ là số / ngày / chữ chiều không."""
    if not cu or not moi or len(cu) > 12 or len(moi) > 12:
        return False
    if not any(SO.match(t) for t in moi):
        return False
    return all(SO.match(t) or t in CHU_DOI for t in cu + moi)


def dang(t):
    """Kiểu viết của số: chữ số → d, giữ dấu ngăn (13,840,000 → d,d,d; 05/11/2026 → d/d/d; 10,5 → d,d)."""
    return re.sub(r'\d+', 'd', t)


def giu_kieu(cu, moi):
    """Ngày mới viết theo kiểu ngày cũ của HTML gửi lên (có / không số 0 đầu)."""
    a, b = NGAY.match(cu), NGAY.match(moi)
    if not (a and b):
        return moi
    return '/'.join(('%02d' % int(y)) if len(x) == 2 else str(int(y))
                    for x, y in zip(a.groups()[:2], b.groups()[:2])) + '/' + b.group(3)


def ghep(goc, moi_html):
    phan_g, tok_g = tach(goc)
    phan_m, tok_m = tach(bo_vang(moi_html), bo_the_ngoai=True)
    # dò vị trí với mọi con số coi như "ô số" → bài lệch số vẫn khớp đúng chỗ; rồi mới so giá trị thật
    kg = ['#' if SO.match(t[0]) else t[0] for t in tok_g]
    km = ['#' if SO.match(t[0]) else t[0] for t in tok_m]
    sm = difflib.SequenceMatcher(None, kg, km, autojunk=False)
    doi, bo_qua, sua = [], [], {}               # sua: đoạn -> [(đầu, cuối, chữ mới)]
    raw_g = lambda t: phan_g[t[1]][t[2]:t[3]]
    raw_m = lambda t: phan_m[t[1]][t[2]:t[3]]

    def thay_tung_cai(ag, am):
        cho = []
        for a, b in zip(ag, am):
            if a[0] != b[0]:
                if SO.match(a[0]) and SO.match(b[0]) and dang(a[0]) != dang(b[0]):
                    bo_qua.append({'cu': html.unescape(raw_g(a)), 'moi': html.unescape(raw_m(b)),
                                   'ly_do': 'hai số khác kiểu viết – có thể không cùng một ô'})
                    continue
                moi = giu_kieu(raw_g(a), raw_m(b))
                if moi != raw_g(a):
                    sua.setdefault(a[1], []).append((a[2], a[3], moi))
                    cho.append((html.unescape(raw_g(a)), html.unescape(moi)))
        return cho

    for op, i1, i2, j1, j2 in sm.get_opcodes():
        ag, am = tok_g[i1:i2], tok_m[j1:j2]
        cu, moi = [t[0] for t in ag], [t[0] for t in am]
        chu_cu = ' '.join(html.unescape(raw_g(t)) for t in ag)
        chu_moi = ' '.join(html.unescape(raw_m(t)) for t in am)
        if op == 'equal':                        # cùng chữ, chỉ số khác → thay từng số tại chỗ
            for c, m in thay_tung_cai(ag, am):
                doi.append({'cu': c, 'moi': m})
            continue
        if op != 'replace' or not any(SO.match(t) for t in cu + moi):
            continue
        khac = [(x, y) for x, y in zip(cu, moi) if x != y]
        if len(cu) == len(moi) and len(cu) <= 12 and all((SO.match(x) and SO.match(y)) or (x in CHU_DOI and y in CHU_DOI)
                                                       for x, y in khac):
            cho = thay_tung_cai(ag, am)         # vd "tăng 50" → "giảm 30"
            if cho:
                doi.append({'cu': chu_cu, 'moi': chu_moi})
        elif doi_duoc(cu, moi) and len({t[1] for t in ag}) == 1:
            if len({t[1] for t in am}) == 1:
                moi_txt = phan_m[am[0][1]][am[0][2]:am[-1][3]]
            else:
                moi_txt = ' '.join(raw_m(t) for t in am)
            sua.setdefault(ag[0][1], []).append((ag[0][2], ag[-1][3], moi_txt))
            doi.append({'cu': chu_cu, 'moi': chu_moi})
        else:
            bo_qua.append({'cu': chu_cu[:200], 'moi': chu_moi[:200]})
    for d, ds in sua.items():                    # thay từ cuối đoạn lên để vị trí không lệch
        p = phan_g[d]
        for a, b, t in sorted(ds, reverse=True):
            p = p[:a] + t + p[b:]
        phan_g[d] = p
    return ''.join(phan_g), {'doi': doi, 'bo_qua': bo_qua, 'khop': round(sm.ratio(), 3), 'so_cho_doi': len(doi)}


if __name__ == '__main__':
    goc = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    moi = open(sys.argv[2], encoding='utf-8').read()
    ra, bc = ghep(goc, moi)
    if bc['khop'] < 0.5:
        bc['canh_bao'] = ('HTML gửi lên khác bài trên web quá nhiều (độ khớp %.0f%%) – có thể dán nhầm bài; '
                          'chỉ đổi những chỗ chắc chắn là số.' % (bc['khop'] * 100))
    open(sys.argv[3], 'w', encoding='utf-8').write(ra)
    json.dump(bc, open(sys.argv[4], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('ghép HTML: đổi %d chỗ, bỏ qua %d chỗ, độ khớp %.0f%%' % (bc['so_cho_doi'], len(bc['bo_qua']), bc['khop'] * 100))

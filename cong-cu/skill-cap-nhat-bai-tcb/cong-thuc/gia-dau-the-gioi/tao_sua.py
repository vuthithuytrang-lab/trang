"""Tự lập sua.json cho bài TCB "Cập nhật giá dầu thế giới hôm nay" (techcombank.com/thong-tin/blog/gia-dau-the-gioi).

  --xem  kết quả `cap_nhat.py xem ... bai1`     --gia  gia.json (lay_gia.js: Brent = UKOIL, WTI = USOIL trên TradingView)
  --goc  cap-nhat/tam/bai1.html (bài gốc – lấy lại ngày cũ khi thiếu nguồn)
  --ra   sua.json                                --kiem soát lại sau khi sửa (in "khớp hết")

Bảng: Loại dầu | Giá (USD/thùng) | Thay đổi so với phiên trước — dòng nhận theo tên ("Brent" / "WTI"), ô nhận theo dạng
(ô giá = một con số "111.43"; ô thay đổi = "+1.70 USD (+1.55%)"), không theo vị trí cột.
Số viết theo đúng ô cũ (dấu thập phân, số chữ số lẻ, kiểu dấu trừ). Câu văn có "Brent/WTI … X USD/thùng" cũng được đổi.
Không có mạng, không gọi AI.
"""
import argparse, datetime, html, json, re, sys, unicodedata

TEN = {'brent': 'Dầu Brent', 'wti': 'Dầu WTI'}
SO = r'\d+(?:[.,]\d+)?'
O_DOI = re.compile(r'^([+\-−]?)(' + SO + r') USD \(([+\-−]?)(' + SO + r')%\)$')


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def loai_dau(t):
    t = t.lower()
    co = [k for k, w in (('brent', 'brent'), ('wti', 'wti')) if re.search(r'\b' + w + r'\b', t)]
    return co[0] if len(co) == 1 else None


def doc_xem(path):
    dong, van = [], ''
    for line in open(path, encoding='utf-8'):
        m = re.match(r'\s*\d+\.\s?(.*)$', line.rstrip('\n'))
        if not m:
            continue
        t = m.group(1)
        la_o = t.startswith('| ')
        chu = nfc(t[2:] if la_o else t)
        dong.append((chu, len(van), la_o))
        van += chu + '\n'
    return dong, van


def lan_thu(van, tim, vt):
    n, i = 0, van.find(tim)
    while i != -1 and i <= vt:
        n += 1
        i = van.find(tim, i + 1)
    return n


def viet(x, cu, dau=False, chu_nguon=None):
    """Viết số theo đúng cách số cũ `cu` đang viết (dấu thập phân + số chữ số lẻ). Dùng nguyên chữ số TradingView
    hiển thị (`chu_nguon`) khi đã cùng số chữ số lẻ; trả (chuỗi, có_làm_tròn). dau=True: chỉ phần trị tuyệt đối."""
    m = re.search(r'([.,])(\d+)$', cu)
    le, tp = (len(m.group(2)), m.group(1)) if m else (2, '.')
    if chu_nguon is not None:
        t = chu_nguon.replace('\u2212', '-').replace(',', '').replace('%', '').strip().lstrip('+')
        if dau:
            t = t.lstrip('-')
        mm = re.fullmatch(r'-?\d+(?:\.(\d+))?', t)
        if mm and len(mm.group(1) or '') == le:
            return t.replace('.', tp), False
    return f'{abs(x) if dau else x:.{le}f}'.replace('.', tp), True


def dau_cua(x, cu_dau):
    """Dấu +/- cho mức thay đổi; dấu trừ viết đúng kiểu bài đang dùng (mặc định '-')."""
    if round(x, 6) > 0:
        return '+'
    if round(x, 6) < 0:
        return cu_dau if cu_dau in ('-', '−') else '-'
    return ''


def ngay_goc(path):
    """Ngày dd/mm/yyyy xuất hiện nhiều nhất trong bài gốc (ngày bài đang ghi trước khi `dung` đổi)."""
    if not path or path == '-':
        return None
    try:
        t = html.unescape(re.sub(r'<[^>]+>', ' ', open(path, encoding='utf-8').read()))
    except OSError:
        return None
    ds = re.findall(r'(?<!\d)\d{1,2}/\d{1,2}/\d{4}(?!\d)', t)
    return max(set(ds), key=ds.count) if ds else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--goc')
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    dong, van = doc_xem(a.xem)
    try:
        gia = json.load(open(a.gia, encoding='utf-8'))
    except (OSError, ValueError):
        gia = {}
    gia = {k: gia.get(k) for k in TEN}
    sua, can, lech = [], [], []
    da_lam = set()   # vị trí đã có quy tắc (để không báo trùng ở phần dò số còn sót)

    def them(cu, vt, moi, nguon, ly, tinh=False):
        da_lam.add(vt)
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        x = {'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
             'nguon': nguon, 'ly_do': ly, '_vt': vt}
        if tinh:
            x['tinh_toan'] = True
        sua.append(x)

    def ly_do(g, them_chu=''):
        return (f'{TEN[[k for k in TEN if gia[k] is g][0]]} = {g["ma"]} (TradingView, TVC): giá {g["chu"]["gia"]} USD/thùng, '
                f'thay đổi {g["chu"]["doi"]} ({g["chu"]["doi_pt"]}) so với giá đóng cửa phiên trước'
                f'{" " + str(g["dong_cua_truoc"]) if g.get("dong_cua_truoc") is not None else ""}; '
                f'{g["cap_nhat"]}, lấy lúc {g["lay_luc"][:16].replace("T", " ")} GMT; {g["trang_thai"]}{them_chu}')

    # ---- 1. Bảng giá: dòng "Dầu Brent" / "Dầu WTI" + các ô ngay sau
    co_dong = set()
    for i, (chu, vt, la_o) in enumerate(dong):
        k = loai_dau(chu)
        if la_o or not k or len(chu) > 40:
            continue
        cells, j = [], i + 1
        while j < len(dong) and dong[j][2]:
            cells.append(dong[j]); j += 1
        o_gia = [c for c in cells if re.fullmatch(SO, c[0])]
        o_doi = [c for c in cells if O_DOI.match(c[0])]
        if not (o_gia or o_doi):
            continue
        co_dong.add(k)
        g = gia[k]
        if not g:
            can.append(f'Bảng giá, dòng "{chu}": không đọc được TradingView ({NGUON_URL[k]}) – giữ nguyên giá cũ.')
            for c in cells:
                da_lam.add(c[1])
            continue
        if len(o_gia) != 1 or len(o_doi) != 1 or len(cells) != 2:
            can.append(f'Bảng giá, dòng "{chu}": bảng đổi dạng ({len(cells)} ô: {" | ".join(c[0] for c in cells)}) – '
                       'chỉ cập nhật ô nhận ra được, các ô khác giữ nguyên, cần xem lại.')
        if len(o_gia) == 1:
            c = o_gia[0]
            v, tron = viet(g['gia'], c[0], chu_nguon=g['chu']['gia'])
            them(c[0], c[1], v, g['nguon'], ly_do(g, ' (làm tròn theo số chữ số lẻ của bài)' if tron else ''), tinh=tron)
        if len(o_doi) == 1:
            c = o_doi[0]
            m = O_DOI.match(c[0])
            d1, t1 = viet(g['doi'], m.group(2), True, g['chu']['doi'])
            d2, t2 = viet(g['doi_pt'], m.group(4), True, g['chu']['doi_pt'])
            moi = f'{dau_cua(g["doi"], m.group(1))}{d1} USD ({dau_cua(g["doi_pt"], m.group(3))}{d2}%)'
            them(c[0], c[1], moi, g['nguon'], ly_do(g, ' (làm tròn theo số chữ số lẻ của bài)' if t1 or t2 else ''), tinh=t1 or t2)
        if g.get('canh_bao'):
            can.append(f'{TEN[k]}: số trên TradingView không khớp nhau ({g["canh_bao"]}) – kiểm tra lại trên {g["nguon"]}.')
    for k in TEN:
        if gia[k] and k not in co_dong:
            can.append(f'Không thấy dòng "{TEN[k]}" trong bảng giá của bài (bài có thể đã đổi bố cục) – chưa cập nhật giá {TEN[k]}.')

    # ---- 2. Câu văn: "… Brent/WTI … 111.43 USD/thùng …" (đổi khi trong câu chỉ nhắc đúng 1 loại dầu)
    for chu, vt, la_o in dong:
        if la_o:
            continue
        for m in re.finditer(r'(' + SO + r')(\s*USD/thùng)', chu):
            if vt + m.start() in da_lam:
                continue
            k = loai_dau(chu[max(0, m.start() - 80):m.start()])
            truoc = chu[max(0, m.start() - 12):m.start()]
            if k and gia[k] and not re.search(r'(tăng|giảm|thêm|bớt|khoảng|từ|đến)\s*$', truoc):
                v, tron = viet(gia[k]['gia'], m.group(1), chu_nguon=gia[k]['chu']['gia'])
                them(m.group(0), vt + m.start(), v + m.group(2), gia[k]['nguon'],
                     ly_do(gia[k], ' (làm tròn theo số chữ số lẻ của bài)' if tron else ''), tinh=tron)
            else:
                da_lam.add(vt + m.start())
                can.append(f'Câu văn có giá dầu chưa có quy tắc tự cập nhật – giữ nguyên, cần xem lại: "{chu[max(0, m.start() - 60):m.end() + 20]}"')

    # ---- 3. Ngày: `dung` đã đổi mọi ngày sang ngày mai. Thiếu nguồn -> đưa ngày về ngày gốc (không ghi ngày mới cho giá cũ)
    thieu = [TEN[k] for k in TEN if not gia[k]]
    if thieu:
        cu = ngay_goc(a.goc)
        mai = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))) + datetime.timedelta(days=1)
        moi = f'{mai.day:02d}/{mai.month:02d}/{mai.year}'
        if cu and cu != moi:
            vt_ngay = [vt + m.start() for chu, vt, _ in dong for m in re.finditer(re.escape(moi), chu)]
            if vt_ngay:
                them(moi, vt_ngay[0], cu, '', 'thiếu nguồn giá dầu – giữ ngày gốc của bài')
                sua[-1]['lan'] = 'tat_ca'          # mọi chỗ ngày mới (kể cả tiêu đề) về ngày gốc
            can.append(f'Không đọc được giá {" và ".join(thieu)} – giữ nguyên giá cũ và giữ ngày gốc {cu} của bài '
                       '(chỗ ngày vẫn tô vàng nhưng là ngày cũ), cần chạy lại khi TradingView vào được.')
        else:
            can.append(f'Không đọc được giá {" và ".join(thieu)} – giữ nguyên giá cũ; ngày trong bài vẫn là {cu or "?"}, cần xem lại.')
    else:
        g = gia['brent']
        can.append(f'Giá Brent/WTI là giá giao dịch trong phiên trên TradingView ({g["cap_nhat"]}, lấy lúc '
                   f'{g["lay_luc"][:16].replace("T", " ")} GMT, {g["trang_thai"].lower()}) nên còn thay đổi; '
                   'bài ghi ngày hôm sau theo quy tắc ghi ngày.')
    sapo = [vt for chu, vt, la_o in dong if not la_o and re.search(r'diễn biến \d+ ngày', chu)]
    if sapo and not re.search(r'\d+ ngày', van[sapo[0]:].split('\n', 1)[1]):
        can.append('Đoạn mô tả đầu bài (sapo) nhắc "diễn biến 5 ngày gần đây" nhưng bài không có bảng 5 ngày – giữ nguyên câu chữ, không thêm bảng.')

    if a.kiem:
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} chỗ lệch: ' + '; '.join(lech))
        sys.exit(1 if lech else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for x in sua:
        print('  ', x['tim'][:70], '→', x['thay'][:70])
    for c in can:
        print('  cần duyệt:', c)


NGUON_URL = {'brent': 'https://vn.tradingview.com/symbols/UKOIL/', 'wti': 'https://vn.tradingview.com/symbols/USOIL/'}

if __name__ == '__main__':
    main()

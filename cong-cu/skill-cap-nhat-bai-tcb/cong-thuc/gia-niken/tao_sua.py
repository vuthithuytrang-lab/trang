"""Tự lập sua.json cho bài TCB "Giá Niken hôm nay" (không dùng mạng, không dùng AI).

  --xem  kết quả `cap_nhat.py xem ... bai1`      --gia  cap-nhat/gia.json (lay_gia.py)
  --goc  cap-nhat/tam/bai1.html (chưa dùng – giữ cho đủ khung chung)
  --ra   sua.json                                 --kiem soát lại sau khi sửa (in "Soát: khớp hết")

Mọi con số viết vào bài lấy THẲNG từ gia.json (Westmetall, LME Nickel 3-month); không đoán. Chỉ đổi số và ngày, giữ nguyên câu chữ.
  1) Bảng "Ngày giao dịch | Giá đóng cửa (USD/tấn) | Thay đổi so với phiên trước (USD/tấn)": N dòng = N phiên mới nhất
     (dòng 1 = mới nhất …): ngày, giá (dấu nghìn ",", 2 số lẻ), thay đổi (có dấu +/-, 2 số lẻ) = giá phiên đó trừ giá phiên liền trước
     trên nguồn. Nhận bảng theo tiêu đề cột, dòng theo ô ngày; chịu được ô sai dạng ("16.162.00") và dòng bị gộp thành 1 dòng chữ.
  2) Câu "… đóng cửa ở mức X USD/tấn, giảm/tăng Y USD/tấn, tương đương Z% so với phiên trước": X, Y = giá và mức thay đổi của phiên
     mới nhất (khớp dòng 1 của bảng); Z = |Y| / giá phiên trước x 100 (số TÍNH RA từ 2 số nguồn → tự ghi cần duyệt); chữ giảm/tăng đổi theo dấu của Y.
  3) Lưới an toàn: số giá còn sót (không phải số nguồn) → cần duyệt "SỐ GIÁ CHƯA CẬP NHẬT …"; tỷ lệ % (vd Indonesia 67%) giữ nguyên + 1 mục cần duyệt.
"""
import argparse, json, re, sys, unicodedata

RE_DATE = re.compile(r'^\d{1,2}/\d{1,2}/\d{4}$')
RE_CAU = re.compile(r'(đóng cửa ở mức )(\d[\d.,]*)( USD/tấn, )(tăng|giảm)( )(\d[\d.,]*)( USD/tấn, tương đương )(\d[\d.,]*)(% so với phiên trước)')
RE_GIA = re.compile(r'\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?(?=\s*USD)|(?<=USD )\d[\d.,]*|(?<=\$)\d[\d.,]*')
RE_PT = re.compile(r'\d+(?:[.,]\d+)?\s*%')


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


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


def f2(x):
    return f'{x:,.2f}'


def fd(x):
    return f'{x:+,.2f}'


def cent(s):
    """số chỉ lấy chữ số (chịu được "16.162.00" → 1616200) để so với số nguồn nhân 100"""
    d = re.sub(r'\D', '', s)
    return int(d) if d else None


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
    wm = gia.get('westmetall') or {}
    ls = wm.get('lich_su') or []
    dc = gia.get('doi_chieu')
    sua, can, lech, vung = [], [], [], []          # vung = các khoảng chữ (đầu, cuối) trong `van` đã được công thức xử lý

    def them(cu, vt, moi, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': wm.get('nguon', ''), 'ly_do': ly, '_vt': vt})

    if not ls:
        can.append('Westmetall (giá LME Nickel 3-month) không đọc được – giữ nguyên toàn bộ bảng giá và câu giá cũ; cần chạy lại hoặc cập nhật tay.')

    # 1) Bảng 5 phiên
    n_hang = 0
    for i, (chu, vt, la_o) in enumerate(dong):
        if la_o or not chu.startswith('Ngày') or i + 2 >= len(dong):
            continue
        if not (dong[i + 1][2] and dong[i + 1][0].startswith('Giá') and dong[i + 2][2] and dong[i + 2][0].startswith('Thay đổi')):
            continue
        hang, j = [], i + 3
        while j < len(dong):
            c, v, o = dong[j]
            m = re.fullmatch(r'(\d{1,2}/\d{1,2}/\d{4}) \| ([\d.,]+) \| ([+\-−]?[\d.,]+) \|?', c.strip()) if not o else None
            if m:                                          # vài dòng bị gộp thành 1 dòng chữ "05/11/2026 | 16.162.00 | -171.50"
                hang.append(tuple((m.group(g), v + m.start(g), True) for g in (1, 2, 3)))
                j += 1
            elif j + 2 < len(dong) and not o and RE_DATE.match(c) and dong[j + 1][2] and dong[j + 2][2]:
                hang.append((dong[j], dong[j + 1], dong[j + 2]))
                j += 3
            else:
                break
        n_hang = len(hang)
        for k, (o_ngay, o_gia, o_doi) in enumerate(hang):
            for o in (o_ngay, o_gia, o_doi):
                vung.append((o[1], o[1] + len(o[0])))
            if k >= len(ls):
                if ls:
                    can.append(f'Bảng giá, dòng {k + 1} ({o_ngay[0]} {o_gia[0]} {o_doi[0]}): nguồn không đủ phiên – giữ nguyên dòng này.')
                continue
            h = ls[k]
            ly = f'Westmetall, LME Nickel 3-month, phiên {h["ngay"]}: {h["chu_nguon"]}; thay đổi = giá phiên này trừ giá phiên liền trước'
            them(o_ngay[0], o_ngay[1], h['ngay'], ly)
            them(o_gia[0], o_gia[1], f2(h['gia']), ly)
            them(o_doi[0], o_doi[1], fd(h['thay_doi']), ly)
        if hang and ls:
            can.append(f'Bảng giá: {len(hang)} dòng = {len(hang)} phiên mới nhất trên Westmetall ({", ".join(h["ngay"] for h in ls[:len(hang)])}); '
                       'giá là LME Nickel 3-month (giá chính thức LME, USD/tấn), có thể khác chuỗi "giá đóng cửa hợp đồng tương lai" mà bài ghi trước đó '
                       '(số cũ có lẻ .25/.75) – cần duyệt xem Trang có muốn dùng chuỗi này; phiên mới nhất trên nguồn có thể cũ hơn ngày ghi trong tiêu đề (quy tắc ngày hôm sau).')
    if not n_hang:
        can.append('Không nhận ra bảng "Ngày giao dịch | Giá đóng cửa | Thay đổi so với phiên trước" trong bài – công thức không sửa bảng, cần xem lại.')

    # 2) Câu giá mới nhất
    thay_cau = 0
    for chu, vt, la_o in dong:
        m = RE_CAU.search(chu)
        if not m:
            continue
        thay_cau += 1
        vung.append((vt + m.start(), vt + m.end()))
        if not ls:
            continue
        h, g = ls[0], list(m.groups())
        cu = list(g)
        t = h['thay_doi']
        truoc = h['gia'] - t
        if t == 0 or truoc <= 0:
            can.append(f'Câu giá mới nhất: nguồn ghi giá không đổi so với phiên trước – câu "{cu[3]} {cu[5]} USD/tấn, tương đương {cu[7]}%" '
                       'không viết được đúng dạng, giữ nguyên số mức thay đổi, cần duyệt.')
            g[1] = f'{h["gia"]:,.0f}' if '.' not in cu[1] and float(h['gia']).is_integer() else f2(h['gia'])
        else:
            g[1] = f'{h["gia"]:,.0f}' if re.fullmatch(r'[\d,]+', cu[1]) and float(h['gia']).is_integer() else f2(h['gia'])
            g[3] = 'giảm' if t < 0 else 'tăng'
            g[5] = f2(abs(t))
            g[7] = f'{abs(t) / truoc * 100:.2f}'
            if g[3] != cu[3]:
                can.append(f'Câu giá mới nhất: chữ chỉ chiều đổi "{cu[3]}" → "{g[3]}" theo dấu của mức thay đổi trên nguồn ({fd(t)}) – đọc lại câu.')
        ly = f'Westmetall, LME Nickel 3-month, phiên {h["ngay"]}: {h["chu_nguon"]}'
        e_moi = ''.join(g)
        if e_moi != m.group(0):
            them(m.group(0), vt + m.start(), e_moi, ly + f'; % = |{fd(t)}| / {truoc:,.2f} x 100 (tính ra từ 2 số nguồn)')
            if t != 0 and truoc > 0:
                sua[-1]['tinh_toan'] = True
        can.append(f'Câu giá mới nhất ("{cu[0]}…"): giá {g[1]} và mức thay đổi {g[5]} lấy từ phiên {h["ngay"]}; tỷ lệ {g[7]}% là số tính ra '
                   f'(mức thay đổi / giá phiên trước) – nguồn không có sẵn con số %.')
    if not thay_cau:
        can.append('Không nhận ra câu "… đóng cửa ở mức X USD/tấn, giảm/tăng Y USD/tấn, tương đương Z% so với phiên trước" – giữ nguyên, cần xem lại.')

    # 3) Lưới an toàn: số giá còn sót + tỷ lệ %
    nguon_cent = set()
    for h in ls:
        for v in (h['gia'], abs(h['thay_doi'])):
            nguon_cent.add(round(v * 100))
            nguon_cent.add(round(v) * 100)
    def da_xu_ly(a0, a1):
        return any(a0 < y1 and a1 > y0 for y0, y1 in vung)
    pt = []
    for chu, vt, la_o in dong:
        for m in RE_GIA.finditer(chu):
            if da_xu_ly(vt + m.start(), vt + m.end()):
                continue
            c = cent(m.group(0))
            if c in nguon_cent or c is None or RE_DATE.match(m.group(0)):
                continue
            can.append(f'SỐ GIÁ CHƯA CẬP NHẬT: "…{chu[max(0, m.start() - 40):m.end() + 12]}" – số này không phải số nguồn, công thức không đổi, cần đọc lại và cập nhật tay.')
        for m in RE_PT.finditer(chu):
            if not da_xu_ly(vt + m.start(), vt + m.end()):
                pt.append(f'"{chu[max(0, m.start() - 35):m.end()]}"')
    if pt:
        can.append(f'Tỷ lệ phần trăm trong bài giữ nguyên (không phải giá, nguồn Westmetall không có): {"; ".join(pt)} '
                   '(vd Indonesia ~67% sản lượng theo USGS năm 2025) – cần duyệt nếu Trang muốn đối chiếu lại số năm.')
    if ls and dc and not dc.get('khop'):
        can.append(f'Đối chiếu giá mới nhất: Westmetall {dc["westmetall"]:,.2f} lệch TradingView {dc["tradingview"]:,.2f} tới {dc["lech_phan_tram"]}% – xem lại nguồn.')
    elif ls and not dc:
        can.append('Chưa đối chiếu được giá mới nhất với nguồn thứ hai (TradingView không đọc được) – chỉ có Westmetall.')

    if a.kiem:
        if not ls:
            print('Soát: khớp hết (không có số nguồn nên bài giữ nguyên số cũ)')
            sys.exit(0)
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


if __name__ == '__main__':
    main()

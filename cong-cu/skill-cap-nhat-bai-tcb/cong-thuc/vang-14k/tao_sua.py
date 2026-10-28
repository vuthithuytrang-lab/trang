"""Tự lập sua.json cho bài TCB "Vàng 14K giá hôm nay".

  --xem  kết quả `cap_nhat.py xem ... bai1`   --gia  gia-14k.json (lay_gia_14k.js, VND/chỉ)
  --goc  cap-nhat/tam/bai1.html (bài gốc, để lấy lại ngày của đoạn "Xu hướng")
  --ra   sua.json                              --kiem soát lại sau khi sửa

Bảng: Thương hiệu | Loại vàng 14K | Mua vào | Bán ra — đơn vị TRIỆU VND/LƯỢNG (= VND/chỉ × 10 / 1.000.000),
viết dấu chấm thập phân, bỏ số 0 cuối (73.669, 73.99, 85).
Khoảng giá tóm tắt (2 đoạn) tính trên SJC + PNJ như bài gốc: thấp nhất giá mua – cao nhất giá bán; theo chỉ = /10, làm tròn 2 số lẻ;
chênh lệch mua–bán = thấp nhất – cao nhất của (bán − mua) từng thương hiệu, làm tròn 1 số lẻ.
Mục 2 (ví dụ nhẫn 1.2 chỉ): giá bán tham khảo = cận trên của khoảng tóm tắt (cao nhất giá bán SJC + PNJ, đ/chỉ, đúng số nguồn),
tính lại "Giá trị phần vàng" và "Tổng giá trị"; tiền công / tiền đá là số giả định → giữ nguyên.
Đoạn "Xu hướng": lịch sử giá PNJ Vàng 585 (14K) (khóa "_lich_su_pnj" trong gia-14k.json, giá đóng phiên) → ngày = phiên mới nhất,
chênh so với phiên trước (triệu/lượng), % 7 ngày, % 1 tháng, % so với cùng kỳ; chữ chỉ chiều (giảm/tăng, cao/thấp hơn) đổi theo dấu.
Thiếu lịch sử → như cũ: giữ nguyên số + trả lại ngày gốc, ghi cần duyệt.
"""
import argparse, html, json, re, sys, unicodedata

THUONG_HIEU = {'sjc': 'sjc', 'pnj': 'pnj', 'huy thanh': 'huythanh'}
TOM_TAT = ['sjc', 'pnj']
RE_XH = re.compile(r'(của PNJ ngày )(\d{1,2}/\d{1,2}/\d{4})( )(giảm|tăng)( khoảng )([\d.]+)( triệu VND/lượng so với phiên trước\. '
                   r'Trong 7 ngày gần đây, mức )(giảm|tăng)( khoảng )([\d.]+)(%; trong 1 tháng, mức )(giảm|tăng)( khoảng )([\d.]+)'
                   r'(%\. So với cùng kỳ năm trước, giá vẫn )(cao|thấp)( hơn khoảng )([\d.]+)(%)')
RE_VD = re.compile(r'(Giá vàng 14K bán ra tham khảo: )([\d,]+)( VND / chỉ)')
RE_GT = re.compile(r'(Giá trị phần vàng: )([\d.]+)( chỉ x )([\d,]+)( = )([\d,]+)( VND)')
RE_TONG = re.compile(r'(Tổng giá trị món trang sức: )([\d,]+)( \+ )([\d,]+)( \(tiền công\) \+ )([\d,]+)( \(tiền đá\) = )([\d,]+)( VND)')


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


def gon(x, le):
    s = f'{x:.{le}f}'
    return s.rstrip('0').rstrip('.') if '.' in s else s


def so_le(cu, x):
    """viết x với đúng số chữ số thập phân như số cũ (0.64 → 2 số lẻ, 1.1 → 1 số lẻ)"""
    n = len(cu.split('.')[1]) if '.' in cu else 0
    return f'{x:.{n}f}'


def ngay_goc(path):
    goc = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', open(path, encoding='utf-8').read())))
    mg = re.search(r'của PNJ ngày (\d{1,2}/\d{1,2}/\d{4})', goc)
    return mg.group(1) if mg else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--goc')
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    ap.add_argument('--bo-to-ngay-xu-huong', metavar='BAI_MIN_HTML',
                    help='sau lệnh sua: bỏ tô vàng ở ngày đoạn Xu hướng NẾU ngày đó trùng ngày gốc của bài (--goc) – không phải chỗ mới')
    a = ap.parse_args()
    if a.bo_to_ngay_xu_huong:
        p = a.bo_to_ngay_xu_huong
        h = open(p, encoding='utf-8').read()
        m = re.search(r'của PNJ ngày (<span style="background-color:#ffff00">(?:<span[^>]*>\d+</span>|[/\d])+</span>)', h)
        goc = ngay_goc(a.goc) if a.goc else None
        if m and a.goc and re.sub(r'<[^>]+>', '', m.group(1)) != goc:
            print('Ngày đoạn Xu hướng đã đổi so với bài gốc (', goc, '→', re.sub(r'<[^>]+>', '', m.group(1)), ') – giữ tô vàng')
        elif m:
            sach = re.sub(r'<[^>]+>', '', m.group(1))
            h = h.replace(m.group(0), 'của PNJ ngày ' + sach, 1)
            open(p, 'w', encoding='utf-8').write(h)
            print('Đã bỏ tô vàng ngày', sach)
        else:
            print('Không thấy ngày tô vàng ở đoạn Xu hướng (không cần làm gì)')
        return
    dong, van = doc_xem(a.xem)
    gia = json.load(open(a.gia, encoding='utf-8'))
    sua, can, lech = [], [], []

    def them(cu, vt, moi, nguon, ly, tinh=False):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        x = {'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
             'nguon': nguon, 'ly_do': ly, '_vt': vt}
        if tinh:
            x['tinh_toan'] = True
        sua.append(x)

    luong = {k: (v['mua'] * 10 / 1e6, v['ban'] * 10 / 1e6) for k, v in gia.items() if v and not k.startswith('_')}

    # 1) Bảng giá theo thương hiệu
    for i, (chu, vt, la_o) in enumerate(dong):
        ma = THUONG_HIEU.get(chu.lower())
        if la_o or not ma:
            continue
        cells = []
        j = i + 1
        while j < len(dong) and dong[j][2]:
            cells.append(dong[j]); j += 1
        if len(cells) < 3:
            continue
        if ma not in luong:
            can.append(f'{chu}: không đọc được nguồn – giữ nguyên giá cũ.')
            continue
        g = gia[ma]
        for k, gt in ((1, luong[ma][0]), (2, luong[ma][1])):
            them(cells[k][0], cells[k][1], gon(gt, 3), g['nguon'],
                 f'{chu} – {g["san_pham"]}: {g["mua" if k == 1 else "ban"]:,} đ/chỉ = {gon(gt, 3)} triệu/lượng (cập nhật {g["cap_nhat"]})')

    # 2) Khoảng giá tóm tắt (SJC + PNJ)
    if all(k in luong for k in TOM_TAT):
        thap = min(luong[k][0] for k in TOM_TAT)
        cao = max(luong[k][1] for k in TOM_TAT)
        cl = [round(luong[k][1] - luong[k][0], 1) for k in TOM_TAT]
        ly = (f'tính từ SJC + PNJ: thấp nhất giá mua {gon(thap, 3)} – cao nhất giá bán {gon(cao, 3)} triệu/lượng; '
              f'theo chỉ = chia 10, làm tròn 2 số lẻ; chênh lệch mua–bán từng thương hiệu {cl}')
        for chu, vt, _ in dong:
            m = re.search(r'(dao động khoảng )([\d.]+)( - )([\d.]+)( triệu VND/lượng[^,]*, tương đương khoảng )([\d.]+)( - )([\d.]+)( triệu VND/chỉ)', chu)
            if m:
                g = list(m.groups())
                hai_le = len(g[5].split('.')[-1]) == 2 and g[5].endswith('0')
                g[1], g[3] = gon(thap, 3), gon(cao, 3)
                g[5] = f'{thap / 10:.2f}' if hai_le else gon(round(thap / 10, 2), 2)
                g[7] = f'{cao / 10:.2f}' if hai_le else gon(round(cao / 10, 2), 2)
                them(m.group(0), vt + m.start(), ''.join(g), '', ly, tinh=True)
            m = re.search(r'(chênh lệch giữa chiều mua vào và bán ra khoảng )([\d.]+)( - )([\d.]+)( triệu VND/lượng)', chu)
            if m:
                g = list(m.groups())
                g[1], g[3] = gon(min(cl), 1), gon(max(cl), 1)
                them(m.group(0), vt + m.start(), ''.join(g), '', ly, tinh=True)
    else:
        can.append('Thiếu giá SJC hoặc PNJ – không tính lại được khoảng giá tóm tắt, giữ nguyên.')

    # 3) Mục 2 – ví dụ nhẫn: giá bán tham khảo = cận trên khoảng tóm tắt (cao nhất giá bán SJC + PNJ, đ/chỉ)
    vd = [(chu, vt, R.search(chu)) for chu, vt, _ in dong for R in (RE_VD, RE_GT, RE_TONG) if R.search(chu)]
    if vd and all(k in gia and gia[k] for k in TOM_TAT):
        ma = max(TOM_TAT, key=lambda k: gia[k]['ban'])
        p = gia[ma]['ban']
        ly0 = (f'giá bán tham khảo = cận trên khoảng giá tóm tắt (cao nhất giá bán SJC + PNJ) = {ma.upper()} '
               f'{gia[ma]["san_pham"]} {p:,} đ/chỉ (cập nhật {gia[ma]["cap_nhat"]})')
        gt = None
        for chu, vt, m in sorted(vd, key=lambda x: x[1]):
            g = list(m.groups())
            if m.re is RE_VD:
                g[1] = f'{p:,}'
                them(m.group(0), vt + m.start(), ''.join(g), gia[ma]['nguon'], ly0)
            elif m.re is RE_GT:
                gt = round(float(g[1]) * p)
                g[3], g[5] = f'{p:,}', f'{gt:,}'
                them(m.group(0), vt + m.start(), ''.join(g), gia[ma]['nguon'], f'{g[1]} chỉ × {p:,} = {gt:,} đ; ' + ly0, tinh=True)
            elif gt is not None:
                cong, da = int(g[3].replace(',', '')), int(g[5].replace(',', ''))
                g[1], g[7] = f'{gt:,}', f'{gt + cong + da:,}'
                them(m.group(0), vt + m.start(), ''.join(g), gia[ma]['nguon'],
                     f'giá trị phần vàng {gt:,} + tiền công {cong:,} + tiền đá {da:,} (giả định của bài, giữ nguyên) = {gt + cong + da:,} đ', tinh=True)
    elif vd:
        can.append('Mục 2 (ví dụ nhẫn 1.2 chỉ): thiếu giá bán SJC hoặc PNJ – giữ nguyên số cũ.')

    # 4) Đoạn "Xu hướng": lịch sử giá PNJ 585 (giá đóng phiên). Thiếu lịch sử → trả lại ngày gốc, giữ số cũ.
    ls = gia.get('_lich_su_pnj')
    xh = [(chu, vt, RE_XH.search(chu)) for chu, vt, _ in dong if RE_XH.search(chu)]
    if xh and ls:
        mc = ls['moc']
        b0 = mc['moi_nhat']['ban'] / 1e6
        def pt(k):
            return (b0 / (mc[k]['ban'] / 1e6) - 1) * 100
        d1 = b0 - mc['phien_truoc']['ban'] / 1e6
        for chu, vt, m in xh:
            g = list(m.groups())
            cu = list(g)
            g[1] = mc['moi_nhat']['ngay']
            for i_chieu, i_so, x, chu_am, chu_duong in ((3, 5, d1, 'giảm', 'tăng'), (7, 9, pt('7_ngay'), 'giảm', 'tăng'),
                                                         (11, 13, pt('1_thang'), 'giảm', 'tăng'), (15, 17, pt('cung_ky'), 'thấp', 'cao')):
                v = so_le(cu[i_so], abs(x))
                if float(v) != 0:
                    g[i_chieu] = chu_am if x < 0 else chu_duong
                g[i_so] = v
                if float(v) == 0:
                    can.append(f'Đoạn Xu hướng: mức thay đổi làm tròn bằng 0 ({x:+.3f}) – giữ chữ "{cu[i_chieu]}", nên đọc lại câu.')
            doi_chieu = [f'"{cu[i]}" → "{g[i]}"' for i in (3, 7, 11, 15) if cu[i] != g[i]]
            ly = (f'PNJ {ls["san_pham"]} giá bán đóng phiên (triệu VND/lượng): {mc["moi_nhat"]["ngay"]} {gon(b0, 3)}; '
                  f'phiên trước {mc["phien_truoc"]["ngay"]} {gon(mc["phien_truoc"]["ban"] / 1e6, 3)} ({d1:+.3f}); '
                  f'7 ngày {mc["7_ngay"]["ngay"]} {gon(mc["7_ngay"]["ban"] / 1e6, 3)} ({pt("7_ngay"):+.2f}%); '
                  f'1 tháng {mc["1_thang"]["ngay"]} {gon(mc["1_thang"]["ban"] / 1e6, 3)} ({pt("1_thang"):+.2f}%); '
                  f'cùng kỳ {mc["cung_ky"]["ngay"]} {gon(mc["cung_ky"]["ban"] / 1e6, 3)} ({pt("cung_ky"):+.2f}%)')
            them(m.group(0), vt + m.start(), ''.join(g), ls['nguon'], ly, tinh=True)
            if doi_chieu and m.group(0) != ''.join(g):
                can.append('Đoạn "1.1. Xu hướng giá vàng 14K gần đây": chữ chỉ chiều đổi theo số mới ' + ', '.join(doi_chieu) + ' – đọc lại câu.')
        if gia.get('pnj') and gia['pnj']['ban'] * 10 != mc['moi_nhat']['ban']:
            can.append(f'Đoạn Xu hướng: giá bán đóng phiên trong lịch sử PNJ ({mc["moi_nhat"]["ban"]:,} đ/lượng, {mc["moi_nhat"]["luc"]}) '
                       f'khác giá bảng PNJ hiện tại ({gia["pnj"]["ban"] * 10:,} đ/lượng) – PNJ có thể vừa đổi giá sau phiên ghi lịch sử.')
    elif a.goc:
        mg = ngay_goc(a.goc)
        for chu, vt, _ in dong:
            m = re.search(r'của PNJ ngày (\d{1,2}/\d{1,2}/\d{4})', chu)
            if m and mg:
                them(m.group(0), vt + m.start(), f'của PNJ ngày {mg}', '',
                     'đoạn xu hướng giữ số liệu cũ (không đọc được lịch sử giá PNJ) nên giữ đúng ngày gốc của số liệu')
                can.append(f'Đoạn "1.1. Xu hướng giá vàng 14K gần đây": không đọc được lịch sử giá PNJ (hoặc câu đã đổi dạng) để tính lại '
                           f'(so với phiên trước / 7 ngày / 1 tháng / cùng kỳ) – giữ nguyên số và ngày gốc {mg}.')

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


if __name__ == '__main__':
    main()

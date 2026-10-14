"""Tự lập sua.json cho bài TCB "Vàng 14K giá hôm nay".

  --xem  kết quả `cap_nhat.py xem ... bai1`   --gia  gia-14k.json (lay_gia_14k.js, VND/chỉ)
  --goc  cap-nhat/tam/bai1.html (bài gốc, để lấy lại ngày của đoạn "Xu hướng")
  --ra   sua.json                              --kiem soát lại sau khi sửa

Bảng: Thương hiệu | Loại vàng 14K | Mua vào | Bán ra — đơn vị TRIỆU VND/LƯỢNG (= VND/chỉ × 10 / 1.000.000),
viết dấu chấm thập phân, bỏ số 0 cuối (73.669, 73.99, 85).
Khoảng giá tóm tắt (2 đoạn) tính trên SJC + PNJ như bài gốc: thấp nhất giá mua – cao nhất giá bán; theo chỉ = /10, làm tròn 2 số lẻ;
chênh lệch mua–bán = thấp nhất – cao nhất của (bán − mua) từng thương hiệu, làm tròn 1 số lẻ.
"""
import argparse, html, json, re, sys, unicodedata

THUONG_HIEU = {'sjc': 'sjc', 'pnj': 'pnj', 'huy thanh': 'huythanh'}
TOM_TAT = ['sjc', 'pnj']


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--goc')
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    ap.add_argument('--bo-to-ngay-xu-huong', metavar='BAI_MIN_HTML',
                    help='sau lệnh sua: bỏ tô vàng ở ngày gốc của đoạn Xu hướng (ngày được trả lại, không phải chỗ mới)')
    a = ap.parse_args()
    if a.bo_to_ngay_xu_huong:
        p = a.bo_to_ngay_xu_huong
        h = open(p, encoding='utf-8').read()
        m = re.search(r'của PNJ ngày (<span style="background-color:#ffff00">(?:<span[^>]*>\d+</span>|[/\d])+</span>)', h)
        if m:
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

    luong = {k: (v['mua'] * 10 / 1e6, v['ban'] * 10 / 1e6) for k, v in gia.items() if v}

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

    # 3) Đoạn "Xu hướng": không có nguồn lịch sử -> trả lại ngày gốc để không ghi số cũ thành "hôm nay"
    if a.goc:
        goc = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', open(a.goc, encoding='utf-8').read())))
        mg = re.search(r'của PNJ ngày (\d{1,2}/\d{1,2}/\d{4})', goc)
        for chu, vt, _ in dong:
            m = re.search(r'của PNJ ngày (\d{1,2}/\d{1,2}/\d{4})', chu)
            if m and mg:
                them(m.group(0), vt + m.start(), f'của PNJ ngày {mg.group(1)}', '',
                     'đoạn xu hướng giữ số liệu cũ (không có nguồn lịch sử giá) nên giữ đúng ngày gốc của số liệu')
                can.append(f'Đoạn "1.1. Xu hướng giá vàng 14K gần đây": không có nguồn lịch sử giá PNJ để tính lại '
                           f'(so với phiên trước / 7 ngày / 1 tháng / cùng kỳ) – giữ nguyên số và ngày gốc {mg.group(1)}. '
                           'Cần bạn quyết: bỏ đoạn này, giữ nguyên, hay đưa nguồn có lịch sử giá.')
    if re.search(r'Giá vàng 14K bán ra tham khảo: [\d,]+ VND', van):
        can.append('Mục 2 (ví dụ cách tính nhẫn 1.2 chỉ): là phép tính minh họa – theo quy tắc không tự cập nhật. '
                   'Nếu muốn khớp giá hôm nay: giá bán PNJ 14K hiện ' + (f'{gia["pnj"]["ban"]:,}' if gia.get('pnj') else '?') + ' đ/chỉ.')

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

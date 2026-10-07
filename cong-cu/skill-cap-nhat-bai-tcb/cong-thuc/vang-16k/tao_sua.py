"""Tự lập sua.json cho bài TCB "Vàng 16K giá hôm nay: Bảng giá chi tiết cập nhật".

  --xem  kết quả `cap_nhat.py xem ... bai1`   --gia  gia-16k.json (lay_gia_16k.js, VND/chỉ)
  --ra   sua.json                              --kiem soát lại sau khi sửa

Bảng: Thương hiệu | Loại vàng 14K | Mua vào | Bán ra — đơn vị TRIỆU VND/LƯỢNG (= VND/chỉ × 10 / 1.000.000),
viết dấu chấm thập phân, bỏ số 0 cuối (87.532, 87.61, 84.5).
Khoảng giá tóm tắt (2 đoạn) tính trên cả 3 hãng: thấp nhất giá mua – cao nhất giá bán, triệu/lượng 1 số lẻ;
theo chỉ = /10, 2 số lẻ (8.45 - 9.73).
"""
import argparse, json, re, sys, unicodedata

THUONG_HIEU = {'sjc': 'sjc', 'pnj': 'pnj', 'mi hồng': 'mihong'}
TOM_TAT = ['sjc', 'pnj', 'mihong']


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
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
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

    # 2) Khoảng giá tóm tắt (cả 3 hãng)
    co = [k for k in TOM_TAT if k in luong]
    if co:
        thap = min(luong[k][0] for k in co)
        cao = max(luong[k][1] for k in co)
        ly = (f'tính từ bảng ({", ".join(co)}): thấp nhất giá mua {gon(thap, 3)} – cao nhất giá bán {gon(cao, 3)} triệu/lượng, '
              'làm tròn 1 số lẻ; theo chỉ = chia 10, 2 số lẻ')
        for chu, vt, _ in dong:
            for m in re.finditer(r'((?:khoảng|dao động) )([\d.]+)( - )([\d.]+)( triệu VND/lượng[^,]*, tương đương khoảng )([\d.]+)( - )([\d.]+)( triệu VND/chỉ)', chu):
                g = list(m.groups())
                g[1], g[3] = f'{thap:.1f}', f'{cao:.1f}'
                g[5], g[7] = f'{thap / 10:.2f}', f'{cao / 10:.2f}'
                them(m.group(0), vt + m.start(), ''.join(g), '', ly, tinh=True)
        if len(co) < len(TOM_TAT):
            can.append('Thiếu nguồn ' + ', '.join(k for k in TOM_TAT if k not in co) + ' – khoảng tóm tắt chỉ tính trên các hãng còn lại.')
    else:
        can.append('Không đọc được nguồn nào – giữ nguyên khoảng giá tóm tắt.')

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

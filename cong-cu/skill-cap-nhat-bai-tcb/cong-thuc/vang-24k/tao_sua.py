"""Tự lập sua.json cho bài TCB "Vàng 24K là gì? … Giá mới nhất".

  --xem   kết quả `cap_nhat.py xem ... bai1`     --gia  gia-vang.json (lay_gia_vang.js)
  --ra    sua.json                                --kiem soát lại sau khi sửa
Bảng giá: mỗi dòng = Thương hiệu | Loại vàng | Giá mua (VND/chỉ) | Giá bán (VND/chỉ).
Ngày trong câu "cập nhật đến ngày d/m/yyyy" (2 chỗ) đổi sang hôm nay, giữ kiểu viết không số 0 đầu.
"""
import argparse, datetime, json, re, sys, unicodedata

THUONG_HIEU = {'sjc': 'sjc', 'pnj': 'pnj', 'doji': 'doji', 'bảo tín minh châu': 'btmc'}


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    dong, van = doc_xem(a.xem)
    gia = json.load(open(a.gia, encoding='utf-8'))
    # Ngày ghi trong bài: chạy từ 15h giờ VN trở đi -> ghi ngày hôm sau (+9 giờ là sang ngày mới)
    hom_nay = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))) + datetime.timedelta(hours=9)
    ngay = f'{hom_nay.day}/{hom_nay.month}/{hom_nay.year}'
    sua, can, lech = [], [], []

    def them(cu, vt, moi, nguon, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    thay_bang = set()
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
        g = gia.get(ma)
        if not g:
            can.append(f'{chu}: không đọc được nguồn – giữ nguyên giá cũ.')
            continue
        thay_bang.add(ma)
        for k, gt in ((1, g['mua']), (2, g['ban'])):
            them(cells[k][0], cells[k][1], f'{gt:,}', g['nguon'],
                 f'{chu} – {g["san_pham"]} ({"mua vào" if k == 1 else "bán ra"}), cập nhật {g["cap_nhat"]}')
    for ma in THUONG_HIEU.values():
        if ma not in thay_bang and gia.get(ma):
            can.append(f'Bảng giá trong bài không còn dòng của nguồn "{ma}".')

    for chu, vt, _ in dong:
        for m in re.finditer(r'(cập nhật đến ngày )(\d{1,2}/\d{1,2}/\d{4})', chu):
            them(m.group(0), vt + m.start(), m.group(1) + ngay, '', 'ngày cập nhật bảng giá = hôm nay')

    if a.kiem:
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} chỗ lệch: ' + '; '.join(lech))
        sys.exit(1 if lech else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for c in can:
        print('  cần duyệt:', c)


if __name__ == '__main__':
    main()

"""Tự lập sua.json cho bài TCB "Giá kim loại thế giới: Bảng giá cập nhật và các yếu tố ảnh hưởng".

  python3 -I tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
  python3 -I tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html

--xem  kết quả `cap_nhat.py xem ... bai1`   --gia  gia.json (lay_gia.py)   --goc  bài gốc tải về (lấy lại ngày cũ)
Không dùng mạng, không đoán số: mọi số viết vào bài lấy thẳng từ gia.json (chép từ trang nguồn trong lần chạy này).

Bảng "Nhóm/kim loại | Giá (VND/lượng) | Thay đổi (%)": nhận dòng theo TÊN kim loại (không theo vị trí), nhận ô theo
dạng số (ô giá = số có dấu nghìn; ô thay đổi = số thập phân có dấu +/-), nên đổi thứ tự dòng/cột vẫn chạy.
- Ô giá: số VNĐ của nguồn, viết dấu nghìn giống ô cũ (bài đang dùng dấu phẩy: 125,921,056).
- Ô thay đổi: chép đúng chữ số % của nguồn, thêm dấu theo mũi tên (▲ -> "+", ▼ -> "-"); 0 -> "0.00" (không dấu).
Kim loại nào nguồn không đọc được -> giữ nguyên 2 ô cũ + cần duyệt, và giữ lại NGÀY CŨ của bài (đọc từ --goc)
để bài không ghi ngày mới cho giá cũ (công cụ chung `dung` đã đổi ngày dd/mm/yyyy sang ngày mới -> đổi ngược lại).
Phần chữ của bài không có con số giá nào (chỉ có mốc năm 2025/2026, "giảm 9%" của World Bank) -> không đụng.
"""
import argparse, collections, html, json, re, sys, unicodedata

TEN = collections.OrderedDict([   # khóa gia.json -> tên có thể gặp trong bài (chữ thường, NFC)
    ('vang', ('vàng',)), ('bac', ('bạc',)), ('dong', ('đồng',)), ('bach_kim', ('bạch kim',)),
    ('niken', ('niken', 'nickel', 'niken (nickel)')), ('chi', ('chì',)), ('nhom', ('nhôm',)), ('kem', ('kẽm',)),
    ('quang_sat', ('quặng sắt 62% fe', 'quặng sắt')), ('thiec', ('thiếc',)),
])
O_GIA = re.compile(r'^\d{1,3}(?:([,.])\d{3})+$')
O_PCT = re.compile(r'^[+\-−]?\d+(?:\.\d+)?%?$')
NGAY = re.compile(r'\b\d{1,2}/\d{1,2}/\d{4}\b')


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def ma_kl(ten):
    t = re.sub(r'\s+', ' ', nfc(ten).lower())
    for k, ds in TEN.items():
        if t in ds:
            return k
    return None


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


def ngay_goc(path):
    """Ngày dd/mm/yyyy xuất hiện nhiều nhất trong bài gốc (trước `dung`)."""
    try:
        t = html.unescape(re.sub(r'<[^>]+>', ' ', open(path, encoding='utf-8').read()))
    except OSError:
        return None
    c = collections.Counter(NGAY.findall(t))
    return c.most_common(1)[0][0] if c else None


def viet_gia(so, cu):
    m = O_GIA.match(cu)
    return f'{so:,}'.replace(',', m.group(1) if m else ',')


def viet_pct(g):
    raw = re.sub(r'\s|%', '', g['thay_doi_goc'])          # chữ số % chép nguyên văn từ nguồn
    if float(raw) == 0:
        return raw
    return ('-' if g['chieu'] == 'arrow_downward' else '+') + raw


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
    url = gia.get('_nguon', 'https://www.thitruonghanghoa.com/gia-kim-loai')
    sua, can, lech, thay_dong = [], [], [], set()

    def them(cu, vt, moi, ly, tim_lan=True):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt) if tim_lan else 'tat_ca',
                    'giu_nguyen_so': True, 'nguon': url, 'ly_do': ly, '_vt': vt})

    # --- Bảng giá: dòng tên kim loại (không phải ô) + các ô ngay sau nó
    for i, (chu, vt, la_o) in enumerate(dong):
        k = ma_kl(chu)
        if la_o or not k:
            continue
        cells, j = [], i + 1
        while j < len(dong) and dong[j][2]:
            cells.append(dong[j]); j += 1
        o_gia = [c for c in cells if O_GIA.match(c[0])]
        o_pct = [c for c in cells if O_PCT.match(c[0]) and not O_GIA.match(c[0])]
        if len(o_gia) != 1 or len(o_pct) != 1:
            continue
        thay_dong.add(k)
        g = gia.get(k)
        if not g:
            can.append(f'{chu}: không đọc được giá trên nguồn – giữ nguyên giá cũ "{o_gia[0][0]}" và mức thay đổi "{o_pct[0][0]}".')
            continue
        goc = f'{g["ten_nguon"]}: "{g["gia_goc"]}" {g["don_vi"]}, thay đổi "{g["thay_doi_goc"]}" ({g["chieu"]}), {g["cap_nhat"]}'
        them(o_gia[0][0], o_gia[0][1], viet_gia(g['gia'], o_gia[0][0]), f'Giá dòng {chu} – nguồn {goc}')
        them(o_pct[0][0], o_pct[0][1], viet_pct(g), f'Thay đổi (%) dòng {chu} – nguồn {goc}')

    thieu = [k for k in TEN if not gia.get(k)]
    if not thay_dong:
        can.append('Không tìm thấy bảng giá kim loại trong bài (bài đổi trình bày?) – chưa cập nhật số nào, cần người kiểm tra.')
    for k in TEN:
        if k not in thay_dong and thay_dong:
            can.append(f'Không thấy dòng "{TEN[k][0]}" trong bảng của bài – nguồn có số nhưng không biết ghi vào đâu.')

    # --- Ngày: thiếu nguồn -> trả lại ngày cũ của bài (công cụ chung đã đổi sang ngày mới)
    if thieu or not thay_dong:
        d0 = ngay_goc(a.goc) if a.goc else None
        moi = collections.Counter(NGAY.findall(van)).most_common(1)
        if d0 and moi and moi[0][0] != d0:
            for chu, vt, _ in dong:
                for m in re.finditer(re.escape(moi[0][0]), chu):
                    them(m.group(0), vt + m.start(), d0, 'giữ ngày cũ của bài vì thiếu nguồn giá')
        can.append('Thiếu số của nguồn (' + (', '.join(thieu) or 'bảng') + ') – giữ nguyên ngày cũ của bài '
                   f'({d0 or "?"}) để bài không ghi ngày mới cho giá cũ.')
    else:
        can.append(f"Giá nguồn chạy theo thời gian thực, {gia.get('_cap_nhat', '').split(' (')[0]}; mở lại trang nguồn có thể thấy số khác. "
                   'Đã dùng số trong "Bảng giá Kim loại", không dùng dải chạy chữ đầu trang.')
    can.append('Tiêu đề cột ghi "Giá (VND/lượng)" nhưng nguồn niêm yết Đồng, Niken, Chì, Nhôm, Kẽm, Thiếc theo VNĐ/tấn và '
               'Quặng sắt theo VNĐ/dmtu – giữ nguyên tiêu đề cột như bài (bài đã có dòng Lưu ý về đơn vị).')
    can.append('Các mốc năm trong phần phân tích (năm 2025, đầu năm 2026, đầu tư khoáng sản giảm 9% năm 2025, World Bank…) '
               '– nguồn không đề cập, giữ nguyên.')

    if a.kiem:
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} chỗ lệch: ' + '; '.join(lech))
        sys.exit(1 if lech else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for x in sua:
        print('  ', x['tim'][:60], '→', x['thay'][:60])
    for c in can:
        print('  cần duyệt:', c)


if __name__ == '__main__':
    main()

"""Tự lập sua.json cho bài TCB "Vàng 18K là gì? Đặc điểm, cách phân biệt và giá mới nhất".

  --xem  kết quả `cap_nhat.py xem ... bai1`   --gia  gia-18k.json (lay_gia_18k.js, VND/chỉ)
  --ra   sua.json                              --kiem soát lại sau khi sửa

Bảng: Thương hiệu | Giá mua vào | Giá bán ra — ô viết "9,765,000 VND/chỉ"; ô bán của DOJI "(Liên hệ…)" giữ nguyên
khi DOJI không niêm yết giá bán. Câu tổng kết: "mua vào cao nhất" = giá mua lớn nhất; "bán ra thấp nhất" = giá bán
nhỏ nhất (trong các hãng có giá bán) — viết triệu VND/chỉ, 3 số lẻ. Ngày "cập nhật đến ngày d/m/yyyy" -> hôm nay.
"""
import argparse, datetime, json, re, sys, unicodedata


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def ma_hang(ten):
    t = ten.lower()
    for k in ('pnj', 'sjc', 'doji'):
        if t.startswith(k):
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
    hn = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))) + datetime.timedelta(hours=9)
    ngay = f'{hn.day}/{hn.month}/{hn.year}'
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

    for i, (chu, vt, la_o) in enumerate(dong):
        ma = ma_hang(chu)
        if la_o or not ma:
            continue
        cells = []
        j = i + 1
        while j < len(dong) and dong[j][2]:
            cells.append(dong[j]); j += 1
        if len(cells) != 2 or 'VND/chỉ' not in cells[0][0]:
            continue
        g = gia.get(ma)
        if not g:
            can.append(f'{chu}: không đọc được nguồn – giữ nguyên giá cũ.')
            continue
        for k, gt in ((0, g['mua']), (1, g['ban'])):
            if gt is None:
                if 'VND/chỉ' in cells[k][0]:
                    can.append(f'{chu}: nguồn không niêm yết giá {"mua" if k == 0 else "bán"} – giữ nguyên "{cells[k][0]}".')
                continue
            them(cells[k][0], cells[k][1], f'{gt:,} VND/chỉ', g['nguon'],
                 f'{chu} – {g["san_pham"]} ({"mua vào" if k == 0 else "bán ra"}), cập nhật {g["cap_nhat"]}')

    mua = [v['mua'] for v in gia.values() if v and v.get('mua')]
    ban = [v['ban'] for v in gia.values() if v and v.get('ban')]
    if mua and ban:
        cao, thap = max(mua) / 1e6, min(ban) / 1e6
        ly = f'tính từ bảng: giá mua cao nhất {max(mua):,} đ/chỉ, giá bán thấp nhất {min(ban):,} đ/chỉ'
        for chu, vt, _ in dong:
            m = re.search(r'(mua vào cao nhất khoảng )([\d.]+)( triệu VND/chỉ và bán ra thấp nhất khoảng )([\d.]+)( triệu VND/chỉ)', chu)
            if m:
                g = list(m.groups()); g[1], g[3] = f'{cao:.3f}', f'{thap:.3f}'
                them(m.group(0), vt + m.start(), ''.join(g), '', ly, tinh=True)
            m = re.search(r'(bán ra hiện dao động từ khoảng )([\d.]+)( triệu VND/chỉ)', chu)
            if m:
                g = list(m.groups()); g[1] = f'{thap:.3f}'
                them(m.group(0), vt + m.start(), ''.join(g), '', ly, tinh=True)

    if all(gia.get(k) for k in ('pnj', 'sjc', 'doji')):
        for chu, vt, _ in dong:
            for m in re.finditer(r'(cập nhật đến ngày )(\d{1,2}/\d{1,2}/\d{4})', chu):
                them(m.group(0), vt + m.start(), m.group(1) + ngay, '', 'ngày cập nhật bảng giá = hôm nay')
    else:
        can.append('Thiếu nguồn – không đổi ngày "cập nhật đến ngày" để bài không ghi ngày mới cho giá cũ.')

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

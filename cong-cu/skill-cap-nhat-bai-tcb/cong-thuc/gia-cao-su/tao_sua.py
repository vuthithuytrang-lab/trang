"""Tự lập sua.json cho bài "Giá cao su" của Techcombank (techcombank.com/thong-tin/blog/gia-cao-su).

  python3 -I tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --ra cap-nhat/sua.json
  python3 -I tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json      # soát lại sau `sua`

- Bảng trong nước (Doanh nghiệp | Loại mủ | Mức giá): so từng ô với giá doanh nghiệp trong gia.json; chỉ đổi số,
  giữ đơn vị ("VND/TSC/kg"…) và dấu nghìn "," như bài.
- Bảng thế giới (Sàn | Chủng loại | Kỳ hạn | Mức giá | Đơn vị): mỗi sàn giữ đúng số dòng của bài, lấy các kỳ hạn đang
  giao dịch đầu tiên của nguồn (kỳ đã đáo hạn tự cuộn lên, đổi cả nhãn kỳ hạn). Nhãn giữ kiểu bài: "1/27" (TOCOM, SHFE),
  "1/2027" (SGX). Giá giữ kiểu bài: "462,60" (2 số lẻ, dấu phẩy), "18,130" (dấu nghìn phẩy).
Quy tắc đã chốt — xem README.md cùng thư mục.
"""
import argparse, json, re, sys, unicodedata

# (tên doanh nghiệp trong bài, loại mủ trong bài) -> khóa trong gia.json["trong_nuoc"]["gia"]
TRONG_NUOC = {
    ('Công ty Cao su Bình Long', 'Mủ nước tại nhà máy'): 'binh_long_nha_may',
    ('Công ty Cao su Bình Long', 'Mủ nước tại đội sản xuất'): 'binh_long_doi_sx',
    ('Công ty Cao su Bình Long', 'Mủ tạp DRC 60%'): 'binh_long_mu_tap',
    ('Công ty Cao su Phú Riềng', 'Mủ nước'): 'phu_rieng_mu_nuoc',
    ('Công ty Cao su Phú Riềng', 'Mủ tạp'): 'phu_rieng_mu_tap',
    ('Công ty Cao su Mang Yang', 'Mủ nước loại 1'): 'mang_yang_mu_nuoc_loai1',
    ('Công ty Cao su Mang Yang', 'Mủ nước loại 2'): 'mang_yang_mu_nuoc_loai2',
    ('Công ty Cao su Mang Yang', 'Mủ đông tạp loại 1'): 'mang_yang_mu_dong_loai1',
    ('Công ty Cao su Mang Yang', 'Mủ đông tạp loại 2'): 'mang_yang_mu_dong_loai2',
    ('Công ty Cao su Bà Rịa', 'Mủ nước TSC 25 đến dưới 30'): 'ba_ria_mu_nuoc',
    ('Công ty Cao su Bà Rịa', 'Mủ đông DRC 35 - 45%'): 'ba_ria_mu_dong',
}
SAN = {'TOCOM': 'tocom', 'SHFE': 'shfe', 'SGX': 'sgx'}


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def doc_xem(path):
    """(danh sách dòng bảng, toàn văn). Mỗi dòng = list ô; mỗi ô = (chữ, vị trí trong toàn văn)."""
    van, rows, cur = '', [], None
    for line in open(path, encoding='utf-8'):
        m = re.match(r'\s*\d+\.\s?(.*)$', line.rstrip('\n'))
        if not m:
            continue
        t = m.group(1)
        la_o = t.startswith('| ')
        c = nfc(t[2:] if la_o else t)
        vt = len(van)
        van += c + '\n'
        if la_o and cur is not None:
            cur.append((c, vt))
        else:
            cur = [(c, vt)]
            rows.append(cur)
    return [r for r in rows if len(r) >= 3], van


def lan_thu(van, tim, vt):
    n, i = 0, van.find(tim)
    while i != -1 and i <= vt:
        n += 1
        i = van.find(tim, i + 1)
    return n


def viet_gia(cu, x):
    """Viết số x theo kiểu của ô cũ."""
    x = float(x)
    if re.fullmatch(r'\d+,\d{2}', cu):                 # 462,60
        return f'{x:.2f}'.replace('.', ',')
    if re.fullmatch(r'\d{1,3}(,\d{3})+', cu) or x >= 1000:   # 18,130
        return f'{round(x):,}'
    return str(round(x))


def viet_ky_han(cu, kh):
    mm, yy = kh.split('/')
    return f'{int(mm)}/{"20" + yy if re.fullmatch(r"\d{1,2}/\d{4}", cu) else yy}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    rows, van = doc_xem(a.xem)
    G = json.load(open(a.gia, encoding='utf-8'))
    sua, can, lech = [], [], []

    def them(o, moi, nguon, ly):
        cu, vt = o
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    # 1) Bảng trong nước
    tn = G.get('trong_nuoc') or {}
    gia_tn = tn.get('gia') or {}
    thay_tn = 0
    for r in rows:
        ten, loai = r[0][0], r[1][0]
        if not ten.startswith('Công ty Cao su'):
            continue
        thay_tn += 1
        k = TRONG_NUOC.get((ten, loai))
        o = r[2]
        m = re.match(r'([\d,]+)(\s.*)$', o[0])
        if ten == 'Công ty Cao su Bà Rịa' and loai.startswith('Mủ chén') and gia_tn.get('ba_ria_mu_nguyen_lieu') is not None:
            can.append(f'Bảng trong nước – Bà Rịa "{loai}" ("{o[0]}"): nguồn chỉ ghi "mủ nguyên liệu '
                       f'{gia_tn["ba_ria_mu_nguyen_lieu"]:,} đồng/kg", không rõ là cùng loại → giữ nguyên, cần duyệt.')
            continue
        if ten == 'Công ty Cao su Mang Yang' and loai.startswith('Mủ đông') and o[0].endswith(' VND/kg'):
            can.append(f'Lỗi có sẵn trong bài – Mang Yang "{loai}" ghi đơn vị "VND/kg" nhưng giá ~400 là giá theo độ DRC '
                       f'(nguồn ghi "đồng/DRC") – không sửa chữ, cần duyệt.')
        if not k or not m:
            can.append(f'Bảng trong nước – {ten} / {loai} ("{o[0]}"): nguồn không có mục khớp rõ ràng → giữ nguyên.')
            continue
        moi = gia_tn.get(k)
        if moi is None:
            can.append(f'Bảng trong nước – {ten} / {loai}: nguồn hôm nay không đọc được giá → giữ nguyên "{o[0]}".')
            continue
        them(o, viet_gia(m.group(1), moi) + m.group(2), tn['nguon'],
             f'{ten} – {loai}: {moi} ({tn.get("thoi_diem", "")})')
        if k == 'ba_ria_mu_dong' and gia_tn.get('ba_ria_mu_dong_nhom_drc') and gia_tn['ba_ria_mu_dong_nhom_drc'] not in loai:
            can.append(f'Bảng trong nước – Bà Rịa: bài ghi nhóm "{loai}", nguồn ghi mủ đông DRC ({gia_tn["ba_ria_mu_dong_nhom_drc"]}) '
                       f'– đã cập nhật giá, giữ nguyên chữ nhóm DRC trong bài, cần duyệt.')
    if thay_tn == 0:
        can.append('LỖI: không thấy bảng giá trong nước trong bài.')

    # 2) Bảng hợp đồng kỳ hạn
    theo_san = {}
    for r in rows:
        if r[0][0] in SAN and len(r) >= 5:
            theo_san.setdefault(r[0][0], []).append(r)
    for ten, ds in theo_san.items():
        src = G.get(SAN[ten])
        if not src or not src.get('hop_dong'):
            can.append(f'Bảng thế giới – {ten}: không đọc được nguồn → giữ nguyên {len(ds)} dòng.')
            continue
        hd = src['hop_dong']
        if len(hd) < len(ds):
            can.append(f'Bảng thế giới – {ten}: nguồn chỉ có {len(hd)} kỳ hạn, bài có {len(ds)} dòng → các dòng cuối giữ nguyên.')
        for r, h in zip(ds, hd):
            kh_moi = viet_ky_han(r[2][0], h['ky_han'])
            gia_moi = viet_gia(r[3][0], h['gia'])
            ly = f'{ten} kỳ hạn {h["ky_han"]}: {h["gia"]} ({src.get("thoi_diem", "")})'
            them(r[2], kh_moi, src['nguon'], ly)
            them(r[3], gia_moi, src['nguon'], ly)

    for ten in ('SHFE', 'SGX'):
        src = G.get(SAN[ten])
        if ten in theo_san and src:
            can.append(f'Bảng thế giới – {ten}: số là "giá khớp" trên giacaphe.com ({src.get("thoi_diem", "")}), có thể là giá '
                       f'đang giao dịch / chưa phải giá chốt phiên chính thức của sàn.')
    if a.kiem:
        print('Soát 2 bảng:', 'khớp hết' if not lech else f'{len(lech)} ô lệch: ' + '; '.join(lech))
        sys.exit(1 if lech else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} ô cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for c in can:
        print('  cần duyệt:', c)


if __name__ == '__main__':
    main()

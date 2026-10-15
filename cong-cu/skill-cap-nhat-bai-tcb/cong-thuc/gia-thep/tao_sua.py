"""Tự lập sua.json cho bài "Giá thép hôm nay" của Techcombank.

Đọc:
  --xem   kết quả `cap_nhat.py xem ... bai1` (lưu ra file)
  --gia   kết quả lay_gia.js (Barchart HRC V7 + Steelonline)
So 2 bảng trong bài với số mới, ghi --ra (sua.json). `--kiem` soát lại sau khi sửa. Quy tắc: README.md cùng thư mục.
"""
import argparse, json, re, sys, unicodedata

MA = 'FGHJKMNQUVXZ'


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def doc_xem(path):
    van, rows, cur = '', [], None
    for line in open(path, encoding='utf-8'):
        m = re.match(r'\s*\d+\.\s?(.*)$', line.rstrip('\n'))
        if not m:
            continue
        t = m.group(1)
        la_o = t.startswith('| ')
        chu = nfc(t[2:] if la_o else t)
        vt = len(van)
        van += chu + '\n'
        if la_o and cur is not None:
            cur.append((chu, vt))
        else:
            cur = [(chu, vt)]
            rows.append(cur)
    return [r for r in rows if len(r) >= 2], van


def lan_thu(van, tim, vt):
    n, i = 0, van.find(tim)
    while i != -1 and i <= vt:
        n += 1
        i = van.find(tim, i + 1)
    return n


def so(x):  # "14.920" (Steelonline, dấu chấm nghìn) -> 14920
    return int(x.replace('.', '').replace(',', ''))


def khop_ten(ten_bai, ten_nguon):
    a = nfc(ten_bai).upper().replace('HÒA', 'HOÀ')
    a = re.sub(r'^THÉP ', '', a)
    b = re.sub(r'^THÉP ', '', nfc(ten_nguon).upper().replace('HÒA', 'HOÀ'))
    return a.replace(' ', '') == b.replace(' ', '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    rows, van = doc_xem(a.xem)
    g = json.load(open(a.gia, encoding='utf-8'))
    sua, can, loi, lech = [], [], [], []

    def them(o, moi, nguon, ly):
        cu, vt = o
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    # 1) Bảng HRC: dòng có ô đầu là mã V7 + tháng + 2 số năm
    cu = [r for r in rows if re.fullmatch(r'V7[FGHJKMNQUVXZ]\d\d', r[0][0]) and len(r) >= 4]
    hd = [x for x in g['hrc']['hop_dong'] if x.get('gia')]
    if hd:
        ngay_moi = max(hd, key=lambda x: (x['ngay'][6:], x['ngay'][:5]))['ngay']
        bo = [x['ma'] for x in hd if x['ngay'] != ngay_moi]
        if bo:
            can.append(f'HRC: bỏ qua {", ".join(bo)} vì Barchart không có giá ngày {ngay_moi} (có thể đã đáo hạn).')
        hd = [x for x in hd if x['ngay'] == ngay_moi]
    if not cu or not hd:
        loi.append(f'Thiếu bảng HRC: bài có {len(cu)} dòng, nguồn có {len(hd)} hợp đồng.')
    else:
        if len(hd) < len(cu):
            can.append(f'HRC: nguồn chỉ có {len(hd)} hợp đồng, bài có {len(cu)} dòng – {len(cu) - len(hd)} dòng cuối giữ nguyên.')
        co_s = any(r[2][0].endswith('s') for r in cu)
        for r, m in zip(cu, hd):
            gia = float(m['gia'].replace(',', ''))
            doi = 0.0 if m['thay_doi'] == 'unch' else float(m['thay_doi'].replace(',', ''))
            gia_txt = f'{gia:,.2f}' + ('s' if co_s and m['chot_phien'] else '')
            doi_txt = '0.00' if doi == 0 else f'{doi:+.2f}'
            ly = (f'Barchart {m["ma"]} (Steel HRC FOB China, sàn LME): {m["gia"]}{"s" if m["chot_phien"] else ""} '
                  f'{m["thay_doi"]} ({m["phan_tram"]}) ngày {m["ngay"]} (tháng/ngày/năm)')
            them(r[0], m['ma'], m['url'], ly)
            them(r[1], m['thang'], m['url'], ly)
            them(r[2], gia_txt, m['url'], ly)
            them(r[3], doi_txt, m['url'], ly)

    # 2) Bảng trong nước: ô cuối 2 cột là "a - b"
    tn = g['trong_nuoc']['thuong_hieu']
    co = False
    for r in rows:
        if len(r) < 3 or not re.fullmatch(r'[\d,]+ - [\d,]+', r[-1][0]) or not re.fullmatch(r'[\d,]+ - [\d,]+', r[-2][0]):
            continue
        ten = r[0][0]
        ten_ng = next((k for k in tn if khop_ten(ten, k)), None)
        if not ten_ng:
            # dòng nhập ô (rowspan) kiểu "Việt Ý | 13,840 ..." vẫn có ô đầu là tên
            loi.append(f'Không thấy thương hiệu "{ten}" trên Steelonline.')
            continue
        co = True
        d = tn[ten_ng]['dong']
        # cột: kg/m, kg/cây, CB240 kg, CB300 kg, CB300 cây, CB400 kg, CB400 cây, CB500 kg, CB500 cây
        kg = [so(x[i]) for x in d for i in (3, 4, 6, 8) if i < len(x) and x[i] not in ('-', '')]
        cay = [so(x[i]) for x in d for i in (5, 7, 9) if i < len(x) and x[i] not in ('-', '')]
        kg_txt, cay_txt = f'{min(kg):,} - {max(kg):,}', f'{min(cay):,} - {max(cay):,}'
        ly = (f'Steelonline {ten_ng} ({tn[ten_ng]["vung_hien_thi_dau"]}, bảng hiện mặc định), ngày {g["trong_nuoc"]["ngay_tren_trang"]}: '
              f'thấp nhất – cao nhất mọi ô VNĐ/kg = {kg_txt}; mọi ô VNĐ/cây (D10 – D28) = {cay_txt}')
        them(r[-2], kg_txt, g['trong_nuoc']['nguon'], ly)
        them(r[-1], cay_txt, g['trong_nuoc']['nguon'], ly)
    if not co:
        loi.append('Không thấy bảng giá thép trong nước theo thương hiệu trong bài.')

    if 'chất lượng cà phê' in van:
        can.append('Câu "Lưu ý" dưới bảng HRC ghi nhầm "tùy theo chất lượng cà phê, sản lượng thu mua…" (chép từ bài cà phê) – '
                   'theo quy tắc không sửa câu chữ, cần biên tập viên duyệt.')

    if a.kiem:
        for l in loi:
            print('LỖI:', l)
        print('Soát 2 bảng:', 'khớp hết' if not lech else f'{len(lech)} ô lệch: ' + '; '.join(lech))
        sys.exit(1 if lech or loi else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} ô cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for c in can:
        print('  cần duyệt:', c)
    for l in loi:
        print('LỖI:', l)
    sys.exit(1 if loi else 0)


if __name__ == '__main__':
    main()

"""Tự lập sua.json cho bài "Giá cà phê Đắk Lắk hôm nay" của Techcombank.

Đọc:
  --xem       kết quả lệnh `cap_nhat.py xem ... bai1` (lưu ra file)
  --nha-be    trang chính Nhà Bè Agri đã tải (cap-nhat/tam/thamkhao1.goc) -> giá 5 vùng (Lâm Đồng, Gia Lai, Đắk Nông...)
  --dak-lak   trang Đắk Lắk của Nhà Bè Agri (cap-nhat/tam/thamkhao2.goc) -> bảng lịch sử giá theo ngày
rồi so bảng 5 ngày + đoạn giá hôm nay + 3 dòng vùng lân cận với số mới, ghi ra --ra (sua.json) và --gia (gia.json).
--kiem: soát lại sau khi sửa. Quy tắc: xem README.md cùng thư mục.
"""
import argparse, html, json, re, sys, unicodedata

NHA_BE = 'https://nhabeagri.com/gia-nong-san/gia-ca-phe/'
DAK_LAK = 'https://nhabeagri.com/gia-nong-san/gia-ca-phe-dak-lak/'
LAN_CAN = ['Lâm Đồng', 'Gia Lai', 'Đắk Nông']


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
    return [r for r in rows if len(r) >= 3], van


def lan_thu(van, tim, vt):
    n, i = 0, van.find(tim)
    while i != -1 and i <= vt:
        n += 1
        i = van.find(tim, i + 1)
    return n


def so(n):
    return f'{n:,}'


def doi_txt(d):
    return '+0' if d == 0 else f'{d:+,}'      # bài ghi "+0" khi không đổi


def doc_nha_be(path):
    s = open(path, encoding='utf-8', errors='replace').read()
    ra = {}
    for ten, gia, lop, doi in re.findall(
            r'>([^<>]{2,20})</a></td>\s*<td>([\d.]+)đ</td>\s*<td class="([^"]*)">\s*([+-]?[\d.]+)đ', s):
        ten = nfc(html.unescape(ten))
        if ten in ra:
            continue
        d = int(doi.replace('.', ''))
        if 'down' in lop and d > 0:
            d = -d
        ra[ten] = (int(gia.replace('.', '')), d)
    m = re.search(r'Cập nhật gần nhất:\s*([^<]+)<', s)
    return ra, (m.group(1).strip() if m else '?')


def doc_lich_su(path):
    s = open(path, encoding='utf-8', errors='replace').read()
    ra = []
    for ngay, gia, lop, doi in re.findall(
            r'<td>(\d\d/\d\d/\d{4})</td>\s*<td>([\d.]+)đ</td>\s*<td class="([^"]*)">\s*([+-]?[\d.]+)đ', s):
        d = int(doi.replace('.', ''))
        if 'down' in lop and d > 0:
            d = -d
        if not any(x['ngay'] == ngay for x in ra):
            ra.append({'ngay': ngay, 'gia': int(gia.replace('.', '')), 'thay_doi': d})
    m = re.search(r'Cập nhật gần nhất:\s*([^<]+)<', s)
    return ra, (m.group(1).strip() if m else '?')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--nha-be', required=True)
    ap.add_argument('--dak-lak', required=True)
    ap.add_argument('--ra')
    ap.add_argument('--gia', help='nơi ghi số liệu thô (gia.json)')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()

    rows, van = doc_xem(a.xem)
    sua, can, loi, lech = [], [], [], []

    def them(cu, vt, moi, nguon, ly, ngu_canh=None):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        x = {'tim': cu, 'thay': moi, 'giu_nguyen_so': True, 'nguon': nguon, 'ly_do': ly, '_vt': vt}
        if ngu_canh:
            x['ngu_canh'] = ngu_canh
        else:
            x['lan'] = lan_thu(van, cu, vt)
        sua.append(x)

    ls, ls_gio = doc_lich_su(a.dak_lak)
    nb, nb_gio = doc_nha_be(a.nha_be)
    if not ls:
        loi.append('Không đọc được bảng lịch sử giá trên trang Đắk Lắk của Nhà Bè Agri.')
    if not nb:
        loi.append('Không đọc được bảng giá các vùng trên trang chính Nhà Bè Agri.')

    # 1) Bảng lịch sử: các dòng có ô đầu là ngày dd/mm/yyyy
    bang = [r for r in rows if re.fullmatch(r'\d\d/\d\d/\d{4}', r[0][0]) and re.fullmatch(r'[\d,]+', r[1][0])]
    if ls and not bang:
        loi.append('Không thấy bảng Ngày | Giá | Thay đổi trong bài.')
    if ls and len(ls) < len(bang):
        can.append(f'Bảng giá theo ngày: nguồn chỉ có {len(ls)} ngày, bài có {len(bang)} dòng – dòng cuối giữ nguyên.')
    for r, m in zip(bang, ls):
        ly = f'Đắk Lắk ngày {m["ngay"]}: {so(m["gia"])} đ/kg, thay đổi {doi_txt(m["thay_doi"])} (Nhà Bè Agri, cập nhật {ls_gio})'
        them(r[0][0], r[0][1], m['ngay'], DAK_LAK, ly)
        them(r[1][0], r[1][1], so(m['gia']), DAK_LAK, ly)
        them(r[2][0], r[2][1], doi_txt(m['thay_doi']), DAK_LAK, ly)
    # 2) Đoạn "giá ... tại Đắk Lắk đang được tham khảo ở mức khoảng X VND/kg, tăng/giảm khoảng Y VND/kg"
    m = re.search(r'ở mức khoảng ([\d,]+) VND/kg, (tăng|giảm) khoảng ([\d,]+) VND/kg', van)
    if m and ls:
        h = ls[0]
        d = h['thay_doi']
        ly = f'Đắk Lắk ngày {h["ngay"]}: {so(h["gia"])} đ/kg, thay đổi {doi_txt(d)} (Nhà Bè Agri, cập nhật {ls_gio})'
        if d == 0:
            them(m.group(1), m.start(1), so(h['gia']), DAK_LAK, ly, ngu_canh=m.group(0))
            can.append('Đoạn giá hôm nay: nguồn ghi giá không đổi so với phiên trước, câu bài viết "tăng/giảm khoảng … VND/kg" '
                       'không ghi được đúng dạng – chỉ đổi mức giá, giữ nguyên phần tăng/giảm cũ, cần duyệt.')
        else:
            tu = 'tăng' if d > 0 else 'giảm'
            moi = f'ở mức khoảng {so(h["gia"])} VND/kg, {tu} khoảng {so(abs(d))} VND/kg'
            them(m.group(0), m.start(), moi, DAK_LAK, ly)
            if tu != m.group(2):
                can.append(f'Đoạn giá hôm nay: đã đổi chữ "{m.group(2)}" thành "{tu}" cho khớp chiều giá của nguồn – cần duyệt.')
        if h['ngay'] != '16/10/2026':
            can.append(f'Đoạn giá hôm nay ghi "cập nhật trong ngày 16/10/2026" nhưng số là giá ngày {h["ngay"]} '
                       f'(ngày gần nhất nguồn có, cập nhật {ls_gio}); bảng theo ngày cũng mở đầu bằng {h["ngay"]} – cần duyệt.')
    elif ls:
        loi.append('Không thấy câu "ở mức khoảng … VND/kg, tăng/giảm khoảng … VND/kg" trong bài.')

    # 3) Vùng lân cận: "Lâm Đồng khoảng 93,600 VND/kg"
    for ten in LAN_CAN:
        m = re.search(re.escape(ten) + r' khoảng ([\d,]+) VND/kg', van)
        if not m:
            loi.append(f'Không thấy dòng "{ten} khoảng … VND/kg" trong bài.')
            continue
        if ten not in nb:
            can.append(f'Nhà Bè Agri không có giá {ten} – giữ nguyên.')
            continue
        gia, d = nb[ten]
        ly = f'{ten}: {so(gia)} đ/kg, thay đổi {doi_txt(d)} (Nhà Bè Agri, cập nhật {nb_gio})'
        them(m.group(0), m.start(), f'{ten} khoảng {so(gia)} VND/kg', NHA_BE, ly)

    # Câu "giá Đắk Lắk đang ở mức tương đối cao" – kiểm tra với số mới
    if 'Đắk Lắk' in nb and 'tương đối cao' in van:
        dl = nb['Đắk Lắk'][0]
        cao_hon = [t for t in LAN_CAN if t in nb and nb[t][0] > dl]
        if cao_hon:
            can.append('Câu "giá Đắk Lắk đang ở mức tương đối cao" so với vùng lân cận: theo nguồn Đắk Lắk '
                       f'{so(dl)} đ/kg, thấp hơn {", ".join(f"{t} {so(nb[t][0])}" for t in cao_hon)} – giữ nguyên câu, cần duyệt.')

    # Lỗi có sẵn trong bài
    if 'theo hình ảnh bạn cung cấp' in van:
        can.append('Bài gốc còn sót câu "Dưới đây là bảng thông tin được trích xuất và kẻ lại y hệt theo hình ảnh bạn cung cấp:" '
                   '(câu nháp, không hợp với bài đăng) – theo quy tắc không sửa chữ, chỉ báo lại.')

    if a.gia:
        json.dump({'thoi_diem_lay': ls_gio, 'nguon': {
            'lich_su_dak_lak': {'url': DAK_LAK, 'cap_nhat': ls_gio, 'bang': ls},
            'cac_vung': {'url': NHA_BE, 'cap_nhat': nb_gio,
                         'bang': {k: {'gia': v[0], 'thay_doi': v[1]} for k, v in nb.items()}}}},
                  open(a.gia, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    if a.kiem:
        for l in loi:
            print('LỖI:', l)
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} ô lệch: ' + '; '.join(lech))
        sys.exit(1 if lech or loi else 0)

    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for c in can:
        print('  cần duyệt:', c)
    for l in loi:
        print('LỖI:', l)
    sys.exit(1 if loi else 0)


if __name__ == '__main__':
    main()

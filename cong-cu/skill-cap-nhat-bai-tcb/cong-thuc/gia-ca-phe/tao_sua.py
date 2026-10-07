"""Tự lập sua.json cho bài "Giá cà phê hôm nay" của Techcombank.

Đọc 3 thứ:
  --xem       kết quả lệnh `cap_nhat.py xem ... bai1` (lưu ra file)
  --nha-be    trang nhabeagri đã tải (cap-nhat/tam/thamkhaoN.goc) -> bảng giá trong nước
  --the-gioi  kết quả lay_gia_the_gioi.js -> bảng Robusta + Arabica
rồi so từng ô của 3 bảng trong bài với số mới và ghi ra --ra (sua.json).

Quy tắc đã chốt với Trang (07/10/2026) — xem README.md cùng thư mục.
"""
import argparse, datetime, html, json, re, sys, unicodedata

NHA_BE = 'https://nhabeagri.com/gia-nong-san/gia-ca-phe/'
MA_THANG = {'01': 'F', '02': 'G', '03': 'H', '04': 'J', '05': 'K', '06': 'M',
            '07': 'N', '08': 'Q', '09': 'U', '10': 'V', '11': 'X', '12': 'Z'}


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def doc_xem(path):
    """Trả về (danh sách dòng bảng, toàn văn). Mỗi dòng bảng = list ô; mỗi ô = (chữ, vị trí trong toàn văn)."""
    dong, van, rows, cur = [], '', [], None
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
    """Chữ `tim` tại vị trí vt là lần xuất hiện thứ mấy trong toàn văn."""
    n, i = 0, van.find(tim)
    while i != -1 and i <= vt:
        n += 1
        i = van.find(tim, i + 1)
    return n


def so_nghin(n):
    return f'{n:,}'


def doc_nha_be(path):
    s = open(path, encoding='utf-8', errors='replace').read()
    ra = {}
    for ten, gia, lop, doi in re.findall(
            r'>([^<>]{2,20})</a></td>\s*<td>([\d.]+)đ</td>\s*<td class="([^"]*)">\s*([\d.]+)đ', s):
        ten = nfc(html.unescape(ten))
        if ten in ra:
            continue
        d = int(doi.replace('.', ''))
        if 'down' in lop:
            d = -d
        ra[ten] = (int(gia.replace('.', '')), d)
    m = re.search(r'Cập nhật gần nhất:\s*([^<]+)<', s)
    return ra, (m.group(1).strip() if m else '?')


def dang_giao_dich(now):
    """Sàn London/New York mở khoảng 15:00 – 01:30 (giờ VN), thứ 2 – thứ 6."""
    if now.hour >= 15:
        return now.weekday() < 5
    if now.hour < 1 or (now.hour == 1 and now.minute <= 30):
        return 1 <= now.weekday() <= 5
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--nha-be', required=True)
    ap.add_argument('--the-gioi', required=True)
    ap.add_argument('--ra', help='nơi ghi sua.json')
    ap.add_argument('--kiem', action='store_true',
                    help='soát lại sau khi sửa: mọi ô trong 3 bảng phải đúng bằng số mới')
    a = ap.parse_args()

    rows, van = doc_xem(a.xem)
    sua, can, loi = [], [], []

    lech = []

    def them(o, moi, nguon, ly):
        cu, vt = o
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    # 1) Bảng trong nước
    nb, nb_gio = doc_nha_be(a.nha_be)
    if not nb:
        loi.append('Không đọc được bảng giá trong nước trên Nhà Bè Agri.')
    co_bang_trong_nuoc = False
    for r in rows:
        ten = r[0][0]
        if ten in nb and re.fullmatch(r'[\d,\s\-]+', r[1][0]):
            co_bang_trong_nuoc = True
            gia, d = nb[ten]
            ly = f'{ten}: {so_nghin(gia)} đ/kg, thay đổi {d:+,} (Nhà Bè Agri, cập nhật {nb_gio})'
            them(r[1], so_nghin(gia), NHA_BE, ly)
            them(r[2], 'Không đổi' if d == 0 else f'{d:+,}', NHA_BE, ly)
    if nb and not co_bang_trong_nuoc:
        loi.append('Không thấy bảng giá trong nước trong bài (cột Khu vực).')

    # 2) Bảng thế giới
    tg = json.load(open(a.the_gioi, encoding='utf-8'))
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    mo = dang_giao_dich(now)
    hau_to = '' if mo else 's'
    if mo:
        can.append(f'Lúc chạy ({now:%H:%M %d/%m/%Y}) sàn London/New York đang giao dịch: giá thế giới là giá trực tuyến, '
                   'chưa phải giá chốt phiên, nên KHÔNG ghi ký tự "s" sau giá. Muốn có giá chốt phiên thì chạy lại trước 15:00.')
    for loai, tien_to, thap_phan in [('robusta', 'RM', 0), ('arabica', 'KC', 2)]:
        moi = tg.get('bang', {}).get(loai) or []
        cu = [r for r in rows if re.fullmatch(tien_to + r'[FGHJKMNQUVXZ]\d\d', r[0][0])]
        if not moi or not cu:
            loi.append(f'Thiếu bảng {loai}: bài có {len(cu)} dòng, nguồn có {len(moi)} dòng.')
            continue
        if len(moi) < len(cu):
            can.append(f'Bảng {loai}: nguồn chỉ có {len(moi)} kỳ hạn, bài có {len(cu)} dòng – '
                       f'{len(cu) - len(moi)} dòng cuối giữ nguyên.')
        for r, m in zip(cu, moi):
            thang, nam = m['ky_han'].split('/')
            gia = float(m['gia'].replace(',', ''))
            doi = float(m['thay_doi'].replace(',', '') or 0)
            if thap_phan:
                gia_txt, doi_txt = f'{gia:,.2f}', ('0.00' if doi == 0 else f'{doi:+.2f}')
            else:
                gia_txt, doi_txt = f'{round(gia):,}', ('0' if doi == 0 else f'{round(doi):+,}')
            ly = (f'{loai.capitalize()} kỳ hạn {m["ky_han"]}: {gia_txt}, thay đổi {doi_txt} '
                  f'(giacaphe.com, {tg.get("cap_nhat", "")}); mã hợp đồng theo quy ước tháng của sàn ICE')
            them(r[0], f'{tien_to}{MA_THANG[thang]}{nam}', tg.get('nguon'), ly)
            them(r[1], m['ky_han'], tg.get('nguon'), ly)
            them(r[2], gia_txt + hau_to, tg.get('nguon'), ly)
            them(r[3], doi_txt, tg.get('nguon'), ly)

    if 'Tây Nuy' in van:
        can.append('Bài gốc trên web có lỗi chính tả "Tây Nuy" (đúng: "Tây Nguyên") – theo quy tắc không sửa câu chữ, chỉ báo lại.')

    if a.kiem:
        for l in loi:
            print('LỖI:', l)
        print('Soát 3 bảng:', 'khớp hết' if not lech else f'{len(lech)} ô lệch: ' + '; '.join(lech))
        sys.exit(1 if lech or loi else 0)

    # Sửa từ cuối bài lên đầu để số thứ tự "lan" của các chỗ phía trên không bị lệch
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f'{len(sua)} ô cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for c in can:
        print('  cần duyệt:', c)
    for l in loi:
        print('LỖI:', l)
    sys.exit(1 if loi else 0)


if __name__ == '__main__':
    main()

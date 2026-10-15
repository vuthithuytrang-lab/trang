"""Tự lập sua.json cho bài "Giá cà phê sàn London và New York mới nhất hôm nay" của Techcombank.

Đọc:
  --xem       kết quả lệnh `cap_nhat.py xem ... bai1` (lưu ra file)
  --the-gioi  kết quả ../gia-ca-phe/lay_gia_the_gioi.js (giacaphe.com trực tuyến: Robusta London + Arabica New York)
rồi so 2 bảng (Tháng đáo hạn | Giá | Thay đổi so với phiên trước) với số mới, ghi ra --ra (sua.json).
--kiem: soát lại sau khi sửa. Quy tắc: xem README.md cùng thư mục.

Cách viết số của bài (khác bài "Giá cà phê hôm nay"):
  Robusta: tháng "11/2026", giá "3.490" (dấu chấm nghìn), thay đổi "-100 USD/tấn"
  Arabica: tháng "12/2026", giá "294.25" (2 số lẻ),       thay đổi "-10.20 cent/pound"
"""
import argparse, datetime, json, re, sys, unicodedata


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


def dang_giao_dich(now):
    if now.hour >= 15:
        return now.weekday() < 5
    if now.hour < 1 or (now.hour == 1 and now.minute <= 30):
        return 1 <= now.weekday() <= 5
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--the-gioi', required=True)
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()

    rows, van = doc_xem(a.xem)
    sua, can, loi, lech = [], [], [], []

    def them(o, moi, nguon, ly):
        cu, vt = o
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    tg = json.load(open(a.the_gioi, encoding='utf-8'))
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    if dang_giao_dich(now):
        can.append(f'Lúc chạy ({now:%H:%M %d/%m/%Y}) sàn London/New York đang giao dịch: số trong 2 bảng là giá trực tuyến '
                   f'({tg.get("cap_nhat", "")}), chưa phải giá chốt phiên.')

    # Hai bảng nằm theo thứ tự trong bài: bảng đầu (USD/tấn) = Robusta, bảng sau (cent/pound) = Arabica.
    # Dòng bảng = ô đầu dạng mm/yyyy, ô cuối có đơn vị.
    for loai, don_vi in [('robusta', 'USD/tấn'), ('arabica', 'cent/pound')]:
        moi = tg.get('bang', {}).get(loai) or []
        cu = [r for r in rows if re.fullmatch(r'\d\d/\d{4}', r[0][0]) and r[2][0].endswith(don_vi)]
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
            if loai == 'robusta':
                gia_txt = f'{round(gia):,}'.replace(',', '.')
                doi_txt = ('0' if doi == 0 else f'{round(doi):+,}'.replace(',', '.')) + ' USD/tấn'
            else:
                gia_txt = f'{gia:,.2f}'
                doi_txt = ('0.00' if doi == 0 else f'{doi:+.2f}') + ' cent/pound'
            ly = (f'{loai.capitalize()} kỳ hạn {m["ky_han"]}: {m["gia"]}, thay đổi {m["thay_doi"]} '
                  f'(giacaphe.com, {tg.get("cap_nhat", "")})')
            them(r[0], f'{thang}/20{nam}', tg.get('nguon'), ly)
            them(r[1], gia_txt, tg.get('nguon'), ly)
            them(r[2], doi_txt, tg.get('nguon'), ly)
            if doi == 0:
                can.append(f'{loai.capitalize()} {thang}/20{nam}: giá không đổi – bài chưa có mẫu ghi "không đổi", '
                           f'đã ghi "{doi_txt}", cần duyệt.')

    if 'chất lượng cà phê, sản lượng thu mua' in van:
        can.append('Câu "Lưu ý" dưới 2 bảng giá sàn nói về "chất lượng cà phê, sản lượng thu mua, chi phí vận chuyển… từng khu vực" '
                   '(câu của giá thu mua trong nước, không khớp với giá hợp đồng trên sàn) – theo quy tắc không sửa chữ, chỉ báo lại.')

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

"""Tự lập sua.json cho bài TCB "Vàng 10K là gì? Bao nhiêu tiền 1 chỉ? Có nên mua không".

  --xem  kết quả `cap_nhat.py xem ... bai1`   --gia  gia-10k.json (lay_gia_10k.js)
  --ra   sua.json                              --kiem soát lại sau khi sửa
Sửa: "Giá mua vào: X VND/chỉ", "Giá bán ra: Y VND/chỉ" theo PNJ "Vàng 416 (10K)"; "cập nhật đến ngày d/m/yyyy" -> hôm nay.
"""
import argparse, datetime, json, re, sys, unicodedata


def doc_xem(path):
    dong, van = [], ''
    for line in open(path, encoding='utf-8'):
        m = re.match(r'\s*\d+\.\s?(.*)$', line.rstrip('\n'))
        if not m:
            continue
        chu = unicodedata.normalize('NFC', m.group(1)).strip()
        if chu.startswith('| '):
            chu = chu[2:]
        dong.append((chu, len(van)))
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
    g = json.load(open(a.gia, encoding='utf-8')).get('pnj')
    # Ngày ghi trong bài: chạy từ 15h giờ VN trở đi -> ghi ngày hôm sau (+9 giờ là sang ngày mới)
    hn = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))) + datetime.timedelta(hours=9)
    ngay = f'{hn.day}/{hn.month}/{hn.year}'
    sua, can, lech, thay = [], [], [], set()

    def them(cu, vt, moi, nguon, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    if not g:
        can.append('Không đọc được giá PNJ – giữ nguyên giá và ngày cũ.')
    else:
        for chu, vt in dong:
            for nhan, gt in (('Giá mua vào: ', g['mua']), ('Giá bán ra: ', g['ban'])):
                m = re.search(re.escape(nhan) + r'([\d,]+)( VND/chỉ)', chu)
                if m:
                    thay.add(nhan)
                    them(m.group(0), vt + m.start(), f'{nhan}{gt:,}{m.group(2)}', g['nguon'],
                         f'PNJ – {g["san_pham"]}, cập nhật {g["cap_nhat"]}')
        if len(thay) < 2:
            can.append('Không thấy đủ 2 dòng "Giá mua vào:" / "Giá bán ra:" trong bài.')
        for chu, vt in dong:
            for m in re.finditer(r'(cập nhật đến ngày )(\d{1,2}/\d{1,2}/\d{4})', chu):
                them(m.group(0), vt + m.start(), m.group(1) + ngay, '', 'ngày cập nhật giá = hôm nay')

    if a.kiem:
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} chỗ lệch: ' + '; '.join(lech))
        sys.exit(1 if lech else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for x in sua:
        print('  ', x['tim'], '→', x['thay'])
    for c in can:
        print('  cần duyệt:', c)


if __name__ == '__main__':
    main()

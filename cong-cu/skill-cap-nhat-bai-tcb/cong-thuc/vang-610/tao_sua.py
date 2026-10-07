"""Tự lập sua.json cho bài TCB "Vàng 610 là vàng gì? Là bao nhiêu K? Giá vàng 610 hôm nay".

  --xem  kết quả `cap_nhat.py xem ... bai1`   --gia  gia-610.json (lay_gia_610.js)
  --ra   sua.json                              --kiem soát lại sau khi sửa
Nguồn duy nhất: PNJ "Vàng 610 (14.6K)" -> chỉ có 1 mức giá mua và 1 mức giá bán, nên các khoảng "từ … đến …" trong bài
được viết thành 1 mức (ghi rõ "theo PNJ"):
  - Tóm tắt: "Giá vàng 610 (tháng mm/yyyy): Mua vào khoảng a – b triệu VNĐ/chỉ, bán ra khoảng c – d triệu VNĐ/chỉ"
  - Mục 3:   "Giá mua vào: Khoảng X VND/chỉ đến Y VND/chỉ" / "Giá bán ra: …"; "tháng mm/yyyy" -> tháng này.
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


def trieu(v, dau):
    """8,632,000 -> '8.63' hoặc '8,63' theo dấu thập phân bài đang dùng ở chỗ đó."""
    return f'{v / 1e6:.2f}'.replace('.', dau)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    dong, van = doc_xem(a.xem)
    g = json.load(open(a.gia, encoding='utf-8')).get('pnj')
    hn = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    thang = f'{hn.month:02d}/{hn.year}'
    sua, can, lech = [], [], []

    def them(cu, vt, moi, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': g['nguon'] if g else '', 'ly_do': ly, '_vt': vt})

    if not g:
        can.append('Không đọc được giá PNJ – giữ nguyên toàn bộ giá và tháng.')
    else:
        ly = f'PNJ – {g["san_pham"]}: mua {g["mua"]:,} / bán {g["ban"]:,} đ/chỉ, cập nhật {g["cap_nhat"]}'
        n = 0
        for chu, vt in dong:
            m = re.search(r'(Giá vàng 610 \(tháng )(\d{2}/\d{4})(\): Mua vào khoảng )([\d.,]+ – [\d.,]+|[\d.,]+)( triệu VNĐ/chỉ, bán ra khoảng )([\d.,]+ – [\d.,]+|[\d.,]+)( triệu VNĐ/chỉ)', chu)
            if m:
                gr = list(m.groups())
                # bài dùng dấu chấm thập phân ("6.78"); tóm tắt cũ lẫn "6,43" -> thống nhất dấu chấm
                gr[1], gr[3], gr[5] = thang, trieu(g['mua'], '.'), trieu(g['ban'], '.')
                them(m.group(0), vt + m.start(), ''.join(gr), ly + ' (tóm tắt: 1 nguồn nên ghi 1 mức)'); n += 1
            for nhan, gt in (('Giá mua vào: Khoảng ', g['mua']), ('Giá bán ra: Khoảng ', g['ban'])):
                m = re.search(re.escape(nhan) + r'([\d,]+ VND/chỉ)( đến [\d,]+ VND/chỉ)?( \(theo PNJ\))?', chu)
                if m:
                    them(m.group(0), vt + m.start(), f'{nhan}{gt:,} VND/chỉ (theo PNJ)', ly); n += 1
            for m in re.finditer(r'(tháng )(\d{2}/\d{4})', chu):
                if 'Giá vàng 610 (tháng' in chu[max(0, m.start() - 20):m.start() + 6]:
                    continue
                them(m.group(0), vt + m.start(), m.group(1) + thang, 'tháng khảo sát = tháng này')
        if n < 3:
            can.append(f'Chỉ thấy {n}/3 chỗ ghi giá vàng 610 trong bài – kiểm tra lại cấu trúc bài.')
        can.append('Bài chỉ có nguồn PNJ (1 mức giá) nên các khoảng "từ … đến …" được ghi thành 1 mức, kèm "(theo PNJ)" ở mục 3. '
                   'Muốn giữ dạng khoảng thì cần thêm nguồn thương hiệu khác.')

    if a.kiem:
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} chỗ lệch: ' + '; '.join(lech))
        sys.exit(1 if lech else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for x in sua:
        print('  ', x['tim'][:90], '→', x['thay'][:90])


if __name__ == '__main__':
    main()

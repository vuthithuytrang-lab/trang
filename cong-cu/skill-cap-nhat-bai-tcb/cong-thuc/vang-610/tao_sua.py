"""Tự lập sua.json cho bài TCB "Vàng 610 là vàng gì?… Giá vàng 610 hôm nay".

  --xem  kết quả `cap_nhat.py xem ... bai1`   --gia  gia-610.json (lay_gia_610.js: PNJ + SJC 61%)
  --ra   sua.json                              --kiem soát lại sau khi sửa
CHỈ CẬP NHẬT SỐ, GIỮ NGUYÊN CÂU CHỮ (Trang dặn 14/10/2026):
  - Mục 3 "Giá mua vào: Khoảng X VND/chỉ đến Y VND/chỉ" -> X = thấp nhất, Y = cao nhất trong các nguồn (PNJ, SJC 61%).
    Thiếu nguồn (chỉ còn 1) -> giữ nguyên dòng đó, ghi cần duyệt. Không bao giờ đổi thành 1 mức / thêm chữ "(theo …)".
  - Tóm tắt "Mua vào khoảng a – b triệu …": giữ dạng như bài (khoảng thì min – max, 1 mức thì giá PNJ), giữ dấu thập phân của bài.
  - "tháng mm/yyyy" -> tháng này.
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


def trieu(v, cu):
    """7,611,000 -> '7.61' (hoặc '7,61' nếu số cũ ở chỗ đó dùng dấu phẩy)."""
    return f'{v / 1e6:.2f}'.replace('.', ',' if re.fullmatch(r'\d+,\d+', cu.strip()) else '.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    dong, van = doc_xem(a.xem)
    gia = json.load(open(a.gia, encoding='utf-8'))
    co = {k: v for k, v in gia.items() if v}
    g = co.get('pnj')
    # Ngày ghi trong bài: chạy từ 15h giờ VN trở đi -> ghi ngày hôm sau (+9 giờ là sang ngày mới)
    hn = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))) + datetime.timedelta(days=1)  # Trang chốt 21/10/2026: luôn ghi ngày hôm sau
    thang = f'{hn.month:02d}/{hn.year}'
    sua, can, lech = [], [], []
    nguon = ', '.join(v['nguon'] for v in co.values())
    ly = '; '.join(f'{k.upper()} – {v["san_pham"]}: mua {v["mua"]:,} / bán {v["ban"]:,} đ/chỉ, cập nhật {v["cap_nhat"]}' for k, v in co.items())

    def them(cu, vt, moi, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    def khoang(loai, cu):
        """Giá mới cho 1 ô theo đúng dạng ô cũ: '7.64 – 8.32' -> min – max; '7.64' -> giá PNJ."""
        vs = [v[loai] for v in co.values()]
        if '–' in cu or ' - ' in cu:
            a_, b_ = re.split(r'\s*[–-]\s*', cu)
            return f'{trieu(min(vs), a_)} – {trieu(max(vs), b_)}' if len(vs) >= 2 else None
        return trieu(g[loai], cu) if g else None

    if not co:
        can.append('Không đọc được nguồn nào (PNJ, SJC) – giữ nguyên toàn bộ giá và tháng.')
    else:
        n = 0
        for chu, vt in dong:
            m = re.search(r'(Giá vàng 610 \(tháng )(\d{2}/\d{4})(\): Mua vào khoảng )([\d.,]+ – [\d.,]+|[\d.,]+)( triệu VNĐ/chỉ, bán ra khoảng )([\d.,]+ – [\d.,]+|[\d.,]+)( triệu VNĐ/chỉ)', chu)
            if m:
                gr = list(m.groups()); n += 1
                mua, ban = khoang('mua', gr[3]), khoang('ban', gr[5])
                if mua and ban:
                    gr[1], gr[3], gr[5] = thang, mua, ban
                    them(m.group(0), vt + m.start(), ''.join(gr), ly + ' (tóm tắt: giữ dạng của bài)')
                else:
                    can.append('Tóm tắt: không đủ nguồn để cập nhật theo đúng dạng của bài – giữ nguyên.')
            for nhan, loai in (('Giá mua vào: Khoảng ', 'mua'), ('Giá bán ra: Khoảng ', 'ban')):
                m = re.search(re.escape(nhan) + r'([\d,]+)( VND/chỉ)(?:( ?đến ?)([\d,]+)( VND/chỉ))?', chu)
                if not m:
                    continue
                n += 1
                vs = [v[loai] for v in co.values()]
                if m.group(3):                                   # dạng khoảng: thấp nhất đến cao nhất
                    if len(vs) < 2:
                        can.append(f'{nhan.strip()} bài ghi dạng khoảng nhưng chỉ đọc được 1 nguồn – giữ nguyên.')
                        continue
                    moi = f'{nhan}{min(vs):,}{m.group(2)}{m.group(3)}{max(vs):,}{m.group(5)}'
                else:                                            # bài ghi 1 mức -> giá PNJ
                    if not g:
                        continue
                    moi = f'{nhan}{g[loai]:,}{m.group(2)}'
                them(m.group(0), vt + m.start(), moi, ly)
            for m in re.finditer(r'(tháng )(\d{2}/\d{4})', chu):
                if 'Giá vàng 610 (tháng' in chu[max(0, m.start() - 20):m.start() + 6]:
                    continue
                them(m.group(0), vt + m.start(), m.group(1) + thang, 'tháng khảo sát = tháng này')
        if n < 3:
            can.append(f'Chỉ thấy {n}/3 chỗ ghi giá vàng 610 trong bài – kiểm tra lại cấu trúc bài.')
        if len(co) < 2:
            can.append('Chỉ đọc được 1 nguồn – các chỗ ghi dạng khoảng "từ … đến …" giữ nguyên.')

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

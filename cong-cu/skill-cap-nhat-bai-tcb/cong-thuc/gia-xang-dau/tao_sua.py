"""Tự lập sua.json cho bài "Giá xăng dầu hôm nay" của Techcombank.

  --xem   kết quả `cap_nhat.py xem ... bai1` (lưu ra file)
  --gia   gia.json: số mới từng hệ thống (xem gia-mau.json)
  --ra    nơi ghi sua.json      |  --kiem  soát lại sau khi sửa (mọi ô phải khớp)

Bảng nào trong bài thuộc hệ thống nào: theo đề mục đứng trước bảng (1.1 Petrolimex, 1.2 PVOIL, 1.3 Mipec).
Hệ thống nào trong gia.json là null (nguồn không đọc được) -> bảng đó giữ nguyên + ghi cần duyệt.
"""
import argparse, json, re, sys, unicodedata


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def ma_hang(ten):
    t = ten.lower()
    if 'dầu hỏa' in t or 'dầu hoả' in t:
        return 'dau_hoa'
    if '0,001s' in t or '0.001s' in t:
        return 'do_0001'
    if '0,05s' in t or '0.05s' in t:
        return 'do_005'
    if '95-v' in t or ('95' in t and 'mức 5' in t):
        return 'e10_95_v'
    if '95-iii' in t:
        return 'e10_95_iii'
    if '92' in t:
        return 'e5_92'
    return None


def doc_xem(path):
    """Các dòng (chữ, vị trí, có phải ô bảng) + toàn văn."""
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


def so(n):
    return f'{n:,}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    dong, van = doc_xem(a.xem)
    gia = json.load(open(a.gia, encoding='utf-8'))
    sua, can, loi, lech = [], [], [], []

    def them(cu, vt, moi, nguon, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    # Gom bảng: mỗi dòng không phải ô + các ô ngay sau = 1 hàng; gán hệ thống theo đề mục gần nhất
    he, hang = None, []
    for i, (chu, vt, la_o) in enumerate(dong):
        if not la_o:
            h = chu.lower()
            if re.match(r'1\.\d+\.', chu):
                he = 'petrolimex' if 'petrolimex' in h else 'pvoil' if 'pvoil' in h else 'mipec' if 'mipec' in h else None
            elif re.match(r'\d+\.\s', chu):
                he = None
            cells = []
            j = i + 1
            # ô bảng thường có dấu '|'; một số bản bài (từ 06/11/2026) để ô số thành dòng riêng → nhận cả dòng chỉ có số
            while j < len(dong) and (dong[j][2] or re.fullmatch(r'[\d.,]+', dong[j][0].strip())):
                cells.append(dong[j]); j += 1
            if he and cells:
                hang.append((he, (chu, vt), cells))

    da_bao = set()
    for he, (ten, _), cells in hang:
        mh = ma_hang(ten)
        if not mh:
            continue
        g = gia.get(he)
        if not g:
            if he not in da_bao:
                can.append(f'Bảng {he.upper()}: không đọc được nguồn ({(gia.get("_ghi_chu") or {}).get(he, "")}) – giữ nguyên số cũ, cần bạn kiểm tra.')
                da_bao.add(he)
            continue
        if mh not in g['gia']:
            can.append(f'Bảng {he.upper()}: nguồn không có "{ten}" – giữ nguyên.')
            continue
        moi = g['gia'][mh]
        for k, (chu, vt, _) in enumerate(cells[:2]):
            if k < len(moi) and moi[k] is not None and re.fullmatch(r'[\d.,]+', chu):
                them(chu, vt, so(moi[k]), g['nguon'],
                     f'{he.upper()} {g["ky"]}: {ten} {"Vùng " + str(k + 1) if len(cells) > 1 else ""} = {so(moi[k])} đ/lít')

    # Câu hỏi thường gặp: số trong câu lấy theo Petrolimex
    p = gia.get('petrolimex')
    if p:
        P = {k: v for k, v in p['gia'].items()}
        thieu = [k for k in ('e10_95_iii', 'e5_92', 'e10_95_v', 'do_0001') if k not in P]
        for k in thieu:
            P[k] = [None, None]          # thiếu nguồn → câu hỏi đáp chứa mặt hàng này giữ nguyên
        mau = [
            (r'(1 lít xăng E10 RON 95-III có giá khoảng )([\d,]+)( VND/lít)', [P['e10_95_iii'][0]], 'E10 RON 95-III Vùng 1'),
            (r'(1 lít xăng E5 RON 92-II có giá khoảng )([\d,]+)( VND/lít)', [P['e5_92'][0]], 'E5 RON 92-II Vùng 1'),
            (r'(Giá E10 RON 95-V là )([\d,]+)( VND/lít tại Vùng 1 và )([\d,]+)( VND/lít tại Vùng 2; E10 RON 95-III lần lượt là )([\d,]+)( VND/lít và )([\d,]+)( VND/lít)',
             P['e10_95_v'] + P['e10_95_iii'], 'RON 95 Vùng 1/Vùng 2'),
            (r'(Giá dầu DO 0,001S-V là )([\d,]+)( VND/lít tại Vùng 1 và )([\d,]+)( VND/lít tại Vùng 2)', P['do_0001'], 'DO 0,001S-V'),
        ]
        for mau_re, so_moi, ten in mau:
            if None in so_moi:
                can.append(f'Câu hỏi thường gặp về {ten}: thiếu nguồn giá mới – giữ nguyên.')
                continue
            for chu, vt, _ in dong:
                m = re.search(mau_re, chu)
                if not m:
                    continue
                cu = m.group(0)
                nhom = list(m.groups())
                for k, v in enumerate(so_moi):
                    nhom[1 + 2 * k] = so(v)
                them(cu, vt + m.start(), ''.join(nhom), p['nguon'], f'Câu hỏi thường gặp – {ten} theo Petrolimex {p["ky"]}')
                break
            else:
                can.append(f'Không thấy câu hỏi thường gặp về {ten} để cập nhật.')

    # Gạch đầu dòng dạng "Xăng E10 RON 95-V: 21,156 VND/lít (Vùng 1) và 21,710 VND/lít (Vùng 2)" (thêm 06/11/2026)
    if p:
        for chu, vt, _ in dong:
            for m in re.finditer(r'((?:Xăng|Dầu)[^:]{2,40}):\s*([\d,.]+)(\s*VND/lít \(Vùng 1\) và )([\d,.]+)(\s*VND/lít \(Vùng 2\))', chu):
                mh = ma_hang(m.group(1))
                if not mh or mh not in p['gia'] or None in p['gia'][mh][:2] or len(p['gia'][mh]) < 2:
                    can.append(f'Gạch đầu dòng "{m.group(1).strip()}": thiếu nguồn giá mới – giữ nguyên.')
                    continue
                v1, v2 = p['gia'][mh][:2]
                them(m.group(2), vt + m.start(2), so(v1), p['nguon'], f'Gạch đầu dòng – {m.group(1).strip()} Vùng 1 theo Petrolimex {p["ky"]}')
                them(m.group(4), vt + m.start(4), so(v2), p['nguon'], f'Gạch đầu dòng – {m.group(1).strip()} Vùng 2 theo Petrolimex {p["ky"]}')

    # Lưới an toàn: mọi số dạng giá (xx,xxx) trong bài phải hoặc đã được sửa, hoặc trùng một giá mới
    moi_tat_ca = {so(v) for g in (gia.get(h) for h in ('petrolimex', 'pvoil', 'mipec')) if g for vs in g['gia'].values() for v in vs if v}
    da_sua = {x['tim'] for x in sua}
    con = []
    for chu, vt, _ in dong:
        for m in re.finditer(r'(?<![\d,.])(\d{2}[,.]\d{3})(?![\d,.])', chu):
            x = m.group(1)
            if x not in moi_tat_ca and x.replace('.', ',') not in moi_tat_ca and x not in da_sua and not any(x in t for t in da_sua):
                con.append(x)
    if con:
        can.append('SỐ GIÁ CHƯA CẬP NHẬT (chưa có quy tắc sửa): ' + ', '.join(dict.fromkeys(con)) + ' – cần sửa tay / thêm quy tắc.')

    if re.search(r'\n5\.1\. ', van) and re.search(r'\n5\.3\. ', van) and not re.search(r'\n5\.2\. ', van):
        can.append('Mục 5 trong bài gốc đánh số 5.1 rồi nhảy sang 5.3 (không có 5.2) – không sửa, chỉ báo lại.')

    if a.kiem:
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} chỗ lệch: ' + '; '.join(lech))
        sys.exit(1 if lech else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for c in can:
        print('  cần duyệt:', c)


if __name__ == '__main__':
    main()

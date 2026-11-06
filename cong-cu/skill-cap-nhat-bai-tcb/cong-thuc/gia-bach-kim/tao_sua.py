"""Tự lập sua.json cho bài TCB "Giá bạch kim" (không dùng mạng, không dùng AI).

  --xem  kết quả `cap_nhat.py xem ... bai1`     --gia  cap-nhat/gia.json (lay_gia.py)
  --goc  cap-nhat/tam/bai1.html (không dùng, để khớp khung chung)
  --ra   sua.json                                --kiem soát lại sau khi sửa (in "khớp hết")

Mọi số viết vào bài lấy THẲNG từ gia.json (Yahoo PL=F); chỉ đổi số/ngày, không đổi chữ.
  1) Bảng "Ngày | Giá (USD/oz) | Thay đổi (USD/oz)": dòng 1 = phiên mới nhất, … (kể cả khi bài web gộp dòng thành
     "30/10/2026 | 1,522.00 | -100.00 |"). Giá 2 số lẻ, dấu nghìn ',', thay đổi luôn có dấu +/-.
  2) Câu "… giá bạch kim đang được tham khảo ở mức khoảng X USD/oz, giảm/tăng khoảng Y USD/oz so với phiên trước":
     X = giá phiên mới nhất (2 số lẻ), Y = |thay đổi| làm tròn số nguyên (đúng dạng bài), chữ tăng/giảm theo dấu + cần duyệt.
  3) Lưới an toàn: số kiểu giá còn sót không khớp số nguồn → "SỐ GIÁ CHƯA CẬP NHẬT".
"""
import argparse, json, re, sys, unicodedata

RE_DATE = re.compile(r'^\d{1,2}/\d{1,2}/\d{4}$')
RE_CAU = re.compile(r'(mức khoảng )(\d[\d.,]*)( USD/oz, )(tăng|giảm)( khoảng )(\d[\d.,]*)( USD/oz so với phiên trước)')
RE_GIA = re.compile(r'(?<![\d/])\d{1,3}(?:,\d{3})+(?:\.\d+)?(?![\d/])|(?<![\d/,.])\d+\.\d{2}(?![\d/])|\d[\d.,]*\s*USD')


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


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


def f2(x):
    return f'{x:,.2f}'


def d2(x):
    return f'{x:+,.2f}'


def nguyen(x):
    """làm tròn nửa lên về số nguyên (đúng dạng "khoảng 11 USD/oz")"""
    return int(abs(x) + 0.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--goc')
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    dong, van = doc_xem(a.xem)
    try:
        gia = json.load(open(a.gia, encoding='utf-8'))
    except (OSError, ValueError):
        gia = None
    ls = (gia or {}).get('lich_su') or []
    NG = (gia or {}).get('nguon', '')
    sua, can, lech, da_xu_ly = [], [], [], set()

    def them(cu, vt, moi, ly):
        da_xu_ly.add(vt)
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': NG, 'ly_do': ly, '_vt': vt})

    if not ls:
        can.append('Yahoo Finance PL=F không đọc được (bị chặn hoặc đổi giao diện) – giữ nguyên MỌI số giá và ngày trong bảng/đoạn văn, cần cập nhật tay.')

    # 1) Bảng giá theo ngày
    co_bang = False
    for i, (chu, vt, la_o) in enumerate(dong):
        if la_o or chu != 'Ngày' or i + 2 >= len(dong):
            continue
        if not (dong[i + 1][2] and dong[i + 1][0].startswith('Giá') and dong[i + 2][2] and dong[i + 2][0].startswith('Thay đổi')):
            continue
        co_bang = True
        hang, j = [], i + 3
        while j < len(dong):
            c, v, o = dong[j]
            m = re.fullmatch(r'(\d{1,2}/\d{1,2}/\d{4}) \| ([\d.,]+) \| ([+\-−]?[\d.,]+) \|?', c.strip()) if not o else None
            if m:                                    # bài web gộp dòng thành 1 chữ "ngày | giá | đổi |"
                hang.append(tuple((m.group(g), v + m.start(g), True) for g in (1, 2, 3)))
                j += 1
            elif j + 2 < len(dong) and not o and RE_DATE.match(c) and dong[j + 1][2] and dong[j + 2][2]:
                hang.append((dong[j], dong[j + 1], dong[j + 2]))
                j += 3
            else:
                break
        for k, (o_ngay, o_gia, o_doi) in enumerate(hang):
            da_xu_ly.update({o_ngay[1], o_gia[1], o_doi[1]})
            if k >= len(ls):
                if ls:
                    can.append(f'Bảng giá theo ngày, dòng {k + 1} ({o_ngay[0]} {o_gia[0]} {o_doi[0]}): nguồn không đủ phiên – giữ nguyên dòng này.')
                continue
            h = ls[k]
            ly = f'Yahoo Finance PL=F (NYMEX), phiên thứ {k + 1} từ mới nhất: "{h["chu_nguon"]}"'
            them(o_ngay[0], o_ngay[1], h['ngay'], ly)
            them(o_gia[0], o_gia[1], f2(h['gia']), ly)
            them(o_doi[0], o_doi[1], d2(h['thay_doi']), ly)
        if hang and ls:
            can.append(f'Bảng giá theo ngày: {len(hang)} dòng = {len(hang)} phiên mới nhất của hợp đồng bạch kim NYMEX '
                       f'({", ".join(h["ngay"] for h in ls[:len(hang)])}); nguồn không có ngày nghỉ nên ngày có thể không liền nhau. '
                       'Số của nguồn có thể lệch vài USD so với số bài cũ vì khác nguồn (bài cũ có thể lấy giá giao ngay).')
            if gia.get('cap_nhat'):
                can.append(f'Phiên mới nhất ({ls[0]["ngay"]}) đọc lúc {gia["cap_nhat"]}; nếu thị trường còn mở, giá là giá đang giao dịch, chưa phải giá chốt phiên.')
    if ls and not co_bang:
        can.append('Không thấy bảng "Ngày | Giá (USD/oz) | Thay đổi (USD/oz)" trong bài – bài đổi bố cục, cần xem lại.')

    # 2) Câu giá mới nhất + mức thay đổi so với phiên trước
    thay_cau = False
    for chu, vt, la_o in dong:
        m = RE_CAU.search(chu)
        if not m:
            continue
        thay_cau = True
        da_xu_ly.add(vt)
        if not ls:
            continue
        h = ls[0]
        g = list(m.groups())
        cu = list(g)
        g[1] = f2(h['gia'])
        ly = f'Yahoo Finance PL=F (NYMEX) phiên {h["ngay"]}: "{h["chu_nguon"]}"'
        y = h['thay_doi']
        if nguyen(y) == 0:
            can.append(f'Câu giá: nguồn ghi thay đổi {y:+.2f} (làm tròn 0) – câu "{cu[3]} khoảng {cu[5]} USD/oz" không viết được đúng dạng, giữ chiều và mức cũ, cần duyệt.')
        else:
            g[3] = 'giảm' if y < 0 else 'tăng'
            g[5] = str(nguyen(y))
            ly += f'; thay đổi so với phiên trước {y:+.2f}, làm tròn {g[5]}'
            if g[3] != cu[3]:
                can.append(f'Câu giá: chữ chỉ chiều đổi "{cu[3]}" → "{g[3]}" theo nguồn ({y:+.2f} USD/oz so với phiên trước) – đọc lại câu.')
        can.append(f'Câu giá: mức thay đổi trong câu là số nguyên làm tròn từ {y:+.2f}.')
        them(m.group(0), vt + m.start(), ''.join(g), ly)
    if ls and not thay_cau:
        can.append('Không thấy câu "… mức khoảng X USD/oz, tăng/giảm khoảng Y USD/oz so với phiên trước" – bài đổi câu chữ, giữ nguyên, cần cập nhật tay.')

    # 3) Đối chiếu nguồn thứ hai
    if ls:
        for ten, v in ((gia.get('doi_chieu') or {}).items()):
            if not v:
                continue
            if ten == 'futures_pl1':
                lech_pt = abs(v['gia'] - gia['gia_hien_tai']) / gia['gia_hien_tai'] * 100 if gia.get('gia_hien_tai') else 0
                if lech_pt > 1:
                    can.append(f'Đối chiếu TradingView NYMEX:PL1! {f2(v["gia"])} lệch {lech_pt:.1f}% so với Yahoo {f2(gia["gia_hien_tai"])} – liếc lại nguồn.')

    # 4) Lưới an toàn: số kiểu giá chưa xử lý và không bằng số nguồn
    hop_le = set()
    for h in ls:
        hop_le.update({f2(h['gia']), d2(h['thay_doi']), str(nguyen(h['thay_doi']))})
    for chu, vt, la_o in dong:
        if vt in da_xu_ly:
            continue
        for m in RE_GIA.finditer(chu):
            s = re.sub(r'\s*USD$', '', m.group(0))
            if s in hop_le or s.lstrip('+-') in hop_le:
                continue
            can.append(f'SỐ GIÁ CHƯA CẬP NHẬT: "…{chu[max(0, m.start() - 40):m.end() + 12]}" – số này công thức không nhận ra và không bằng số nguồn nào, giữ nguyên, cần đọc lại và cập nhật tay.')

    if a.kiem:
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} chỗ lệch: ' + '; '.join(lech))
        sys.exit(1 if lech else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for x in sua:
        print('  ', x['tim'][:70], '→', x['thay'][:70])
    for c in can:
        print('  cần duyệt:', c)


if __name__ == '__main__':
    main()

"""Tự lập sua.json cho bài TCB "Giá cà phê Đắk Lắk hôm nay" (không dùng mạng, không dùng AI).

  --xem  kết quả `cap_nhat.py xem ... bai1`      --gia  cap-nhat/gia.json (lay_gia.js)
  --goc  cap-nhat/tam/bai1.html (bài gốc, để trả lại ngày "cập nhật trong ngày" khi không có số mới)
  --ra   sua.json                                 --kiem soát lại sau khi sửa (in "khớp hết")

Mọi con số viết vào bài lấy THẲNG từ gia.json (số đọc được trên trang nguồn trong lần chạy này); không tự tính, không đoán.
  1) Bảng "Ngày | Giá (VND/kg) | Thay đổi (VND/kg)": thay từng dòng bằng các ngày mới nhất trên giacaphe.com Đắk Lắk
     (dòng 1 = ngày mới nhất …), đúng ngày / giá / mức thay đổi như nguồn. Không có lịch sử giacaphe → giữ nguyên bảng.
  2) Đoạn "… tại Đắk Lắk đang được tham khảo ở mức khoảng X VND/kg, tăng/giảm khoảng Y VND/kg so với phiên trước":
     X = giá Đắk Lắk mới nhất (giacaphe, dự phòng Nhà Bè Agri); Y = mức thay đổi giacaphe ghi cho ngày đó (Nhà Bè không có
     mức so với phiên trước → giữ Y + cần duyệt). Chữ tăng/giảm đổi theo dấu của Y (là chiều của chính con số) + cần duyệt.
  3) "Lâm Đồng / Gia Lai / Đắk Nông khoảng X VND/kg": giá mới nhất từng tỉnh (giacaphe, dự phòng Nhà Bè Agri).
"""
import argparse, html, json, re, sys, unicodedata

TINH = {'Đắk Lắk': 'dak_lak', 'Lâm Đồng': 'lam_dong', 'Gia Lai': 'gia_lai', 'Đắk Nông': 'dak_nong'}
RE_DATE = re.compile(r'^\d{2}/\d{2}/\d{4}$')
RE_DL = re.compile(r'(tại Đắk Lắk[^.]*?mức khoảng )(\d[\d.,]*)( VND/kg, )(tăng|giảm)( khoảng )(\d[\d.,]*)( VND/kg so với phiên trước)')
RE_TINH = re.compile(r'(Lâm Đồng|Gia Lai|Đắk Nông)( khoảng )(\d[\d.,]*)( VND/kg)')
RE_NGAY_CN = re.compile(r'(cập nhật trong ngày )(\d{2}/\d{2}/\d{4})')


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


def viet(x, cu, dau=False):
    """viết số nguyên x theo kiểu số cũ: dấu nghìn ',' (hoặc '.' nếu số cũ dùng '.'); dau=True → luôn có +/-"""
    ng = '.' if re.search(r'\d\.\d{3}', cu) and ',' not in cu else ','
    s = f'{abs(x):,}'.replace(',', ng)
    if dau:
        return ('-' if x < 0 else '+') + s
    return ('-' if x < 0 else '') + s


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
        gia = {}
    gc = gia.get('giacaphe') or {}
    nb = gia.get('nha_be') or {}
    sua, can, lech, da_xu_ly = [], [], [], set()

    def them(cu, vt, moi, nguon, ly):
        da_xu_ly.add(vt)
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    def hien_tai(ten):
        """giá mới nhất 1 tỉnh: giacaphe trước, Nhà Bè Agri dự phòng"""
        ma = TINH[ten]
        v = gc.get(ma)
        if v:
            return {'gia': v['gia'], 'ngay': v['ngay'], 'nguon': v['nguon'], 'thay_doi': v['thay_doi'],
                    'chu': v['lich_su'][0]['chu_nguon'], 'cap_nhat': v['cap_nhat'], 'du_phong': False}
        v = nb.get(ma)
        if v:
            return {'gia': v['gia'], 'ngay': v.get('ngay') or '?', 'nguon': v['nguon'], 'thay_doi': None,
                    'chu': v['chu_nguon'], 'cap_nhat': v['cap_nhat'], 'du_phong': True}
        return None

    for ten in TINH:
        if not gc.get(TINH[ten]):
            can.append(f'giacaphe.com {ten} không đọc được (bị chặn hoặc đổi giao diện)'
                       + (' – đã dùng giá Nhà Bè Agri (cùng giá nhân xô trong ngày) cho giá mới nhất.' if nb.get(TINH[ten])
                          else ' và Nhà Bè Agri cũng không có số – giữ nguyên giá cũ của tỉnh này.'))

    # 1) Bảng giá theo ngày (Đắk Lắk) – nhận bảng theo tiêu đề cột, dòng theo ô ngày
    dl_ls = (gc.get('dak_lak') or {}).get('lich_su') or []
    for i, (chu, vt, la_o) in enumerate(dong):
        if la_o or chu != 'Ngày' or i + 2 >= len(dong):
            continue
        if not (dong[i + 1][2] and dong[i + 1][0].startswith('Giá') and dong[i + 2][2] and dong[i + 2][0].startswith('Thay đổi')):
            continue
        hang, j = [], i + 3
        while j + 2 < len(dong) and not dong[j][2] and RE_DATE.match(dong[j][0]) and dong[j + 1][2] and dong[j + 2][2]:
            hang.append((dong[j], dong[j + 1], dong[j + 2]))
            j += 3
        for k, (o_ngay, o_gia, o_doi) in enumerate(hang):
            da_xu_ly.update({o_ngay[1], o_gia[1], o_doi[1]})
            if k >= len(dl_ls):
                can.append(f'Bảng giá theo ngày, dòng {k + 1} ({o_ngay[0]} {o_gia[0]} {o_doi[0]}): nguồn giacaphe.com Đắk Lắk '
                           f'{"không đọc được" if not dl_ls else "không đủ ngày"} – giữ nguyên dòng này.')
                continue
            h = dl_ls[k]
            ly = f'giacaphe.com Đắk Lắk, bảng "Giá cà phê Đắk Lắk theo ngày", dòng {k + 1}: "{h["chu_nguon"]}"'
            them(o_ngay[0], o_ngay[1], h['ngay'], gc['dak_lak']['nguon'], ly)
            them(o_gia[0], o_gia[1], viet(h['gia'], o_gia[0]), gc['dak_lak']['nguon'], ly)
            them(o_doi[0], o_doi[1], viet(h['thay_doi'], o_doi[0], dau=True), gc['dak_lak']['nguon'], ly)
        if hang and dl_ls:
            ngay_moi = [h['ngay'] for h in dl_ls[:len(hang)]]
            can.append(f'Bảng giá theo ngày: {len(hang)} dòng = {len(hang)} ngày mới nhất trên giacaphe.com ({", ".join(ngay_moi)}); '
                       'nguồn không ghi ngày nghỉ (chủ nhật, ngày không giao dịch) nên các ngày có thể không liền nhau.')

    # 2) Đoạn giá Đắk Lắk + mức thay đổi so với phiên trước
    dl = hien_tai('Đắk Lắk')
    for chu, vt, la_o in dong:
        m = RE_DL.search(chu)
        if not m:
            continue
        da_xu_ly.add(vt)
        if not dl:
            can.append('Đoạn giá Đắk Lắk ("… mức khoảng ' + m.group(2) + ' VND/kg …"): không đọc được nguồn nào – giữ nguyên số và ngày cũ.')
            continue
        g = list(m.groups())
        cu = list(g)
        g[1] = viet(dl['gia'], cu[1])
        ly = f'{"Nhà Bè Agri (dự phòng)" if dl["du_phong"] else "giacaphe.com"} Đắk Lắk ngày {dl["ngay"]}: "{dl["chu"]}" (cập nhật {dl["cap_nhat"]})'
        y = dl['thay_doi']
        if y is None:
            can.append(f'Đoạn giá Đắk Lắk: giá đã lấy theo Nhà Bè Agri, nhưng nguồn này không có mức thay đổi so với phiên trước '
                       f'– giữ nguyên "{cu[3]} khoảng {cu[5]} VND/kg so với phiên trước", cần đọc lại câu.')
        elif y == 0:
            can.append(f'Đoạn giá Đắk Lắk: nguồn ghi giá không đổi so với phiên trước – câu "{cu[3]} khoảng {cu[5]} VND/kg" '
                       'không viết được đúng dạng, giữ nguyên, cần duyệt.')
        else:
            g[3] = 'giảm' if y < 0 else 'tăng'
            g[5] = viet(abs(y), cu[5])
            ly += f'; mức thay đổi so với phiên trước theo nguồn: {y:+,}'
            if g[3] != cu[3]:
                can.append(f'Đoạn giá Đắk Lắk: chữ chỉ chiều đổi "{cu[3]}" → "{g[3]}" theo nguồn ({y:+,} đ/kg so với phiên trước) – đọc lại câu.')
        them(m.group(0), vt + m.start(), ''.join(g), dl['nguon'], ly)

    # 3) Các tỉnh lân cận
    moi = {}
    for chu, vt, la_o in dong:
        for m in RE_TINH.finditer(chu):
            da_xu_ly.add(vt)
            t = hien_tai(m.group(1))
            if not t:
                continue
            moi[m.group(1)] = t['gia']
            g = list(m.groups())
            g[2] = viet(t['gia'], g[2])
            them(m.group(0), vt + m.start(), ''.join(g), t['nguon'],
                 f'{"Nhà Bè Agri (dự phòng)" if t["du_phong"] else "giacaphe.com"} {m.group(1)} ngày {t["ngay"]}: "{t["chu"]}" (cập nhật {t["cap_nhat"]})')
            if dl and t['ngay'] != dl['ngay']:
                can.append(f'{m.group(1)}: số mới nhất trên nguồn là ngày {t["ngay"]}, Đắk Lắk là ngày {dl["ngay"]} – câu "trong cùng ngày" có thể không đúng.')

    # 4) Câu so sánh "giá Đắk Lắk đang ở mức tương đối cao"
    if dl and moi and any('tương đối cao' in c for c, _, _ in dong):
        cao_hon = [k for k, v in moi.items() if v > dl['gia']]
        bang = [k for k, v in moi.items() if v == dl['gia']]
        if cao_hon or bang:
            can.append('Câu "giá Đắk Lắk đang ở mức tương đối cao" giữ nguyên, nhưng với số mới Đắk Lắk '
                       f'{dl["gia"]:,}' + (f' thấp hơn {", ".join(f"{k} {moi[k]:,}" for k in cao_hon)}' if cao_hon else '')
                       + (f'{"," if cao_hon else ""} bằng {", ".join(bang)}' if bang else '') + ' → câu có thể không còn đúng, cần duyệt.')

    # 5) Ngày "cập nhật trong ngày": công cụ chung đổi sang ngày hôm sau; không có số Đắk Lắk mới → trả lại ngày gốc
    for chu, vt, _ in dong:
        m = RE_NGAY_CN.search(chu)
        if not m:
            continue
        if not dl and a.goc:
            goc = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', open(a.goc, encoding='utf-8').read())))
            mg = RE_NGAY_CN.search(goc)
            if mg:
                them(m.group(0), vt + m.start(), m.group(1) + mg.group(2), '', 'không có số Đắk Lắk mới nên giữ đúng ngày gốc của số liệu')
        elif dl and dl['ngay'] != m.group(2):
            can.append(f'Ngày trong bài ghi {m.group(2)} (quy tắc ngày hôm sau) nhưng số mới nhất trên nguồn là ngày {dl["ngay"]} '
                       f'→ mọi số giá trong bài là số ngày {dl["ngay"]}.')

    # 6) Soát thêm
    for chu, vt, _ in dong:
        if 'theo hình ảnh bạn cung cấp' in chu:
            can.append(f'Câu "{chu[:90]}" có sẵn trên bài web (giống câu trả lời của AI sót lại) – không sửa, nên báo nhóm web xem lại.')
    for chu, vt, la_o in dong:                   # giá VND/kg còn sót mà công thức không nhận ra
        if vt in da_xu_ly:
            continue
        for m in re.finditer(r'\d{1,3}(?:[.,]\d{3})+\s*(?:VND|đ)/kg', chu):
            can.append(f'Có số giá công thức chưa nhận ra: "…{chu[max(0, m.start() - 40):m.end()]}" – giữ nguyên, cần đọc lại và cập nhật tay.')
    for ma, v in gc.items():
        w = nb.get(ma)
        if v and w and w.get('ngay') == v['ngay'] and w['gia'] != v['gia']:
            can.append(f'{v["ten"]}: giacaphe.com {v["gia"]:,} khác Nhà Bè Agri {w["gia"]:,} cùng ngày {v["ngay"]} – bài theo giacaphe.com.')
    gl = (gc.get('gia_lai') or {}).get('lich_su')
    if dl_ls and gl and [(h['ngay'], h['gia']) for h in dl_ls] == [(h['ngay'], h['gia']) for h in gl]:
        can.append('Chuỗi giá Đắk Lắk trên giacaphe.com trùng hệt Gia Lai mọi ngày – nên liếc lại nguồn.')

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

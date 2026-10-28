"""Tự lập sua.json cho bài TCB "Giá tiêu hôm nay" (không dùng mạng, không dùng AI).

  python3 -I tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
  python3 -I tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   → "khớp hết"

Mọi con số ghi vào bài lấy THẲNG từ nguồn đã tải trong lần chạy này (gia.json của lay_gia.py) — không tự tính, không đoán.
Ba bảng của bài khớp theo TÊN DÒNG với 3 bảng của banggianongsan.com (nguồn chính):
  - "Bảng giá hồ tiêu trong nước" ↔ bảng "Nông sản (tên + đơn vị tính)"  (đúng tên vùng như bài)
  - "Giá hồ tiêu tại các thị trường xuất khẩu" ↔ bảng "Thị trường xuất khẩu"
  - "Giá hồ tiêu nội địa Ấn Độ" ↔ bảng "Giá tiêu nội địa Ấn Độ" (không phân biệt hoa/thường)
Ô Giá cũ / Giá mới: số của nguồn, viết theo dấu nghìn của ô cũ (137,000 · 5.950 · 8,450).
Ô Thay đổi: chữ của nguồn bỏ biểu tượng (▼ ▲ ➖) và phần "(-0,7%)" / "(0)": "Không đổi", "-1,000 đ" (dấu nghìn ","). Số trong ô
nguồn phải đúng bằng Giá mới − Giá cũ của nguồn, sai → giữ cả dòng + cần duyệt.
Đối chiếu (không lấy số, chỉ để chặn số sai):
  - 5 vùng ↔ giatieu.com/gia-tieu-hom-nay (Gia Lai=Gia Lai, Đắk Lắk=Đắk Lắk, Lâm Đồng=Đắk Nông, Đồng Nai=Bình Phước,
    TP. Hồ Chí Minh=Bà Rịa - Vũng Tàu — tỉnh cũ sáp nhập 2025). Cùng ngày mà Giá mới lệch → giữ cả dòng + cần duyệt;
    Giá mới khớp nhưng thay đổi lệch → vẫn ghi theo banggianongsan + cần duyệt (như lần chạy tay 29/10/2026).
  - 8 dòng xuất khẩu ↔ bảng đầu trang của chính banggianongsan (Tiêu Đen Indonesia…). Lệch → giữ dòng + cần duyệt.
  - Ấn Độ ↔ giatieu.com/gia-tieu-truc-tuyen: lệch → vẫn ghi theo banggianongsan + cần duyệt (lần chạy tay 22, 23, 29/10 làm vậy).
Ngày: "hôm nay d/m/yyyy", "trong nước ngày …", "thế giới …" và dòng ngày đăng = ngày mai (giờ VN). Nguồn chính không đọc được
→ ngày ở câu "cập nhật giá … trong nước ngày …" và tiêu đề "Bảng giá tiêu thế giới …" trả về ngày gốc của bài.
"""
import argparse, datetime, html, json, re, sys, unicodedata

DOI_CHIEU_VUNG = {'hồ tiêu gia lai (đ/kg)': 'gia lai', 'hồ tiêu đắk lắk (đ/kg)': 'đắk lắk',
                  'hồ tiêu lâm đồng (đắk nông cũ sáp nhập) (đ/kg)': 'đắk nông',
                  'hồ tiêu đồng nai (đ/kg)': 'bình phước', 'hồ tiêu tp. hồ chí minh (đ/kg)': 'bà rịa - vũng tàu'}
DOI_CHIEU_XK = {'indonesia - black pepper': 'tiêu đen indonesia (usd/tấn)',
                'indonesia - white pepper': 'tiêu trắng indonesia (usd/tấn)',
                'brazil black - pepper asta 570': 'tiêu đen brazil asta 570 (usd/tấn)',
                'malaysia - black pepper asta': 'tiêu đen malaysia (usd/tấn)',
                'malaysia - white pepper asta': 'tiêu trắng malaysia asta (usd/tấn)',
                'viet nam - black pepper 500 g/l': 'tiêu đen việt nam 500 g/l (usd/tấn)',
                'viet nam - black pepper 550 g/l': 'tiêu đen việt nam 550 g/l (usd/tấn)',
                'viet nam - white pepper asta': 'tiêu trắng việt nam (usd/tấn)'}
TEN_BANG = {'trong_nuoc': 'Bảng giá hồ tiêu trong nước', 'xuat_khau': 'Giá hồ tiêu tại các thị trường xuất khẩu',
            'an_do': 'Giá hồ tiêu nội địa Ấn Độ'}
RE_NGAY = re.compile(r'(hôm nay |trong nước ngày |tiêu thế giới )(\d{1,2}/\d{1,2}/\d{4})')


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def khoa(s):
    return re.sub(r'\s+', ' ', nfc(s).lower())


def bo_dau(s):
    return ''.join(c for c in unicodedata.normalize('NFD', khoa(s)) if unicodedata.category(c) != 'Mn')


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


def viet_so(x, cu):
    """số nguyên x viết theo dấu nghìn của ô cũ (5.950 → dấu chấm; 137,000 → dấu phẩy)."""
    dau = '.' if re.fullmatch(r'\d{1,3}(\.\d{3})+', cu.strip()) else ','
    return f'{x:,}'.replace(',', dau)


def o_thay_doi(goc):
    """chữ ô Thay đổi của nguồn → (chữ ghi vào bài, số thay đổi) ; không hiểu → (None, None)."""
    t = re.sub(r'^[^\w+\-]+', '', nfc(goc))                    # bỏ ▼ ▲ ➖
    t = re.sub(r'\s*\([^)]*\)\s*$', '', t).strip()              # bỏ "(-0,7%)" / "(0)"
    if t.lower() == 'không đổi':
        return 'Không đổi', 0
    m = re.fullmatch(r'([+-])\s*(\d{1,3}(?:[.,]\d{3})*|\d+)\s*(đ)', t)
    if m:
        n = int(re.sub(r'\D', '', m.group(2)))
        return f'{m.group(1)}{n:,} đ', (n if m.group(1) == '+' else -n)
    return None, None


def ngay_goc(path):
    """ngày gốc của 2 câu 'trong nước ngày …' và 'tiêu thế giới …' trong bài gốc tải về."""
    if not path:
        return {}
    goc = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', open(path, encoding='utf-8').read())))
    out = {}
    for tien_to in ('trong nước ngày ', 'tiêu thế giới '):
        m = re.search(re.escape(tien_to) + r'(\d{1,2}/\d{1,2}/\d{4})', goc)
        if m:
            out[tien_to] = m.group(1)
    return out


def ngay_so(s):
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', s or '')
    return tuple(int(x) for x in m.groups()) if m else None


def ngay_mai():
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=7, days=1)).strftime('%d/%m/%Y')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--goc')
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    dong, van = doc_xem(a.xem)
    gia = json.load(open(a.gia, encoding='utf-8'))
    B = gia.get('banggianongsan') or {}
    GH = gia.get('giatieu_hom_nay')
    GT = gia.get('giatieu_truc_tuyen')
    sua, can, lech = [], [], []

    def them(cu, vt, moi, nguon, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    nguon_bang = {k: {khoa(t): (t, v) for t, v in (B.get(k) or {}).items()} for k in TEN_BANG}
    top = nguon_bang['trong_nuoc']
    gh_vung = {khoa(t): v for t, v in (GH['vung'] if GH else {}).items()}
    cung_ngay = bool(GH and B and ngay_so(GH.get('ngay', '')) and ngay_so(GH.get('ngay', '')) == ngay_so(B.get('cap_nhat', '')))
    gt_ando = {bo_dau(t): v for t, v in ((GT or {}).get('an_do') or {}).items()}
    bang_thieu, giu = set(), []

    # 1) Ba bảng giá – khớp theo tên dòng
    for i, (ten, vt, la_o) in enumerate(dong):
        if la_o:
            continue
        cells, j = [], i + 1
        while j < len(dong) and dong[j][2]:
            cells.append(dong[j]); j += 1
        if len(cells) < 3 or not re.fullmatch(r'[\d.,]+', cells[0][0]):
            continue
        k = khoa(ten)
        bang = next((b for b in TEN_BANG if k in nguon_bang[b]), None)
        if bang is None:
            if not B:
                bang_thieu.add('tat_ca')
            else:
                can.append(f'Dòng "{ten}": không có trong banggianongsan.com – giữ nguyên {cells[0][0]} / {cells[1][0]} / {cells[2][0]}.')
            continue
        ten_ng, v = nguon_bang[bang][k]
        chu_td, so_td = o_thay_doi(v['thay_doi'])
        tho = '"' + v.get('tho', f'{ten_ng} | {v["cu"]:,} | {v["moi"]:,} | {v["thay_doi"]}') + '"'
        ly = f'banggianongsan.com (đăng {B.get("cap_nhat", "?")}), bảng "{TEN_BANG[bang]}", dòng {tho}'
        # kiểm tra trước khi ghi
        if chu_td is None:
            giu.append(f'{TEN_BANG[bang]} – {ten}: ô Thay đổi của nguồn "{v["thay_doi"]}" có dạng bài chưa có '
                       f'(bài chỉ có "Không đổi" / "-1,000 đ") – giữ nguyên cả dòng ({tho}), cần người ghi tay.')
            continue
        if so_td != v['moi'] - v['cu']:
            giu.append(f'{TEN_BANG[bang]} – {ten}: nguồn tự mâu thuẫn ({tho}: {v["cu"]:,} → {v["moi"]:,} nhưng ô Thay đổi ghi khác) – giữ nguyên cả dòng.')
            continue
        if bang == 'trong_nuoc' and k in DOI_CHIEU_VUNG and GH:
            g = gh_vung.get(DOI_CHIEU_VUNG[k])
            if g and cung_ngay and g['gia'] != v['moi']:
                giu.append(f'{TEN_BANG[bang]} – {ten}: 2 nguồn cùng ngày lệch Giá mới – banggianongsan {v["moi"]:,}, '
                           f'giatieu.com ({DOI_CHIEU_VUNG[k].title()}) {g["gia"]:,} → giữ nguyên cả dòng, cần người chọn nguồn.')
                continue
            if g and cung_ngay and g['thay_doi'] != so_td:
                can.append(f'{TEN_BANG[bang]} – {ten}: đã ghi theo banggianongsan ({v["cu"]:,} → {v["moi"]:,}, {chu_td}); '
                           f'giatieu.com ({DOI_CHIEU_VUNG[k].title()}, {GH["ngay"]}) cùng Giá mới {g["gia"]:,} nhưng thay đổi '
                           f'{g["thay_doi"]:+,} → hai nguồn khác nhau ở Giá cũ / Thay đổi, cần người xem lại.')
        if bang == 'xuat_khau':
            t2 = top.get(DOI_CHIEU_XK.get(k, ''))
            if t2 and t2[1]['moi'] != v['moi']:
                giu.append(f'{TEN_BANG[bang]} – {ten}: banggianongsan tự mâu thuẫn – bảng "Thị trường xuất khẩu" ghi {v["moi"]:,}, '
                           f'bảng đầu trang ("{t2[0]}") ghi {t2[1]["moi"]:,} → giữ nguyên cả dòng.')
                continue
        if bang == 'an_do' and gt_ando:
            g = gt_ando.get(bo_dau(ten_ng))
            if g and g['gia'] != v['moi']:
                can.append(f'{TEN_BANG[bang]} – {ten}: ghi theo banggianongsan ({v["moi"]:,}); giatieu.com/gia-tieu-truc-tuyen '
                           f'ghi {g["gia"]:,} (thay đổi {g["thay_doi"]}) – lệch {abs(g["gia"] - v["moi"]):,} Rupee → cần người chọn nguồn.')
        if so_td != 0 and bang != 'trong_nuoc':
            giu.append(f'{TEN_BANG[bang]} – {ten}: nguồn ghi có thay đổi ({tho}) nhưng cột Thay đổi của bảng này trong bài chỉ có dạng '
                       f'"Không đổi" – giữ nguyên cả dòng, cần người ghi tay.')
            continue
        them(cells[0][0], cells[0][1], viet_so(v['cu'], cells[0][0]), B['url'], f'Giá cũ: {ly}')
        them(cells[1][0], cells[1][1], viet_so(v['moi'], cells[1][0]), B['url'], f'Giá mới: {ly}')
        them(cells[2][0], cells[2][1], chu_td, B['url'], f'Thay đổi: {ly}')
    can.extend(giu)
    if not B:
        can.insert(0, 'banggianongsan.com KHÔNG ĐỌC ĐƯỢC – mọi bảng giá giữ nguyên số cũ; ngày ở câu "cập nhật giá … trong nước ngày …" '
                      'và tiêu đề "Bảng giá tiêu thế giới …" giữ ngày gốc của bài.')
    else:
        for b in ('xuat_khau', 'an_do'):
            if not B.get(b):
                can.append(f'banggianongsan.com không có bảng "{TEN_BANG[b]}" – các dòng bảng này giữ nguyên.')
        if GH and not cung_ngay:
            can.append(f'giatieu.com/gia-tieu-hom-nay ghi ngày {GH.get("ngay")} khác ngày banggianongsan ({B.get("cap_nhat")}) '
                       f'– không đối chiếu được giá trong nước, đã ghi theo banggianongsan.')
    if not GH:
        can.append('giatieu.com/gia-tieu-hom-nay KHÔNG ĐỌC ĐƯỢC – giá trong nước chỉ có 1 nguồn (banggianongsan).')
    if not (GT and GT.get('the_gioi')):
        can.append('giatieu.com/gia-tieu-truc-tuyen: bảng giá thế giới trống ("Hệ thống đang bận") hoặc không đọc được – '
                   'bảng xuất khẩu chỉ có 1 nguồn (banggianongsan).')
    if not (GT and GT.get('an_do')) and B.get('an_do'):
        can.append('giatieu.com/gia-tieu-truc-tuyen: không đọc được giá Ấn Độ – bảng Ấn Độ chỉ có 1 nguồn (banggianongsan).')

    # 2) Ngày: các câu "hôm nay / trong nước ngày / tiêu thế giới <ngày>" + dòng ngày đăng = ngày mai;
    #    nguồn chính hỏng → 2 câu nói "cập nhật ngày" trả về ngày gốc của bài.
    N, goc = ngay_mai(), ngay_goc(a.goc)
    giu_ngay = {'trong nước ngày ': not B or not B.get('trong_nuoc'), 'tiêu thế giới ': not B or not B.get('xuat_khau')}
    for chu, vt, la_o in dong:
        if la_o:
            continue
        if re.fullmatch(r'\d{1,2}/\d{1,2}/\d{4}', chu):
            them(chu, vt, N, '', f'quy tắc ngày: luôn ghi ngày hôm sau ({N})')
            continue
        for m in RE_NGAY.finditer(chu):
            moi = N
            if giu_ngay.get(m.group(1)):
                if m.group(1) not in goc:
                    continue
                moi = goc[m.group(1)]
            them(m.group(0), vt + m.start(), m.group(1) + moi, '',
                 'nguồn không đọc được nên giữ ngày gốc của bài' if moi != N else f'quy tắc ngày: luôn ghi ngày hôm sau ({N})')

    # 3) Số liệu không có trong 3 nguồn
    for chu, _, _ in dong:
        for m in re.finditer(r'(?:^|(?<=\. ))(?:[^.]|\.(?=\d))*xuất khẩu [\d.,]+ tấn(?:[^.]|\.(?=\d))*', chu):
            can.append(f'Mục 3: "{m.group(0).strip()[:160]}" – 3 nguồn không có số liệu xuất khẩu này, giữ nguyên.')

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

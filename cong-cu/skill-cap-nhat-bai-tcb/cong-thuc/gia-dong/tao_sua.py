"""Tự lập sua.json cho bài TCB "Giá đồng hôm nay trực tuyến & các yếu tố tác động đến thị trường".

  python3 -I tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
  python3 -I tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"

Không gọi mạng, không gọi AI. Mọi số viết vào bài lấy thẳng từ gia.json (lay_gia.py tải trong lần chạy này).
- Bảng 1.1 "Loại đồng | Giá (VND/kg)": khớp dòng theo TÊN với bảng "Loại đồng" của nguồn phế liệu. Tên trùng nhau trong bài
  (vd 2 dòng "Đồng cháy") → lần đầu lấy theo tên; lần sau lấy dòng nguồn CÙNG VỊ TRÍ nếu tên dòng nguồn đó không có trong bài
  (vd "Đồng vàng") + ghi cần duyệt. Viết số giữ đúng dấu nghìn của chính ô cũ (155,000 hoặc 130.000) và gạch nối cũ (" - ").
- Bảng 1.2 "Hợp đồng | Giá (USD) | Thay đổi (%)": chỉ cập nhật khi nguồn thế giới đọc được VÀ cùng mã gốc (bài ghi ALI… =
  nhôm, nguồn là HG = đồng → không cập nhật). Không cập nhật được → giữ nguyên bảng + cần duyệt, và trả ngày ở tiêu đề
  "1.2. Bảng giá đồng thế giới <ngày>" về ngày gốc của bài (để tiêu đề không ghi ngày mới cho giá cũ).
- Nguồn phế liệu lỗi → giữ nguyên bảng 1.1 + cần duyệt, trả ngày ở tiêu đề 1.1 về ngày gốc.
"""
import argparse, datetime, html, json, re, sys, unicodedata

THANG = 'FGHJKMNQUVXZ'


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


def bang(dong, tieu_de, so_cot):
    """Tìm bảng có ô đầu = tieu_de; trả [(tên, vt tên, [(ô, vt)...])] cho từng dòng có đúng so_cot ô."""
    for i, (chu, vt, la_o) in enumerate(dong):
        if la_o or chu.lower() != tieu_de.lower():
            continue
        j = i + 1 + so_cot            # bỏ dòng tiêu đề
        out = []
        while j < len(dong) and not dong[j][2]:
            o = dong[j + 1: j + 1 + so_cot]
            if len(o) != so_cot or not all(x[2] for x in o):
                break
            out.append((dong[j][0], dong[j][1], [(x[0], x[1]) for x in o]))
            j += 1 + so_cot
        return out
    return []


def viet(n, mau):
    """Viết số nguyên n theo dấu nghìn của chuỗi mẫu (155,000 → ','; 130.000 → '.')."""
    sep = ',' if re.search(r'\d,\d{3}', mau) else '.'
    return f'{n:,}'.replace(',', sep)


def ngay_goc(goc_path, nhan):
    """Ngày dd/mm/yyyy đứng sau `nhan` trong bài gốc (trước khi công cụ chung đổi ngày)."""
    try:
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', open(goc_path, encoding='utf-8').read())))
    except Exception:
        return None
    m = re.search(re.escape(nhan) + r'\s*(\d{1,2}/\d{1,2}/\d{4})', nfc(t))
    return m.group(1) if m else None


def ma_hd(s):
    """ALIV2026 / HGZ26 → (gốc, tháng, năm 2 số)."""
    m = re.fullmatch(r'([A-Z]{1,4}?)([FGHJKMNQUVXZ])(\d{4}|\d{2})', s.strip().upper())
    return (m.group(1), m.group(2), m.group(3)[-2:]) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--goc', required=True)
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    dong, van = doc_xem(a.xem)
    gia = json.load(open(a.gia, encoding='utf-8'))
    sua, can, lech = [], [], []

    def them(cu, vt, moi, nguon, ly, tinh=False):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        x = {'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
             'nguon': nguon, 'ly_do': ly, '_vt': vt}
        if tinh:
            x['tinh_toan'] = True
        sua.append(x)

    def tra_ngay(nhan, ly):
        """Trả ngày ở tiêu đề `nhan <ngày>` về ngày gốc của bài."""
        cu = ngay_goc(a.goc, nhan)
        for chu, vt, la_o in dong:
            m = re.search(re.escape(nhan) + r'\s*(\d{1,2}/\d{1,2}/\d{4})', chu)
            if m and not la_o:
                if cu:
                    them(m.group(0), vt + m.start(), m.group(0)[:m.start(1) - m.start()] + cu, '', ly)
                else:
                    can.append(f'Không tìm được ngày gốc của tiêu đề "{nhan}" – kiểm tra lại ngày ở tiêu đề này.')
                return

    # ---------- Bảng 1.1: giá đồng phế liệu ----------
    b1 = bang(dong, 'Loại đồng', 1)
    pl = gia.get('phe_lieu')
    if not b1:
        can.append('Không thấy bảng "Loại đồng | Giá (VND/kg)" trong bài – bài đổi bố cục, cần xem lại công thức.')
    elif not pl:
        can.append('Bảng 1.1: không đọc được nguồn thumuaphelieugiacao24h.vn – giữ nguyên toàn bộ giá cũ.')
        tra_ngay('Bảng giá đồng phế liệu trong nước theo chủng loại', 'nguồn phế liệu không đọc được – giữ ngày gốc của bài')
    else:
        theo_ten = {}
        for k, d in enumerate(pl['dong']):
            theo_ten.setdefault(d['ten'].lower(), (k, d))
        ten_bai = [t.lower() for t, _, _ in b1]
        da_dung = set()
        for k, (ten, vt, o) in enumerate(b1):
            cu, vo = o[0]
            m = re.fullmatch(r'([\d.,]+)(\s*[–—-]\s*)([\d.,]+)', cu)
            if not m:
                can.append(f'Bảng 1.1 – {ten}: ô giá "{cu}" không đúng dạng "thấp - cao" – giữ nguyên.')
                continue
            hit, ghi = None, None
            if ten.lower() in theo_ten and ten.lower() not in da_dung:
                hit = theo_ten[ten.lower()]
                da_dung.add(ten.lower())
            elif k < len(pl['dong']) and pl['dong'][k]['ten'].lower() not in ten_bai:
                hit = (k, pl['dong'][k])
                ghi = (f'Bảng 1.1: dòng thứ {k + 1} bài ghi "{ten}" (trùng tên dòng khác), nguồn ở cùng vị trí ghi '
                       f'"{hit[1]["ten"]}" – lấy giá dòng "{hit[1]["ten"]}", giữ nguyên tên trong bài (không đổi tên riêng), nhờ biên tập xem lại tên.')
            if not hit:
                can.append(f'Bảng 1.1 – {ten}: nguồn không có dòng tên này – giữ nguyên "{cu}".')
                continue
            d = hit[1]
            moi = viet(d['thap'], m.group(1)) + m.group(2) + viet(d['cao'], m.group(3))
            them(cu, vo, moi, pl['nguon'], f'{ten}: nguồn ghi "{d["chu_goc"]}" (trang sửa lần cuối {pl["cap_nhat"]})')
            if ghi:
                can.append(ghi)
        seps = {('.' if re.search(r'\d\.\d{3}', o[0][0]) else ',') for _, _, o in b1}
        if len(seps) > 1:
            can.append('Bảng 1.1: có dòng viết dấu phẩy (155,000), có dòng viết dấu chấm (130.000) – giữ nguyên cách viết của từng ô, nhờ biên tập thống nhất nếu muốn.')
        try:
            ng = datetime.datetime.fromisoformat(pl['cap_nhat'].replace('Z', '+00:00'))
            if (datetime.datetime.now(datetime.timezone.utc) - ng).days > 7:
                can.append(f'Bảng 1.1: trang nguồn thumuaphelieugiacao24h.vn ghi sửa lần cuối {ng:%d/%m/%Y} – nguồn có thể không cập nhật hằng ngày, nhờ biên tập lưu ý.')
        except Exception:
            pass

    # ---------- Bảng 1.2: hợp đồng kỳ hạn thế giới ----------
    b2 = bang(dong, 'Hợp đồng', 2)
    tg = gia.get('the_gioi')
    goc_bai = sorted({ma_hd(t)[0] for t, _, _ in b2 if ma_hd(t)})
    xong = False
    if not b2:
        can.append('Không thấy bảng "Hợp đồng | Giá (USD) | Thay đổi (%)" trong bài – bài đổi bố cục, cần xem lại công thức.')
    elif not tg:
        can.append(f'Bảng 1.2 (giá đồng thế giới): nguồn Barchart HG*0 chặn máy chủ (CloudFront) nên không đọc được số – giữ nguyên cả bảng. '
                   f'Lưu ý thêm: bài đang ghi mã hợp đồng {"/".join(goc_bai) or "?"}… ({b2[0][0]} … {b2[-1][0]})'
                   + (' – ALI là mã hợp đồng NHÔM, không phải đồng (đồng COMEX là HG, USD/pound); cần Trang/biên tập chốt bảng này dùng đồng HG hay nhôm ALI.' if 'ALI' in goc_bai else '.'))
    elif goc_bai != [tg.get('goc')]:
        can.append(f'Bảng 1.2: bài ghi mã hợp đồng {"/".join(goc_bai)}… nhưng nguồn là {tg.get("goc")} ({tg.get("don_vi")}) – khác hàng hóa/đơn vị, '
                   f'không thể cập nhật mà không đổi mã hợp đồng → giữ nguyên cả bảng; cần Trang/biên tập chốt.')
    else:
        theo_ma = {ma_hd(h['ma']): h for h in tg['hop_dong'] if ma_hd(h['ma'])}
        xong = True
        for ten, vt, o in b2:
            h = theo_ma.get(ma_hd(ten))
            if not h:
                xong = False
                can.append(f'Bảng 1.2 – {ten}: nguồn không còn hợp đồng này (đã đáo hạn?) – giữ nguyên dòng.')
                continue
            (gcu, gvt), (pcu, pvt) = o
            sl = len(gcu.split('.')[1]) if '.' in gcu else 0
            them(gcu, gvt, f'{h["gia"]:,.{sl}f}', tg['nguon'], f'{ten}: nguồn ghi "{h.get("dong", h["gia"])}" (cập nhật {tg.get("cap_nhat", "?")})')
            mp = re.fullmatch(r'([+-]?)([\d.]+)%', pcu)
            pt = h.get('thay_doi_pt')
            if mp and pt:
                v = float(pt.rstrip('%'))
                sp = len(mp.group(2).split('.')[1]) if '.' in mp.group(2) else 0
                them(pcu, pvt, f'{v:+.{sp}f}%', tg['nguon'], f'{ten}: nguồn ghi thay đổi {pt}')
            else:
                xong = False
                can.append(f'Bảng 1.2 – {ten}: nguồn không có % thay đổi – giữ nguyên "{pcu}".')
    if b2 and not xong:
        tra_ngay('Bảng giá đồng thế giới', 'bảng 1.2 không cập nhật được – giữ ngày gốc của bài để tiêu đề không ghi ngày mới cho giá cũ')

    can.append('Các số trong phần phân tích (thiếu khoảng 25% vào năm 2035; nhu cầu 26.7 triệu tấn năm 2024 → 34.1 triệu tấn năm 2040; năm 2025) '
               'không có trong nguồn được chọn nên giữ nguyên.')

    if a.kiem:
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} chỗ lệch: ' + '; '.join(lech))
        sys.exit(1 if lech else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for x in sua:
        print('  ', x['tim'][:60], '→', x['thay'][:60])
    for c in can:
        print('  cần duyệt:', c)


if __name__ == '__main__':
    main()

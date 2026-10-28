"""Tự lập sua.json cho bài TCB "Giá cà phê sàn London và New York mới nhất hôm nay".

  python3 -I tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
  python3 -I tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html

  --xem  kết quả `cap_nhat.py xem ... bai1`     --gia  gia.json (lay_gia.py: 5 hợp đồng đầu tiên mỗi sàn)
  --goc  bài gốc tải về (để lấy lại ngày gốc khi không có giá mới)   --kiem  soát lại sau khi sửa ("khớp hết")

Bài có 2 bảng: Tháng đáo hạn | Giá | Thay đổi so với phiên trước. Bảng nhận theo đơn vị ở dòng tiêu đề
("USD/tấn" = Robusta London, "cent/pound" = Arabica New York), không theo vị trí trong bài.
Dòng thứ i của bảng = hợp đồng thứ i trên nguồn (Trang chốt: luôn lấy 5 hợp đồng hiển thị đầu tiên, hợp đồng cuộn theo
nguồn) -> đổi cả ô tháng đáo hạn khi nguồn đã cuộn. Số viết theo cách bài đang viết ở chính ô đó (3.240 / 293.75);
thay đổi: "+" khi tăng, "-" khi giảm, không dấu khi không đổi; đơn vị giữ nguyên chữ của bài.
Không dùng mạng, không dùng AI.
"""
import argparse, datetime, html, json, re, sys, unicodedata
from decimal import Decimal

SAN = {'robusta': ('Robusta London', 'USD/tấn', ('london', 'robusta')),
       'arabica': ('Arabica New York', 'cent/pound', ('new york', 'arabica'))}


def nfc(s):
    return unicodedata.normalize('NFC', s)


def doc_xem(path):
    """-> (van, nhom). van = toàn bộ chữ; nhom = các khối: [(chữ ô, vị trí trong van), ...].
    Dòng không bắt đầu bằng '| ' mở khối mới (đầu một dòng bảng hoặc một đoạn văn); dòng '| …' là các ô tiếp theo."""
    van, nhom = '', []
    for line in open(path, encoding='utf-8'):
        m = re.match(r'\s*\d+\.\s?(.*)$', line.rstrip('\n'))
        if not m:
            continue
        t = nfc(m.group(1))
        goc = len(van)
        van += t + '\n'
        o = [(x.group(0).strip(), goc + x.start()) for x in re.finditer(r'[^|]+', t) if x.group(0).strip()]
        o = [(c, v + (len(van[v:]) - len(van[v:].lstrip(' ')))) for c, v in o]   # vị trí sau khoảng trắng đầu ô
        if t.startswith('|') and nhom:
            nhom[-1].extend(o)
        else:
            nhom.append(o)
    return van, nhom


def so_nguon(x):
    """Số kiểu Việt Nam của nguồn: 3.240 / 284,65 -> Decimal."""
    return Decimal(x.replace('.', '').replace(',', '.'))


def kieu_so(cu):
    """Cách viết số trong ô cũ -> (dấu nghìn, dấu thập phân, số chữ số lẻ)."""
    m = re.search(r'\d[\d.,]*', cu)
    s = m.group(0) if m else ''
    if re.fullmatch(r'\d{1,3}([.,])\d{3}(\1\d{3})*', s):
        return s[-4], '', 0
    m2 = re.fullmatch(r'\d+(?:([.,])\d{3})*([.,])(\d{1,2})', s)       # 293.75 / 1,234.50
    if m2:
        return (m2.group(1) or ('.' if m2.group(2) == ',' else ',')), m2.group(2), len(m2.group(3))
    return '.', ',', 0


def viet(v, kieu):
    nghin, tp, le = kieu
    s = f'{abs(v):,.{le}f}'
    nguyen, _, phan = s.partition('.')
    return nguyen.replace(',', nghin) + (tp + phan if le else '')


def lan_thu(van, tim, vt):
    n, i = 0, van.find(tim)
    while i != -1 and i <= vt:
        n += 1
        i = van.find(tim, i + 1)
    return n


def tim_bang(van, nhom):
    """-> {'robusta': [dòng], 'arabica': [dòng]}; dòng = [(ô tháng, vt), (ô giá, vt), (ô thay đổi, vt)]."""
    bang = {}
    for i, g in enumerate(nhom):
        if len(g) < 3 or not g[0][0].lower().startswith('tháng đáo hạn'):
            continue
        tieu_de = ' '.join(c for c, _ in g).lower()
        ma = next((k for k, (_, dv, _t) in SAN.items() if dv.lower() in tieu_de), None)
        if not ma:                                                # không có đơn vị ở tiêu đề -> theo đề mục gần nhất phía trên
            truoc = ' '.join(c for gg in nhom[max(0, i - 3):i] for c, _ in gg).lower()
            ma = next((k for k, (_, _d, tu) in SAN.items() if any(t in truoc for t in tu)), None)
        if not ma or ma in bang:
            continue
        dong = []
        for gg in nhom[i + 1:]:
            if len(gg) >= 3 and re.fullmatch(r'\d{1,2}/\d{4}', gg[0][0]):
                dong.append(gg[:3])
            else:
                break
        bang[ma] = dong
    return bang


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--goc')
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    van, nhom = doc_xem(a.xem)
    try:
        gia = json.load(open(a.gia, encoding='utf-8'))
    except (OSError, ValueError):
        gia = {}
    sua, can, lech = [], [], []

    def them(cu, vt, moi, nguon, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    bang = tim_bang(van, nhom)
    co_gia = []
    for ma, (ten, don_vi, _) in SAN.items():
        dong, g = bang.get(ma), gia.get(ma)
        if not dong:
            can.append(f'Không thấy bảng giá {ten} trong bài (bài đổi trình bày?) – chưa cập nhật bảng này, cần xem lại bằng tay.')
            continue
        if not g:
            can.append(f'Không đọc được giá {ten} trên nguồn baolamdong.vn – giữ nguyên cả bảng {ten} (giá cũ).')
            continue
        co_gia.append(ma)
        hd = g['hop_dong']
        if len(dong) != len(hd):
            can.append(f'Bảng {ten}: bài có {len(dong)} dòng, nguồn hiển thị {len(hd)} hợp đồng đầu tiên – chỉ cập nhật '
                       f'{min(len(dong), len(hd))} dòng đầu, các dòng còn lại giữ nguyên.')
        cu_thang = [d[0][0] for d in dong[:len(hd)]]
        moi_thang = [h['ky_han'] for h in hd[:len(dong)]]
        if cu_thang != moi_thang and not a.kiem:
            can.append(f'Bảng {ten}: nguồn đã cuộn hợp đồng – tháng đáo hạn đổi từ {", ".join(cu_thang)} sang '
                       f'{", ".join(moi_thang)} (luôn lấy 5 hợp đồng hiển thị đầu tiên). Đọc lại bảng.')
        for (o_thang, o_gia, o_td), h in zip(dong, hd):
            ly = f'{ten} kỳ hạn {h["ky_han"]}: giá khớp {h["gia"]} {don_vi}, ' + \
                 ('không đổi' if h['chieu'] == 'flat' else f'{"tăng" if h["chieu"] == "up" else "giảm"} {h["thay_doi"]}') + \
                 f' so với hôm trước {h["hom_truoc"]} (nguồn cập nhật {g["cap_nhat"]})'
            them(o_thang[0], o_thang[1], h['ky_han'], g['nguon'], f'{ten}: hợp đồng thứ {hd.index(h) + 1} trên nguồn là kỳ hạn {h["ky_han"]}')
            kieu = kieu_so(o_gia[0])
            m = re.match(r'(.*?)\d[\d.,]*(.*)$', o_gia[0])
            them(o_gia[0], o_gia[1], m.group(1) + viet(so_nguon(h['gia']), kieu) + m.group(2), g['nguon'], ly)
            td = so_nguon(h['thay_doi']) * (-1 if h['chieu'] == 'down' else 0 if h['chieu'] == 'flat' else 1)
            m = re.match(r'\s*([+\-−]?)\s*\d[\d.,]*(.*)$', o_td[0])
            if not m:
                can.append(f'{ten} kỳ hạn {h["ky_han"]}: ô thay đổi "{o_td[0]}" không đúng dạng "+/-số đơn vị" – giữ nguyên.')
                continue
            tru = '−' if '−' in van else '-'
            dau = '+' if td > 0 else tru if td < 0 else ''
            them(o_td[0], o_td[1], dau + viet(td, kieu) + m.group(2), g['nguon'], ly)
            if not a.kiem:
                if h['chieu'] == 'flat':
                    can.append(f'{ten} kỳ hạn {h["ky_han"]}: nguồn ghi "Không đổi" – ô thay đổi ghi "{viet(td, kieu) + m.group(2)}" '
                               f'(không dấu), xem cách ghi có ổn không.')
                if h.get('hom_truoc'):
                    try:
                        if so_nguon(h['gia']) - so_nguon(h['hom_truoc']) != td:
                            can.append(f'{ten} kỳ hạn {h["ky_han"]}: nguồn tự lệch – giá khớp {h["gia"]} trừ hôm trước '
                                       f'{h["hom_truoc"]} không bằng mức thay đổi nguồn ghi ({h["thay_doi"]}); bài dùng mức nguồn ghi.')
                    except Exception:
                        pass

    # Ngày "dữ liệu tham khảo được cập nhật ngày …": công cụ chung đã đổi sang ngày mai; không có giá mới nào -> trả lại ngày gốc
    if not co_gia and a.goc:
        try:
            goc = nfc(html.unescape(re.sub(r'<[^>]+>', ' ', open(a.goc, encoding='utf-8').read())))
            ngay_goc = re.search(r'được cập nhật ngày\s+(\d{1,2}/\d{1,2}/\d{4})', goc)
        except OSError:
            ngay_goc = None
        for m in re.finditer(r'(được cập nhật ngày )(\d{1,2}/\d{1,2}/\d{4})', van):
            if ngay_goc:
                them(m.group(0), m.start(), m.group(1) + ngay_goc.group(1), '', 'không có giá mới – giữ ngày cập nhật số liệu như bài gốc')
        if not a.kiem:
            can.append('Không có giá mới nào: câu "dữ liệu tham khảo được cập nhật ngày …" giữ ngày gốc; các ngày khác (sapo, ngày đăng, '
                       'đề mục) vẫn là ngày mới – cân nhắc chưa đăng bản này.')

    # Lưới an toàn: giá ngoài 2 bảng (đoạn văn, hỏi đáp…) chưa có công thức -> báo để đọc lại
    if not a.kiem:
        o_bang = {vt for d in bang.values() for r in d for _, vt in r}
        for g_ in nhom:
            for c, vt in g_:
                if vt not in o_bang and re.search(r'\d[\d.,]*\s*(USD/tấn|cent/pound|USD|cent)\b', c):
                    can.append(f'Có giá nằm ngoài 2 bảng chưa có công thức tự cập nhật: "{c[:120]}" – cần sửa tay.')
        if co_gia:
            tt = gia.get('trang_thai')
            gio = '; '.join(f'{SAN[k][0]} {gia[k]["cap_nhat"]}' for k in co_gia)
            can.append(f'Giá lấy theo lần cập nhật của nguồn ({gio})' + (f', lúc đó thị trường "{tt}"' if tt else '') +
                       ' – nếu sàn đang giao dịch thì đây là giá trong phiên, có thể còn đổi; bài ghi ngày hôm sau theo quy tắc chung.')

    if a.kiem:
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} chỗ lệch: ' + '; '.join(lech))
        sys.exit(1 if lech else 0)
    sua.sort(key=lambda x: -x['_vt'])          # áp từ cuối bài lên để "lan" (lần xuất hiện thứ mấy) không lệch
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for x in reversed(sua):
        print('  ', x['tim'][:60], '→', x['thay'][:60])
    for c in can:
        print('  cần duyệt:', c)


if __name__ == '__main__':
    main()

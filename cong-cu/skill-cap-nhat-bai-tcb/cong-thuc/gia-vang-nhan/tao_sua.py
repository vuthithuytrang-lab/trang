"""Tự lập sua.json cho bài TCB "Giá vàng nhẫn hôm nay" (https://techcombank.com/thong-tin/blog/gia-vang-nhan-hom-nay).

  python3 -I tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
  python3 -I tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   -> "khớp hết"

Bảng bài: Thương hiệu - sản phẩm | Mua vào | Bán ra | Chênh lệch (triệu VND/lượng, 1 số lẻ), 5 dòng.
- Giá nguồn là VND/chỉ (lay_gia.js đã quy về VND/chỉ) -> triệu/lượng = VND/chỉ / 100.000 (chính xác, không làm tròn lung tung).
  Làm tròn về 1 số lẻ (như bài); nếu nguồn có chữ số bị làm tròn -> cần duyệt.
- Chênh lệch = Bán ra - Mua vào, tính từ 2 số ĐÃ GHI trong bài, cùng số lẻ như bài. (số tính ra -> cần duyệt nhẹ không cần: có ghi cách tính ở ly_do)
- Đoạn mở mục 1: "dao động quanh mức MIN - MAX triệu VND/lượng" của giá bán ra và giá mua vào = min - max của bảng sau khi cập nhật.
- Đoạn mục 3: "giá vàng giao ngay trên Kitco ở quanh mức X USD/ounce (*), giảm khoảng Y USD/ounce" <- giavang.org/the-gioi (XAU/USD, biến động 24 giờ). Luôn cần duyệt (nguồn khác Kitco, mốc so sánh khác).
- Thương hiệu nguồn hỏng: giữ nguyên dòng cũ + cần duyệt. Mọi nguồn hỏng: trả mọi ngày về ngày gốc.
- Lưới an toàn: số giá (có đơn vị triệu/VND/USD/đồng/$) ngoài bảng mà công thức không đụng và không bằng số mới -> "SỐ GIÁ CHƯA CẬP NHẬT".
- Câu "Trong phiên 23/10, … giảm … vài trăm nghìn" là diễn biến phiên, không có nguồn -> giữ nguyên + cần duyệt.
Ngày trong bài: lệnh `dung` đã đổi sang ngày hôm sau.
"""
import argparse, html, json, re, sys, unicodedata
from decimal import Decimal, ROUND_HALF_UP

RE_NGAY = re.compile(r'\d{1,2}/\d{1,2}/\d{4}')
# số đi kèm đơn vị tiền (hoặc $ đứng trước) = "số giá"
RE_GIA = re.compile(r'\d[\d.,]*(?:\s*[-–]\s*\d[\d.,]*)?\s*(?:triệu|nghìn|ngàn|VND|VNĐ|USD|đồng|đ)\b|\$\s*\d[\d.,]*', re.I)
THUONG_HIEU = [('sjc', r'\bSJC\b'), ('pnj', r'\bPNJ\b'), ('doji', r'\bDOJI\b'), ('btmc', r'Bảo Tín Minh Châu'), ('phuquy', r'Phú Quý')]
TEN_NGUON = {'sjc': 'webgia.com (SJC)', 'btmc': 'webgia.com (Bảo Tín Minh Châu)', 'phuquy': 'phuquygroup.vn',
             'doji': 'banggia.doji.vn', 'pnj': 'pnj.com.vn', 'thegioi': 'giavang.org (vàng thế giới)'}
MOT_SO_LE = Decimal('0.1')


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


def chu_goc(path):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', open(path, encoding='utf-8').read())))


def trieu_luong(vnd_chi):
    """VND/chỉ -> triệu VND/lượng (Decimal chính xác)"""
    return Decimal(vnd_chi) / Decimal(100000)


def viet_1(d):
    return str(d.quantize(MOT_SO_LE, rounding=ROUND_HALF_UP))


def viet_nhu(v, cu):
    """số nguyên theo kiểu số cũ: có dấu phẩy ngăn nghìn thì giữ"""
    s = f'{int(Decimal(v).quantize(Decimal(1), rounding=ROUND_HALF_UP)):,}'
    return s if ',' in cu else s.replace(',', '')


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
        g = json.load(open(a.gia, encoding='utf-8'))
    except Exception:
        g = {}
    sua, can, lech = [], [], []
    xu_ly = set()          # chỉ số dòng văn bản đã được công thức xử lý (để lưới an toàn bỏ qua)

    def them(cu, vt, moi, nguon, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    # 1) Bảng: dòng tên (không phải ô) có tên thương hiệu + ≥3 ô số theo sau
    hang = []
    for i, (chu, vt, la_o) in enumerate(dong):
        if la_o:
            continue
        ma = next((m for m, rx in THUONG_HIEU if re.search(rx, chu)), None)
        cells = []
        j = i + 1
        while j < len(dong) and dong[j][2]:
            cells.append(dong[j]); j += 1
        if ma and len(cells) >= 3 and all(re.fullmatch(r'\d+(?:\.\d+)?', c[0]) for c in cells[:3]):
            hang.append((ma, chu, cells))
            xu_ly.add(i)
            xu_ly.update(range(i + 1, j))
    gia_hieu_luc = {}      # giá (Decimal) đang là giá trong bài sau cập nhật: nguồn mới nếu có, ngược lại số cũ
    so_nguon_ok = 0
    for ma, ten, cells in hang:
        mua_cu, ban_cu = Decimal(cells[0][0]), Decimal(cells[1][0])
        n = g.get(ma)
        ok = bool(n and n.get('mua') and n.get('ban'))
        if not ok:
            can.append(f'Dòng "{ten}": không đọc được nguồn {TEN_NGUON[ma]} – giữ nguyên giá cũ ({cells[0][0]} / {cells[1][0]} / {cells[2][0]}).')
            gia_hieu_luc[ma] = (mua_cu, ban_cu)
            continue
        so_nguon_ok += 1
        mua_t, ban_t = trieu_luong(n['mua']), trieu_luong(n['ban'])
        mua, ban = (Decimal(viet_1(mua_t)), Decimal(viet_1(ban_t)))
        for ten_cot, t, w in (('Mua vào', mua_t, mua), ('Bán ra', ban_t, ban)):
            if t != w:
                can.append(f'Dòng "{ten}", {ten_cot}: nguồn {t} triệu/lượng, bài ghi 1 số lẻ nên làm tròn thành {w} – xem lại.')
        if ban < mua:
            can.append(f'Dòng "{ten}": nguồn có giá bán ({ban}) thấp hơn giá mua ({mua}) – kiểm tra lại nguồn.')
        gia_hieu_luc[ma] = (mua, ban)
        ly = (f'{TEN_NGUON[ma]} ({n["url"]}), dòng "{n["ten_dong"]}", cập nhật {n["cap_nhat"]}: '
              f'mua {n["mua"]:,} / bán {n["ban"]:,} VND/chỉ = {mua_t} / {ban_t} triệu VND/lượng')
        chenh = ban - mua
        for k, w, mo_ta in ((0, viet_1(mua), 'Mua vào'), (1, viet_1(ban), 'Bán ra')):
            them(cells[k][0], cells[k][1], w, n['url'], f'{mo_ta} – ' + ly)
        them(cells[2][0], cells[2][1], viet_1(chenh), n['url'],
             f'Chênh lệch = Bán ra − Mua vào = {ban} − {mua} = {chenh} (tính từ 2 số ghi trong bài; ' + ly + ')')
    if len(hang) != 5:
        can.append(f'Bảng trong bài có {len(hang)} dòng thương hiệu nhận ra được (kỳ vọng 5) – xem lại bảng bằng tay.')

    # 2) Đoạn mở mục 1: khoảng giá bán ra / mua vào = min - max của bảng sau cập nhật
    if gia_hieu_luc:
        for i, (chu, vt, la_o) in enumerate(dong):
            m = re.search(r'(Giá bán ra của vàng nhẫn dao động quanh mức )(\d+(?:\.\d+)?)( - )(\d+(?:\.\d+)?)( triệu VND/lượng \(\*\), còn giá mua vào quanh mức )(\d+(?:\.\d+)?)( - )(\d+(?:\.\d+)?)( triệu VND/lượng)', chu)
            if not m or la_o:
                continue
            xu_ly.add(i)
            bans = [b for _, b in gia_hieu_luc.values()]
            muas = [x for x, _ in gia_hieu_luc.values()]
            gg = list(m.groups())
            gg[1], gg[3], gg[5], gg[7] = viet_1(min(bans)), viet_1(max(bans)), viet_1(min(muas)), viet_1(max(muas))
            them(m.group(0), vt + m.start(), ''.join(gg), 'bảng giá trong bài',
                 f'khoảng giá = nhỏ nhất - lớn nhất của cột Bán ra / Mua vào trong bảng sau cập nhật ({len(gia_hieu_luc)} thương hiệu)')
            if len(muas) and so_nguon_ok < len(hang):
                can.append('Đoạn khoảng giá mua/bán: có thương hiệu giữ giá cũ nên khoảng giá lẫn số cũ – xem lại.')
    # 3) Câu diễn biến phiên (không có nguồn)
    for i, (chu, vt, la_o) in enumerate(dong, 0):
        m = re.search(r'Trong phiên (\d{1,2}/\d{1,2})[^.]*\.', chu)
        if m and not la_o:
            xu_ly.add(i)
            can.append(f'Câu "{m.group(0)}" (diễn biến phiên, mức giảm "vài trăm nghìn") không có nguồn để tính lại – giữ nguyên, cần người viết lại.')

    # 4) Giá vàng thế giới
    tg = g.get('thegioi')
    for i, (chu, vt, la_o) in enumerate(dong):
        m = re.search(r'(giá vàng giao ngay trên Kitco ở quanh mức )([\d.,]+)( USD/ounce \(\*\), )(giảm|tăng)( khoảng )([\d.,]+)( USD/ounce)', chu)
        if not m or la_o:
            continue
        xu_ly.add(i)
        if not (tg and tg.get('usd')):
            can.append('Giá vàng thế giới (Kitco): không đọc được nguồn giavang.org – giữ nguyên số cũ trong mục 3.')
            continue
        gg = list(m.groups())
        gg[1] = viet_nhu(tg['usd'], m.group(2))
        ly = f'giavang.org/the-gioi (XAU/USD) cập nhật {tg["cap_nhat"]}: {tg["usd"]} USD/ounce'
        doi = tg.get('doi_24h')
        huong = m.group(4)
        if doi is not None and ((doi < 0) == (huong == 'giảm')) and doi != 0:
            gg[5] = viet_nhu(abs(Decimal(str(doi))), m.group(6))
            ly += f', biến động 24 giờ {doi:+} USD'
        else:
            can.append(f'Mục 3: bài ghi "{huong} khoảng {m.group(6)} USD/ounce" nhưng nguồn cho biến động 24 giờ = {doi} USD – '
                       'chỉ đổi giá, giữ nguyên mức biến động, cần viết lại câu.')
        them(m.group(0), vt + m.start(), ''.join(gg), tg['url'], ly)
        can.append('Mục 3: bài ghi nguồn "Kitco" nhưng số lấy từ giavang.org (XAU/USD); mốc "so với đầu giờ sáng hôm trước" được thay bằng biến động 24 giờ của nguồn – xem lại.')
    # ngày hôm sau đã do `dung`; ngày "Sáng dd/mm" nằm trong câu trên

    # 5) Mọi nguồn hỏng -> trả mọi ngày về ngày gốc
    if not so_nguon_ok and not (tg and tg.get('usd')):
        can.append('Không đọc được nguồn nào – giữ nguyên toàn bộ giá, trả mọi ngày về ngày gốc của bài.')
        if a.goc:
            goc = chu_goc(a.goc)
            for chu, vt, la_o in dong:
                if la_o or not RE_NGAY.search(chu):
                    continue
                mau = RE_NGAY.split(chu)
                rx = r'\s*(\d{1,2}/\d{1,2}/\d{4})\s*'.join(r'\s*'.join(map(re.escape, p.split())) for p in mau)
                mg = re.search(rx, goc)
                if not mg:
                    can.append(f'Không tìm thấy ngày gốc cho dòng "{chu[:60]}" – kiểm tra ngày bằng tay.')
                    continue
                for m, ngay_cu in zip(RE_NGAY.finditer(chu), mg.groups()):
                    bd = max(0, m.start() - 25)
                    them(chu[bd:m.end()], vt + bd, chu[bd:m.start()] + ngay_cu, '', 'nguồn giá không đọc được nên giữ ngày gốc của bài')

    # 6) Lưới an toàn: số giá ngoài bảng chưa được đụng tới
    moi_so = {viet_1(x) for p in gia_hieu_luc.values() for x in p} | {viet_1(b - m) for m, b in gia_hieu_luc.values()}
    for i, (chu, vt, la_o) in enumerate(dong):
        if la_o or i in xu_ly:
            continue
        for m in RE_GIA.finditer(chu):
            toan = re.findall(r'\d[\d.,]*\d|\d', m.group(0))
            if toan and all(t in moi_so for t in toan):
                continue
            can.append(f'SỐ GIÁ CHƯA CẬP NHẬT: đoạn {i + 1} có "{m.group(0)}" – công thức không có quy tắc/nguồn cho số này, giữ nguyên, kiểm tra bằng tay.')

    if a.kiem:
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} chỗ lệch: ' + '; '.join(lech))
        sys.exit(1 if lech else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    print(f'  bảng giá: {len(hang)} dòng thương hiệu trong bài, {so_nguon_ok} dòng có nguồn')
    for x in sua:
        print('  ', x['tim'][:70], '→', x['thay'][:70])
    for c in can:
        print('  cần duyệt:', c)


if __name__ == '__main__':
    main()

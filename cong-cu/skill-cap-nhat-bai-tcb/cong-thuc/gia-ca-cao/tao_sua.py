"""Tự lập sua.json cho bài TCB "Giá ca cao hôm nay: Biến động thị trường và góc nhìn cho nhà đầu tư".

  --xem  kết quả `cap_nhat.py xem ... bai1`     --gia  gia.json (lay_gia.js)
  --goc  cap-nhat/tam/bai1.html (bài gốc trên web – để biết ngày cũ của tiêu đề bảng thế giới)
  --ra   sua.json                                 --kiem soát lại sau khi sửa ("khớp hết")

Không mạng, không LLM. Mọi số viết vào bài lấy thẳng từ gia.json (đã chép từ nguồn trong lần chạy này)
hoặc tính từ số đó (đánh dấu tinh_toan, ghi công thức). Thiếu số → giữ nguyên số cũ + cần duyệt.

1. Bảng trong nước (banggianongsan): khớp dòng theo TÊN (bỏ "(đ/kg)", "ca cao" = "cacao").
   "Giá hiện tại" = cột Giá cũ, "Giá mới dự kiến" = cột Giá mới, viết "70,000 - 79,000".
   "Thay đổi": nguồn ghi "Không đổi" → "0 VND/kg"; nguồn ghi khác (khoảng, ▲/▼) → giữ nguyên + cần duyệt.
2. Bảng New York (CC…) / London (CA…) (ICE): khớp dòng theo MÃ HỢP ĐỒNG (CCZ26 = tháng Dec26 trên ICE).
   "Giá" = giá khớp gần nhất (LAST) của ICE, viết "5,843". "Thay đổi so với phiên trước" = TÍNH:
   giá − giá / (1 + %thay đổi/100), làm tròn số nguyên, viết "+42" / "-58" (chỉ khi kết quả gần số nguyên ≤ 0,05).
   Hợp đồng không có trên ICE / chưa có giá / giá của ngày cũ hơn các hợp đồng khác → giữ nguyên + cần duyệt.
3. Tiêu đề "Bảng giá ca cao thế giới dd/mm/yyyy": bước `dung` đã đổi sang ngày mới; nếu cả một sàn không đọc được
   → trả về ngày cũ của bài gốc (để không ghi ngày mới cho giá cũ) + cần duyệt.
4. Đoạn văn có giá (VND/kg, USD/tấn, GBP/tấn) ngoài bảng → chưa có quy tắc → cần duyệt (bài hiện không có).
"""
import argparse, datetime, html as H, json, re, sys, unicodedata

THANG = {'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6, 'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12}
TEN_THANG = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
SAN = {'CC': ('new_york', 'New York', 'USD/tấn'), 'CA': ('london', 'London', 'GBP/tấn')}


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def chuan_ten(s):
    t = nfc(s).lower().replace('(đ/kg)', '').replace('ca cao', 'cacao')
    return re.sub(r'\s+', '', t)


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


def khoang(s):
    """'7.300 – 8.000' (nguồn) → '7,300 - 8,000' (cách bài viết); không đúng dạng 2 số → None."""
    so = re.findall(r'\d[\d.]*', s or '')
    if len(so) != 2 or not re.fullmatch(r'\s*\d[\d.]*\s*[–-]\s*\d[\d.]*\s*', s):
        return None
    a, b = (int(x.replace('.', '')) for x in so)
    return f'{a:,} - {b:,}'


def ngay_ice(luc):
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', luc or '')
    return datetime.date(int(m.group(3)), int(m.group(1)), int(m.group(2))) if m else None


def thoi_diem(luc):
    try:
        return datetime.datetime.strptime(luc, '%m/%d/%Y %I:%M %p GMT')
    except (TypeError, ValueError):
        return datetime.datetime.min


def chu_goc(path):
    t = open(path, encoding='utf-8', errors='replace').read()
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', t, flags=re.S | re.I)
    t = H.unescape(re.sub(r'<[^>]+>', ' ', t))
    return nfc(re.sub(r'\s+', ' ', t))


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

    def o_sau(i, n):
        cells, j = [], i + 1
        while j < len(dong) and dong[j][2]:
            cells.append(dong[j]); j += 1
        return cells if len(cells) == n else None

    # ---------- 1. Bảng trong nước ----------
    tn = gia.get('trong_nuoc')
    nguon_tn = {chuan_ten(r['ten']): r for r in (tn or {}).get('dong', [])}
    da_khop_tn = set()
    co_bang_tn = False
    for i, (chu, vt, la_o) in enumerate(dong):
        if la_o:
            continue
        cells = o_sau(i, 3)
        if not cells or 'VND/kg' not in cells[2][0] or not re.fullmatch(r'[\d,]+ - [\d,]+', cells[0][0]):
            continue
        co_bang_tn = True
        if not tn:
            continue
        r = nguon_tn.get(chuan_ten(chu))
        if not r:
            can.append(f'Bảng trong nước, dòng "{chu}": banggianongsan không có dòng cùng tên – giữ nguyên.')
            continue
        da_khop_tn.add(chuan_ten(chu))
        luc = f'đăng {tn.get("dang_luc") or "?"}'
        for k, cot, ten_cot in ((0, 'gia_cu', 'Giá cũ'), (1, 'gia_moi', 'Giá mới')):
            moi = khoang(r[cot])
            if moi is None:
                can.append(f'Bảng trong nước, dòng "{chu}": nguồn cột {ten_cot} ghi "{r[cot]}" – không đúng dạng khoảng, giữ nguyên "{cells[k][0]}".')
                continue
            them(cells[k][0], cells[k][1], moi, tn['nguon'],
                 f'banggianongsan ({luc}), dòng "{r["ten"]}", cột {ten_cot}: "{r[cot]}"')
        cl = r['chenh_lech']
        if re.fullmatch(r'\W*\s*Không đổi', nfc(cl)):
            them(cells[2][0], cells[2][1], '0 VND/kg', tn['nguon'],
                 f'banggianongsan ({luc}), dòng "{r["ten"]}", cột Chênh lệch: "{cl}"')
        else:
            can.append(f'Bảng trong nước, cột "Thay đổi" dòng "{chu}": nguồn ghi "{cl}" ({r["gia_cu"]} → {r["gia_moi"]}), '
                       f'bài ghi "{cells[2][0]}" – không ghi được đúng dạng của bài, giữ nguyên.')
    if co_bang_tn and not tn:
        can.append('Bảng giá trong nước: không đọc được banggianongsan.com – giữ nguyên toàn bộ bảng.')
    elif tn:
        for k, r in nguon_tn.items():
            if k not in da_khop_tn:
                can.append(f'banggianongsan có dòng "{r["ten"]}" ({r["gia_cu"]} / {r["gia_moi"]}) nhưng bài không có dòng này – không thêm.')
        hn = (datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))).date()
        nb = tn.get('ngay_bang') or ''
        m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', nb)
        if not m or datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1))) != hn:
            can.append(f'banggianongsan: bảng ghi ngày "{nb or "?"}" (đăng {tn.get("dang_luc") or "?"}), không phải hôm nay '
                       f'{hn.day:02d}/{hn.month:02d}/{hn.year} – đã dùng số của bảng này, cần xem lại.')

    # ---------- 2. Bảng New York / London ----------
    hop_dong_bai = {'CC': [], 'CA': []}
    for i, (chu, vt, la_o) in enumerate(dong):
        m = re.fullmatch(r'(CC|CA)([FGHJKMNQUVXZ])(\d{2})', chu)
        if la_o or not m:
            continue
        cells = o_sau(i, 3)
        if not cells:
            continue
        hop_dong_bai[m.group(1)].append((chu, m, cells))
    san_hong = []
    for tien_to, ds in hop_dong_bai.items():
        if not ds:
            continue
        ma_san, ten_san, dv = SAN[tien_to]
        s = gia.get(ma_san)
        if not s:
            san_hong.append(ten_san)
            can.append(f'Bảng giá ca cao {ten_san}: không đọc được trang ICE – giữ nguyên toàn bộ {len(ds)} hợp đồng.')
            continue
        theo_thang = {h['thang']: h for h in s['hop_dong']}
        ngay_moi = max([d for d in (ngay_ice(h['luc']) for h in s['hop_dong'] if h.get('gia') is not None) if d], default=None)
        gio = sorted({h['luc'] for h in s['hop_dong'] if h.get('gia') is not None and h.get('luc')}, key=thoi_diem)
        for chu, m, cells in ds:
            thang = THANG[m.group(2)]
            nam = 2000 + int(m.group(3))
            if cells[0][0] != f'{thang}/{nam}':
                can.append(f'{ten_san} {chu}: cột tháng đáo hạn ghi "{cells[0][0]}" không khớp mã hợp đồng – giữ nguyên.')
                continue
            h = theo_thang.get(f'{TEN_THANG[thang - 1]}{m.group(3)}')
            if not h:
                can.append(f'{ten_san} {chu}: trang ICE không liệt kê hợp đồng này – giữ nguyên "{cells[1][0]}" / "{cells[2][0]}".')
                continue
            if h.get('gia') is None or h.get('thay_doi_pct') is None:
                can.append(f'{ten_san} {chu}: trang ICE chưa có giá khớp cho hợp đồng này (KL {h.get("khoi_luong")}) – giữ nguyên "{cells[1][0]}" / "{cells[2][0]}".')
                continue
            d = ngay_ice(h['luc'])
            if not d or (ngay_moi and d < ngay_moi):
                can.append(f'{ten_san} {chu}: giá ICE {h["gia"]} khớp lúc {h["luc"]}, cũ hơn các hợp đồng khác – giữ nguyên.')
                continue
            g, pct = h['gia'], h['thay_doi_pct']
            if g != int(g):
                can.append(f'{ten_san} {chu}: giá ICE "{g}" có phần lẻ – giữ nguyên.')
                continue
            chg = g - g / (1 + pct / 100)
            if abs(chg - round(chg)) > 0.05:
                can.append(f'{ten_san} {chu}: ICE ghi giá {g}, thay đổi {pct}% → mức thay đổi tính ra {chg:.2f} không tròn – giữ nguyên cả dòng.')
                continue
            c = int(round(chg))
            ly = f'ICE {ten_san} ({s["nguon"]}, dữ liệu {s.get("api") or ""}): hợp đồng {h["thang"]}, lastPrice {g}, lastTime "{h["luc"]}"'
            them(cells[1][0], cells[1][1], f'{int(g):,}', s['nguon'], ly + ' – giá khớp gần nhất, trễ tối thiểu 15 phút')
            them(cells[2][0], cells[2][1], '0' if c == 0 else f'{c:+,d}', s['nguon'],
                 f'{ly}, change {pct}% → thay đổi = {g} − {g}/(1 + ({pct})/100) = {chg:.3f} ≈ {c:+d} {dv}', tinh=True)
        if gio:
            can.append(f'Bảng {ten_san}: số lấy từ trang chính thức của sàn ICE (Barchart chặn máy chủ) – là giá khớp gần nhất '
                       f'({gio[0]}{" – " + gio[-1] if len(gio) > 1 else ""}, trễ tối thiểu 15 phút), không phải giá chốt phiên; '
                       f'nếu sàn đang mở phiên thì số còn thay đổi.')

    # ---------- 3. Ngày tiêu đề bảng thế giới ----------
    if san_hong:
        for chu, vt, la_o in dong:
            m = re.search(r'(Bảng giá ca cao thế giới )(\d{1,2}/\d{1,2}/\d{4})', chu)
            if la_o or not m:
                continue
            cu = None
            if a.goc:
                mg = re.search(r'Bảng giá ca cao thế giới (\d{1,2}/\d{1,2}/\d{4})', chu_goc(a.goc))
                cu = mg.group(1) if mg else None
            if cu and cu != m.group(2):
                them(m.group(0), vt + m.start(), m.group(1) + cu, '',
                     f'không đọc được giá {", ".join(san_hong)} → giữ ngày cũ của bài gốc ({cu}) để không ghi ngày mới cho giá cũ')
                can.append(f'Tiêu đề "Bảng giá ca cao thế giới": giữ ngày cũ {cu} vì thiếu giá {", ".join(san_hong)}.')
            elif cu is None:
                can.append(f'Tiêu đề "{m.group(0)}": thiếu giá {", ".join(san_hong)} nhưng không tìm được ngày cũ trong bài gốc – cần xem lại ngày.')

    # ---------- 4. Giá trong đoạn văn ----------
    for chu, vt, la_o in dong:
        if la_o:
            continue
        if re.search(r'\d[\d.,]*\s*(VND/kg|USD/tấn|GBP/tấn|đồng/kg|đ/kg)', chu) and not re.fullmatch(r'[\d,]+ - [\d,]+|[+-]?[\d,]+ VND/kg', chu):
            can.append(f'Đoạn văn có giá chưa có quy tắc tự cập nhật: "{chu[:120]}" – cần xem tay.')

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

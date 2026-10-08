"""Tự lập sua.json cho bài TCB "1 chỉ vàng bao nhiêu tiền? Giá vàng 24K, 18K, 9999 hôm nay".

  --xem  kết quả `cap_nhat.py xem ... bai1`     --nguon bang-nguon.json (lay_bang.js)
  --goc  cap-nhat/tam/bai1.html (để trả lại ngày gốc mục giá vàng thế giới)
  --ra   sua.json                                --kiem  soát lại sau khi sửa
  --bo-to-ngay-the-gioi <bai1.min.html>          sau lệnh sua: bỏ tô vàng 2 ngày gốc của mục 3

Bài có 6 bảng VND/chỉ; mỗi bảng thuộc 1 nguồn theo đề mục đứng trước:
  "1. Giá vàng 24K…" -> huythanh | "2.1. SJC" -> sjc | "2.2. Bảo Tín Minh Châu" -> btmc | "2.3. Phú Quý" -> phuquy
  "2.4. DOJI" -> doji | "2.5. PNJ" -> pnj | "3. …thế giới" -> giavang.org/the-gioi (tỷ giá Vietcombank).
Chú thích ảnh SJC / Rồng Thăng Long (ngày dd.mm.yyyy, giá RTL) cũng được cập nhật.
Mỗi dòng trong bài khớp 1 dòng nguồn theo bảng KHOP bên dưới. Không khớp / nguồn thiếu giá -> giữ nguyên + cần duyệt.
"""
import argparse, datetime, html as H, json, re, sys, unicodedata

# (nguồn, mẫu tên dòng trong bài, mẫu tên dòng ở nguồn)
KHOP = {
    'huythanh': [(r'thị trường 24K', r'^Vàng thị trường 24k$'), (r'nguyên liệu 22K', r'nguyên liệu 22K$'),
                 (r'nguyên liệu 18K', r'nguyên liệu 18K$'), (r'nguyên liệu 14K', r'nguyên liệu 14K$'),
                 (r'nguyên liệu 10K', r'nguyên liệu 10K$')],
    'sjc': [(r'^Vàng SJC 1L', r'^Vàng SJC 1L, 10L, 1KG$'), (r'^Vàng SJC 5 chỉ', r'^Vàng SJC 5 chỉ$'),
            (r'^Vàng SJC 0\.5 chỉ', r'^Vàng SJC 0\.5 chỉ, 1 chỉ, 2 chỉ$'),
            (r'nhẫn SJC 99,99% \(1', r'^Vàng nhẫn SJC 99,99% 1 chỉ, 2 chỉ, 5 chỉ$'),
            (r'nhẫn SJC 99,99% \(0\.3', r'^Vàng nhẫn SJC 99,99% 0\.5 chỉ, 0\.3 chỉ$'),
            (r'^Nữ trang 99,99%', r'^Nữ trang 99,99%$'), (r'^Nữ trang 99%', r'^Nữ trang 99%$'),
            (r'^Nữ trang 75%', r'^Nữ trang 75%$'), (r'^Nữ trang 68%', r'^Nữ trang 68%$'),
            (r'^Nữ trang 61%', r'^Nữ trang 61%$'), (r'^Nữ trang 58,3%', r'^Nữ trang 58,3%$'),
            (r'^Nữ trang 41,7%', r'^Nữ trang 41,7%$')],
    'btmc': [(r'Vàng miếng VRTL', r'^VRTL Vàng miếng 999\.9'), (r'^Nhẫn tròn trơn', r'Nhẫn tròn trơn 999\.9'),
             (r'Quà mừng bản vị', r'Quà mừng bản vị vàng 999\.9'), (r'Vàng miếng SJC', r'^Vàng SJC Vàng miếng 999\.9'),
             (r'Rồng Thăng Long 999\.9', r'Rồng Thăng Long 999\.9'), (r'Rồng Thăng Long 99\.9', r'Rồng Thăng Long 99\.9 '),
             (r'Vàng nguyên liệu', r'^Vàng Thị Trường Vàng 999\.9')],
    'phuquy': [(r'^Vàng miếng SJC$', r'^Vàng miếng SJC$'), (r'^Nhẫn tròn Phú Quý 999\.9$', r'^Nhẫn tròn Phú Quý 999\.9$'),
               (r'^Phú Quý 1 lượng 999\.9$', r'^Phú Quý 1 Lượng 999\.9$'), (r'^Phú Quý 1 lượng 99\.9$', r'^Phú quý 1 lượng 99\.9$'),
               (r'^Vàng trang sức 999\.9$', r'^Vàng trang sức 999\.9$'), (r'^Vàng trang sức 999$', r'^Vàng trang sức 999$'),
               (r'^Vàng trang sức 99$', r'^Vàng trang sức 99$'), (r'^Vàng trang sức 98$', r'^Vàng trang sức 98$'),
               (r'^Vàng 999\.9 phi SJC$', r'^Vàng 999\.9 phi SJC$'), (r'^Vàng 999\.0 phi SJC$', r'^Vàng 999\.0 phi SJC$')],
    'doji': [(r'^Miếng SJC', r'^VÀNG MIẾNG SJC$'), (r'^KNT \+ KTT \+ Kim Giáp', r'^KIM TT/AVPL$'),
             (r'^Nữ trang 9999', r'^NỮ TRANG 9999$'), (r'^Nhẫn tròn 9999', r'^NHẪN TRÒN 9999 HƯNG THỊNH VƯỢNG$'),
             (r'nguyên liệu 18K', r'NGUY.N LI.U 18K$'), (r'nguyên liệu 14K', r'NGUY.N LI.U 14K$'),
             (r'nguyên liệu 10K', r'NGUY.N LI.U 10K$')],
    'pnj': [(r'^Vàng miếng SJC 999\.9$', r'^Vàng miếng SJC 999\.9$'), (r'^Nhẫn tròn PNJ 999\.9$', r'^Nhẫn Trơn PNJ 999\.9$'),
            (r'^Vàng Kim Bảo 999\.9$', r'^Vàng Kim Bảo 999\.9$'), (r'^Vàng Phúc Lộc Tài 999\.9$', r'^Vàng Phúc Lộc Tài 999\.9$'),
            (r'Phượng Hoàng$', r'Phượng Hoàng$'), (r'^Vàng trang sức 999\.9$', r'^Vàng nữ trang 999\.9$'),
            (r'^Vàng trang sức 999$', r'^Vàng nữ trang 999$'), (r'^Vàng trang sức 990$', r'^Vàng nữ trang 9920$'),
            (r'^Vàng trang sức 99$', r'^Vàng nữ trang 99$'), (r'^Vàng 916 \(22K\)$', r'^Vàng 916 \(22K\)$'),
            (r'^Vàng 750 \(18K\)$', r'^Vàng 750 \(18K\)$'), (r'^Vàng 680 \(16\.3K\)$', r'^Vàng 680 \(16\.3K\)$'),
            (r'^Vàng 650 \(15\.6K\)$', r'^Vàng 650 \(15\.6K\)$'), (r'^Vàng 610 \(14\.6K\)$', r'^Vàng 610 \(14\.6K\)$'),
            (r'^Vàng 585 \(14K\)$', r'^Vàng 585 \(14K\)$'), (r'^Vàng 333 \(8K\)$', r'^Vàng 333 \(8K\)$')],
}
GHI_CHU_KHOP = {('doji', r'^KNT \+ KTT \+ Kim Giáp'): 'DOJI không còn dòng "KNT + KTT + Kim Giáp" – lấy dòng "KIM TT/AVPL" (kim thần tài/ An Vượng Phát Lộc).',
                ('pnj', r'^Vàng trang sức 990$'): 'PNJ không có "990" – lấy dòng "Vàng nữ trang 9920".'}
DE_MUC = [(r'^1\. Giá vàng 24K', 'huythanh'), (r'^2\.1\. SJC', 'sjc'), (r'^2\.2\. Bảo Tín', 'btmc'),
          (r'^2\.3\. Phú Quý', 'phuquy'), (r'^2\.4\. DOJI', 'doji'), (r'^2\.5\. PNJ', 'pnj'), (r'^\d\. ', None)]
GIA_TRI = re.compile(r'^(?:[\d.,]+(?: đ)?|–|-|Liên hệ)$')


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def doc_xem(path):
    """Các dòng: (danh sách ô [(chữ, vị trí)], có phải dòng bắt đầu bằng '|'), toàn văn."""
    dong, van = [], ''
    for line in open(path, encoding='utf-8'):
        m = re.match(r'\s*\d+\.\s?(.*)$', line.rstrip('\n'))
        if not m:
            continue
        t = nfc(m.group(1))
        la_o = t.startswith('| ')
        noi = t[2:] if la_o else t
        bd = len(van)
        o, vt = [], 0
        for phan in noi.split(' | '):
            sach = phan.strip().rstrip('|').strip()
            if sach:
                o.append((sach, bd + noi.find(sach, vt)))
            vt += len(phan) + 3
        dong.append((o, la_o, noi))
        van += noi + '\n'
    return dong, van


def lan_thu(van, tim, vt):
    n, i = 0, van.find(tim)
    while i != -1 and i <= vt:
        n += 1
        i = van.find(tim, i + 1)
    return n


def so(x):
    d = re.sub(r'\D', '', x or '')
    return int(d) if d else None


def dong_nguon(ma, nguon):
    """Danh sách (tên, mua, bán) VND/chỉ của 1 nguồn; BTMC ghép tên nhóm vào dòng con."""
    out, nhom = [], ''
    for r in nguon['rows']:
        if len(r) < 2:
            continue
        if ma == 'btmc':
            if len(r) == 4 and so(r[2]):
                nhom = r[0]
                ten = f'{r[0]} {r[1]}'
                g = r[2:4]
            elif len(r) == 3 and so(r[1]):
                ten = f'{nhom} {r[0]}'
                g = r[1:3]
            else:
                continue
        else:
            # DOJI: cột đầu là STT; SJC (webgia): dòng đầu mỗi khu vực có thêm ô tên khu vực
            k = 1 if (ma == 'doji' and len(r) >= 3 and r[0].isdigit()) or (ma == 'sjc' and len(r) == 4) else 0
            ten, g = r[k], r[k + 1:k + 3]
        mua = so(g[0]) if g else None
        ban = so(g[1]) if len(g) > 1 else None
        if mua is None:
            continue
        nhan = 1000 if mua < 100000 else 1
        out.append((nfc(ten), mua * nhan, ban * nhan if ban else None))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem')
    ap.add_argument('--nguon')
    ap.add_argument('--goc')
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    ap.add_argument('--bo-to-ngay-the-gioi', metavar='BAI_MIN_HTML')
    a = ap.parse_args()

    if a.bo_to_ngay_the_gioi:
        p = a.bo_to_ngay_the_gioi
        h = open(p, encoding='utf-8').read()
        n = 0
        for nhan in ('thế giới hôm nay', 'Giá vàng thế giới ngày'):
            m = re.search(re.escape(nhan) + r'([ \xa0])(<span style="background-color:#ffff00[^"]*">(?:<span[^>]*>\d+</span>|[/\d])+</span>)', h)
            if m:
                h = h.replace(m.group(0), nhan + m.group(1) + re.sub(r'<[^>]+>', '', m.group(2)), 1)
                n += 1
        open(p, 'w', encoding='utf-8').write(h)
        print(f'Đã bỏ tô vàng {n} ngày gốc ở mục giá vàng thế giới')
        return

    dong, van = doc_xem(a.xem)
    nguon = json.load(open(a.nguon, encoding='utf-8'))
    bang = {ma: dong_nguon(ma, v) for ma, v in nguon.items() if v}
    sua, can, lech = [], [], []

    def them(cu, vt, moi, ng, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': ng, 'ly_do': ly, '_vt': vt})

    # Gom dòng bảng: dòng không bắt đầu bằng "|" mở hàng mới, các dòng "|" sau nó nối vào
    hang, ma = [], None
    for o, la_o, noi in dong:
        if not la_o:
            for mau, m2 in DE_MUC:
                if re.match(mau, noi):
                    ma = m2
                    break
            hang.append([ma, list(o)])
        elif hang:
            hang[-1][1].extend(o)
    da_bao = set()
    for ma, o in hang:
        if not ma:
            continue
        gt = [x for x in o if GIA_TRI.match(x[0])]
        ten = ' '.join(x[0] for x in o if not GIA_TRI.match(x[0]))
        if len(gt) < 2 or not ten:
            continue
        mua_o, ban_o = gt[-2], gt[-1]
        khop = next(((ma_bai, ma_ng) for ma_bai, ma_ng in KHOP.get(ma, []) if re.search(ma_bai, ten)), None)
        if not khop:
            can.append(f'Bảng {ma.upper()}: dòng "{ten}" không có ở nguồn – giữ nguyên.')
            continue
        if ma not in bang:
            if ma not in da_bao:
                can.append(f'Bảng {ma.upper()}: không đọc được nguồn – giữ nguyên cả bảng.')
                da_bao.add(ma)
            continue
        src = next((r for r in bang[ma] if re.search(khop[1], r[0], re.I)), None)
        if not src:
            can.append(f'Bảng {ma.upper()}: nguồn không còn dòng khớp "{ten}" – giữ nguyên.')
            continue
        if (ma, khop[0]) in GHI_CHU_KHOP:
            can.append(GHI_CHU_KHOP[(ma, khop[0])])
        ly = f'{ma.upper()} – "{src[0]}", cập nhật {nguon[ma]["cap_nhat"]}'
        for (cu, vt), moi, chieu in ((mua_o, src[1], 'mua'), (ban_o, src[2], 'bán')):
            so_cu = re.match(r'[\d,]+', cu)
            if moi is None:
                if so_cu:   # nguồn không còn niêm yết -> không để số cũ, ghi như các ô trống khác trong bảng
                    thay = 'Liên hệ' if ma == 'btmc' else '–'
                    them(cu, vt, thay, nguon[ma]['url'], f'{ly} – nguồn không niêm yết giá {chieu}')
                    can.append(f'Bảng {ma.upper()}, "{ten}": nguồn không niêm yết giá {chieu} – ghi "{thay}" thay số cũ {cu}.')
                continue
            if so_cu:
                them(so_cu.group(0), vt, f'{moi:,}', nguon[ma]['url'], ly)
            else:
                them(cu, vt, f'{moi:,}', nguon[ma]['url'], ly)

    # Chú thích ảnh có ngày dạng dd.mm.yyyy (+ giá Rồng Thăng Long) -> hôm nay / giá mới
    # Ngày ghi trong bài: chạy từ 15h giờ VN trở đi -> ghi ngày hôm sau (+9 giờ là sang ngày mới)
    hn = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))) + datetime.timedelta(hours=9)
    ngay_cham = hn.strftime('%d.%m.%Y')
    rtl = next((r for r in bang.get('btmc', []) if re.search(r'Rồng Thăng Long 999\.9', r[0])), None)
    for o, la_o, noi in dong:
        # dòng ảnh có dạng "[ẢNH: chữ thay thế]Chú thích hiện ra" -> chỉ sửa phần chú thích hiện ra (lần khớp cuối)
        m = ([None] + list(re.finditer(r'(Vàng miếng SJC vẫn có giá trên 14 vào ngày )(\d{2}\.\d{2}\.\d{4})', noi)))[-1]
        if m and o:
            ban_sjc = next((r[2] for r in bang.get('sjc', []) if r[0].startswith('Vàng SJC 1L')), None)
            if ban_sjc and ban_sjc > 14_000_000:
                them(m.group(0), o[0][1] + m.start(), m.group(1) + ngay_cham, '', 'chú thích ảnh: ngày = hôm nay (giá bán SJC vẫn trên 14 triệu/chỉ)')
            else:
                can.append('Chú thích ảnh SJC "vẫn có giá trên 14": giá bán SJC hôm nay không còn trên 14 triệu – giữ nguyên, cần sửa câu.')
        m = ([None] + list(re.finditer(r'(Vàng Rồng Thăng Long niêm yết giá )([\d,]+)( VND 1 chỉ vào ngày )(\d{2}\.\d{2}\.\d{4})', noi)))[-1]
        if m and o and rtl and rtl[2]:
            them(m.group(0), o[0][1] + m.start(), f'{m.group(1)}{rtl[2]:,}{m.group(3)}{ngay_cham}', nguon['btmc']['url'],
                 'chú thích ảnh: giá bán trang sức Rồng Thăng Long 999.9 hôm nay')

    # Mục 3 (giá vàng thế giới) theo giavang.org/the-gioi (quy đổi theo tỷ giá Vietcombank của nguồn)
    tg = nguon.get('thegioi')
    chu_tg = ' '.join(r[0] for r in tg['rows']) if tg else ''
    usd = re.search(r'XAU\) hôm nay là ([\d,]+\.?\d*) USD', chu_tg)
    luong = re.search(r'1 cây vàng[^.]*?có giá là ([\d.]+) VNĐ', chu_tg)
    ngay = f'{hn.day:02d}/{hn.month:02d}/{hn.year}'
    if usd and luong:
        usd_tron = round(float(usd.group(1).replace(',', '')))
        vnd = int(luong.group(1).replace('.', ''))
        for o, la_o, noi in dong:
            m = re.search(r'(Cập nhật giá vàng thế giới hôm nay )(\d{1,2}/\d{1,2}/\d{4})', noi)
            if m and o:
                them(m.group(0), o[0][1] + m.start(), m.group(1) + ngay, tg['url'], 'đề mục: ngày = hôm nay')
            m = re.search(r'(Giá vàng thế giới ngày )(\d{1,2}/\d{1,2}/\d{4})( giao dịch quanh ngưỡng )([\d,]+)( USD/ounce \(tương đương khoảng )([\d,]+)( VND/lượng quy đổi theo tỷ giá )(\w+)', noi)
            if m and o:
                g = list(m.groups())
                g[1], g[3], g[5], g[7] = ngay, f'{usd_tron:,}', f'{vnd:,}', 'Vietcombank'
                them(m.group(0), o[0][1] + m.start(), ''.join(g), tg['url'],
                     f'giavang.org {tg["cap_nhat"]}: {usd.group(1)} USD/ounce; 1 lượng = 1.20565303 ounce = {vnd:,} VNĐ theo tỷ giá Vietcombank')
        can.append('Mục 3: nguồn giavang.org quy đổi theo tỷ giá VIETCOMBANK (không có tỷ giá Techcombank) – câu đã đổi '
                   '"theo tỷ giá Techcombank" thành "theo tỷ giá Vietcombank" cho đúng nguồn, đồng thời sửa lỗi cũ (số cũ tính theo ounce). '
                   'Muốn giữ chữ Techcombank thì cần nguồn tỷ giá Techcombank.')
    else:
        can.append('Mục 3: không đọc được giavang.org/the-gioi – giữ nguyên đoạn giá vàng thế giới (cả ngày).')

    if a.kiem:
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} chỗ lệch: ' + '; '.join(lech[:20]))
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

"""Tự lập sua.json cho bài TCB "Giá lúa gạo hôm nay" (không gọi mạng, không dùng AI).

  python3 -I tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
  python3 -I tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   → "khớp hết"

Bảng gạo / nếp / lúa trong nước (Tên | Giá cũ | Giá mới | Thay đổi): khớp từng dòng theo TÊN với bảng banggianongsan.com
  (bỏ "(đ/kg)", bỏ ngoặc, không phân biệt hoa thường) → chép đúng giá cũ, giá mới, thay đổi của nguồn, viết theo kiểu bài
  ("8,900 - 9,000", "28,000"; thay đổi "+50đ đến +100đ" / "Không đổi" – kiểu chữ lấy theo ô thay đổi đang có trong bài).
  Nguồn để trống giá mới / không có dòng đó → giữ nguyên cả dòng + cần duyệt.
Bảng thế giới (Thị trường | Loại gạo | Giá | Thay đổi): ưu tiên bảng Thái Lan / Ấn Độ trong bài vietbao.vn 3 ngày gần nhất;
  không có → bản tin VFA (vietfood.org.vn, số Oryza) mới nhất ≤ 4 ngày; thay đổi = giá kỳ này − giá bản tin kỳ trước (tính toán).
  Không có nguồn nào → giữ nguyên số + trả lại ngày gốc ở tiêu đề mục 2 (không để ngày mới đứng cạnh giá cũ) + cần duyệt.
banggianongsan.com không đọc được → giữ mọi số trong nước + trả lại mọi ngày về ngày gốc của bài (trừ ngày không tìm lại được).
"""
import argparse, datetime, html, json, re, sys, unicodedata

VN = datetime.timezone(datetime.timedelta(hours=7))
RE_NGAY = re.compile(r'\b(\d{1,2}/\d{1,2}/\d{4})\b')
VFA_TUOI = 4          # bản tin VFA cũ hơn số ngày này → không dùng


def nfc(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', s)).strip()


def chuan_ten(s):
    s = nfc(s).lower()
    s = re.sub(r'\((đ|vnd)/kg\)', ' ', s)
    return re.sub(r'\s+', ' ', re.sub(r'[()]', ' ', s)).strip()


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


def hang(dong):
    """Các dòng bảng: (tên, vị trí, [ô (chữ, vị trí)…]) — tên là khối thường, ngay sau là các ô '| '."""
    kq = []
    for i, (chu, vt, la_o) in enumerate(dong):
        if la_o:
            continue
        o, j = [], i + 1
        while j < len(dong) and dong[j][2]:
            o.append((dong[j][0], dong[j][1])); j += 1
        if o:
            kq.append((chu, vt, o))
    return kq


def kieu_so(cu):
    """lấy kiểu viết của ô cũ: dấu nghìn và dấu nối khoảng"""
    nghin = '.' if re.search(r'\d\.\d{3}\b', cu) and not re.search(r'\d,\d{3}\b', cu) else ','
    m = re.search(r'\d(\s*[-–~]\s*)\d', cu)
    return nghin, (m.group(1) if m else ' - ')


def viet_so(x, nghin):
    return f'{x:,}'.replace(',', nghin)


def viet_khoang(k, cu):
    nghin, noi = kieu_so(cu)
    return viet_so(k[0], nghin) if k[0] == k[1] else viet_so(k[0], nghin) + noi + viet_so(k[1], nghin)


def kieu_thay_doi(cac_o):
    """kiểu ghi cột Thay đổi đang có trong bài: 'A' = '+50đ đến +100đ', 'B' = '+50 đến +100 đ'"""
    for o in cac_o:
        if re.search(r'\d+đ\b', o):
            return 'A'
        if re.search(r'\d+ đ\b', o):
            return 'B'
    return 'A'


def viet_thay_doi(src, kieu):
    if re.search(r'không đổi', src, re.I):
        return 'Không đổi'
    so = re.findall(r'[+-]?\d[\d.]*', src.replace('−', '-'))
    if not so or len(so) > 2:
        return None
    vals = [int(x.replace('.', '')) for x in so]
    if all(v == 0 for v in vals):
        return 'Không đổi'
    ky = [f'{v:+,}' if v else '0' for v in vals]
    if kieu == 'A':
        return ' đến '.join(k + 'đ' for k in ky)
    return ' đến '.join(ky) + ' đ'


def ngay_goc_cua(dong_chu, goc_txt, goc_raw=''):
    """tìm lại ngày gốc của 1 khối chữ có ngày (khớp phần chữ quanh ngày trong bài gốc)"""
    if not goc_txt or not RE_NGAY.search(dong_chu):
        return None
    phan = RE_NGAY.split(dong_chu)
    if len(''.join(phan[::2]).strip()) < 15:          # khối chỉ có ngày = ngày đăng: công cụ chung lấy từ article-header-body--date
        m = re.search(r'article-header-body--date">(\d{4})-(\d{2})-(\d{2})', goc_raw)
        return (f'{m.group(3)}/{m.group(2)}/{m.group(1)}',) if m and dong_chu.strip() == RE_NGAY.search(dong_chu).group(1) else None
    mau = ''
    for k, p in enumerate(phan):
        mau += re.escape(p[-60:] if k == 0 else p[:60]) if k % 2 == 0 else r'(\d{1,2}/\d{1,2}/\d{4})'
        if k % 2 == 0 and k > 0:
            break
    m = re.search(mau, goc_txt)
    return m.groups() if m else None


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
    goc_txt = goc_raw = ''
    if a.goc:
        try:
            g = goc_raw = open(a.goc, encoding='utf-8').read()
            g = re.sub(r'(?s)<(script|style)[^>]*>.*?</\1>', ' ', g)
            goc_txt = nfc(html.unescape(re.sub(r'<[^>]+>', ' ', g)))
        except OSError:
            pass
    hn = datetime.datetime.now(VN).date()
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

    cac_hang = hang(dong)
    # ---------- 1. Bảng trong nước ----------
    noi_dia = [h for h in cac_hang if len(h[2]) == 3 and re.search(r'\d', h[2][0][0])
               and re.match(r'(gạo|nếp|lúa|tp)\b', chuan_ten(h[0]))]
    kieu = kieu_thay_doi([h[2][2][0] for h in noi_dia])
    b = gia.get('bgns')
    if not b:
        can.append('banggianongsan.com không đọc được → giữ nguyên mọi giá gạo, nếp, lúa trong nước; ngày trong bài trả lại như bài gốc.')
    else:
        nguon = b['nguon']
        theo_ten = {chuan_ten(d['ten']): d for d in b['dong']}
        da_dung = set()
        can.append(f"Giá trong nước lấy từ bảng mới nhất của banggianongsan.com: 'Bảng giá lúa gạo mới nhất - {b['ngay_bang']}' "
                   f"(đăng {b['dang_luc']}); bài ghi ngày hôm sau theo quy tắc.")
        for ten, vt, o in noi_dia:
            d = theo_ten.get(chuan_ten(ten))
            if not d:
                can.append(f'Dòng "{ten}": nguồn không có dòng này → giữ nguyên.')
                continue
            da_dung.add(chuan_ten(d['ten']))
            if not d['moi'] or not d['cu']:
                can.append(f'Dòng "{ten}": nguồn chưa có đủ giá ("{d["goc"]}") → giữ nguyên cả dòng.')
                continue
            td = viet_thay_doi(d['thay_doi'], kieu)
            if td is None:
                can.append(f'Dòng "{ten}": không đọc được cột thay đổi của nguồn ("{d["thay_doi"]}") → giữ nguyên cả dòng.')
                continue
            ly = f"{b['ngay_bang']} (đăng {b['dang_luc']}), nguồn ghi: {d['goc']}"
            them(o[0][0], o[0][1], viet_khoang(d['cu'], o[0][0]), nguon, f'{ten} – giá cũ. {ly}')
            them(o[1][0], o[1][1], viet_khoang(d['moi'], o[1][0]), nguon, f'{ten} – giá mới. {ly}')
            them(o[2][0], o[2][1], td, nguon, f'{ten} – thay đổi. {ly}')
        thua = [d for d in b['dong'] if chuan_ten(d['ten']) not in da_dung]
        if thua:
            can.append('Nguồn có thêm ' + '; '.join(f"{d['ten']} ({d['goc'].split(' | ', 1)[1]})" for d in thua)
                       + ' nhưng bài không có các dòng này → không thêm (quy tắc không thay đổi nội dung).')

    # ---------- 2. Bảng thế giới ----------
    the_gioi = [h for h in cac_hang if len(h[2]) == 3 and re.match(r'(thái lan|ấn độ|pakistan|việt nam)$', chuan_ten(h[0]))]

    def loai_ngan(s):
        s = chuan_ten(s)
        s = re.sub(r'\b(gạo|trắng|stxd|tấm)\b', ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return '100%' if s == 'a1 super' else s

    tg_ok = False
    vb = (gia.get('vietbao') or {}).get('the_gioi')
    vfa = gia.get('vfa')
    vfa_ngay = datetime.datetime.strptime(vfa['ngay'], '%d/%m/%Y').date() if vfa else None
    if the_gioi and vb:
        bang = {(chuan_ten(d['thi_truong']), loai_ngan(d['loai'])): d for d in vb['dong']}
        so_dong = 0
        for ten, vt, o in the_gioi:
            d = bang.get((chuan_ten(ten), loai_ngan(o[0][0])))
            if not d or not d['gia']:
                can.append(f'Bảng thế giới – {ten} {o[0][0]}: bài vietbao {vb["ngay"]} không có dòng này → giữ nguyên.')
                continue
            so_dong += 1
            ly = f"vietbao.vn {vb['ngay']}, nguồn ghi: {d['goc']}"
            them(o[1][0], o[1][1], viet_khoang(d['gia'], o[1][0]), vb['url'], f'{ten} {o[0][0]} – giá. {ly}')
            m = re.search(r'không đổi', d['thay_doi'], re.I) or re.search(r'([+-]\s?\d+)', d['thay_doi'])
            if m:
                td = 'Không đổi' if m.group(0).lower() == 'không đổi' else m.group(1).replace(' ', '')
                them(o[2][0], o[2][1], td, vb['url'], f'{ten} {o[0][0]} – thay đổi. {ly}')
            else:
                can.append(f'Bảng thế giới – {ten} {o[0][0]}: nguồn không ghi mức thay đổi → giữ "{o[2][0]}".')
        tg_ok = so_dong > 0
    elif the_gioi and vfa and (hn - vfa_ngay).days <= VFA_TUOI:
        bang = {(chuan_ten(d['quoc_gia']), loai_ngan(d['loai'])): d for d in vfa['dong']}
        truoc = {(chuan_ten(d['quoc_gia']), loai_ngan(d['loai'])): d for d in (vfa['truoc'] or {}).get('dong', [])}
        so_dong = 0
        for ten, vt, o in the_gioi:
            k = (chuan_ten(ten), loai_ngan(o[0][0]))
            d = bang.get(k)
            if not d:
                can.append(f'Bảng thế giới – {ten} {o[0][0]}: bản tin VFA {vfa["ngay"]} không có dòng này → giữ nguyên.')
                continue
            so_dong += 1
            ly = f"VFA (vietfood.org.vn, số liệu Oryza) bản tin {vfa['ngay']}, nguồn ghi: {d['goc']}"
            them(o[1][0], o[1][1], viet_khoang(d['gia'], o[1][0]), vfa['url'], f'{ten} {o[0][0]} – giá. {ly}')
            t = truoc.get(k)
            if not t:
                can.append(f'Bảng thế giới – {ten} {o[0][0]}: không có bản tin VFA kỳ trước để tính thay đổi → giữ "{o[2][0]}".')
                continue
            c = [d['gia'][0] - t['gia'][0], d['gia'][1] - t['gia'][1]]
            td = 'Không đổi' if c == [0, 0] else (f'{c[0]:+d}' if c[0] == c[1] else f'{c[0]:+d} đến {c[1]:+d}')
            them(o[2][0], o[2][1], td, vfa['url'],
                 f"{ten} {o[0][0]} – thay đổi = giá {vfa['ngay']} ({d['gia'][0]} - {d['gia'][1]}) − giá kỳ trước "
                 f"{vfa['truoc']['ngay']} ({t['goc']}) = {c[0]:+d} / {c[1]:+d}. {ly}", tinh=True)
        tg_ok = so_dong > 0
        if tg_ok:
            can.append(f"Bảng giá gạo thế giới lấy từ nguồn THAY THẾ: Hiệp hội Lương thực Việt Nam (VFA, số liệu Oryza) bản tin {vfa['ngay']} "
                       f"vì bài vietbao.vn 3 ngày gần nhất không có bảng thế giới. Ghép dòng: Thái Lan 5% tấm = '5% tấm'; "
                       f"Thái Lan 100% tấm = 'A1 Super'; Ấn Độ 100% tấm = '100% tấm Stxd'; Ấn Độ gạo đồ 5% tấm = 'Gạo đồ 5% Stxd'. "
                       f"Cột thay đổi tính so với bản tin {vfa['truoc']['ngay'] if vfa.get('truoc') else '?'} – cần duyệt.")
    if the_gioi and not tg_ok:
        ly = []
        if not gia.get('vietbao'):
            ly.append('vietbao.vn không đọc được')
        elif not vb:
            ly.append('các bài vietbao.vn 3 ngày gần nhất không có bảng giá gạo thế giới')
        if 'vfa' in gia and not vfa:
            ly.append('VFA không đọc được')
        elif vfa and (hn - vfa_ngay).days > VFA_TUOI:
            ly.append(f'bản tin VFA mới nhất đã cũ ({vfa["ngay"]})')
        can.append('Mục 2 – Bảng giá lúa gạo thế giới: ' + '; '.join(ly or ['không có nguồn'])
                   + ' → giữ nguyên số, ngày ở tiêu đề mục 2 giữ như bài gốc.')

    # ---------- 3. Ngày: trả lại ngày gốc ở chỗ giá không được cập nhật ----------
    for chu, vt, la_o in dong:
        if la_o or not RE_NGAY.search(chu):
            continue
        la_tg = bool(re.search(r'giá lúa gạo thế giới', chu, re.I))
        if b and not (la_tg and the_gioi and not tg_ok):
            continue
        cu = ngay_goc_cua(chu, goc_txt, goc_raw)
        moi = RE_NGAY.search(chu).group(1)
        if cu is None:
            if b is None:
                can.append(f'Ngày "{moi}" ở khối "{chu[:50]}" không tìm lại được ngày gốc → để nguyên, cần duyệt.')
            continue
        m = RE_NGAY.search(chu)
        dau = max(0, m.start() - 40)
        them(chu[dau:m.end()], vt + dau, chu[dau:m.start()] + cu[0], '',
             'giá ở phần này chưa cập nhật được → giữ ngày như bài gốc')

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

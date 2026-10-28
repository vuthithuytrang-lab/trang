"""Tự lập sua.json cho bài TCB "Giá nhôm hôm nay: Bảng giá cập nhật và các yếu tố ảnh hưởng đến thị trường".

  python3 -I tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
  python3 -I tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html

--gia: kết quả lay_gia.js (TradingView + Phế Liệu Quang Phong). --goc: bài gốc tải từ web (để lấy lại ngày cũ khi nguồn hỏng).
Mọi con số ghi vào bài đều lấy thẳng từ chữ trên nguồn (gia.json giữ nguyên chữ gốc), chỉ đổi cách viết cho giống bài:
- Bảng thế giới: khớp từng dòng theo MÃ hợp đồng (ALIV2026…). Giá: bài ghi số nguyên thì bỏ phần lẻ (3,285.25 -> 3,285),
  bài ghi 2 số lẻ thì giữ; % thay đổi chép nguyên (dấu trừ "−" -> "-").
  Mã trong bài không còn trên nguồn (hợp đồng đã đáo hạn) -> cuộn bảng: các dòng lấy đúng N hợp đồng đầu tiên trên nguồn
  (xếp theo ngày đáo hạn), ghi cần duyệt.
- Bảng trong nước: khớp theo TÊN loại nhôm với bảng Quang Phong; "67.000 - 90.000 đ/kg" -> "67,000 - 90,000".
- Nguồn nào không đọc được: giữ số cũ + cần duyệt, và trả ngày ở tiêu đề/câu dẫn của bảng đó về ngày cũ của bài
  (để bài không ghi ngày mới cho giá cũ). Cả 2 nguồn hỏng -> trả mọi ngày trong bài về ngày cũ.
Không dùng mạng, không dùng số nào ngoài gia.json và bài.
"""
import argparse, datetime, html, json, re, sys, unicodedata
from decimal import Decimal, ROUND_DOWN

MA = re.compile(r'^ALI[FGHJKMNQUVXZ]\d{4}$')
NGAY = r'\d{1,2}/\d{1,2}/\d{4}'


def nfc(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', s)).strip()


def doc_xem(path):
    """-> danh sách (chữ, vị trí trong 'van', là_ô); van = các khối nối bằng 1 dấu cách (giống chữ hiển thị mà lệnh sua tìm)."""
    dong, van = [], ''
    for line in open(path, encoding='utf-8'):
        m = re.match(r'\s*\d+\.\s?(.*)$', line.rstrip('\n'))
        if not m:
            continue
        t = m.group(1)
        la_o = t.startswith('| ')
        chu = nfc(t[2:] if la_o else re.sub(r'^\[ẢNH: [^\]]*\]', '', t))
        if not chu:
            continue
        if van:
            van += ' '
        dong.append((chu, len(van), la_o))
        van += chu
    return dong, van


def lan_thu(van, tim, vt):
    n, i = 0, van.find(tim)
    while i != -1 and i <= vt:
        n += 1
        i = van.find(tim, i + 1)
    return max(n, 1)


def ten_chuan(x):
    x = nfc(x).lower()
    return re.sub(r'^giá ', '', x)


def viet_gia_tg(goc, cu):
    """Giá nguồn '3,285.25' -> theo cách viết ô cũ: số nguyên (bỏ phần lẻ) hoặc giữ đúng số chữ số lẻ của ô cũ."""
    d = Decimal(goc.replace(',', ''))
    m = re.search(r'\.(\d+)$', cu)
    le = len(m.group(1)) if m else 0
    d = d.quantize(Decimal(1).scaleb(-le), rounding=ROUND_DOWN)
    s = f'{d:,.{le}f}'
    if ',' not in cu and len(cu.split('.')[0]) > 3:
        s = s.replace(',', '')
    return s


def viet_khoang(goc, cu):
    """'67.000 - 90.000 đ/kg' -> thay lần lượt từng số trong ô cũ ('67,000 - 90,000'), giữ dấu nghìn của ô cũ."""
    moi = [int(x.replace('.', '').replace(',', '')) for x in re.findall(r'\d{1,3}(?:[.,]\d{3})+|\d+', goc)]
    so_cu = list(re.finditer(r'\d{1,3}(?:[.,]\d{3})+|\d+', cu))
    if len(moi) != len(so_cu) or not moi:
        return None
    nghin = ',' if ',' in cu else '.'
    ra, cuoi = '', 0
    for m, v in zip(so_cu, moi):
        ra += cu[cuoi:m.start()] + f'{v:,}'.replace(',', nghin)
        cuoi = m.end()
    return ra + cu[cuoi:]


def ngay_goc(path):
    goc = nfc(html.unescape(re.sub(r'<[^>]+>', ' ', open(path, encoding='utf-8').read())))
    kq = {}
    for k, p in (('tg', r'Giá nhôm thế giới ngày (' + NGAY + ')'), ('tg2', r'tại thời điểm ngày (' + NGAY + ')'),
                 ('tn', r'Giá nhôm trong nước ngày (' + NGAY + ')'), ('chung', r'[Gg]iá nhôm hôm nay (' + NGAY + ')')):
        m = re.search(p, goc)
        kq[k] = m.group(1) if m else None
    return kq


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
    except Exception:
        gia = {}
    tv, qp = gia.get('tradingview'), gia.get('quangphong')
    sua, can, lech = [], [], []

    def them(cu, vt, moi, nguon, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    # ---------- bảng thế giới: dòng = ô mã (không phải ô "|") + 2 ô ----------
    hang_tg = []
    for i, (chu, vt, la_o) in enumerate(dong):
        if not la_o and MA.match(chu) and i + 2 < len(dong) and dong[i + 1][2] and dong[i + 2][2]:
            hang_tg.append((chu, dong[i + 1][0], dong[i + 2][0], vt))
    if not hang_tg:
        can.append('Không tìm thấy bảng giá nhôm thế giới (mã ALI…) trong bài – bài có thể đã đổi trình bày, cần xem tay.')
    elif not tv:
        can.append('Bảng giá nhôm thế giới: không đọc được TradingView – giữ nguyên giá và % thay đổi cũ, giữ ngày cũ của bảng.')
    else:
        nguon_tg = tv['nguon']
        hd = {h['ma']: h for h in tv['hop_dong']}
        ma_bai = [h[0] for h in hang_tg]
        if all(m in hd for m in ma_bai):
            dich = ma_bai
        else:                                            # hợp đồng đầu đã đáo hạn -> cuộn theo danh sách của nguồn
            theo_han = sorted(tv['hop_dong'], key=lambda h: h['dao_han'])
            dich = [h['ma'] for h in theo_han[:len(ma_bai)]]
            if len(dich) < len(ma_bai):
                dich = None
                can.append(f'Bảng giá nhôm thế giới: nguồn chỉ có {len(theo_han)} hợp đồng, ít hơn {len(ma_bai)} dòng của bài – giữ nguyên cả bảng.')
            elif not a.kiem:
                bo = [m for m in ma_bai if m not in hd]
                can.append(f'Bảng giá nhôm thế giới: hợp đồng {", ".join(bo)} không còn trên TradingView (đã đáo hạn) → đã cuộn mã: '
                           f'bảng nay là {len(dich)} hợp đồng đầu tiên trên nguồn ({dich[0]} … {dich[-1]}). Kiểm tra lại mã hợp đồng.')
                ky = [chu for chu, _, _ in dong if chu.startswith('Ký tự ')]
                if ky:
                    co = set(re.findall(r'\b([A-Z])\b', ky[0].split(':')[0]))
                    thieu = sorted({m[3] for m in dich} - co)
                    if thieu:
                        can.append(f'Dòng "{ky[0][:60]}…" chưa có ký tự tháng {", ".join(thieu)} của mã mới – giữ nguyên câu, cần thêm tay nếu muốn.')
        if dich:
            for (ma, gcu, tcu, vt), mm in zip(hang_tg, dich):
                h = hd[mm]
                try:
                    gmoi = viet_gia_tg(h['gia'], gcu)
                except Exception:
                    can.append(f'{ma}: giá trên nguồn "{h["gia"]}" không đọc được thành số – giữ nguyên dòng này.')
                    continue
                tmoi = h['thay_doi'].strip()
                if not re.fullmatch(r'[+-]?\d+(\.\d+)?%', tmoi):
                    can.append(f'{ma}: % thay đổi trên nguồn "{h["thay_doi"]}" lạ – giữ nguyên dòng này.')
                    continue
                cu, moi = f'{ma} {gcu} {tcu}', f'{mm} {gmoi} {tmoi}'
                them(cu, vt, moi, nguon_tg,
                     f'TradingView dòng {mm} (đáo hạn {h["dao_han"]}): Price "{h["gia"]}", Chg % "{h["thay_doi"]}"'
                     f' – As of {tv.get("cap_nhat", "?")}{" (giá trễ D)" if h.get("tre") else ""}. Bài ghi giá số nguyên thì bỏ phần lẻ.')

    # ---------- bảng trong nước: dòng = tên (không phải ô) + 1 ô "số - số" ----------
    hang_tn = []
    for i, (chu, vt, la_o) in enumerate(dong):
        if not la_o and 'nhôm' in chu.lower() and i + 1 < len(dong) and dong[i + 1][2] \
                and re.fullmatch(r'[\d.,]+\s*-\s*[\d.,]+', dong[i + 1][0]):
            hang_tn.append((chu, dong[i + 1][0], vt))
    if not hang_tn:
        can.append('Không tìm thấy bảng giá nhôm trong nước trong bài – bài có thể đã đổi trình bày, cần xem tay.')
    elif not qp:
        can.append('Bảng giá nhôm trong nước: không đọc được Phế Liệu Quang Phong – giữ nguyên giá cũ, giữ ngày cũ của bảng.')
    else:
        nguon_qp = qp['nguon']
        ds = {ten_chuan(k): (k, v) for k, v in qp['dong'].items()}
        for ten, ocu, vt in hang_tn:
            x = ds.get(ten_chuan(ten))
            if not x:
                can.append(f'Bảng giá nhôm trong nước: dòng "{ten}" không có trên bảng Quang Phong – giữ nguyên "{ocu}".')
                continue
            omoi = viet_khoang(x[1], ocu)
            if not omoi:
                can.append(f'Bảng giá nhôm trong nước: dòng "{ten}" nguồn ghi "{x[1]}" khác dạng "{ocu}" – giữ nguyên.')
                continue
            them(f'{ten} {ocu}', vt, f'{ten} {omoi}', nguon_qp,
                 f'Quang Phong dòng "{x[0]}": "{x[1]}" (bảng "Cập nhật ngày {qp.get("cap_nhat", "?")}").')
        try:
            d = datetime.datetime.strptime(qp.get('cap_nhat', ''), '%d/%m/%Y').date()
            hom_nay = (datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))).date()
            if (hom_nay - d).days > 10 and not a.kiem:
                can.append(f'Bảng Quang Phong ghi "Cập nhật ngày {qp["cap_nhat"]}" – đã cũ hơn 10 ngày, kiểm tra lại giá trong nước.')
        except ValueError:
            if not a.kiem:
                can.append('Bảng Quang Phong không ghi rõ ngày cập nhật – kiểm tra lại giá trong nước.')

    # ---------- ngày: nguồn hỏng -> trả về ngày cũ của bài gốc ----------
    if a.goc and (not tv or not qp):
        g = ngay_goc(a.goc)
        mau = []
        if not tv:
            mau += [(r'(Giá nhôm thế giới ngày )(' + NGAY + ')', g['tg']), (r'(tại thời điểm ngày )(' + NGAY + ')', g['tg2'])]
        if not qp:
            mau += [(r'(Giá nhôm trong nước ngày )(' + NGAY + ')', g['tn'])]
        if not tv and not qp:
            mau += [(r'([Gg]iá nhôm hôm nay )(' + NGAY + ')', g['chung']), (r'^()(' + NGAY + ')$', g['chung'])]
        for p, cu_ngay in mau:
            if not cu_ngay:
                continue
            for chu, vt, _ in dong:
                for m in re.finditer(p, chu):
                    them(m.group(0), vt + m.start(), m.group(1) + cu_ngay, '',
                         'nguồn không đọc được → giữ ngày cũ của bài để không ghi ngày mới cho giá cũ')
        if not a.kiem:
            can.append('Có nguồn không đọc được → ngày của phần đó giữ như bài cũ.')

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

"""Tự lập sua.json cho bài TCB "Giá điều hôm nay" (https://techcombank.com/thong-tin/blog/gia-dieu-hom-nay).

  python3 -I tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
  python3 -I tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   -> "khớp hết"

Bảng bài: Nông sản (Đơn vị tính) | Giá cũ | Giá mới | Thay đổi — chép đúng theo bảng banggianongsan.com (cùng 12 dòng, cùng cột).
- Ghép dòng theo TÊN (bỏ dấu cách thừa, "vnđ" = "VND", không phân biệt hoa thường), không theo thứ tự.
- Giá cũ / Giá mới: khoảng "X - Y" viết theo cách của ô cũ: VND dấu phẩy ngăn nghìn (25,000), USD dấu phẩy thập phân (10,5),
  nối bằng đúng dấu nối của ô cũ (" - "). Số lượng số khác ô cũ (vd nguồn chỉ ghi 1 mức) -> giữ nguyên + cần duyệt.
- Thay đổi: chép chữ của nguồn ("Không đổi"); khác "Không đổi" -> vẫn chép (đổi cách viết số theo bài) + cần duyệt để đọc lại.
Đoạn văn: bài hiện không có giá nào ngoài bảng. Dòng chữ nào (ngoài bảng) có số tiền VND/USD -> cần duyệt (chưa có quy tắc).
Ngày: lệnh `dung` đã đổi mọi ngày sang ngày hôm sau. Nguồn hỏng -> trả mọi ngày về đúng ngày gốc (đọc từ --goc) + giữ giá cũ.
"""
import argparse, datetime, html, json, re, sys, unicodedata

RE_NGAY = re.compile(r'\d{1,2}/\d{1,2}/\d{4}')
RE_TIEN = re.compile(r'\d{1,3}(?:[.,]\d{3})+\s*(?:VND|VNĐ|đồng|đ)\b|\d+(?:[.,]\d+)?\s*(?:USD|\$)', re.I)


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def khoa(ten):
    t = nfc(ten).lower().replace('vnđ', 'vnd')
    return re.sub(r'\s+', ' ', re.sub(r'\s*([()/])\s*', r'\1', t)).strip()


def khoa_ngan(ten, usd):
    """dự phòng: tên bỏ phần trong ngoặc + loại tiền"""
    return (re.sub(r'\(.*?\)', '', khoa(ten)).strip(), usd)


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


def viet_so(x, usd, o_cu):
    """x = chuỗi số đúng như nguồn ('10.5', '25000'); chỉ đổi dấu phân cách theo ô cũ, không làm tròn"""
    if usd:
        return x.replace('.', ',') if re.search(r'\d,\d', o_cu) else x
    s = f'{int(x):,}'
    return s.replace(',', '.') if re.search(r'\d\.\d{3}', o_cu) else s


def viet_o(ds, usd, o_cu):
    """viết list số theo kiểu ô cũ; None nếu số lượng số khác ô cũ"""
    so_cu = list(re.finditer(r'\d[\d.,]*\d|\d', o_cu))
    if len(so_cu) != len(ds):
        return None
    ra, cuoi = [], 0
    for m, x in zip(so_cu, ds):
        ra.append(o_cu[cuoi:m.start()] + viet_so(x, usd, o_cu))
        cuoi = m.end()
    return ''.join(ra) + o_cu[cuoi:]


def viet_thay_doi(t, usd, o_cu):
    t = re.sub(r'vnđ', 'VND', nfc(t), flags=re.I)
    if usd:   # USD: dấu chấm thập phân -> dấu phẩy như bài
        return re.sub(r'(\d)\.(\d)', r'\1,\2', t)
    return re.sub(r'(\d)\.(\d{3})', r'\1,\2', t)


def chu_goc(path):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', open(path, encoding='utf-8').read())))


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
        g = json.load(open(a.gia, encoding='utf-8')).get('banggianongsan')
    except Exception:
        g = None
    sua, can, lech = [], [], []

    def them(cu, vt, moi, nguon, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    # 1) Bảng giá: dòng tên (không phải ô) + 3 ô theo sau
    hang = []
    for i, (chu, vt, la_o) in enumerate(dong):
        if la_o or 'điều' not in chu.lower():
            continue
        cells = []
        j = i + 1
        while j < len(dong) and dong[j][2]:
            cells.append(dong[j]); j += 1
        if len(cells) >= 3 and re.search(r'\d', cells[0][0] + cells[1][0]):
            hang.append((chu, cells))
    da_ghep = set()
    if g:
        theo_ten = {khoa(d['ten']): d for d in g['dong']}
        theo_ten_ngan = {khoa_ngan(d['ten'], d['usd']): d for d in g['dong']}
        for ten, cells in hang:
            usd = 'usd' in ten.lower()
            d = theo_ten.get(khoa(ten)) or theo_ten_ngan.get(khoa_ngan(ten, usd))
            if not d:
                can.append(f'Dòng "{ten}": nguồn không có dòng cùng tên – giữ nguyên giá cũ.')
                continue
            da_ghep.add(d['ten'])
            ly0 = f'banggianongsan.com, dòng "{d["ten"]}" (cập nhật {g["cap_nhat"]}): ' + ' | '.join(d['chu_goc'])
            for k, ds in ((0, d['cu']), (1, d['moi'])):
                o_cu, vt = cells[k][:2]
                moi = viet_o(ds, usd, o_cu) if ds else None
                if moi is None:
                    can.append(f'Dòng "{ten}", cột {"Giá cũ" if k == 0 else "Giá mới"}: nguồn ghi "{d["chu_goc"][k]}" '
                               f'không cùng dạng với bài ("{o_cu}") – giữ nguyên.')
                    continue
                them(o_cu, vt, moi, g['nguon'], ('Giá cũ' if k == 0 else 'Giá mới') + ' theo ' + ly0)
            o_cu, vt = cells[2][:2]
            moi = viet_thay_doi(d['thay_doi'], usd, o_cu)
            if not moi:
                can.append(f'Dòng "{ten}", cột Thay đổi: nguồn để trống – giữ nguyên.')
            elif moi.lower() == 'không đổi':
                them(o_cu, vt, moi, g['nguon'], 'Thay đổi theo ' + ly0)
            else:
                them(o_cu, vt, moi, g['nguon'], 'Thay đổi theo ' + ly0)
                can.append(f'Dòng "{ten}", cột Thay đổi: chép từ nguồn "{d["thay_doi"]}" thành "{moi}" – đọc lại cách ghi.')
        for d in g['dong']:
            if d['ten'] not in da_ghep:
                can.append(f'Nguồn có dòng "{d["ten"]}" mà bài không có – không tự thêm dòng.')
        try:
            ngay = datetime.datetime.strptime(g['cap_nhat'].split()[-1], '%d/%m/%Y').date()
            hom_nay = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).date()
            if (hom_nay - ngay).days > 2:
                can.append(f'Nguồn banggianongsan.com cập nhật lần cuối {g["cap_nhat"]} (đã {(hom_nay - ngay).days} ngày) – '
                           'giá trong bài lấy theo bảng đó, nên xem lại.')
        except Exception:
            pass
    else:
        can.append('Không đọc được nguồn banggianongsan.com – giữ nguyên toàn bộ bảng giá điều, giữ nguyên ngày gốc của bài.')
        if a.goc:
            goc = chu_goc(a.goc)
            for chu, vt, la_o in dong:
                if la_o or not RE_NGAY.search(chu):
                    continue
                mau = RE_NGAY.split(chu)
                rx = '(\\d{1,2}/\\d{1,2}/\\d{4})'.join(r'\s*'.join(map(re.escape, p.split())) for p in mau)
                rx = rx.replace('(\\d{1,2}/\\d{1,2}/\\d{4})', r'\s*(\d{1,2}/\d{1,2}/\d{4})\s*')
                mg = re.search(rx, goc)
                if not mg:
                    can.append(f'Không tìm thấy ngày gốc cho dòng "{chu[:60]}" – kiểm tra ngày bằng tay.')
                    continue
                for m, ngay_cu in zip(RE_NGAY.finditer(chu), mg.groups()):
                    bd = max(0, m.start() - 25)
                    cu = chu[bd:m.end()]
                    them(cu, vt + bd, chu[bd:m.start()] + ngay_cu, '', 'nguồn giá không đọc được nên giữ ngày gốc của bài')

    # 2) Số tiền nằm ngoài bảng (đoạn văn, FAQ, ví dụ) – bài hiện không có; có thì báo
    o_bang = {c[0] for _, cells in hang for c in cells} | {t for t, _ in hang}
    for i, (chu, vt, la_o) in enumerate(dong, 1):
        if la_o or chu in o_bang:
            continue
        m = RE_TIEN.search(chu)
        if m:
            can.append(f'Đoạn {i} có số tiền ngoài bảng ("{m.group(0)}") – công thức chưa có quy tắc cập nhật, kiểm tra bằng tay.')

    if a.kiem:
        print('Soát:', 'khớp hết' if not lech else f'{len(lech)} chỗ lệch: ' + '; '.join(lech))
        sys.exit(1 if lech else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    print(f'  bảng giá: {len(hang)} dòng trong bài' + (f', nguồn cập nhật {g["cap_nhat"]}' if g else ''))
    for x in sua:
        print('  ', x['tim'][:70], '→', x['thay'][:70])
    for c in can:
        print('  cần duyệt:', c)


if __name__ == '__main__':
    main()

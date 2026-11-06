"""Tự lập sua.json cho bài TCB "Giá vàng SJC" (https://techcombank.com/thong-tin/blog/gia-vang-sjc).

  python3 -I tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
  python3 -I tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   -> "Soát: khớp hết"

Nguồn: webgia.com/gia-vang/sjc/ (khối Hồ Chí Minh = bảng niêm yết SJC), giá VND/CHỈ ("13.800.000").
Bài viết giá triệu VND/LƯỢNG, dấu chấm thập phân  ->  số bài = số nguồn x 10 / 1.000.000 = số nguồn / 100.000
(13.800.000 -> 138 ; 14.102.000 -> 141.02 ; 13.092.100 -> 130.921), bỏ số 0 thừa ở cuối, KHÔNG làm tròn.
- Ghép dòng theo TÊN sản phẩm (bỏ khác biệt "1L"="1 lượng", "1KG"="1 kg", "99,99%"="99.99%", bỏ ngoặc, hoa/thường, dấu cách), không theo thứ tự.
- Ô nào số mới lệch quá xa số cũ (ngoài 0,5–2 lần: nghi đổi đơn vị) -> giữ nguyên + cần duyệt.
- Đoạn văn: "X - Y triệu VND/lượng" (mua vào - bán ra) của vàng miếng 1 lượng / vàng nhẫn 99.99% 1,2,5 chỉ; "hơn N triệu VND/lượng".
- Lưới an toàn cuối: số giá nào còn sót mà không bằng số nguồn nào -> cần duyệt "SỐ GIÁ CHƯA CẬP NHẬT …".
Ngày: lệnh `dung` đã đổi sang ngày hôm sau; công thức này không đụng tới ngày.
"""
import argparse, datetime, json, re, sys, unicodedata
from decimal import Decimal

RE_SO_O = re.compile(r'^\d[\d.,]*$')


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def khoa(ten):
    t = nfc(ten).lower()
    t = re.sub(r'[()]', ' ', t)
    t = re.sub(r'(\d)\s*,\s*(\d)', r'\1.\2', t)          # 99,99% -> 99.99%
    t = re.sub(r'(?<![\w.])(\d+(?:\.\d+)?)\s*l\b', r'\1 lượng', t)
    t = re.sub(r'(?<![\w.])(\d+(?:\.\d+)?)\s*kg\b', r'\1 kg', t)
    t = re.sub(r'\s+và\s+', ', ', t)
    t = re.sub(r'\s*,\s*', ', ', t)
    t = re.sub(r'(\d)\s*%', r'\1%', t)
    return re.sub(r'\s+', ' ', t).strip(' ,')


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


def sang_bai(x):
    """'13.092.100' (VND/chỉ) -> '130.921' (triệu VND/lượng); None nếu không phải số."""
    d = re.sub(r'\D', '', x or '')
    if not d:
        return None
    v = (Decimal(int(d)) / Decimal(100000)).normalize()
    return format(v, 'f')


def so_thuc(s):
    try:
        return float(re.sub(r'\.{2,}', '.', s.replace(',', '.')))
    except ValueError:
        return None


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
        g = json.load(open(a.gia, encoding='utf-8')).get('webgia')
    except Exception:
        g = None
    sua, can, lech = [], [], []

    def them(cu, vt, moi, nguon, ly):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        sua.append({'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True,
                    'nguon': nguon, 'ly_do': ly, '_vt': vt})

    # ---- bảng nguồn ----
    nguon = {}                       # khoa(tên) -> {ten, mua, ban (chuỗi số bài), goc}
    if g:
        for d in g['dong']:
            k = khoa(d['ten'])
            nguon[k] = {'ten': d['ten'], 'mua': sang_bai(d.get('mua')), 'ban': sang_bai(d.get('ban')),
                        'goc': f'mua {d.get("mua")} | bán {d.get("ban")} (VND/chỉ)'}
    moi_so = {v for d in nguon.values() for v in (d['mua'], d['ban']) if v}   # mọi số nguồn (đã đổi sang số bài)
    da_thay = set()                  # số đã/được phép xuất hiện trong bài (để lưới an toàn bỏ qua)
    da_ghep = set()
    dong_o = set()                   # vị trí các ô đã xử lý (để lưới an toàn)
    ly_chung = lambda d: f'webgia.com (bảng SJC, Hồ Chí Minh) dòng "{d["ten"]}", cập nhật {g["cap_nhat"]}: {d["goc"]}; x10 chỉ→lượng, /1.000.000'

    def gia_o(d, cot, o_cu, vt, ten, nhan):
        """ô số: trả về chuỗi mới (hoặc None nếu giữ nguyên + ghi cần duyệt)"""
        moi = d[cot]
        if not moi:
            can.append(f'Dòng "{ten}", cột {nhan}: nguồn không có số (bị che/để trống) – giữ nguyên "{o_cu}".')
            return None
        x, y = so_thuc(o_cu), float(moi)
        if x and not (0.5 <= y / x <= 2):
            can.append(f'Dòng "{ten}", cột {nhan}: số nguồn {moi} lệch quá xa số trong bài {o_cu} (nghi đổi đơn vị) – giữ nguyên.')
            return None
        if not re.fullmatch(r'\d+(?:\.\d+)?', o_cu):
            can.append(f'Dòng "{ten}", cột {nhan}: ô cũ "{o_cu}" viết lạ (không phải số bình thường) – đã thay bằng {moi} theo nguồn, đọc lại.')
        return moi

    # 1) Bảng: dòng tên (không phải ô) + 2 ô số theo sau (Mua vào, Bán ra)
    hang = []
    for i, (chu, vt, la_o) in enumerate(dong):
        if la_o:
            continue
        cells = []
        j = i + 1
        while j < len(dong) and dong[j][2]:
            cells.append(dong[j]); j += 1
        if len(cells) == 2 and all(re.search(r'\d', c[0]) and re.fullmatch(r'[\d.,\s]+', c[0]) for c in cells):
            hang.append((chu, cells))
    ghep_bai = {}
    if g:
        for ten, cells in hang:
            d = nguon.get(khoa(ten))
            if not d:
                can.append(f'Dòng "{ten}": nguồn không có dòng cùng tên – giữ nguyên cả 2 ô.')
                continue
            da_ghep.add(khoa(ten))
            ghep_bai[khoa(ten)] = d
            for k, (cot, nhan) in enumerate((('mua', 'Mua vào'), ('ban', 'Bán ra'))):
                o_cu, vt = cells[k][:2]
                dong_o.add(vt)
                moi = gia_o(d, cot, o_cu, vt, ten, nhan)
                if moi:
                    da_thay.add(moi)
                    them(o_cu, vt, moi, g['url'], f'{nhan} ← ' + ly_chung(d))
        for k, d in nguon.items():
            if k not in da_ghep:
                can.append(f'Nguồn có dòng "{d["ten"]}" mà bài không có – không tự thêm dòng.')
        try:
            ngay = datetime.datetime.strptime(g['cap_nhat'].split()[-1], '%d/%m/%Y').date()
            hom_nay = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).date()
            if (hom_nay - ngay).days > 2:
                can.append(f'Nguồn webgia.com cập nhật lần cuối {g["cap_nhat"]} (đã {(hom_nay - ngay).days} ngày) – xem lại giá.')
        except Exception:
            pass
    else:
        can.append('Không đọc được nguồn webgia.com – giữ nguyên TOÀN BỘ giá trong bài (ngày trong bài vẫn đã đổi sang ngày hôm sau, '
                   'nên giá và ngày đang lệch nhau – không đăng khi chưa xử lý).')

    # 2) Đoạn văn
    mau_khoang = re.compile(r'(\d+(?:\.\d+)?) - (\d+(?:\.\d+)?)( triệu VND/lượng)')
    mau_hon = re.compile(r'(hơn )(\d+)( triệu VND/lượng)')
    bang_ten = {khoa(t) for t, _ in hang}
    for chu, vt, la_o in dong:
        if la_o or chu in {t for t, _ in hang}:
            continue
        # 2a) "X - Y triệu VND/lượng" = mua vào - bán ra
        truoc = 0
        for m in mau_khoang.finditer(chu):
            ngu = chu[truoc:m.start()].lower(); truoc = m.end()
            if 'vàng miếng' in ngu and 'sjc' in ngu and '1 lượng' in ngu:
                key = khoa('Vàng SJC 1 lượng, 10 lượng, 1 kg')
            elif 'vàng nhẫn' in ngu and 'sjc' in ngu and '99.99' in ngu and '1 chỉ' in ngu and '5 chỉ' in ngu:
                key = khoa('Vàng nhẫn SJC 99.99% 1 chỉ, 2 chỉ, 5 chỉ')
            else:
                can.append(f'Đoạn có "{m.group(0)}" – không nhận ra là sản phẩm nào, giữ nguyên.')
                continue
            d = ghep_bai.get(key) or (nguon.get(key) if g else None)
            if not d:
                can.append(f'Đoạn có "{m.group(0)}" ({key}): nguồn không có dòng này – giữ nguyên.')
                continue
            if not (d['mua'] and d['ban']):
                can.append(f'Đoạn có "{m.group(0)}": nguồn thiếu số – giữ nguyên.')
                continue
            moi = f'{d["mua"]} - {d["ban"]}{m.group(3)}'
            da_thay.update({d['mua'], d['ban'], m.group(1), m.group(2)})   # số cũ đã được thay -> lưới an toàn bỏ qua
            them(m.group(0), vt + m.start(), moi, g['url'], 'Mua vào - bán ra theo ' + ly_chung(d))
        # 2b) "hơn N triệu VND/lượng" = mốc làm tròn xuống chục của giá bán vàng miếng 1 lượng
        for m in mau_hon.finditer(chu):
            d = nguon.get(khoa('Vàng SJC 1 lượng, 10 lượng, 1 kg')) if g else None
            if not d or not d['ban']:
                can.append(f'Đoạn có "{m.group(0)}": không có giá bán vàng miếng SJC 1 lượng từ nguồn – giữ nguyên.')
                continue
            n = int(float(d['ban']) // 10 * 10)
            da_thay.add(m.group(2)); da_thay.add(str(n))
            if str(n) != m.group(2):
                them(m.group(0), vt + m.start(), f'{m.group(1)}{n}{m.group(3)}', g['url'],
                     f'mốc "hơn" = giá bán vàng miếng 1 lượng {d["ban"]} làm tròn xuống chục (' + ly_chung(d) + ')')
                can.append(f'Đoạn "{m.group(0)}": mốc "hơn" tính ra từ giá bán {d["ban"]} → "{n}" (không có sẵn trên nguồn) – đọc lại câu.')

    # 3) Lưới an toàn: số giá còn sót
    sot = []
    for chu, vt, la_o in dong:
        if la_o:
            if vt in dong_o or not re.fullmatch(r'\d+(?:\.\d+)?|\d[\d.]*', chu):
                continue
            if so_thuc(chu) and so_thuc(chu) >= 1 and chu not in moi_so:
                sot.append(f'ô "{chu}"')
            continue
        for m in re.finditer(r'(\d+(?:\.\d+)?)(?:\s*-\s*(\d+(?:\.\d+)?))?\s*triệu\b', chu):
            for s in m.groups():
                if s and float(s) >= 20 and s not in moi_so and s not in da_thay:
                    sot.append(f'"{s}" trong "{chu[max(0, m.start() - 40):m.end() + 12].strip()}"')
    # số giá trong ô bảng mà nguồn đã thay xong thì bỏ (so khớp theo số mới)
    moi_thay = {x['thay'] for x in sua}
    sot = [s for s in sot if not any(f'"{t}"' in s.split(' trong ')[0] for t in moi_thay)]
    if sot:
        can.append('SỐ GIÁ CHƯA CẬP NHẬT (công thức không có quy tắc/nguồn để tính lại, giữ nguyên): ' + '; '.join(sot))

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

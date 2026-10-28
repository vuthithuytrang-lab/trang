"""Tự lập sua.json cho bài TCB "Giá gas hôm nay" (không cần Claude, không cần mạng).

  python3 -I tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
  python3 -I tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   → "khớp hết"

  --xem  kết quả `cap_nhat.py xem ... bai1`   --gia  gia.json (lay_gia.py, đ/bình đúng số nguồn)
  --goc  bài gốc tải về (để trả lại ngày "dữ liệu cập nhật gần nhất ngày …" khi nguồn bảng 1.1 lỗi)

Bảng nhận ra theo dòng tiêu đề (cột có "…kg"), dòng nhận ra theo TÊN (thương hiệu + địa phương), không theo vị trí:
- bảng không có cột "Thương hiệu" (1.1 theo khu vực) và dòng Petrolimex → pgas.com.vn, cùng tên tỉnh/thành, cùng loại bình
- dòng Saigon Petro → saigonpetro.com.vn (một giá chung, không theo tỉnh)
- dòng PV GAS → pvgaslpg.com.vn, cùng tên tỉnh/thành
Ô "—" giữ nguyên. Số viết như số cũ (dấu phẩy ngăn nghìn: 598,752).
Câu "... điều chỉnh đầu tháng M": M = tháng hiệu lực ghi trên cả 3 nguồn (phải đọc được cả 3 và trùng nhau), không thì giữ + cần duyệt.
"""
import argparse, html, json, re, sys, unicodedata

NGUON_TEN = {'pgas': 'pgas.com.vn (Gas Petrolimex)', 'saigon': 'saigonpetro.com.vn (Saigon Petro)',
             'pvgas': 'pvgaslpg.com.vn (PV GAS LPG)'}
THUONG_HIEU = {'petrolimex': 'pgas', 'saigon petro': 'saigon', 'pv gas': 'pvgas', 'pvgas': 'pvgas'}
THUONG_HIEU_BIET = ['Petrolimex', 'Saigon Petro', 'Pacific Petro', 'PV GAS']
RE_THANG = re.compile(r'(điều chỉnh (?:đầu |giữa |cuối )?tháng )(\d{1,2})(?![\d/])')
RE_NGAY_DL = re.compile(r'(dữ liệu cập nhật gần nhất ngày )(\d{1,2}/\d{1,2}/\d{4})')
RE_GIA = re.compile(r'(?<![\d.,])\d{1,3}(?:[.,]\d{3})+(?![\d.,]*\d)')


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
        c = nfc(t[2:] if la_o else t)
        dong.append((c, len(van), la_o))
        van += c + '\n'
    return dong, van


def lan_thu(van, tim, vt):
    n, i = 0, van.find(tim)
    while i != -1 and i <= vt:
        n += 1
        i = van.find(tim, i + 1)
    return n


def cac_bang(dong):
    """→ danh sách bảng; bảng = danh sách dòng; dòng = danh sách (chữ ô, vị trí); kèm chỉ số các dòng xem thuộc bảng"""
    hang, i = [], 0
    while i < len(dong):
        c, vt, la_o = dong[i]
        if la_o:
            i += 1
            continue
        o, k = [], 0
        for p in c.split(' | '):
            o.append((p.strip(), vt + c.find(p, k)))
            k = c.find(p, k) + len(p)
        j = i + 1
        while j < len(dong) and dong[j][2]:
            o.append((dong[j][0], dong[j][1]))
            j += 1
        hang.append((i, j, o))
        i = j
    bang, cur, het = [], [], -1
    for i, j, o in hang:
        if len(o) >= 2 and (cur and i == het):
            cur.append(o)
        else:
            if len(cur) >= 2:
                bang.append(cur)
            cur = [o] if len(o) >= 2 else []
        het = j
    if len(cur) >= 2:
        bang.append(cur)
    return bang


def ten_noi(s):
    s = re.sub(r'^(TP\.?|Thành phố)\s*', '', nfc(s), flags=re.I)
    return s.lower()


def viet(v, cu):
    s = f'{v:,}'
    return s.replace(',', '.') if re.search(r'\d\.\d{3}', cu) else s


def la_so(s):
    return bool(re.fullmatch(r'\d{1,3}(?:[.,]\d{3})+', s.strip()))


def ngay_goc(path):
    goc = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', open(path, encoding='utf-8').read())))
    m = RE_NGAY_DL.search(unicodedata.normalize('NFC', goc))
    return m.group(2) if m else None


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
    vt_bang = set()

    def them(cu, vt, moi, nguon, ly, tinh=False):
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        x = {'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True, 'nguon': nguon, 'ly_do': ly, '_vt': vt}
        if tinh:
            x['tinh_toan'] = True
        sua.append(x)

    # 1) Các bảng giá
    doi_gia, co_dong = 0, set()
    for b in cac_bang(dong):
        dau = [nfc(c).lower() for c, _ in b[0]]
        cot = {i: int(m.group(1)) for i, c in enumerate(dau) for m in [re.search(r'(\d+)\s*kg', c)] if m}
        if not cot:
            continue
        i_th = next((i for i, c in enumerate(dau) if 'thương hiệu' in c), None)
        i_noi = next((i for i, c in enumerate(dau) if 'địa phương' in c or 'tham khảo' in c), None)
        if i_noi is None:
            i_noi = next((i for i, c in enumerate(dau) if 'khu vực' in c), None)
        ten_bang = 'Bảng giá theo thương hiệu' if i_th is not None else 'Bảng giá theo khu vực'
        for o in b[1:]:
            for c, vt in o:
                vt_bang.add(vt)
            if len(o) != len(dau):
                if any(la_so(c) for c, _ in o):
                    can.append(f'{ten_bang}: dòng "{" | ".join(c for c, _ in o)}" có số ô khác tiêu đề – không nhận ra, giữ nguyên.')
                continue
            th = o[i_th][0] if i_th is not None else None
            noi = o[i_noi][0] if i_noi is not None else ''
            if th is not None:
                co_dong.add(th.lower())
            ma = THUONG_HIEU.get(th.lower()) if th is not None else 'pgas'
            nhan = f'{ten_bang}, dòng {th + " – " if th else ""}{noi}'
            if ma is None:
                if any(la_so(c) for c, _ in o):
                    can.append(f'{nhan}: chưa có nguồn cho thương hiệu này – giữ nguyên giá.')
                continue
            g = gia.get(ma)
            if not g:
                if any(la_so(c) for c, _ in o):
                    can.append(f'{nhan} ({", ".join(c for c, _ in o if la_so(c))}): không đọc được nguồn '
                               f'{NGUON_TEN[ma]} – giữ nguyên giá cũ.')
                continue
            if ma == 'saigon':
                dl, goc_txt, tieu = g['gia'], g['chu_goc'], f'giá bán lẻ gas từ {g["ngay"]}'
            else:
                x = g['tinh'].get(ten_noi(noi))
                if not x:
                    can.append(f'{nhan}: nguồn {NGUON_TEN[ma]} không có tỉnh/thành "{noi}" – giữ nguyên giá.')
                    continue
                dl = x['gia']
                goc_txt = {k: x['chu_goc'] for k in dl}
                tieu = f'bảng "{g["tieu_de"]}"' + (f', hiệu lực {x["hieu_luc"]}' if x.get('hieu_luc') else '')
            for i, kg in cot.items():
                c, vt = o[i]
                v = dl.get(str(kg)) or dl.get(kg)
                if not la_so(c):
                    if v and c not in ('—', '-', '–'):
                        can.append(f'{nhan}, bình {kg}kg: ô ghi "{c}" (không phải số) – giữ nguyên.')
                    continue
                if not v:
                    can.append(f'{nhan}, bình {kg}kg ({c}): nguồn {NGUON_TEN[ma]} không có giá bình {kg}kg – giữ nguyên.')
                    continue
                moi = viet(v, c)
                if moi != c:
                    doi_gia += 1
                them(c, vt, moi, g['nguon'],
                     f'{NGUON_TEN[ma]}, {tieu}: "{goc_txt[str(kg)] if str(kg) in goc_txt else goc_txt.get(kg)}" → bình {kg}kg {v:,} đ')

    # 2) "... điều chỉnh đầu tháng M": theo tháng hiệu lực của các nguồn đọc được
    thang = {ma: tuple(gia[ma]['thang']) for ma in NGUON_TEN if gia.get(ma)}
    for c, vt, la_o in dong:
        if la_o:
            continue
        for m in RE_THANG.finditer(c):
            if len(thang) < len(NGUON_TEN):
                can.append(f'Câu "{m.group(0)}": có nguồn không đọc được (giá của nguồn đó giữ số cũ) – giữ nguyên tháng, nhờ xem lại.')
            elif len(set(thang.values())) > 1:
                can.append(f'Câu "{m.group(0)}": các nguồn ghi tháng khác nhau ('
                           + ', '.join(f'{NGUON_TEN[k]} tháng {t[0]}/{t[1]}' for k, t in thang.items()) + ') – giữ nguyên, nhờ xem lại.')
            else:
                t = next(iter(thang.values()))
                ly = '; '.join(f'{NGUON_TEN[k]}: "{gia[k]["tieu_de"] if k != "saigon" else "Ngày " + gia[k]["ngay"]}"' for k in thang)
                them(m.group(0), vt + m.start(), m.group(1) + str(t[0]), ', '.join(gia[k]['nguon'] for k in thang),
                     f'tháng hiệu lực của bảng giá nguồn = tháng {t[0]}/{t[1]} ({ly})')

    # 3) "dữ liệu cập nhật gần nhất ngày …": nguồn bảng khu vực (pgas) lỗi → trả lại ngày gốc, không ghi ngày mới
    if not gia.get('pgas') and a.goc:
        mg = ngay_goc(a.goc)
        for c, vt, la_o in dong:
            m = RE_NGAY_DL.search(c)
            if m and mg:
                them(m.group(0), vt + m.start(), m.group(1) + mg, '', 'bảng giá theo khu vực giữ số cũ (không đọc được pgas.com.vn) nên giữ ngày gốc')
                can.append(f'Câu "dữ liệu cập nhật gần nhất ngày …": không đọc được pgas.com.vn – giữ ngày gốc {mg}.')

    # 4) Những chỗ công thức chưa lo được → báo để người đọc lại
    if doi_gia and any('tiếp tục duy trì mặt bằng' in c for c, _, _ in dong):
        can.append(f'Có {doi_gia} giá đổi so với bài – câu "tiếp tục duy trì mặt bằng sau đợt điều chỉnh…" giữ nguyên chữ, nhờ đọc lại xem còn đúng không.')
    for c, vt, la_o in dong:
        if la_o or vt in vt_bang or RE_NGAY_DL.search(c):
            continue
        so_gia = [s for s in RE_GIA.findall(c) if int(re.sub(r'\D', '', s)) >= 10000]
        if so_gia:
            can.append(f'Đoạn "{c[:60]}…" có số {", ".join(so_gia)} – công thức chưa có quy tắc cập nhật, giữ nguyên, nhờ kiểm tra.')
    toan = ' '.join(c for c, _, _ in dong)
    for t in THUONG_HIEU_BIET:
        if t in toan and t.lower() not in co_dong and t.lower() not in THUONG_HIEU:
            can.append(f'Bài có nhắc thương hiệu {t} nhưng không có dòng giá {t} và không có nguồn {t} – không có gì để cập nhật, chỉ báo lại.')

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

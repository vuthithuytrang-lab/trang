"""Tự lập sua.json cho bài "Giá ca cao hôm nay" của Techcombank.

Đọc:
  --xem    kết quả `cap_nhat.py xem ... bai1` (lưu ra file)
  --bgns   trang https://banggianongsan.com/bang-gia-cacao-hom-nay/ đã tải (HTML) -> bảng giá trong nước
  --ice    kết quả lay_gia_ice.py -> 2 bảng New York (CC, USD/tấn) + London (CA, GBP/tấn)
Ghi --ra (sua.json) và --gia (gia.json: số liệu thô đã dùng). --kiem: soát lại sau khi sửa.
Quy tắc đã chốt — xem README.md cùng thư mục.
"""
import argparse, datetime, html, json, re, sys, unicodedata

BGNS = 'https://banggianongsan.com/bang-gia-cacao-hom-nay/'
MA_THANG = {1: 'F', 2: 'G', 3: 'H', 4: 'J', 5: 'K', 6: 'M', 7: 'N', 8: 'Q', 9: 'U', 10: 'V', 11: 'X', 12: 'Z'}
THANG_EN = {m: i for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}
# tên dòng trong bài -> tên dòng trên banggianongsan
TEN = {'Ca cao tươi': 'Cacao tươi', 'Hạt ca cao xô': 'Hạt cacao xô', 'Hạt ca cao lên men loại I': 'Hạt cacao lên men loại I',
       'Ca cao lên men loại II': 'Cacao lên men loại II', 'Ca cao lên men loại III': 'Cacao lên men loại III',
       'Bột ca cao nguyên chất': 'Bột cacao nguyên chất'}


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def doc_xem(path):
    van, rows, cur = '', [], None
    for line in open(path, encoding='utf-8'):
        m = re.match(r'\s*\d+\.\s?(.*)$', line.rstrip('\n'))
        if not m:
            continue
        t = m.group(1)
        la_o = t.startswith('| ')
        chu = nfc(t[2:] if la_o else t)
        vt = len(van)
        van += chu + '\n'
        if la_o and cur is not None:
            cur.append((chu, vt))
        else:
            cur = [(chu, vt)]
            rows.append(cur)
    return [r for r in rows if len(r) >= 3], van


def lan_thu(van, tim, vt):
    n, i = 0, van.find(tim)
    while i != -1 and i <= vt:
        n += 1
        i = van.find(tim, i + 1)
    return n


def so(s):
    return int(s.replace('.', '').replace(',', ''))


def doc_bgns(path):
    s = open(path, encoding='utf-8', errors='replace').read()
    m = re.search(r'Bảng giá Cacao mới nhất\s*(?:-|&#8211;)\s*(\d\d/\d\d/\d{4})', s)
    md = re.search(r'"dateModified":"([^"]+)"', s)
    ra = {}
    for ten, cu, moi, doi in re.findall(r'<td>([^<]+?) \(đ/kg\)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>(.*?)</td>', s, re.S):
        ten = nfc(html.unescape(ten))
        if ten in ra:
            continue
        p = [so(x) for x in re.findall(r'[\d.]+\d', html.unescape(moi))]
        q = [so(x) for x in re.findall(r'[\d.]+\d', html.unescape(cu))]
        ra[ten] = {'gia_cu': q, 'gia_moi': p, 'chenh_lech': nfc(re.sub(r'<[^>]+>', '', html.unescape(doi)))}
    return ra, (m.group(1) if m else '?'), (md.group(1) if md else '?')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--bgns', required=True)
    ap.add_argument('--ice', required=True)
    ap.add_argument('--ra')
    ap.add_argument('--gia')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    rows, van = doc_xem(a.xem)
    sua, can, loi, lech = [], [], [], []

    def them(o, moi, nguon, ly, tinh=False):
        cu, vt = o
        if cu == moi:
            return
        lech.append(f'"{cu}" (cần là "{moi}")')
        x = {'tim': cu, 'thay': moi, 'lan': lan_thu(van, cu, vt), 'giu_nguyen_so': True, 'nguon': nguon, 'ly_do': ly, '_vt': vt}
        if tinh:
            x['tinh_toan'] = True
        sua.append(x)

    # 1) Bảng trong nước: "Giá hiện tại" <- giá hôm nay của nguồn; "Giá mới dự kiến" giữ nguyên (nguồn không có dự báo);
    #    "Thay đổi" <- mức chênh lệch so với hôm trước của nguồn ("Không đổi" khi bằng 0)
    bg, bg_ngay, bg_sua = doc_bgns(a.bgns)
    if not bg:
        loi.append('Không đọc được bảng giá trong nước trên banggianongsan.com.')
    thay_tn = 0
    for r in rows:
        ten = r[0][0]
        if ten in TEN and len(r) >= 4:
            n = bg.get(TEN[ten])
            if not n:
                loi.append(f'Nguồn không có dòng "{TEN[ten]}"'); continue
            thay_tn += 1
            g = n['gia_moi']
            gia_txt = ' - '.join(f'{x:,}' for x in g)
            ly = f'{TEN[ten]}: giá mới {gia_txt.replace(",", ".")} đ/kg, chênh lệch "{n["chenh_lech"]}" (banggianongsan.com, bảng ngày {bg_ngay}, trang sửa lúc {bg_sua})'
            them(r[1], gia_txt, BGNS, ly)
            cl = n['chenh_lech'].replace('➖', '').strip()
            if cl == 'Không đổi':
                them(r[3], 'Không đổi', BGNS, ly)
            else:
                nums = re.findall(r'[+-]?\s*[\d.]*\d', cl)
                if nums and ('▼' in cl or '▲' in cl or re.search(r'[+-]', cl)):
                    vals = [(-1 if ('▼' in cl and not x.strip().startswith('+')) else 1) * abs(int(x.replace(' ', '').replace('.', ''))) for x in nums]
                    them(r[3], ' - '.join(f'{v:+,}' for v in vals) + ' VND/kg', BGNS, ly)
                else:
                    can.append(f'{ten}: không hiểu cột chênh lệch của nguồn "{n["chenh_lech"]}" – giữ nguyên ô Thay đổi.')
    if bg and not thay_tn:
        loi.append('Không thấy bảng giá trong nước trong bài.')
    if thay_tn:
        can.append('Bảng giá trong nước: cột "Giá mới dự kiến" GIỮ NGUYÊN (nguồn không có giá dự kiến). '
                   'Lưu ý: số cũ của bài khớp đúng bảng giacaphehomnay.vn ngày 09/10/2026 – "Giá hiện tại" cũ = giá hôm trước, '
                   '"Giá mới dự kiến" cũ = giá hôm đó của nguồn, "Thay đổi" = mức đổi trong ngày. Nếu muốn theo cách đó thì '
                   '"Giá mới dự kiến" cũng nên lấy giá mới của nguồn – cần duyệt.')
        can.append('Bảng giá trong nước: cột "Thay đổi" ghi theo mức chênh lệch so với hôm trước của nguồn (hôm nay "Không đổi"), '
                   'không phải hiệu "Giá mới dự kiến" – "Giá hiện tại" – cần duyệt cách ghi.')

    # 2) Bảng thế giới (ICE): giá khớp gần nhất; thay đổi = giá − giá chốt phiên trước (tính từ lịch sử ngày của ICE)
    ice = json.load(open(a.ice, encoding='utf-8'))
    for san, tien_to, ten_san in [('newyork', 'CC', 'New York (ICE US, USD/tấn)'), ('london', 'CA', 'London (ICE Europe, GBP/tấn)')]:
        s = ice['san'].get(san) or {}
        moi = s.get('ky_han') or []
        cu = [r for r in rows if re.fullmatch(tien_to + r'[FGHJKMNQUVXZ]\d\d', r[0][0])]
        if not moi or not cu:
            loi.append(f'Thiếu bảng {san}: bài có {len(cu)} dòng, nguồn có {len(moi)} dòng.'); continue
        if len(moi) < len(cu):
            can.append(f'Bảng ca cao {ten_san}: ICE chỉ niêm yết {len(moi)} kỳ hạn, bài có {len(cu)} dòng – '
                       f'{len(cu) - len(moi)} dòng cuối ({", ".join(r[0][0] for r in cu[len(moi):])}) giữ nguyên số cũ.')
        for r, m in zip(cu, moi):
            thang, nam = THANG_EN[m['ky_han'][:3]], 2000 + int(m['ky_han'][3:])
            if m['gia'] is not None:
                gia, doi = m['gia'], m['thay_doi']
                ly = (f'{ten_san} kỳ hạn {thang}/{nam}: {gia:,.0f} lúc {m["luc"]}; giá chốt phiên trước '
                      f'({m["chot_truoc_ngay"]}) {m["chot_truoc"]:,.0f} → thay đổi {doi:+,.0f}')
                tinh = True
            else:
                h = m['lich_su_cuoi']
                gia, doi = h[-1][1], h[-1][1] - h[-2][1]
                ly = (f'{ten_san} kỳ hạn {thang}/{nam}: hôm nay chưa có giao dịch – lấy giá chốt phiên {h[-1][0][4:10]} '
                      f'{gia:,.0f}, so với phiên trước ({h[-2][0][4:10]}) {h[-2][1]:,.0f} → {doi:+,.0f}')
                tinh = True
                can.append(f'Bảng {ten_san} dòng {tien_to}{MA_THANG[thang]}{nam % 100:02d}: hôm nay chưa có giao dịch – ghi giá chốt phiên 14/10 và mức đổi so với 13/10 (khác thời điểm các dòng trên).')
            ly += f' – nguồn ICE {s["trang"]}; mã hợp đồng theo quy ước tháng của sàn ICE'
            them(r[0], f'{tien_to}{MA_THANG[thang]}{nam % 100:02d}', s['trang'], ly)
            them(r[1], f'{thang}/{nam}', s['trang'], ly)
            them(r[2], f'{round(gia):,}', s['trang'], ly, tinh)
            them(r[3], '0' if round(doi) == 0 else f'{round(doi):+,}', s['trang'], ly, tinh)
    vn = (datetime.datetime.strptime(ice['lay_luc_utc'], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=7)).strftime('%H:%M %d/%m/%Y')
    can.append(f'Giá thế giới lấy lúc {vn} (giờ VN) khi hai sàn đang giao dịch: là giá khớp gần nhất trong phiên 15/10, '
               'chưa phải giá chốt phiên; cột "Thay đổi" tính = giá khớp − giá chốt phiên 14/10 (ICE không ghi sẵn số tuyệt đối).')
    if 'chất lượng cà phê' in van:
        can.append('Lỗi có sẵn trong bài: câu "Lưu ý" dưới bảng ca cao New York ghi "chất lượng cà phê" (nhầm sản phẩm) – không sửa chữ, chỉ báo lại.')

    if a.kiem:
        for l in loi:
            print('LỖI:', l)
        print('Soát 3 bảng:', 'khớp hết' if not lech else f'{len(lech)} ô lệch: ' + '; '.join(lech))
        sys.exit(1 if lech or loi else 0)
    sua.sort(key=lambda x: -x['_vt'])
    for x in sua:
        del x['_vt']
    json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if a.gia:
        json.dump({'trong_nuoc': {'nguon': BGNS, 'bang_ngay': bg_ngay, 'trang_sua_luc': bg_sua, 'gia': bg},
                   'the_gioi': ice}, open(a.gia, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} ô cần đổi, {len(can)} mục cần duyệt → {a.ra}')
    for c in can:
        print('  cần duyệt:', c)
    for l in loi:
        print('LỖI:', l)
    sys.exit(1 if loi else 0)


if __name__ == '__main__':
    main()

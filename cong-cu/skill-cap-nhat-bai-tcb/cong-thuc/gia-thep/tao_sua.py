"""Tự lập sua.json cho bài TCB "Giá thép hôm nay: Bảng giá cập nhật và các yếu tố ảnh hưởng đến thị trường".
Không mạng, không AI — chỉ đọc chữ bài (xem) + gia.json (lay_gia.py) + bài gốc.

  --xem  kết quả `cap_nhat.py xem … bai1`      --gia  gia.json (lay_gia.py)
  --goc  cap-nhat/tam/bai1.html (bài gốc trước `dung`, để lấy lại ngày tiêu đề mục khi nguồn lỗi)
  --ra   sua.json                               --kiem soát lại sau khi sửa ("khớp hết")

Bảng 1 (thế giới, Barchart): dòng "V7V26 | 10/2026 | 487.00 | 0.00" — khớp theo MÃ hợp đồng, không theo vị trí.
  Giá 2 số lẻ (487.00); thay đổi 2 số lẻ, dương có "+", âm có "-", không đổi (unch) = "0.00".
  Hợp đồng đầu bảng đã hết hạn (qua ngày làm việc cuối của tháng đáo hạn) → chuyển kỳ: dòng thứ i lấy hợp đồng còn
  hạn thứ i trên Barchart (đổi cả mã + tháng + giá + thay đổi), ghi cần duyệt.
Bảng 2 (trong nước, steelonline): dòng thương hiệu → "Khoảng giá (VND/kg)" và "(VND/cây)" viết "14,210 - 14,920";
  khớp theo tên hãng (bỏ dấu, bỏ chữ "Thép" đầu tên).
Nguồn lỗi → giữ nguyên số + cần duyệt, và trả ngày ở tiêu đề mục đó ("… hôm nay dd/mm/yyyy") về ngày của bài gốc
  để bài không ghi ngày mới cho giá cũ.
"""
import argparse, datetime, html, json, re, sys, unicodedata

VN = datetime.timezone(datetime.timedelta(hours=7))
CHU_THANG = 'FGHJKMNQUVXZ'
RE_MA = re.compile(r'^V7([FGHJKMNQUVXZ])(\d\d)$')
RE_KHOANG = re.compile(r'^\d{1,3}(?:,\d{3})+ - \d{1,3}(?:,\d{3})+$')
RE_SO = re.compile(r'^[+-]?\d+\.\d\d$')


def nfc(s):
    return unicodedata.normalize('NFC', s).strip()


def khong_dau(s):
    s = unicodedata.normalize('NFD', s.lower().replace('đ', 'd'))
    s = re.sub(r'\s+', ' ', ''.join(c for c in s if unicodedata.category(c) != 'Mn')).strip()
    return re.sub(r'^thep ', '', s)


def doc_xem(path):
    """-> danh sách ô theo thứ tự (chữ, vị trí trong văn bản ghép bằng dấu cách), văn bản ghép."""
    o, van = [], ''
    for line in open(path, encoding='utf-8'):
        m = re.match(r'\s*\d+\.\s?(.*)$', line.rstrip('\n'))
        if not m:
            continue
        for p in re.split(r'\s*\|\s*', m.group(1)):
            p = nfc(p)
            if p:
                o.append((p, len(van)))
                van += p + ' '
    return o, van


def lan_thu(van, tim, vt):
    n, i = 0, van.find(tim)
    while i != -1 and i <= vt:
        n += 1
        i = van.find(tim, i + 1)
    return n


def het_han(ma, hom_nay):
    m = RE_MA.match(ma)
    t, n = CHU_THANG.index(m.group(1)) + 1, 2000 + int(m.group(2))
    d = datetime.date(n + (t == 12), t % 12 + 1, 1) - datetime.timedelta(days=1)
    while d.weekday() >= 5:
        d -= datetime.timedelta(days=1)
    return d < hom_nay


def ngay_goc(path):
    g = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', open(path, encoding='utf-8').read())))
    out = {}
    for k in ('thế giới', 'trong nước'):
        m = re.search(r'Bảng giá thép ' + k + r' hôm nay (\d{1,2}/\d{1,2}/\d{4})', unicodedata.normalize('NFC', g))
        out[k] = m.group(1) if m else None
    return out


def tinh(o, van, gia, goc):
    hom_nay = datetime.datetime.now(VN).date()
    sua, can = [], []

    def them(cu, vt, moi, nguon, ly, ngu=None):
        if cu == moi:
            return
        x = {'tim': cu, 'thay': moi, 'giu_nguyen_so': True, 'nguon': nguon, 'ly_do': ly, '_vt': vt}
        if ngu and ngu != cu and van.count(ngu) == 1:
            x['ngu_canh'] = ngu
        else:
            x['lan'] = lan_thu(van, cu, vt)
        sua.append(x)

    def tra_ngay(k, ten):
        if not goc or not goc.get(k):
            can.append(f'{ten}: không tìm thấy ngày tiêu đề mục trong bài gốc để giữ lại.')
            return
        for p, vt in o:
            m = re.match(r'(\d+\. )?Bảng giá thép ' + k + r' hôm nay (\d{1,2}/\d{1,2}/\d{4})$', p)
            if m:
                them(m.group(2), vt + m.start(2), goc[k], '',
                     f'nguồn {ten.lower()} lỗi → giữ ngày của bài gốc ở tiêu đề mục, không ghi ngày mới cho giá cũ',
                     ngu=p)

    # ---- Bảng 1: thép thế giới (Barchart)
    dong = []
    for i in range(len(o) - 3):
        if RE_MA.match(o[i][0]) and re.fullmatch(r'\d{1,2}/\d{4}', o[i + 1][0]) \
                and RE_SO.match(o[i + 2][0]) and RE_SO.match(o[i + 3][0]):
            dong.append(o[i:i + 4])
    b = gia.get('barchart')
    if not dong:
        can.append('Bảng giá thép thế giới: không nhận ra bảng hợp đồng V7 trong bài – không sửa, nhờ kiểm tra bố cục bài.')
    elif not b:
        can.append('Bảng giá thép thế giới: Barchart không đọc được (trang chặn máy chủ tự động, trả HTTP 202/403) – '
                   'giữ nguyên toàn bộ giá và mức thay đổi cũ, giữ ngày cũ ở tiêu đề mục 1. Nhờ người cập nhật tay.')
        if het_han(dong[0][0][0], hom_nay):
            can.append(f'Bảng giá thép thế giới: hợp đồng {dong[0][0][0]} đã đáo hạn – cần chuyển sang các hợp đồng kỳ sau.')
        tra_ngay('thế giới', 'Bảng giá thép thế giới')
    else:
        hd = {x['ma']: x for x in b['hop_dong']}
        chuyen = het_han(dong[0][0][0], hom_nay)
        if chuyen:
            can.append(f'Bảng giá thép thế giới: hợp đồng {dong[0][0][0]} đã đáo hạn → chuyển kỳ, mỗi dòng lấy hợp đồng còn hạn '
                       f'theo thứ tự trên Barchart (đổi cả mã + tháng đáo hạn). Nhờ duyệt.')
        phien = set()
        for i, d in enumerate(dong):
            x = (b['hop_dong'][i] if i < len(b['hop_dong']) else None) if chuyen else hd.get(d[0][0])
            if not x:
                can.append(f'Bảng giá thép thế giới: Barchart không có số cho dòng {d[0][0]} – giữ nguyên.')
                continue
            phien.add(x['phien'])
            g, td = f'{x["gia"]:.2f}', ('0.00' if x['thay_doi'] == 0 else f'{x["thay_doi"]:+.2f}')
            ly = f'Barchart {x["ma"]}: {x["chu_goc"]}, phiên {x["phien"]}'
            hang = ' '.join(c[0] for c in d)
            if chuyen:
                them(hang, d[0][1], f'{x["ma"]} {x["thang"]} {g} {td}', b['nguon'], ly)
            else:
                them(f'{d[2][0]} {d[3][0]}', d[2][1], f'{g} {td}', b['nguon'], ly, ngu=hang)
        can.append(f'Bảng giá thép thế giới: giá Barchart là giá thanh toán phiên {", ".join(sorted(phien))} (giờ Mỹ), '
                   f'chạy lúc {gia.get("chay_luc", "?")}.')

    # ---- Bảng 2: thép trong nước (steelonline)
    s = gia.get('steelonline')
    hang2 = []
    for j in range(len(o) - 1):                      # 2 ô khoảng giá liền nhau = 1 dòng hãng; tên hãng = ô chữ gần nhất phía trước
        if RE_KHOANG.match(o[j][0]) and RE_KHOANG.match(o[j + 1][0]) and not (j and RE_KHOANG.match(o[j - 1][0])):
            k = j - 1
            while k >= 0 and re.match(r'^(D\d|CB\d)', o[k][0]):
                k -= 1
            if k >= 0 and len(o[k][0]) <= 40:
                hang2.append((o[k][0], o[j], o[j + 1]))
    if not hang2:
        can.append('Bảng giá thép trong nước: không nhận ra bảng thương hiệu trong bài – không sửa, nhờ kiểm tra bố cục bài.')
    elif not s:
        can.append('Bảng giá thép trong nước: steelonline.vn không đọc được – giữ nguyên các khoảng giá cũ, giữ ngày cũ ở '
                   'tiêu đề mục 2. Nhờ người cập nhật tay.')
        tra_ngay('trong nước', 'Bảng giá thép trong nước')
    else:
        nguon2 = {khong_dau(v['ten']): v for v in s['hang'].values()}
        for ten, kg, cay in hang2:
            v = nguon2.get(khong_dau(ten))
            if not v:
                can.append(f'Bảng giá thép trong nước: steelonline ngày {s["ngay"]} không có bảng "{ten}" – giữ nguyên.')
                continue
            moi = f'{v["kg"][0]:,} - {v["kg"][1]:,} {v["cay"][0]:,} - {v["cay"][1]:,}'
            them(f'{kg[0]} {cay[0]}', kg[1], moi, s['nguon'],
                 f'steelonline {v["ten"]} (bảng đầu tiên) ngày {s["ngay"]}: {v["chu_goc"]}')
        con = sorted(set(nguon2) - {khong_dau(t) for t, _, _ in hang2})
        if con:
            can.append('Bảng giá thép trong nước: steelonline có thêm hãng chưa có trong bài: '
                       + ', '.join(nguon2[k]['ten'] for k in con) + ' – không thêm dòng.')
        can.append(f'Bảng giá thép trong nước: dùng bảng steelonline.vn ngày {s["ngay"]} (trang mới nhất có số); khoảng giá = '
                   'thấp nhất – cao nhất mọi ô VNĐ/kg và VNĐ/cây ở tab đầu tiên của mỗi hãng.')
    return sua, can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xem', required=True)
    ap.add_argument('--gia', required=True)
    ap.add_argument('--goc')
    ap.add_argument('--ra')
    ap.add_argument('--kiem', action='store_true')
    a = ap.parse_args()
    o, van = doc_xem(a.xem)
    gia = json.load(open(a.gia, encoding='utf-8'))
    goc = ngay_goc(a.goc) if a.goc else None
    sua, can = tinh(o, van, gia, goc)
    if a.kiem:
        lech = [f'"{x["tim"]}" (cần là "{x["thay"]}")' for x in sua]
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

"""Tự lập sua.json cho bảng "Giá nhôm thế giới" (hợp đồng kỳ hạn nhôm COMEX, mã ALI) trong bài "Giá nhôm hôm nay" (Techcombank).

Nguồn: barchart.com (trang từng hợp đồng, mã ALV26, ALX26…) – lấy bằng lay_gia_barchart.js; bổ sung giá chốt hôm trước từ
Yahoo Finance (query1.finance.yahoo.com/v8/finance/chart/ALIZ26.CMX) cho hợp đồng đang giao dịch dở phiên.
Quy tắc: lấy GIÁ CHỐT PHIÊN gần nhất (ký hiệu "s" trên barchart) cho cả 10 dòng; giá làm tròn tới đơn vị như bài (3,238);
% ghi 2 số lẻ có dấu (+0.18% / -0.02%). Mã trong bài ALIV2026 = mã barchart ALV26.
Cách chạy:
  python3 -I tao_sua_nhom.py --xem cap-nhat/xem.txt --barchart cap-nhat/al.json [--yahoo-dir cap-nhat/yh] --gia cap-nhat/gia.json --ra cap-nhat/sua.json
"""
import argparse, datetime, json, os, re, sys
from decimal import Decimal, ROUND_HALF_UP

THANG = 'FGHJKMNQUVXZ'


def ma_bc(ma_bai):                       # ALIV2026 -> ALV26
    m = re.fullmatch(r'ALI([FGHJKMNQUVXZ])20(\d\d)', ma_bai)
    return f'AL{m.group(1)}{m.group(2)}' if m else None


def ma_bai(ma_bc_):                      # ALV26 -> ALIV2026
    return f'ALI{ma_bc_[2]}20{ma_bc_[3:]}'


def doc_bang(xem):
    L = [re.sub(r'^\s*\d+\.\s?', '', x.rstrip('\n')) for x in open(xem, encoding='utf-8')]
    return [(x, L[i + 1][2:], L[i + 2][2:]) for i, x in enumerate(L)
            if re.fullmatch(r'ALI[FGHJKMNQUVXZ]20\d\d', x) and i + 2 < len(L) and L[i + 1].startswith('| ')]


def yahoo_chot(d, ma):
    """(giá chốt hôm qua, giá chốt hôm kia) theo dữ liệu ngày của Yahoo (bỏ phiên chưa chốt)."""
    p = os.path.join(d, f'ALI{ma[2:]}.json') if d else ''
    if not p or not os.path.exists(p):
        return None
    r = json.load(open(p))['chart']['result'][0]
    ds = [(datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%d/%m'), c)
          for t, c in zip(r['timestamp'], r['indicators']['quote'][0]['close']) if c is not None]
    return ds


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--xem', required=True); a.add_argument('--barchart', required=True)
    a.add_argument('--yahoo-dir'); a.add_argument('--gia'); a.add_argument('--ra'); a.add_argument('--kiem', action='store_true')
    o = a.parse_args()
    bc = {h['ma']: h for h in json.load(open(o.barchart))['hop_dong']}
    rows = doc_bang(o.xem)
    if len(rows) != 10:
        sys.exit(f'LỖI: bài có {len(rows)} dòng hợp đồng (cần 10)')
    sua, can, gia = [], [], {}
    for ten, g_cu, p_cu in rows:
        h = bc.get(ma_bc(ten))
        if not h or not h.get('gia'):
            can.append(f'Hợp đồng {ten}: không đọc được giá trên barchart – giữ nguyên {g_cu} / {p_cu}.'); continue
        tinh = False
        if h['chot']:
            g, pt, luc = Decimal(h['gia'].replace(',', '')), Decimal(h['phan_tram'].rstrip('%')), 'giá chốt phiên ' + h['thoi_diem']
            pt_txt = f'{pt:+.2f}%'
        else:                                          # đang giao dịch dở phiên -> dùng giá chốt phiên trước (= "Previous Close")
            ys = yahoo_chot(o.yahoo_dir, h['ma'])
            g = Decimal(h['gia_truoc'].replace(',', ''))
            truoc = None
            if ys:
                # phiên trước nữa = giá chốt ngay trước phiên có giá bằng Previous Close
                for i in range(len(ys) - 1, 0, -1):
                    if Decimal(str(ys[i][1])) == g:
                        truoc = Decimal(str(ys[i - 1][1])); break
            if truoc is None:
                can.append(f'Hợp đồng {ten}: đang giao dịch, không tìm được giá chốt phiên trước để tính % – giữ nguyên.'); continue
            pt = ((g - truoc) / truoc * 100).quantize(Decimal('0.01'), ROUND_HALF_UP)
            pt_txt, tinh, luc = f'{pt:+.2f}%', True, f'giá chốt phiên trước (Previous Close {h["gia_truoc"]}); % = ({g} − {truoc}) / {truoc} (giá chốt hôm trước nữa theo Yahoo Finance)'
        g_txt = f'{int(g.quantize(Decimal("1"), ROUND_HALF_UP)):,}'
        gia[ten] = {'ma_nguon': h['ma'], 'gia_nguon': str(g), 'phan_tram': pt_txt, 'thoi_diem': luc, 'url': h['url']}
        if (g_cu, p_cu) == (g_txt, pt_txt):
            continue
        e = {'tim': f'{ten} {g_cu} {p_cu}', 'thay': f'{ten} {g_txt} {pt_txt}', 'giu_nguyen_so': True, 'nguon': h['url'],
             'ly_do': f'{h.get("ten", ten)}: {g} USD/tấn ({luc}), thay đổi {pt_txt}; làm tròn tới đơn vị như bài'}
        if tinh:
            e['tinh_toan'] = True
        sua.append(e)
    if o.kiem:
        print('khớp hết' if not sua else '\n'.join(x['tim'] + ' ≠ ' + x['thay'] for x in sua)); sys.exit(1 if sua else 0)
    if o.gia:
        json.dump(gia, open(o.gia, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if o.ra:
        json.dump({'bai1': {'sua': sua, 'can_duyet': can}}, open(o.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ sửa; {len(can)} cần duyệt')
    for x in sua: print(' ', x['tim'], '->', x['thay'])


main()

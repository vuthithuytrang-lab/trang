"""Tự lập sua.json + gia.json cho bài "Giá kim loại thế giới" (Techcombank).

Nguồn: https://www.thitruonghanghoa.com/gia-kim-loai (bảng 10 kim loại, đã quy ra VNĐ, cùng thứ tự + cùng đơn vị với bài).
Cách chạy:
  curl -sS -A "Mozilla/5.0" -o cap-nhat/tthh.html https://www.thitruonghanghoa.com/gia-kim-loai
  python3 -I tao_sua_kim_loai.py --xem cap-nhat/xem.txt --nguon cap-nhat/tthh.html --gia cap-nhat/gia.json --ra cap-nhat/sua.json
  (--kiem: chỉ so bài đã sửa với nguồn, in ô lệch)
"""
import argparse, datetime, html, json, re, sys

URL = 'https://www.thitruonghanghoa.com/gia-kim-loai'
# tên dòng trong bài -> tên trên nguồn
TEN = {'Vàng': 'Vàng', 'Bạc': 'Bạc', 'Đồng': 'Đồng', 'Bạch kim': 'Bạch kim', 'Niken': 'Nickel', 'Chì': 'Chì',
       'Nhôm': 'Nhôm', 'Kẽm': 'Kẽm', 'Quặng sắt 62% Fe': 'Quặng sắt 62% Fe', 'Thiếc': 'Thiếc'}


def doc_nguon(p):
    t = open(p, encoding='utf-8', errors='ignore').read()
    t = re.sub(r'(?s)<script.*?</script>|<style.*?</style>', '', t)
    t = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', t)))
    i = t.find('Bảng giá Kim loại')
    t = t[i:]
    ra = {}
    for m in re.finditer(r'[A-Z]{2} (Vàng|Bạc|Đồng|Bạch kim|Nickel|Chì|Nhôm|Kẽm|Quặng sắt 62% Fe|Thiếc) [A-Z /]+? ([\d.]+) VNĐ / (\w+) ([\d,.]+) \S+ / \w+ arrow_(upward|downward) ([\d.]+)% ([+-][\d,.]+) (\S+ / \w+)', t):
        ten, vnd, dv, usd, huong, pt, doi, dv_goc = m.groups()
        if ten in ra:
            continue
        ra[ten] = {'vnd': vnd, 'don_vi_vnd': 'VNĐ/' + dv, 'gia_goc': usd, 'thay_doi_goc': doi + ' ' + dv_goc.replace(' ', ''),
                   'phan_tram': ('-' if huong == 'downward' else '+') + pt}
    return ra


def doc_bang(xem):
    L = [re.sub(r'^\s*\d+\.\s?', '', x.rstrip('\n')) for x in open(xem, encoding='utf-8')]
    rows = []
    for i, x in enumerate(L):
        if x in TEN and i + 2 < len(L) and L[i + 1].startswith('| ') and L[i + 2].startswith('| '):
            rows.append((x, L[i + 1][2:], L[i + 2][2:]))
    return rows


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--xem', required=True); a.add_argument('--nguon', required=True)
    a.add_argument('--gia'); a.add_argument('--ra'); a.add_argument('--kiem', action='store_true')
    o = a.parse_args()
    ng = doc_nguon(o.nguon)
    rows = doc_bang(o.xem)
    if len(ng) != 10 or len(rows) != 10:
        sys.exit(f'LỖI: nguồn đọc được {len(ng)}/10 kim loại, bài có {len(rows)}/10 dòng')
    luc = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime('%d/%m/%Y %H:%M')
    sua, lech = [], []
    for ten, gia, pt in rows:
        n = ng[TEN[ten]]
        gia_moi = f"{int(n['vnd'].replace('.', '')):,}"
        pt_moi = f"{float(n['phan_tram']):+.2f}"
        if o.kiem:
            if (gia, pt) != (gia_moi, pt_moi):
                lech.append(f'{ten}: bài {gia} {pt} / nguồn {gia_moi} {pt_moi}')
            continue
        if (gia, pt) == (gia_moi, pt_moi):
            continue
        sua.append({'tim': f'{ten} {gia} {pt}', 'thay': f'{ten} {gia_moi} {pt_moi}', 'giu_nguyen_so': True, 'nguon': URL,
                    'ly_do': f"{ten}: {gia_moi} {n['don_vi_vnd']} (giá gốc {n['gia_goc']}, thay đổi {n['phan_tram']}%) – thitruonghanghoa.com, lấy lúc {luc} giờ VN; số VNĐ ghi theo dấu nghìn ',' của bài"})
    if o.kiem:
        print('khớp hết' if not lech else '\n'.join(lech)); sys.exit(1 if lech else 0)
    if o.gia:
        json.dump({'nguon': URL, 'lay_luc': luc + ' (giờ VN)', 'gia': ng}, open(o.gia, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if o.ra:
        json.dump({'bai1': {'sua': sua, 'can_duyet': []}}, open(o.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(sua)} chỗ sửa')


main()

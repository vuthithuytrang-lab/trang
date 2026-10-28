"""Đọc giá Robusta London + Arabica New York (5 hợp đồng hiển thị đầu tiên) từ baolamdong.vn/gia-ca-phe/the-gioi.

  python3 -I lay_gia.py <thư mục làm việc>/cap-nhat/gia.json

Không tự tải mạng: trang nguồn đã được công cụ chung tải về ở bước `cap_nhat.py lay` (cau-hinh.json -> tham_khao[0])
thành cap-nhat/tam/thamkhao1.goc (HTML tĩnh, không cần trình duyệt). File này chỉ đọc file đó.

Ra gia.json:
  {"robusta": {"hop_dong": [{"ky_han": "11/2026", "gia": "3.240", "thay_doi": "0", "chieu": "flat", "hom_truoc": "3.240"}, ...],
               "cap_nhat": "22:37 ngày 28/10/2026", "nguon": url},
   "arabica": {...}, "trang_thai": "đang giao dịch" | ... }
Số giữ đúng chữ của nguồn (dấu chấm nghìn, dấu phẩy thập phân kiểu Việt Nam); tao_sua.py tự đổi sang cách viết của bài.
Sàn nào không đọc được -> null (in "<sàn> KHÔNG ĐỌC ĐƯỢC").
"""
import html, json, os, re, sys

URL = 'https://baolamdong.vn/gia-ca-phe/the-gioi'
SO_HOP_DONG = 5          # Trang chốt: luôn lấy 5 hợp đồng hiển thị đầu tiên (hợp đồng cuộn theo nguồn)


def chu(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def doc_bang(h, tieu_de):
    """Bảng ngay sau <h3> có chữ `tieu_de` -> danh sách hợp đồng theo đúng thứ tự trên trang."""
    m = re.search(r'<h3[^>]*>[^<]*' + re.escape(tieu_de) + r'[^<]*</h3>(.*?)</table>', h, re.S)
    if not m:
        return None
    tb = m.group(1)
    cap = re.search(r'<caption>(.*?)</caption>', tb, re.S)
    cap_nhat = re.search(r'Cập nhật\s*(\d{1,2}:\d{2}\s*ngày\s*\d{1,2}/\d{1,2}/\d{4})', chu(cap.group(1))) if cap else None
    body = re.search(r'<tbody>(.*?)</tbody>', tb, re.S)
    hd = []
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', body.group(1) if body else '', re.S):
        th = re.search(r'<th[^>]*>(.*?)</th>', tr, re.S)
        ky = re.match(r'\d{2}/\d{4}', chu(th.group(1))) if th else None
        gia = re.search(r'class="[^"]*gcf-price[ "][^>]*>([^<]+)<', tr)
        dl = re.search(r'class="gcf-delta (\w+)"[^>]*>(.*?)</span>\s*</span>', tr, re.S)
        ht = re.search(r'data-label="Hôm trước"[^>]*>([^<]+)<', tr)
        if not (ky and gia and dl):
            continue
        chieu = dl.group(1)                                    # up / down / flat
        so = re.search(r'\d[\d.,]*', chu(dl.group(2)))
        hd.append({'ky_han': ky.group(0), 'gia': gia.group(1).strip(),
                   'thay_doi': so.group(0) if so else '0', 'chieu': chieu if so else 'flat',
                   'hom_truoc': ht.group(1).strip() if ht else None})
    if not hd:
        return None
    return {'hop_dong': hd[:SO_HOP_DONG], 'cap_nhat': cap_nhat.group(1) if cap_nhat else '?', 'nguon': URL}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'gia.json'
    goc = os.path.join(os.path.dirname(os.path.abspath(out)), 'tam', 'thamkhao1.goc')
    try:
        h = open(goc, encoding='utf-8', errors='replace').read()
    except OSError:
        h = ''
        print(f'Không thấy {goc} – bước `cap_nhat.py lay` không tải được {URL}')
    kq = {'robusta': doc_bang(h, 'Robusta London'), 'arabica': doc_bang(h, 'Arabica New York')}
    tt = re.search(r'thị trường\s*<strong>([^<]+)</strong>', h)
    kq['trang_thai'] = chu(tt.group(1)) if tt else None
    json.dump(kq, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for san, ten in (('robusta', 'Robusta London'), ('arabica', 'Arabica New York')):
        v = kq[san]
        if not v:
            print(f'{ten} KHÔNG ĐỌC ĐƯỢC')
            continue
        print(f'{ten} (cập nhật {v["cap_nhat"]}):')
        for x in v['hop_dong']:
            print(f'   {x["ky_han"]}  {x["gia"]:>8}  {x["chieu"]:>4} {x["thay_doi"]:>6}  (hôm trước {x["hom_truoc"]})')
    print('Trạng thái thị trường:', kq['trang_thai'] or '?')
    if not (kq['robusta'] and kq['arabica']):
        sys.exit(1)


if __name__ == '__main__':
    main()

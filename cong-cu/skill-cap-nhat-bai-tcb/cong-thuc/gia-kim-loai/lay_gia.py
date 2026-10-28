"""Lấy giá 10 kim loại cho bài TCB "Giá kim loại thế giới" -> gia.json (đầu vào của tao_sua.py).

  python3 -I lay_gia.py <file-ra.json>

Nguồn (Trang chọn): https://www.thitruonghanghoa.com/gia-kim-loai — bảng "Bảng giá Kim loại" (trang dựng sẵn
trên máy chủ, không cần trình duyệt). Mỗi dòng có thẻ data-live-commodity="<id>" với các ô local-price (VNĐ),
diff-arrow (arrow_upward / arrow_downward), diff-pct ("0.10%"). KHÔNG dùng dải chạy chữ đầu trang (số khác bảng).
Khóa mỗi kim loại theo tên tiếng Anh dưới tên (GOLD / XAU USD, SILVER…, IRON ORE, TIN) — không theo vị trí.
Trang không ghi giờ cập nhật (giá chạy theo thời gian thực) → ghi giờ lấy số (giờ VN).
Kim loại nào không đọc được -> null + in "<tên> KHÔNG ĐỌC ĐƯỢC"; cả trang lỗi -> mọi kim loại null.
"""
import datetime, html, json, re, subprocess, sys

URL = 'https://www.thitruonghanghoa.com/gia-kim-loai'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36'
# khóa -> nhận diện bằng tên tiếng Anh in dưới tên kim loại trong bảng nguồn
KIM_LOAI = {
    'vang': r'^GOLD\b', 'bac': r'^SILVER\b', 'dong': r'^COPPER$', 'bach_kim': r'^PLATINUM$', 'niken': r'^NICKEL$',
    'chi': r'^LEAD$', 'nhom': r'^ALUMINU?M$', 'kem': r'^ZINC$', 'quang_sat': r'^IRON ORE', 'thiec': r'^TIN$',
}


def chu(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def tai(url):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '40', '--retry', '2', '-A', UA, '-w', '\n%{http_code}', url],
                       capture_output=True)
    body = r.stdout.decode('utf-8', 'replace')
    body, _, code = body.rpartition('\n')
    if r.returncode != 0 or code != '200':
        raise RuntimeError(f'HTTP {code} {r.stderr.decode()[:120]}')
    return body


def doc_bang(s):
    """Các dòng bảng giá (bản máy tính: <tr class="hidden md:table-row">) -> {khóa: {...}}."""
    kq = {}
    for tr in re.findall(r'<tr[^>]*md:table-row[^>]*>(.*?)</tr>', s, re.S):
        ten = re.search(r'<span[^>]*font-bold[^>]*>([^<]+)</span>\s*<span[^>]*block[^>]*>([^<]+)</span>', tr)
        if not ten:
            continue
        ten_vn, ten_en = chu(ten.group(1)), chu(ten.group(2)).upper()
        k = next((k for k, p in KIM_LOAI.items() if re.search(p, ten_en)), None)
        if not k or k in kq:
            continue
        f = {m.group(1): chu(m.group(2)) for m in
             re.finditer(r'data-live-field="([a-z-]+)"[^>]*>(.*?)</span>', tr, re.S)}
        don_vi = re.search(r'data-live-field="local-price"[^>]*>[^<]*</span>\s*<span[^>]*>([^<]+)</span>', tr)
        gia = re.sub(r'\D', '', f.get('local-price', ''))
        pct = re.fullmatch(r'(\d+(?:\.\d+)?)\s*%', f.get('diff-pct', ''))
        mui = f.get('diff-arrow', '')
        if not gia or not pct or mui not in ('arrow_upward', 'arrow_downward', 'remove', ''):
            print(f'{ten_vn} ({ten_en}): dòng nguồn lạ – bỏ qua', file=sys.stderr)
            continue
        p = float(pct.group(1))
        kq[k] = {'ten_nguon': f'{ten_vn} ({ten_en})', 'gia': int(gia), 'don_vi': chu(don_vi.group(1)) if don_vi else '',
                 'thay_doi': -p if mui == 'arrow_downward' else p, 'chieu': mui,
                 'gia_goc': f.get('local-price', ''), 'thay_doi_goc': f.get('diff-pct', '')}
    return kq


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'gia.json'
    luc = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    try:
        bang = doc_bang(tai(URL))
    except Exception as e:
        print('thitruonghanghoa LỖI', str(e)[:150], file=sys.stderr)
        bang = {}
    cap_nhat = f'lấy lúc {luc:%Hh%M} giờ VN {luc:%d/%m/%Y} (nguồn cập nhật theo thời gian thực)'
    kq = {'_nguon': URL, '_cap_nhat': cap_nhat}
    for k in KIM_LOAI:
        v = bang.get(k)
        kq[k] = dict(v, nguon=URL, cap_nhat=cap_nhat) if v else None
    json.dump(kq, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k in KIM_LOAI:
        v = kq[k]
        print(k.ljust(10), f"{v['ten_nguon']} | {v['gia']:,} {v['don_vi']} | {v['thay_doi']:+.2f}% | {cap_nhat}"
              if v else f'{k} KHÔNG ĐỌC ĐƯỢC')
    if any(kq[k] is None for k in KIM_LOAI):
        sys.exit(1)


if __name__ == '__main__':
    main()

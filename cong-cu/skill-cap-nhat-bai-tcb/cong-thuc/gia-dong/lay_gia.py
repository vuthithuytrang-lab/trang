"""Lấy giá cho bài TCB "Giá đồng hôm nay" -> gia.json (đầu vào của tao_sua.py).

  python3 -I lay_gia.py <file-ra.json>

- phe_lieu: bảng "Loại đồng | Giá (vnđ/kg)" trên https://thumuaphelieugiacao24h.vn/gia-dong-phe-lieu-hom-nay/
  (Trang chọn). Mỗi dòng: tên, giá thấp, giá cao, chữ gốc trên trang; kèm ngày sửa trang (article:modified_time).
- the_gioi: luôn null. Nguồn Trang chọn (Barchart HG*0) chặn máy chủ (CloudFront 403 / HTTP 202) — công thức KHÔNG
  vượt chặn. Bảng 1.2 của bài lại là mã hợp đồng NHÔM (ALI…), không phải đồng → giữ nguyên + cần duyệt (xem README).
Tải 1 lần như công cụ chung (curl), không giả mạo, không lách chặn. Nguồn lỗi -> null + in "<nguồn> KHÔNG ĐỌC ĐƯỢC".
"""
import html, json, re, subprocess, sys

PL = 'https://thumuaphelieugiacao24h.vn/gia-dong-phe-lieu-hom-nay/'
BC = 'https://www.barchart.com/futures/quotes/HG*0/futures-prices?viewName=main'


def tai(url):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '60', '--retry', '2', '-A', 'Mozilla/5.0', '-w', '\n%{http_code}', url],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[:120].strip())
    body, _, code = r.stdout.decode('utf-8', 'replace').rpartition('\n')
    if code != '200':
        raise RuntimeError(f'HTTP {code}')
    return body


def chu(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def so(x):
    d = re.sub(r'\D', '', x)
    return int(d) if d else None


def phe_lieu():
    s = tai(PL)
    for t in re.findall(r'<table.*?</table>', s, re.S | re.I):
        rows = [[chu(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S | re.I)]
                for r in re.findall(r'<tr.*?</tr>', t, re.S | re.I)]
        if not rows or not rows[0] or rows[0][0].lower() != 'loại đồng':
            continue
        dong = []
        for r in rows[1:]:
            m = len(r) >= 2 and re.fullmatch(r'([\d.,]+)\s*[–—-]\s*([\d.,]+)', r[1])
            if r and r[0] and m:
                dong.append({'ten': r[0], 'thap': so(m.group(1)), 'cao': so(m.group(2)), 'chu_goc': f'{r[0]} | {r[1]}'})
        if dong:
            m = re.search(r'article:modified_time"\s+content="([^"]+)"', s)
            return {'dong': dong, 'cap_nhat': m.group(1) if m else '?', 'nguon': PL}
    raise RuntimeError('không thấy bảng "Loại đồng"')


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'gia.json'
    kq = {'phe_lieu': None, 'the_gioi': None}
    try:
        kq['phe_lieu'] = phe_lieu()
    except Exception as e:
        print('thumuaphelieugiacao24h.vn KHÔNG ĐỌC ĐƯỢC:', e)
    print(f'barchart.com (đồng COMEX HG) KHÔNG ĐỌC ĐƯỢC: trang chặn máy chủ (CloudFront), công thức không vượt chặn — {BC}')
    json.dump(kq, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if kq['phe_lieu']:
        p = kq['phe_lieu']
        print('phế liệu:', '; '.join(d['chu_goc'] for d in p['dong']), '| trang sửa lần cuối', p['cap_nhat'])


if __name__ == '__main__':
    main()

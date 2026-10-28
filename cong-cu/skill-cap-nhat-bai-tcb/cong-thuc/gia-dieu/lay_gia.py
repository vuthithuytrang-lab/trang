"""Lấy bảng giá hạt điều cho bài TCB "Giá điều hôm nay" -> gia.json (đầu vào của tao_sua.py).

  python3 -I lay_gia.py <file-ra.json>

Nguồn (Trang chọn): https://banggianongsan.com/bang-gia-hat-dieu/ — trang HTML thường, đọc bằng curl (không cần trình duyệt).
Bảng: Nông sản (đơn vị tính) | Giá cũ | Giá mới | Thay đổi. Mỗi dòng ghi lại: tên, giá cũ, giá mới (list số), số chữ số lẻ, chữ cột Thay đổi.
Giờ cập nhật: "dateModified" (giờ VN) trong trang; dự phòng: dòng "Đăng bởi … hh:mm dd/mm/yyyy".
Không đọc được -> "banggianongsan": null, in "banggianongsan KHÔNG ĐỌC ĐƯỢC", thoát mã 1.
"""
import html, json, re, subprocess, sys

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36'
URL = 'https://banggianongsan.com/bang-gia-hat-dieu/'


def tai(url):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '40', '--retry', '2', '-A', UA, url], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode('utf-8', 'replace')[:160])
    return r.stdout.decode('utf-8', 'replace')


def chu(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def doc_gia(o):
    """'25.000 – 30.000 vnđ/kg' -> ['25000', '30000']; '10.5 – 12.8 USD/kg' -> ['10.5', '12.8'].
    Giữ nguyên chữ số của nguồn (chuỗi), không làm tròn, không đổi kiểu số."""
    usd = 'usd' in o.lower()
    so = re.findall(r'\d[\d.,]*\d|\d', o)
    if not so:
        return None
    if usd:                                   # USD: dấu chấm (hoặc phẩy) là phần thập phân
        return [s.replace(',', '.') for s in so]
    return [re.sub(r'\D', '', s) for s in so]   # VND: dấu chấm là phân cách nghìn


def doc_trang(s):
    bang = None
    for t in re.findall(r'<table.*?</table>', s, re.S | re.I):
        rows = [[chu(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S | re.I)]
                for r in re.findall(r'<tr.*?</tr>', t, re.S | re.I)]
        if rows and len(rows[0]) >= 4 and 'giá mới' in rows[0][2].lower() and 'thay đổi' in rows[0][3].lower():
            bang = rows
            break
    if not bang:
        raise RuntimeError('không thấy bảng "Giá cũ | Giá mới | Thay đổi"')
    dong = []
    for r in bang[1:]:
        if len(r) < 4 or 'điều' not in r[0].lower():
            continue
        cu, moi = doc_gia(r[1]), doc_gia(r[2])
        if not moi:
            continue
        dong.append({'ten': r[0], 'cu': cu, 'moi': moi,
                     'usd': 'usd' in (r[0] + r[2]).lower(), 'thay_doi': r[3], 'chu_goc': r[1:4]})
    if not dong:
        raise RuntimeError('bảng không có dòng giá điều nào')
    m = re.search(r'"dateModified"\s*:\s*"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})[^"]*\+07:00"', s)
    if m:
        y, mo, d, hh, mi = m.groups()
        cap_nhat = f'{hh}:{mi} {d}/{mo}/{y}'
    else:
        m = re.search(r'(\d{1,2}:\d{2})\s*(\d{1,2}/\d{1,2}/\d{4})', chu(s))
        cap_nhat = f'{m.group(1)} {m.group(2)}' if m else '?'
    mt = re.search(r'Giá điều ngày hôm nay:\s*([^<]{0,300})', s)
    return {'dong': dong, 'cap_nhat': cap_nhat, 'nhan_dinh': chu(mt.group(1)) if mt else '', 'nguon': URL}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'gia.json'
    try:
        kq = {'banggianongsan': doc_trang(tai(URL))}
    except Exception as e:
        print('banggianongsan LỖI', str(e)[:160], file=sys.stderr)
        kq = {'banggianongsan': None}
    json.dump(kq, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    v = kq['banggianongsan']
    if not v:
        print('banggianongsan KHÔNG ĐỌC ĐƯỢC')
        sys.exit(1)
    print(f'banggianongsan: {len(v["dong"])} dòng, cập nhật {v["cap_nhat"]} – {v["nhan_dinh"][:80]}')
    for d in v['dong']:
        print(f'  {d["ten"]:<40} cũ {d["cu"]} | mới {d["moi"]} | {d["thay_doi"]}')


if __name__ == '__main__':
    main()

"""Lấy giá tiêu cho bài TCB "Giá tiêu hôm nay" -> gia.json (đầu vào của tao_sua.py).

  python3 -I lay_gia.py <file-ra.json>

Nguồn (Trang chọn):
- banggianongsan.com/bang-gia-tieu/  — NGUỒN CHÍNH: bảng trong nước (8 dòng, đúng tên vùng như bài), bảng "Thị trường xuất khẩu"
  (8 dòng, đúng tên như bài), bảng "Giá tiêu nội địa Ấn Độ". Giờ đăng bài ("08:32 28/10/2026").
- giatieu.com/gia-tieu-hom-nay/      — ĐỐI CHIẾU giá trong nước (Gia Lai, Bà Rịa - Vũng Tàu, Đắk Lắk, Bình Phước, Đắk Nông).
- giatieu.com/gia-tieu-truc-tuyen/   — ĐỐI CHIẾU bảng thế giới (hay báo "Hệ thống đang bận" → null) + giá Ấn Độ.
Trang tĩnh (không cần trình duyệt). Nguồn nào không đọc được → null và in "<nguồn> KHÔNG ĐỌC ĐƯỢC".
Mỗi bảng: {tên dòng: {"cu": số, "moi": số, "thay_doi": chữ gốc của ô Thay đổi, "tho": nguyên dòng như trên trang}} — số là số nguyên (bỏ dấu nghìn).
"""
import html, json, re, subprocess, sys

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36'
BGNS = 'https://banggianongsan.com/bang-gia-tieu/'
GT_HN = 'https://giatieu.com/gia-tieu-hom-nay/'
GT_TT = 'https://giatieu.com/gia-tieu-truc-tuyen/'


def tai(url):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '60', '--retry', '3', '-A', UA, url], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode('utf-8', 'replace')[:150])
    s = r.stdout.decode('utf-8', 'replace')
    if len(s) < 2000:
        raise RuntimeError(f'trang quá ngắn ({len(s)} ký tự)')
    return s


def chu(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def so(x):
    d = re.sub(r'\D', '', x or '')
    return int(d) if d else None


def cac_bang(s):
    """Mọi bảng trong trang -> list các bảng, mỗi bảng = list dòng (list ô chữ)."""
    return [[[chu(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)]
             for r in re.findall(r'<tr.*?</tr>', t, re.S)]
            for t in re.findall(r'<table.*?</table>', s, re.S)]


def bang_3_cot(b):
    """Dòng: tên | giá cũ | giá mới | thay đổi [| VNĐ/kg] -> dict."""
    out = {}
    for r in b[1:]:
        if len(r) >= 4 and so(r[1]) and so(r[2]):
            out[r[0]] = {'cu': so(r[1]), 'moi': so(r[2]), 'thay_doi': r[3], 'tho': ' | '.join(r[:4])}
    return out or None


def bang_gia_nong_san():
    s = tai(BGNS)
    trong_nuoc = xuat_khau = an_do = None
    for b in cac_bang(s):
        if not b or not b[0]:
            continue
        dau = ' '.join(b[0]).lower()
        if trong_nuoc is None and dau.startswith('nông sản'):
            trong_nuoc = bang_3_cot(b)
        elif xuat_khau is None and dau.startswith('thị trường') and 'usd' in dau:
            xuat_khau = bang_3_cot(b)
        elif an_do is None and 'rupee' in dau:
            an_do = bang_3_cot(b)
    m = re.search(r'author-date">\s*(\d{1,2}:\d{2}\s+\d{1,2}/\d{1,2}/\d{4})', s) or \
        re.search(r'(\d{1,2}:\d{2}\s+\d{1,2}/\d{1,2}/\d{4})', chu(s))
    if not trong_nuoc:
        raise RuntimeError('không thấy bảng giá trong nước')
    return {'url': BGNS, 'cap_nhat': m.group(1) if m else '?', 'trong_nuoc': trong_nuoc,
            'xuat_khau': xuat_khau, 'an_do': an_do}


def gia_tieu_hom_nay():
    s = tai(GT_HN)
    vung = {}
    for b in cac_bang(s):
        if b and b[0] and b[0][0].lower().startswith('khu vực'):
            for r in b[1:]:
                if len(r) >= 3 and so(r[1]):
                    vung[r[0]] = {'gia': so(r[1]), 'thay_doi': int(re.sub(r'[^\d-]', '', r[2]) or 0)}
    m = re.search(r'Giá tiêu hôm nay (\d{1,2}/\d{1,2}/\d{4})', s)
    if not vung:
        raise RuntimeError('không thấy bảng giá theo khu vực')
    return {'url': GT_HN, 'ngay': m.group(1) if m else '?', 'vung': vung}


def gia_tieu_truc_tuyen():
    s = tai(GT_TT)
    the_gioi = an_do = None
    for b in cac_bang(s):
        if not b or not b[0]:
            continue
        dau = ' '.join(b[0]).lower()
        dong = {r[0]: {'gia': so(r[1]), 'thay_doi': r[2]} for r in b[1:] if len(r) >= 3 and so(r[1])}
        if dau.startswith('thị trường'):
            the_gioi = dong or None
        elif 'rupee' in dau:
            an_do = dong or None
    if 'Hệ thống đang bận' in s and not the_gioi:
        print('giatieu.com/gia-tieu-truc-tuyen: bảng thế giới báo "Hệ thống đang bận"')
    m = re.search(r'"time_update":"([^"]+)"', s)
    if not the_gioi and not an_do:
        raise RuntimeError('không thấy bảng giá')
    return {'url': GT_TT, 'cap_nhat': m.group(1) if m else '?', 'the_gioi': the_gioi, 'an_do': an_do}


def main():
    ra = sys.argv[1] if len(sys.argv) > 1 else 'gia.json'
    kq = {}
    for ma, ham in (('banggianongsan', bang_gia_nong_san), ('giatieu_hom_nay', gia_tieu_hom_nay),
                    ('giatieu_truc_tuyen', gia_tieu_truc_tuyen)):
        try:
            kq[ma] = ham()
        except Exception as e:  # noqa: BLE001 – nguồn lỗi nào cũng chỉ làm nguồn đó = null
            kq[ma] = None
            print(ma, 'KHÔNG ĐỌC ĐƯỢC:', str(e)[:150])
    json.dump(kq, open(ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    b = kq['banggianongsan']
    if b:
        print(f'banggianongsan (đăng {b["cap_nhat"]}): trong nước {len(b["trong_nuoc"])} dòng, '
              f'xuất khẩu {len(b["xuat_khau"] or {})} dòng, Ấn Độ {len(b["an_do"] or {})} dòng')
        for t, v in b['trong_nuoc'].items():
            print(f'   {t}: {v["cu"]:,} → {v["moi"]:,} ({v["thay_doi"]})')
    g = kq['giatieu_hom_nay']
    if g:
        print(f'giatieu hôm nay ({g["ngay"]}):', ', '.join(f'{k} {v["gia"]:,} ({v["thay_doi"]:+,})' for k, v in g['vung'].items()))
    t = kq['giatieu_truc_tuyen']
    if t:
        print(f'giatieu trực tuyến ({t["cap_nhat"]}): thế giới {"có" if t["the_gioi"] else "TRỐNG"}; Ấn Độ',
              ', '.join(f'{k} {v["gia"]:,}' for k, v in (t['an_do'] or {}).items()))
    if not b:
        print('banggianongsan KHÔNG ĐỌC ĐƯỢC – mọi bảng giá sẽ giữ nguyên')
        sys.exit(1)


if __name__ == '__main__':
    main()

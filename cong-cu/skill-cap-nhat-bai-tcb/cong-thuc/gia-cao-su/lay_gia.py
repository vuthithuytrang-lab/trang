"""Lấy giá cao su mới nhất cho bài TCB "Giá cao su" -> gia.json (đầu vào của tao_sua.py).

  python3 -I lay_gia.py <thư mục làm việc>/cap-nhat
  (chạy SAU lay_gia_the_gioi.js — file <cap-nhat>/gia-the-gioi.json phải có sẵn)

- Trong nước: bài "Giá cao su hôm nay dd/mm/yyyy" MỚI NHẤT trên doanhnghiephoinhap.vn (đăng ~9h sáng mỗi ngày,
  số lấy từ giacaphe.com lúc ~8h). Lấy giá Bình Long, Phú Riềng, Mang Yang, Bà Rịa bằng mẫu câu cố định.
- TOCOM (RSS3, nay là sàn OSE/JPX): file giá thanh toán chính thức của JPX (rb_eYYYYMMDD.csv).
- SHFE + SGX TSR20: bảng giacaphe.com/gia-cao-su-truc-tuyen/ (đọc bằng lay_gia_the_gioi.js).
Thiếu mục nào thì mục đó = null và in "THIẾU" — tao_sua.py sẽ giữ số cũ + ghi cần duyệt.
"""
import html, json, os, re, subprocess, sys

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36'
DNHN_LIST = 'https://doanhnghiephoinhap.vn/nhan-dinh-thi-truong'
JPX_IDX = 'https://www.jpx.co.jp/english/markets/derivatives/settlement-price/index.html'


def tai(url):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '40', '--retry', '2', '-A', UA, url], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'không tải được {url}: {r.stderr.decode()[:120]}')
    return r.stdout.decode('utf-8', 'replace')


def chu(x):
    x = re.sub(r'(?s)<(script|style).*?</\1>', ' ', x)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def so(x):
    return int(x.replace('.', '').replace(',', ''))


def bai_dnhn_moi_nhat():
    s = tai(DNHN_LIST)
    links = re.findall(r'https://doanhnghiephoinhap\.vn/gia-cao-su-hom-nay-\d{7,8}-[^"]+\.html', s)
    best = None
    for u in set(links):
        m = re.search(r'hom-nay-(\d{7,8})-', u)
        d = m.group(1)
        # ngày dạng dmmyyyy hoặc ddmmyyyy
        dd, mm, yy = (d[:-6], d[-6:-4], d[-4:])
        key = (int(yy), int(mm), int(dd))
        if best is None or key > best[0]:
            best = (key, u)
    if not best:
        raise RuntimeError('không thấy bài "giá cao su hôm nay" trên doanhnghiephoinhap.vn')
    return best[1]


def doc_trong_nuoc(t):
    """Trả về dict giá + câu gốc của từng công ty (để đối chiếu bằng mắt)."""
    g, cau = {}, {}
    mau = {
        'phu_rieng_mu_tap': r'Phú Riềng(?:[^.]|\.\d)*?mủ tạp(?:[^.]|\.\d)*?(\d{3}) đồng/DRC',
        'phu_rieng_mu_nuoc': r'Phú Riềng(?:[^.]|\.\d)*?mủ nước (\d{3}) đồng/TSC',
        'mang_yang_mu_nuoc': r'Mang ?Yang(?:[^.]|\.\d)*?mủ nước(?:[^.]|\.\d)*?(\d{3}) - (\d{3}) đồng/TSC \(loại 2-loại 1\)',
        'mang_yang_mu_dong': r'Mang ?Yang(?:[^.]|\.\d)*?mủ đông tạp(?:[^.]|\.\d)*?(\d{3}) - (\d{3}) đồng/DRC \(loại 2-loại 1\)',
        'binh_long_nha_may': r'Bình Long(?:[^.]|\.\d)*?Nhà máy ở mức (\d{3}) đồng',
        'binh_long_doi_sx': r'Bình Long(?:[^.]|\.\d)*?đội sản xuất (\d{3}) đồng',
        'binh_long_mu_tap': r'Bình Long(?:[^.]|\.\d)*?mủ tạp \(DRC 60%\)(?:[^.]|\.\d)*?(\d{1,2}\.\d{3}) đồng/kg',
        'ba_ria_mu_nuoc': r'Bà Rịa(?:[^.]|\.\d)*?mủ nước ở mức (\d{3}) đồng/độ TSC/kg \(áp dụng cho độ TSC từ 25 đến dưới 30\)',
        'ba_ria_mu_dong': r'Bà Rịa(?:[^.]|\.\d)*?mủ đông DRC \((35 - 4\d%)\) ở mức (\d{1,2}\.\d{3}) đồng/kg',
        'ba_ria_mu_nguyen_lieu': r'Bà Rịa(?:[^.]|\.\d)*?mủ nguyên liệu (\d{1,2}\.\d{3}) đồng/kg',
    }
    for k, p in mau.items():
        m = re.search(p, t)
        if not m:
            g[k] = None
            continue
        cau[k] = m.group(0)
        if k.startswith('mang_yang'):
            g[k + '_loai2'], g[k + '_loai1'] = so(m.group(1)), so(m.group(2))
        elif k == 'ba_ria_mu_dong':
            g[k] = so(m.group(2))
            g[k + '_nhom_drc'] = m.group(1)
        else:
            g[k] = so(m.group(1))
    return g, cau


def doc_jpx():
    s = tai(JPX_IDX)
    m = re.search(r'href="([^"]*rb_e(\d{8})\.csv)"', s)
    if not m:
        raise RuntimeError('không thấy file giá thanh toán JPX')
    url = 'https://www.jpx.co.jp' + m.group(1)
    csv = tai(url)
    hd = []
    for line in csv.splitlines():
        c = line.split(',')
        if len(c) > 11 and c[1].startswith('FUT_RSS3_'):
            hd.append({'ky_han': c[3][4:6] + '/' + c[3][2:4], 'gia': c[5], 'ngay_dao_han_con': c[10]})
    return {'nguon': url, 'ngay': m.group(2), 'rss3': hd}


def main():
    cn = sys.argv[1] if len(sys.argv) > 1 else 'cap-nhat'
    out = {'trong_nuoc': None, 'tocom': None, 'shfe': None, 'sgx': None}
    try:
        u = bai_dnhn_moi_nhat()
        t = chu(tai(u))
        m = re.search(r'cập nhật lúc ([\d:]+ ngày \d{1,2}/\d{1,2}/\d{4}) trên trang ([\w.]+)', t)
        g, cau = doc_trong_nuoc(t)
        out['trong_nuoc'] = {'nguon': u, 'thoi_diem': m.group(0) if m else '?', 'gia': g, 'cau_goc': cau}
    except Exception as e:
        print('THIẾU trong nước:', e)
    try:
        j = doc_jpx()
        out['tocom'] = {'nguon': j['nguon'], 'thoi_diem': f'giá thanh toán ngày {j["ngay"]}',
                        'hop_dong': [{'ky_han': x['ky_han'], 'gia': x['gia']} for x in j['rss3']]}
    except Exception as e:
        print('THIẾU TOCOM/JPX:', e)
    tg_path = os.path.join(cn, 'gia-the-gioi.json')
    if os.path.exists(tg_path):
        tg = json.load(open(tg_path, encoding='utf-8'))
        for san in ('shfe', 'sgx', 'tocom'):
            rows = tg['bang'].get(san) or []
            hd = [{'ky_han': re.search(r'(\d\d/\d\d)$', r[0]).group(1), 'gia': r[1], 'thay_doi': r[2], 'hom_truoc': r[7]}
                  for r in rows if re.search(r'\d\d/\d\d$', r[0])]
            key = san if san != 'tocom' else 'tocom_giacaphe'
            out[key] = {'nguon': tg['nguon'], 'thoi_diem': ' '.join(tg['cap_nhat']) + f' (lấy lúc {tg.get("lay_luc", "?")} UTC)',
                        'hop_dong': hd} if hd else None
    else:
        print('THIẾU', tg_path, '– chạy lay_gia_the_gioi.js trước')
    json.dump(out, open(os.path.join(cn, 'gia.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    # đối chiếu TOCOM: JPX vs giacaphe
    if out.get('tocom') and out.get('tocom_giacaphe'):
        a = {x['ky_han']: float(x['gia']) for x in out['tocom']['hop_dong']}
        for x in out['tocom_giacaphe']['hop_dong']:
            if x['ky_han'] in a and abs(a[x['ky_han']] - float(x['gia'])) > 1e-9:
                print(f'LƯU Ý TOCOM {x["ky_han"]}: JPX {a[x["ky_han"]]} ≠ giacaphe {x["gia"]}')
    for k, v in (out['trong_nuoc'] or {}).get('gia', {}).items():
        if v is None:
            print('THIẾU giá trong nước:', k)


if __name__ == '__main__':
    main()

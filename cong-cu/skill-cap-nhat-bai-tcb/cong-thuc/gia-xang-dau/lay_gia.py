"""Lấy giá xăng dầu mới nhất cho bài TCB "Giá xăng dầu hôm nay" -> gia.json (đầu vào của tao_sua.py).

  python3 -I lay_gia.py <thư mục làm việc>/cap-nhat

- Petrolimex: tìm thông cáo "điều chỉnh giá xăng dầu" MỚI NHẤT trên petrolimex.com.vn, tải ảnh bảng giá về
  cap-nhat/tam/plx-gia.jpg (Claude PHẢI mở ảnh này đối chiếu); số lấy từ bảng Petrolimex trên topi.vn.
- PVOIL: bảng PVOIL trên topi.vn (pvoil.com.vn chặn máy chủ).
- Mipec: mipec.com.vn/pages/gia-xang-dau-ban-le.
In bảng so sánh để đối chiếu. Thiếu nguồn nào thì hệ thống đó = null.
"""
import html, json, os, re, subprocess, sys

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36'
PLX_LIST = 'https://www.petrolimex.com.vn/ndi/thong-cao-bao-chi.html'
TOPI = 'https://topi.vn/gia-xang-dau-hom-nay.html'
MIPEC = 'https://www.mipec.com.vn/pages/gia-xang-dau-ban-le'


def tai(url, ra=None):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '40', '--retry', '2', '-A', UA, url] + (['-o', ra] if ra else []),
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'không tải được {url}: {r.stderr.decode()[:120]}')
    return None if ra else r.stdout.decode('utf-8', 'replace')


def chu(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def so(x):
    d = re.sub(r'\D', '', x)
    return int(d) if d else None


def ma_hang(ten):
    t = ten.lower().replace(' ', '')
    if 'dầuhỏa' in t or 'dầuhoả' in t:
        return 'dau_hoa'
    if '0,001s' in t:
        return 'do_0001'
    if '0,05s' in t:
        return 'do_005'
    if '95-v' in t and '95-iii' not in t or 'mức5' in t and '95' in t:
        return 'e10_95_v'
    if '95-iii' in t:
        return 'e10_95_iii'
    if '92' in t:
        return 'e5_92'
    return None


def bang(s):
    """Mọi bảng trong trang -> list các dòng (list ô chữ)."""
    out = []
    for t in re.findall(r'<table.*?</table>', s, re.S):
        out.append([[chu(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)]
                    for r in re.findall(r'<tr.*?</tr>', t, re.S)])
    return out


def doc_bang_gia(rows, so_cot):
    g = {}
    for r in rows:
        if len(r) < 1 + so_cot:
            continue
        mh = ma_hang(r[0])
        vals = [so(c) for c in r[1:1 + so_cot]]
        if mh and all(v and 10000 < v < 100000 for v in vals):
            g[mh] = vals
    return g


def main():
    thu_muc = sys.argv[1] if len(sys.argv) > 1 else 'cap-nhat'
    os.makedirs(os.path.join(thu_muc, 'tam'), exist_ok=True)
    kq = {'_ghi_chu': {}}

    # 1) Thông cáo Petrolimex mới nhất
    plx = {}
    try:
        ds = tai(PLX_LIST)
        m = re.search(r'href="(/ndi/thong-cao-bao-chi/[^"]*dieu-chinh-gia-xang-dau[^"]*)"', ds)
        plx['url'] = 'https://www.petrolimex.com.vn' + m.group(1)
        bai = tai(plx['url'])
        plx['tieu_de'] = chu(re.search(r'<title>(.*?)</title>', bai, re.S).group(1)).split('::')[0].strip()
        sau = bai[bai.find('mức giá mới như sau'):]
        anh = re.search(r'<img[^>]+src="([^"]+\.jpg)"', sau)
        if anh:
            src = anh.group(1)
            src = 'https:' + src if src.startswith('//') else src
            tai(src.replace(' ', '%20'), os.path.join(thu_muc, 'tam', 'plx-gia.jpg'))
            plx['anh'] = os.path.join(thu_muc, 'tam', 'plx-gia.jpg')
    except Exception as e:
        kq['_ghi_chu']['petrolimex_tcbc'] = f'lỗi đọc thông cáo Petrolimex: {e}'
    kq['_petrolimex_tcbc'] = plx

    # 2) Topi: bảng 0 = Petrolimex (2 vùng), bảng PVOIL (1 cột giá)
    try:
        tb = bang(tai(TOPI))
        p = doc_bang_gia(tb[0], 2) if tb else {}
        pv = {}
        for rows in tb[1:]:
            if rows and 'điều chỉnh' in ' '.join(rows[0]).lower():
                pv = {k: v for k, v in doc_bang_gia(rows, 1).items()}
                break
        ky = plx.get('tieu_de', '').replace('Petrolimex điều chỉnh giá xăng dầu', 'kỳ điều chỉnh').strip()
        kq['petrolimex'] = {'ky': f'{ky} (số theo topi.vn, đối chiếu ảnh thông cáo)', 'nguon': plx.get('url') or TOPI,
                            'gia': p} if p else None
        kq['pvoil'] = {'ky': f'{ky} (theo topi.vn)', 'nguon': TOPI, 'gia': pv} if pv else None
        if not p:
            kq['_ghi_chu']['petrolimex'] = 'topi.vn không có bảng Petrolimex'
        if not pv:
            kq['_ghi_chu']['pvoil'] = 'topi.vn không có bảng PVOIL'
    except Exception as e:
        kq['petrolimex'] = kq['pvoil'] = None
        kq['_ghi_chu']['pvoil'] = kq['_ghi_chu']['petrolimex'] = f'lỗi đọc topi.vn: {e}'

    # 3) Mipec
    try:
        mp = {}
        for rows in bang(tai(MIPEC)):
            mp.update(doc_bang_gia(rows, 2))
        kq['mipec'] = {'ky': 'giá đang áp dụng trên mipec.com.vn', 'nguon': MIPEC, 'gia': mp} if mp else None
        if not mp:
            kq['_ghi_chu']['mipec'] = 'mipec.com.vn không có bảng giá'
    except Exception as e:
        kq['mipec'] = None
        kq['_ghi_chu']['mipec'] = f'lỗi đọc mipec.com.vn: {e}'

    ra = os.path.join(thu_muc, 'gia.json')
    json.dump(kq, open(ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('Thông cáo Petrolimex mới nhất:', plx.get('tieu_de', '?'))
    print('  ', plx.get('url', '?'))
    print('  Ảnh bảng giá (PHẢI mở ra đối chiếu):', plx.get('anh', 'KHÔNG TẢI ĐƯỢC'))
    ten = {'e10_95_v': 'E10 RON 95-V', 'e10_95_iii': 'E10 RON 95-III', 'e5_92': 'E5 RON 92-II',
           'do_0001': 'DO 0,001S-V', 'do_005': 'DO 0,05S-II', 'dau_hoa': 'Dầu hỏa 2-K'}
    print(f'{"Mặt hàng":16} | {"Petrolimex V1/V2 (Topi)":24} | {"PVOIL (Topi)":12} | Mipec V1/V2')
    for k, t in ten.items():
        f = lambda h: '/'.join(f'{v:,}' for v in ((kq.get(h) or {}).get('gia') or {}).get(k, [])) or '-'
        print(f'{t:16} | {f("petrolimex"):24} | {f("pvoil"):12} | {f("mipec")}')
    for k, v in kq['_ghi_chu'].items():
        print('LƯU Ý:', k, '-', v)
    print('→', ra)


if __name__ == '__main__':
    main()

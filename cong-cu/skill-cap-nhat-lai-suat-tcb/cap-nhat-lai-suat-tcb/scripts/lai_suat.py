#!/usr/bin/env python3
"""Cập nhật bảng lãi suất trong bài blog Techcombank từ các nguồn số liệu, xuất bản HTML để tạo Google Docs.

Mọi lệnh nhận đường dẫn file cấu hình JSON (xem references/cau-hinh-mau.json). File tạm nằm ở <thư mục cấu hình>/tam/.

  python3 lai_suat.py lay  cau-hinh.json                     tải bài Techcombank + các nguồn
  python3 lai_suat.py dung cau-hinh.json dd/mm/yyyy          dựng tam/baiN.min.html (đã tô vàng) + tam/ket-qua.json
  python3 lai_suat.py soat cau-hinh.json baiN <export.json>  so bản xuất HTML của Google Docs với bản dựng (exit 0 = khớp)
  python3 lai_suat.py bao-cao cau-hinh.json dd/mm/yyyy <link Google Docs bài 1> [<link Docs bài 2> ...] [--ghi-chu "..."]
"""
import base64, difflib, html, json, os, re, subprocess, sys, time, unicodedata
from datetime import date

VNE_API = 'https://gw.vnexpress.net/th?types=bank_rate_'   # trang lãi suất VnExpress vẽ bảng bằng JS, số nằm ở API này
KY_VNE = ['1', '3', '6', '9', '12']
THU_TU = ['1', '2', '3', '6', '9', '12', '13', '18', '24', '36']
TEN_BANG = {'quay': 'Tại quầy', 'online': 'Online'}
# tên trong bài Techcombank -> các tên khác nhau của cùng ngân hàng trên nguồn (ghép đã kiểm chứng)
TEN_GHEP = {
    'MBBank': ['MB', 'MB Bank'], 'PVcomBank': ['PVCombank'], 'BAOVIET Bank': ['BaoVietBank', 'Bảo Việt'],
    'Viet Capital Bank (BVBANK)': ['BVBank'], 'PG Bank': ['PGBank'], 'BacABank': ['Bắc Á'],
    'VCB Neo (CBBank)': ['VCBNeo', 'VCBNeo (CBBank)'], 'CBBank': ['VCBNeo', 'VCBNeo (CBBank)'],
    'OceanBank': ['MBV', 'MBV (OceanBank)'], 'Kienlongbank': ['Kiên Long'], 'VietBank': ['Vietbank'],
    'NamABank': ['Nam Á Bank'], 'Vikki Bank': ['Vikkibank (Đông Á)'],
}
VANG = 'background-color:#ffff00'
XANH = {'rgb(10,132,255)', 'rgb(66,133,244)', '#0a84ff', '#4285f4'}
DO = {'rgb(237,28,36)', 'rgb(255,0,0)', '#ed1c24', '#ff0000'}
TEN_MAU = {'xanh': 'xanh (cao nhất)', 'do': 'đỏ (thấp nhất)', 'thuong': 'chữ thường'}


# ======================= TIỆN ÍCH =======================
def chu(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).replace('\xa0', ' ').strip()


def so(x):
    try:
        return float(str(x).strip().replace(',', '.'))
    except ValueError:
        return None


def thay_o(row, i, o_moi):
    """Thay ô thứ i trong một dòng bảng theo VỊ TRÍ — không theo nội dung, vì nhiều ô giống hệt nhau."""
    phan = re.split(r'(<td[^>]*>.*?</td>)', row, flags=re.S)
    vt = [j for j, x in enumerate(phan) if x.startswith('<td')]
    phan[vt[i]] = o_moi
    return ''.join(phan)


def ghep_dong(tb, hang):
    phan = re.split(r'(<tr.*?</tr>)', tb, flags=re.S)
    vt = [j for j, x in enumerate(phan) if x.startswith('<tr')]
    for j, h in zip(vt, hang):
        phan[j] = h
    return ''.join(phan)


def chuan_ten(x):
    """'Nam Á Bank' -> 'nama', 'Viet Capital Bank' -> 'vietcapital': bỏ dấu, khoảng trắng, chữ 'bank'/'ngân hàng'."""
    x = unicodedata.normalize('NFD', x.replace('Đ', 'D').replace('đ', 'd'))
    x = ''.join(c for c in x if unicodedata.category(c) != 'Mn').lower()
    x = re.sub(r'ngan\s*hang|bank', '', x)
    return re.sub(r'[^a-z0-9]', '', x)


def bien_the(ten):
    """Các khóa so khớp của một tên: cả tên, phần ngoài ngoặc, phần trong ngoặc."""
    out = {chuan_ten(ten)}
    m = re.match(r'(.*?)\((.*?)\)', ten)
    if m:
        out |= {chuan_ten(m.group(1)), chuan_ten(m.group(2))}
    return {x for x in out if x}


def doc_cau_hinh(p):
    ch = json.load(open(p, encoding='utf-8'))
    ch['_tam'] = os.path.join(os.path.dirname(os.path.abspath(p)), 'tam') + '/'
    for ten, khac in ch.get('ten_ghep', {}).items():      # tên ghép thêm do người dùng / AI khai trong cấu hình
        TEN_GHEP[ten] = TEN_GHEP.get(ten, []) + list(khac)
    for i, b in enumerate(ch['bai'], 1):
        b.setdefault('ma', f'bai{i}')
    for i, n in enumerate(ch['nguon'], 1):
        n.setdefault('ma', f'nguon{i}')
        n.setdefault('ten', ten_nguon(n))
        if n.get('ky_han'):
            n['ky_han'] = [str(k) for k in n['ky_han']]
    return ch


def ten_nguon(n):
    if n.get('tep') or n.get('tep_html'):
        return os.path.basename(n.get('tep') or n['tep_html'])
    host = re.sub(r'^www\.', '', re.sub(r'^https?://([^/]+).*', r'\1', n['url']))
    return {'vnexpress.net': 'VnExpress', 'topi.vn': 'Topi'}.get(host, host)


def la_vne(n):
    return 'vnexpress.net' in n.get('url', '') and not n.get('tep_html')


# ======================= LẤY NGUỒN =======================
def tai(url, dich):
    """curl có thử lại (Techcombank hay ngắt kết nối giữa chừng). Trả 'ok' hoặc mô tả lỗi."""
    loi = ''
    for lan in range(5):
        r = subprocess.run(['curl', '-sS', '-L', '-m', '60', '--retry', '3', '-A', 'Mozilla/5.0',
                            '-o', dich, '-w', '%{http_code}', url], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip() == '200' and os.path.getsize(dich) > 1000:
            return 'ok'
        loi = f'lỗi (HTTP {r.stdout.strip() or "?"} {r.stderr.strip()[:100]})'
        if '403' in r.stderr or 'CONNECT tunnel' in r.stderr:   # mạng của môi trường chặn tên miền này, thử lại vô ích
            break
        time.sleep(3 * (lan + 1))
    return loi


def chep(nguon, dich):
    if not os.path.exists(nguon):
        return f'lỗi (không thấy file {nguon})'
    open(dich, 'wb').write(open(nguon, 'rb').read())
    return 'ok'


def lay(ch):
    T = ch['_tam']
    os.makedirs(T, exist_ok=True)
    tt = {}
    for b in ch['bai']:
        # "tep_html": trang đã lưu sẵn (Ctrl+S) khi môi trường không vào được techcombank.com
        tt[b['ma']] = chep(b['tep_html'], f'{T}{b["ma"]}.html') if b.get('tep_html') else tai(b['url'], f'{T}{b["ma"]}.html')
    for n in ch['nguon']:
        if n.get('tep_html'):
            tt[n['ma']] = chep(n['tep_html'], f'{T}{n["ma"]}.html')
        elif n.get('tep'):
            tt[n['ma']] = 'ok' if os.path.exists(n['tep']) else f'lỗi (không thấy file {n["tep"]})'
        elif la_vne(n):
            kq = [tai(VNE_API + t, f'{T}{n["ma"]}-{t}.json') for t in ['offline', 'online']]
            tt[n['ma']] = 'ok' if 'ok' in kq else kq[0]
        else:
            tt[n['ma']] = tai(n['url'], f'{T}{n["ma"]}.html')
    for k, v in tt.items():
        print(k, v)
    json.dump(tt, open(T + 'trang-thai-nguon.json', 'w'), ensure_ascii=False, indent=1)


def hien_vne(v):
    """Số như VnExpress hiển thị: tối thiểu 1 chữ số thập phân (7 -> 7.0, 4.75 -> 4.75)."""
    f = so(v) if v not in (None, '', '-') else None
    if not f:
        return None
    s = ('%.4f' % f).rstrip('0')
    return s + '0' if s.endswith('.') else s


def doc_vne(T, n):
    out, ngay = {'quay': None, 'online': None}, None
    for key, t in [('quay', 'offline'), ('online', 'online')]:
        try:
            ds = json.load(open(f'{T}{n["ma"]}-{t}.json'))['data']['bank_rate_' + t]
            assert len(ds) > 5
        except Exception:
            continue
        out[key] = {r['bank'].strip(): {k: hien_vne(r.get('rate_' + k)) for k in KY_VNE} for r in ds}
        # chỉ bảng tại quầy có trường "update" (= dòng "Cập nhật đến ngày" trên trang); "updated_at" là giờ máy chủ, không phải ngày số liệu
        for r in ds:
            if r.get('update') and not ngay:
                m, d, y = r['update'].split('/')
                ngay = f'{int(d):02d}/{int(m):02d}/{y}'
    ghi_chu = 'ngày cập nhật chỉ có ở bảng Tại quầy, bảng Online VnExpress không ghi ngày' if ngay else None
    return {'bang': out, 'ngay': ngay, 'tieu_de': ghi_chu}


def doc_html(T, n):
    """Nguồn là trang web có bảng HTML (vd Topi): mỗi bảng có dòng đầu là kỳ hạn, cột đầu là tên ngân hàng.
    Bảng tại quầy / online nhận theo chữ ngay phía trên bảng. Ngày dữ liệu: mẫu Topi, không có thì ngày đầu tiên trong trang."""
    s = open(f'{T}{n["ma"]}.html', encoding='utf-8', errors='replace').read()
    t = chu(re.sub(r'<script.*?</script>|<style.*?</style>', '', s, flags=re.S))
    m = re.search(r'(\d{2}/\d{2}/\d{4})\s*Trang chủ\s*>\s*Blog', t) or re.search(r'(?<![\d/])(\d{1,2}/\d{1,2}/20\d{2})(?![\d/])', t)
    ngay = m.group(1) if m else None
    m = re.search(r'<title>(.*?)</title>', s, re.S)
    tieu_de = chu(m.group(1)) if m else None
    out = {'quay': None, 'online': None}
    for m in re.finditer(r'<table.*?</table>', s, re.S):
        truoc = chu(s[max(0, m.start() - 1500):m.start()])[-250:].lower()
        vt_q, vt_o = max(truoc.rfind('tại quầy'), truoc.rfind('quầy')), max(truoc.rfind('online'), truoc.rfind('trực tuyến'))
        if vt_q < 0 and vt_o < 0:
            continue
        key = 'online' if vt_o > vt_q else 'quay'
        if out[key] is not None:
            continue
        rows = [[chu(c) for c in re.findall(r'<t[dh].*?</t[dh]>', r, re.S)] for r in re.findall(r'<tr.*?</tr>', m.group(0), re.S)]
        if len(rows) < 3:
            continue
        cot = [re.sub(r'\D', '', c).lstrip('0') for c in rows[0]]
        if sum(c in THU_TU for c in cot) < 2:
            continue
        out[key] = {r[0]: {k: (r[cot.index(k)].replace(',', '.') if k in cot and cot.index(k) < len(r)
                               and so(r[cot.index(k)]) is not None else None) for k in THU_TU if k in cot}
                    for r in rows[1:] if r}
    return {'bang': out, 'ngay': ngay, 'tieu_de': tieu_de}


def doc_tep(n):
    """Nguồn nhập tay (AI tự đọc trang rồi ghi lại): {"ngay": "dd/mm/yyyy", "quay": {tên: {kỳ: số}}, "online": {...}}."""
    d = json.load(open(n['tep'], encoding='utf-8'))
    bang = {k: ({ten: {str(kk): (str(v).replace(',', '.') if v not in (None, '', '-') else None) for kk, v in r.items()}
                 for ten, r in d[k].items()} if d.get(k) else None) for k in ['quay', 'online']}
    return {'bang': bang, 'ngay': d.get('ngay'), 'tieu_de': d.get('ghi_chu')}


def doc_nguon(ch):
    T, tt = ch['_tam'], json.load(open(ch['_tam'] + 'trang-thai-nguon.json'))
    for n in ch['nguon']:
        if tt.get(n['ma']) != 'ok':
            n['du_lieu'] = {'bang': {'quay': None, 'online': None}, 'ngay': None, 'tieu_de': None, 'loi': tt.get(n['ma'])}
            continue
        n['du_lieu'] = doc_tep(n) if n.get('tep') and not n.get('tep_html') else doc_vne(T, n) if la_vne(n) else doc_html(T, n)
        # chỉ mục tên đã chuẩn hóa -> tên gốc trên nguồn
        n['chi_muc'] = {}
        for key, bg in n['du_lieu']['bang'].items():
            idx = {}
            for ten in (bg or {}):
                for k in bien_the(ten):
                    idx.setdefault(k, ten)
            n['chi_muc'][key] = idx
    return tt


def tim_dong(n, key, ten):
    """Dòng của ngân hàng `ten` (tên trong bài Techcombank) trên nguồn n, bảng key. Không có -> None."""
    bg = n['du_lieu']['bang'].get(key)
    if not bg:
        return None
    for t in [ten] + TEN_GHEP.get(ten, []):
        if t in bg:
            return bg[t]
    idx = n['chi_muc'].get(key, {})
    for t in [ten] + TEN_GHEP.get(ten, []):
        for k in bien_the(t):
            if k in idx:
                return bg[idx[k]]
    return None


# ======================= DỰNG FILE =======================
def kieu_so(moi, cu, hai_so_le):
    """Dòng đang ghi kiểu 2 chữ số thập phân (2.10, 5.90) -> số mới cũng 2 chữ số; còn lại ghi đúng như nguồn."""
    moi = moi.replace(',', '.')
    if hai_so_le and re.fullmatch(r'\d+\.\d+', cu.strip()) and moi != '-':
        return '%.2f' % float(moi)
    return moi


def dung(ch, hom_nay):
    tt = doc_nguon(ch)
    kq = {'hom_nay': hom_nay, 'nguon': [], 'loi_nguon': [], 'bai': {}}
    for n in ch['nguon']:
        d = n['du_lieu']
        kq['nguon'].append({'ten': n['ten'], 'url': n.get('url') or n.get('tep'), 'ky_han': n.get('ky_han'),
                            'ngay': d['ngay'], 'tieu_de': d['tieu_de']})
        if d.get('loi'):
            kq['loi_nguon'].append(f'{n["ten"]} ({n.get("url") or n.get("tep")})')
        else:
            for key in ['quay', 'online']:
                if d['bang'][key] is None:
                    print(f'Lưu ý: {n["ten"]} không có bảng {TEN_BANG[key]} (hoặc không nhận ra bảng).')
    for b in ch['bai']:
        if tt.get(b['ma']) != 'ok':
            kq['bai'][b['ma']] = {'loi': f'Chưa cập nhật được bài do không truy cập được Techcombank ({b["url"]})'}
            continue
        try:
            kq['bai'][b['ma']] = dung_bai(ch, b, hom_nay)
        except Exception as e:
            kq['bai'][b['ma']] = {'loi': f'Không đọc được cấu trúc bài {b["url"]} ({e}) – có thể không phải bài blog Techcombank.'}
    json.dump(kq, open(ch['_tam'] + 'ket-qua.json', 'w'), ensure_ascii=False, indent=1)
    for ma, r in kq['bai'].items():
        print(ma, r.get('loi') or f"{r['ten_file']}: {len(r['bang'])} bảng lãi suất {r['bang']}, {len(r['sua'])} ô sửa, "
                                    f"{len(r['gan_nhat'])} ô kỳ hạn gần nhất, {len(r['gach'])} ô '-', "
                                    f"{len(r['doi_mau'])} ô đổi màu, đổi ngày/tháng: {len(r['doi_ngay'])}")


def dung_bai(ch, cfg, hom_nay):
    T, ma, thang_nay = ch['_tam'], cfg['ma'], hom_nay[3:]
    src = open(f'{T}{ma}.html', encoding='utf-8').read()
    ghi = {'doi_mau': [], 'sua': [], 'gan_nhat': [], 'gan_nhat_trung': [], 'gach': [], 'can_duyet': [],
           'doi_ngay': [], 'bang': []}
    nguon = [n for n in ch['nguon'] if not n['du_lieu'].get('loi')]
    nguon_loi = [n for n in ch['nguon'] if n['du_lieu'].get('loi')]

    def to_vang(x):
        return f'<span style="{VANG}">{x}</span>'

    def sua_ngay(text, vi_tri):
        def d(m):
            if m.group(0) == hom_nay:
                return m.group(0)
            ghi['doi_ngay'].append(f'{vi_tri}: {m.group(0)} → {hom_nay}')
            return to_vang(hom_nay)
        text = re.sub(r'(?<![\d/])\d{2}/\d{2}/\d{4}(?![\d/])', d, text)

        def t(m):
            if m.group(2) == thang_nay:
                return m.group(0)
            ghi['doi_ngay'].append(f'{vi_tri}: tháng {m.group(2)} → tháng {thang_nay}')
            return m.group(1) + to_vang(thang_nay)
        return re.sub(r'(tháng\s*(?:<[^>]+>\s*)*)(\d{2}/\d{4})(?![\d/])', t, text)

    # ----- phần đầu bài -----
    h1 = html.unescape(re.search(r'<h1[^>]*>(.*?)</h1>', src, re.S).group(1)).strip()
    m = re.search(r'article-header-body--subTitle">(.*?)</p>', src, re.S)
    sapo = html.unescape(m.group(1)).strip() if m else ''
    iso = re.search(r'article-header-body--date">(\d{4})-(\d{2})-(\d{2})', src)
    ngay_dang = f'{iso.group(3)}/{iso.group(2)}/{iso.group(1)}' if iso else ''
    if not cfg.get('ten_file'):
        cfg['ten_file'] = re.sub(r'\s*\[[^\]]*\]|\s*\d{2}/\d{2}/\d{4}|\s+hôm nay\s*$', '', chu(h1)).strip(' -–|')
    # Docs không nhận nền xám của đoạn văn khi nhập HTML -> phần đầu bài đặt trong 1 ô bảng nền xám, không viền
    O = 'style="font-family:Arial;text-align:center;margin:0;font-size:11pt;font-weight:400;'
    head = ('<table style="border-collapse:collapse;width:100%"><tbody><tr>'
            '<td style="background-color:#f5f6f8;border:0pt solid #f5f6f8;padding:4pt">'
            f'<h1 {O}color:#000000;line-height:1.5"><span style="font-weight:400">{sua_ngay(h1, "Tiêu đề")}</span></h1>'
            + (f'<p {O}color:#8d8175;line-height:1.25">{sua_ngay(sapo, "Sapo")}</p>' if sapo else '')
            + (f'<p {O}color:#a2a2a2;font-style:italic;line-height:1.5">{sua_ngay(ngay_dang, "Ngày đăng")}</p>' if ngay_dang else '')
            + '</td></tr></tbody></table><p></p>').replace(VANG + '"', VANG + ';font-weight:400"')

    # ----- thân bài: các khối chữ, tới hết phần liên hệ (bỏ công cụ tính, nút bấm, quảng cáo) -----
    khoi = re.findall(r'<div id="text-[0-9a-f]+" class="cmp-text">\s*<html><head></head><body>(.*?)</body></html>', src, re.S)
    if not khoi:
        raise ValueError('không thấy khối nội dung "cmp-text"')
    # bài kết thúc ở khối thông tin liên hệ (email call_center / hotline); sau đó là khối quảng cáo của trang
    het = next((i for i, k in enumerate(khoi) if 'call_center' in k), None)
    if het is None:
        het = next((i for i, k in enumerate(khoi) if re.search(r'Hotline|1800\s*588\s*822', k)), len(khoi) - 1)
    body = '\n'.join(khoi[:het + 1])
    body = body.replace('="/content/', '="https://techcombank.com/content/').replace('href="/', 'href="https://techcombank.com/')
    body = re.sub(r'\s*\n\s*"', '"', body).replace('style="\t', 'style="')
    body = re.sub(r'<figure[^>]*>\s*(<img[^>]*>)(.*?)</figure>',
                  r'<p style="text-align:center">\1</p><p style="text-align:center">\2</p>', body, flags=re.S)
    body = body.replace('<img ', '<img style="width:100%;max-width:451pt" ')

    # ----- bảng lãi suất -----
    def loai_bang(m):
        tb = m.group(0)
        if not re.search(r'Ngân hàng\s*</b>', tb) or 'Techcombank' not in tb:
            return None
        truoc = chu(body[:m.start()])[-400:].lower()
        h = truoc.rfind('online'), truoc.rfind('tại quầy')
        return 'online' if h[0] > h[1] else 'quay'

    def loai_cot(tieu_de, mac_dinh):
        """Cột ghi rõ "tại quầy / phòng giao dịch" hay "online / trực tuyến" thì theo cột, không thì theo cả bảng."""
        h = tieu_de.lower()
        if any(x in h for x in ['quầy', 'phòng giao dịch', 'chi nhánh']):
            return 'quay'
        if any(x in h for x in ['online', 'trực tuyến']):
            return 'online'
        return mac_dinh

    def sua_bang(m):
        key_bang = loai_bang(m)
        if key_bang is None:
            return m.group(0)
        tb = m.group(0)
        hang = re.findall(r'<tr.*?</tr>', tb, re.S)
        dau = [chu(c) for c in re.findall(r'<td[^>]*>.*?</td>', hang[0], re.S)]
        nhom = {}                                  # loại bảng -> {kỳ hạn: vị trí cột}
        for i, t in enumerate(dau[1:], 1):
            k, key = re.sub(r'\D', '', t), loai_cot(t, key_bang)
            if k in THU_TU and key in cfg.get('bang', ['quay', 'online']):
                nhom.setdefault(key, {}).setdefault(k, i)
        if not nhom:
            return tb
        ghi['bang'].append(' + '.join(TEN_BANG[x] for x in nhom))
        for j, row in enumerate(hang[1:], 1):
            cells = re.findall(r'<td[^>]*>.*?</td>', row, re.S)
            ten = chu(cells[0]).replace(' (', '(').replace('(', ' (')
            if ten != 'Techcombank':
                for key, vt in nhom.items():
                    row = sua_dong(key, ten, vt, cells, row)
                hang[j] = row
        moi_tb = ghep_dong(tb, hang)
        # bảng có chú thích "Màu xanh … cao nhất, màu đỏ … thấp nhất" ngay bên dưới -> tô lại màu theo số mới
        if 'Màu xanh' in chu(body[m.end():m.end() + 3000]):
            moi_tb = to_lai_mau(key_bang, moi_tb)
        return moi_tb

    def mau_hien_tai(cell):
        """Màu chữ đang hiển thị của con số trong ô: 'xanh' / 'do' / 'thuong' (lấy màu của thẻ span trong cùng)."""
        so_txt = chu(cell)
        vi_tri = [x.start() for x in re.finditer(r'>\s*' + re.escape(so_txt) + r'\s*<', cell)]
        if not vi_tri:
            return None
        ngan = []
        for t in re.finditer(r'<(/?)(span|b|strong|p|td)\b([^>]*)>', cell[:vi_tri[0] + 1]):
            if t.group(2) != 'span':
                continue
            if t.group(1):
                if ngan:
                    ngan.pop()
            else:
                mm = re.search(r'color:\s*([^;"]+)', t.group(3).replace('background-color', 'bg'))
                ngan.append(mm.group(1).strip().replace(' ', '') if mm else None)
        mau = next((c for c in reversed(ngan) if c), None)
        return 'xanh' if mau in XANH else 'do' if mau in DO else 'thuong'

    def to_lai_mau(key, tb):
        hang = re.findall(r'<tr.*?</tr>', tb, re.S)
        cot = [re.sub(r'\D', '', chu(c)) for c in re.findall(r'<td[^>]*>.*?</td>', hang[0], re.S)]
        dong = []
        for j, row in enumerate(hang[1:], 1):
            cells = re.findall(r'<td[^>]*>.*?</td>', row, re.S)
            ten = chu(cells[0]).replace(' (', '(').replace('(', ' (')
            if ten != 'Techcombank':
                dong.append([j, ten, cells])
        for i, k in enumerate(cot):
            if k not in THU_TU:
                continue
            gia_tri = [so(chu(d[2][i])) for d in dong]
            co = [v for v in gia_tri if v is not None]
            if not co:
                continue
            cao, thap = max(co), min(co)
            for d, v in zip(dong, gia_tri):
                if v is None:
                    continue
                can = 'xanh' if v == cao else 'do' if v == thap else 'thuong'
                cell = d[2][i]
                dang = mau_hien_tai(cell)
                if dang is None or dang == can:
                    continue
                so_txt = chu(cell)
                vang = f'<span style="{VANG}">{so_txt}</span>'
                noi_dung = {'xanh': f'<b><span style="color: rgb(10,132,255);">{vang}</span></b>',
                            'do': f'<b><span style="color: rgb(237,28,36);">{vang}</span></b>', 'thuong': vang}[can]
                d[2][i] = re.match(r'<td[^>]*>', cell).group(0) + f'<p style="text-align: center;">{noi_dung}</p></td>'
                hang[d[0]] = thay_o(hang[d[0]], i, d[2][i])
                ghi['doi_mau'].append([TEN_BANG[key], d[1], k, so_txt, TEN_MAU[dang], TEN_MAU[can]])
        return ghep_dong(tb, hang)

    def sua_dong(key, ten, vt, cells, row):
        """Sửa các ô của một ngân hàng trong một loại bảng; vt = {kỳ hạn: vị trí cột}."""
        bang = TEN_BANG[key]
        ky_bai = [k for k in THU_TU if k in vt]
        hai_so_le = any(re.fullmatch(r'\d+\.\d0', chu(c)) for c in cells[1:])
        dong = {n['ma']: tim_dong(n, key, ten) for n in nguon}
        co_tren_web = any(v is not None for v in dong.values())
        moi = {}   # kỳ -> (chuỗi | 'giu', tên nguồn | 'A' | 'B', kỳ căn cứ)
        for k in ky_bai:
            phu_trach = [n for n in ch['nguon'] if not n.get('ky_han') or k in n['ky_han']]
            for n in phu_trach:
                if n['du_lieu'].get('loi') or n['du_lieu']['bang'].get(key) is None:
                    continue
                r = dong.get(n['ma'])
                if r and r.get(k):
                    moi[k] = (r[k], n['ten'], None)
                    break
            else:
                # nguồn phụ trách kỳ này bị lỗi và không nguồn nào khác có số -> giữ nguyên ô
                if any(n['du_lieu'].get('loi') or n['du_lieu']['bang'].get(key) is None for n in phu_trach) or not phu_trach:
                    moi[k] = ('giu', 'nguồn lỗi', None)
        for n in nguon:
            if dong[n['ma']] is None and n['du_lieu']['bang'].get(key) is not None and co_tren_web and n.get('ky_han'):
                ghi['can_duyet'].append(f'Bảng {bang} – {ten}: {n["ten"]} không có ngân hàng này ở bảng {bang.lower()} '
                                        f'→ kỳ hạn {", ".join(x for x in n["ky_han"] if x in ky_bai)} tháng lấy theo kỳ hạn gần nhất.')
        co = [(k, so(moi[k][0])) for k in ky_bai if k in moi and moi[k][0] != 'giu']
        for (k1, v1), (k2, v2) in zip(co, co[1:]):
            if v1 is not None and v2 is not None and v1 - v2 >= 0.8:
                ghi['can_duyet'].append(f'Bảng {bang} – {ten}: {k2} tháng ({v2:g}, {moi[k2][1]}) thấp hơn hẳn '
                                        f'{k1} tháng ({v1:g}, {moi[k1][1]}) – số bất thường trên nguồn, vẫn điền theo nguồn.')
        for k, v in co:
            if v is not None and v < 1:
                ghi['can_duyet'].append(f'Bảng {bang} – {ten} – {k} tháng: nguồn ghi {v:g}, thấp bất thường.')
        thieu = [k for k in ky_bai if k not in moi]
        if thieu and co_tren_web:                      # Trường hợp A: lấy theo kỳ hạn gần nhất (ưu tiên kỳ ngắn hơn)
            co_so = [k for k in ky_bai if k in moi and moi[k][0] != 'giu']
            for k in thieu:
                i = ky_bai.index(k)
                ngan = [x for x in reversed(ky_bai[:i]) if x in co_so]
                dai = [x for x in ky_bai[i + 1:] if x in co_so]
                can_cu = (ngan or dai or [None])[0]
                moi[k] = (moi[can_cu][0], 'A', can_cu) if can_cu else ('-', 'A', None)
        elif thieu and nguon_loi:
            for k in thieu:
                moi[k] = ('giu', 'nguồn lỗi', None)
            ghi['can_duyet'].append(f'Bảng {bang} – {ten}: không thấy trên nguồn còn truy cập được, có nguồn lỗi → giữ nguyên.')
        elif thieu:                                     # Trường hợp B: không nguồn nào có ngân hàng này -> "-"
            for k in thieu:
                moi[k] = ('-', 'B', None)
        for k in ky_bai:
            gia_tri, ng, can_cu = moi[k]
            if gia_tri == 'giu':
                continue
            cell = cells[vt[k]]
            cu = chu(cell)
            gt = kieu_so(gia_tri, cu, hai_so_le)
            if (so(cu) is not None and so(gt) is not None and so(cu) == so(gt)) or cu == gt:
                if ng == 'A':
                    ghi['gan_nhat_trung'].append([bang, ten, k, cu, can_cu])
                continue
            m = re.search(r'>(\s*)' + re.escape(cu) + r'(\s*)<', cell)
            if not m:
                ghi['can_duyet'].append(f'Bảng {bang} – {ten} – {k} tháng: không thay được số trong ô (ô ghi "{cu}"), giữ nguyên.')
                continue
            cell2 = cell[:m.start()] + '>' + m.group(1) + to_vang(gt) + m.group(2) + '<' + cell[m.end():]
            row = thay_o(row, vt[k], cell2)
            cells[vt[k]] = cell2
            if ng == 'A':
                ghi['gan_nhat'].append([bang, ten, k, cu, gt, can_cu])
            elif ng == 'B':
                ghi['gach'].append([bang, ten, k, cu])
            else:
                ghi['sua'].append([bang, ten, k, cu, gt, ng])
        return row

    body = re.sub(r'<table.*?</table>', sua_bang, body, flags=re.S)
    if not ghi['bang']:
        ghi['can_duyet'].append('Không tìm thấy bảng lãi suất nào (bảng có cột "Ngân hàng" và dòng Techcombank) trong bài.')

    # ----- kẻ bảng giống file mẫu: viền xám nhạt, cột tên ngân hàng 92.5pt, cột kỳ hạn 51.3pt -----
    TD = 'border:1px solid #ddd'

    def td_moi(tag, them=''):
        st = re.search(r'style="([^"]*)"', tag)
        return f'<td style="{TD}{them}{";" + st.group(1) if st else ""}">'

    def ke_bang(m):
        tb = m.group(0)
        if not re.search(r'Ngân hàng\s*</b>', tb):
            return re.sub(r'<td[^>]*>', lambda x: td_moi(x.group(0), ';padding:4pt'), tb)
        dau, con_lai = tb.split('</tr>', 1)
        i = [0]

        def o(x):
            i[0] += 1
            return td_moi(x.group(0), f';width:{92.5 if i[0] == 1 else 51.3}pt')
        return re.sub(r'<td[^>]*>', o, dau) + '</tr>' + re.sub(r'<td[^>]*>', lambda x: td_moi(x.group(0)), con_lai)
    body = re.sub(r'<table.*?</table>', ke_bang, body, flags=re.S)
    body = re.sub(r'<table[^>]*>', '<table style="border-collapse:collapse">', body)
    body = ''.join(p if p.startswith('<table') else sua_ngay(p, 'Đoạn văn')
                   for p in re.split(r'(<table.*?</table>)', body, flags=re.S))

    doc = ('<html><head><meta charset="utf-8"></head><body style="font-family:Arial;font-size:11pt">'
           + head + body + '</body></html>')
    open(f'{T}{ma}.full.html', 'w', encoding='utf-8').write(doc)
    # bản gọn để tải lên Drive
    g = re.sub(r'\s*\n\s*', ' ', doc).replace('&#61;', '=')
    g = re.sub(r'(</(?:p|td|tr|li|ul|table|h1|h2|h3|tbody)>) +(<)', r'\1\2', g)
    g = re.sub(r'(<(?:tr|td|tbody|ul|table)[^>]*>) +(<)', r'\1\2', g)
    g = re.sub(r' (?:class|id|rel|target)="[^"]*"', '', g).replace('style="text-align: center;"', 'align="center"')
    g = re.sub(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', lambda m: '#%02x%02x%02x' % tuple(int(x) for x in m.groups()), g)
    g = re.sub(r'style="([^"]*)"', lambda m: 'style="' + re.sub(r'\s*([:;])\s*', r'\1', m.group(1)).strip(' ;') + '"', g)
    open(f'{T}{ma}.min.html', 'w', encoding='utf-8').write(g)
    ghi['ten_file'] = f'{cfg["ten_file"]} – {hom_nay}'
    ghi['url'] = cfg['url']
    ghi['kich_thuoc'] = len(g)
    return ghi


# ======================= SOÁT =======================
def o_bang(h):
    out = []
    for tb in re.findall(r'<table.*?</table>', h, re.S):
        for tr in re.findall(r'<tr.*?</tr>', tb, re.S):
            out.append([(chu(td), VANG in td.replace(' ', '')) for td in re.findall(r'<td.*?</td>', tr, re.S)])
    return out


def soat(ch, ma, duong_dan):
    raw = open(duong_dan, encoding='utf-8').read()
    try:
        d = json.loads(raw)
        g = d['content']
        try:
            g = base64.b64decode(g, validate=True).decode('utf-8')
        except Exception:
            pass
    except (json.JSONDecodeError, KeyError, TypeError):
        g = raw                                   # đã là HTML thuần
    mau = open(f'{ch["_tam"]}{ma}.min.html', encoding='utf-8').read()
    G, M = o_bang(g), o_bang(mau)
    lech = [(i, a, b) for i, (a, b) in enumerate(zip(G, M)) if a != b]
    ngoai = lambda h: chu(re.sub(r'<table.*?</table>|<style.*?</style>', '', h, flags=re.S))
    ty_le = difflib.SequenceMatcher(None, ngoai(g), ngoai(mau)).ratio()
    print(f'Ảnh: {g.count("<img")}/{mau.count("<img")} | dòng bảng: {len(G)}/{len(M)} | dòng lệch: {len(lech)} | '
          f'ô vàng: {sum(y for r in G for _, y in r)}/{sum(y for r in M for _, y in r)} | chữ ngoài bảng giống: {ty_le:.2%}')
    for x in lech[:10]:
        print('  LỆCH', x)
    return not lech and len(G) == len(M) and ty_le > 0.999


# ======================= BÁO CÁO =======================
def bao_cao(ch, hom_nay, links, them):
    kq = json.load(open(ch['_tam'] + 'ket-qua.json', encoding='utf-8'))
    L = [f'# Báo cáo cập nhật lãi suất – {hom_nay}', '']
    for x in kq['loi_nguon']:
        L.append(f'> **Chưa cập nhật được từ {x} do không truy cập được.**')
    L += [f'> {x}' for x in them]
    h = list(map(int, hom_nay.split('/')))
    for so_bai, ((ma, b), link) in enumerate(zip(kq['bai'].items(), links + [''] * len(kq['bai'])), 1):
        L += ['', f'## BÀI {so_bai} – {b.get("url") or next(x["url"] for x in ch["bai"] if x["ma"] == ma)}', '']
        if 'loi' in b:
            L += [b['loi'], '']
            continue
        k = lambda x: f'{x} tháng'
        lk = f'[{b["ten_file"]}]({link})' if link else b['ten_file']
        if not (b['sua'] or b['gan_nhat'] or b['gach'] or b['doi_mau']):
            L += [f'**Link file:** {lk}', '', '**Không có thay đổi lãi suất.**', '']
            continue
        L += [f'**1. Link file:** {lk}', '', '**2. Ngày tháng đã đổi:**', '']
        L += [f'- {x}' for x in b['doi_ngay']] or ['- Ngày, tháng trong bài đã đúng, không đổi.']
        L += ['', '**3. Ngày dữ liệu nguồn:**', '']
        for n in kq['nguon']:
            pt = f' (kỳ hạn {", ".join(n["ky_han"])} tháng)' if n['ky_han'] else ''
            td = f' – "{n["tieu_de"]}"' if n['tieu_de'] else ''
            L.append(f'- {n["ten"]}{pt}: {n["ngay"] or "không đọc được ngày"}{td}')
        L += ['', f'**4. Ô đã sửa theo nguồn ({len(b["sua"])} ô):**', '']
        L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} → {c[4]} (nguồn: {c[5]})' for c in b['sua']] or ['- Không có.']
        L += ['', f'**4b. Ô đổi màu cao nhất / thấp nhất ({len(b["doi_mau"])} ô, đều tô vàng):**', '']
        L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} — {c[4]} → {c[5]}' for c in b['doi_mau']] or ['- Không có.']
        L += ['', f'**5. Ô lấy theo kỳ hạn gần nhất – Trường hợp A ({len(b["gan_nhat"])} ô):**', '']
        L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} → {c[4]} (lấy theo kỳ hạn {c[5]} tháng)' for c in b['gan_nhat']] or ['- Không có.']
        if b['gan_nhat_trung']:
            L += ['', 'Ô cũng lấy theo kỳ hạn gần nhất nhưng ra đúng số cũ (không sửa, không tô):', '']
            L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} (theo kỳ hạn {c[4]} tháng)' for c in b['gan_nhat_trung']]
        L += ['', f'**6. Ô điền "-" do không nguồn nào có ngân hàng này – Trường hợp B ({len(b["gach"])} ô):**', '']
        L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} → -' for c in b['gach']] or ['- Không có.']
        L += ['', '**7. Trường hợp cần người duyệt kiểm tra:**', '']
        cu = []
        for n in kq['nguon']:
            if n['ngay'] and re.fullmatch(r'\d{1,2}/\d{1,2}/\d{4}', n['ngay']):
                d, m, y = map(int, n['ngay'].split('/'))
                tre = (date(h[2], h[1], h[0]) - date(y, m, d)).days
                if tre > 3:
                    cu.append(f'Dữ liệu {n["ten"]}{" (bảng Tại quầy)" if n["ten"] == "VnExpress" else ""} cũ {tre} ngày (cập nhật đến {n["ngay"]}); số có thể đã đổi mà nguồn chưa cập nhật.')
        manh = [f'Bảng {c[0]} – {c[1]} – {c[2]} tháng: đổi mạnh {c[3]} → {c[4]} (nguồn {c[5]}).' for c in b['sua']
                if so(c[3]) is not None and so(c[4]) is not None and abs(so(c[4]) - so(c[3])) >= 0.8]
        L += [f'- {x}' for x in cu + b['can_duyet'] + manh] or ['- Không có.']
        L += ['', f'**8.** Có thay đổi: {len(b["sua"]) + len(b["gan_nhat"]) + len(b["gach"])} ô lãi suất, {len(b["doi_mau"])} ô đổi màu.']
    thu_muc = os.path.join(os.path.dirname(ch['_tam'].rstrip('/')), 'bao-cao')
    os.makedirs(thu_muc, exist_ok=True)
    p = os.path.join(thu_muc, f'{hom_nay[6:]}-{hom_nay[3:5]}-{hom_nay[:2]}.md')
    open(p, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    print(f'\n(Đã lưu: {p})')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    lenh, ch = sys.argv[1], doc_cau_hinh(sys.argv[2])
    if lenh == 'lay':
        lay(ch)
    elif lenh == 'dung':
        dung(ch, sys.argv[3])
    elif lenh == 'soat':
        sys.exit(0 if soat(ch, sys.argv[3], sys.argv[4]) else 1)
    elif lenh == 'bao-cao':
        a = sys.argv[4:]
        them = a[a.index('--ghi-chu') + 1:] if '--ghi-chu' in a else []
        links = a[:a.index('--ghi-chu')] if '--ghi-chu' in a else a
        bao_cao(ch, sys.argv[3], links, them)
    else:
        sys.exit(__doc__)

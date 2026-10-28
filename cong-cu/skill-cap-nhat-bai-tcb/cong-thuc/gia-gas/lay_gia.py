"""Lấy giá gas bán lẻ mới nhất cho bài TCB "Giá gas hôm nay" -> gia.json (đầu vào của tao_sua.py).

  python3 -I lay_gia.py <file-ra.json>        (chỉ dùng thư viện có sẵn của Python, không cần cài gì)

Nguồn (Trang chọn):
- pgas      https://pgas.com.vn/                       – Tổng công ty Gas Petrolimex, bảng "GIÁ GAS THÁNG mm/yyyy"
                                                         (Hà Nội, Hải Phòng, Đà Nẵng, Hồ Chí Minh, Cần Thơ; bình 12 kg, 48 kg)
- saigon    https://saigonpetro.com.vn/ban-le-gas      – Saigon Petro: dòng chạy chữ "Giá bán lẻ gas" (chai 12 kg, 45 kg)
                                                         + ô chọn "Thời gian: Ngày dd.mm.yyyy"
- pvgas     https://pvgaslpg.com.vn/vi/gas-price/      – PV GAS LPG: bảng "GIÁ BÁN LẺ GAS THÁNG mm/yyyy" theo tỉnh (bình 12 kg, 45 kg)
- gaspetrolimex https://gaspetrolimex.vn/              – trang đại lý: chỉ ghi lại để đối chiếu, KHÔNG dùng sửa bài (xem README)

Mỗi nguồn: giá (đ/bình, đúng số trên trang), tháng/ngày hiệu lực trên trang, chữ gốc trên trang, url.
Nguồn lỗi → null và in "<nguồn> KHÔNG ĐỌC ĐƯỢC". Thoát mã 1 nếu có nguồn dùng sửa bài bị lỗi (chay.sh vẫn chạy tiếp).

Riêng pvgaslpg.com.vn: máy chủ gửi thiếu chứng chỉ trung gian (lỗi "unable to get local issuer certificate").
Trình duyệt tự tải chứng chỉ trung gian theo địa chỉ ghi trong chứng chỉ của trang (AIA); ở đây làm y như vậy:
thử bình thường trước, lỗi đúng kiểu đó thì tải chứng chỉ trung gian Sectigo từ địa chỉ AIA rồi kết nối lại –
VẪN KIỂM TRA CHỨNG CHỈ ĐẦY ĐỦ tới chứng chỉ gốc có sẵn trong máy (tắt chế độ "chuỗi dở dang"), không tắt kiểm tra.
"""
import html, json, re, ssl, sys, unicodedata, urllib.request
from html.parser import HTMLParser

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36'
PGAS = 'https://pgas.com.vn/'
SAIGON = 'https://saigonpetro.com.vn/ban-le-gas'
PVGAS = 'https://pvgaslpg.com.vn/vi/gas-price/'
GPLX = 'https://gaspetrolimex.vn/'
# địa chỉ "CA Issuers" ghi trong chứng chỉ của pvgaslpg.com.vn (chứng chỉ trung gian công khai của Sectigo)
AIA = {'pvgaslpg.com.vn': 'http://crt.sectigo.com/SectigoPublicServerAuthenticationCADVR36.crt'}


def nfc(s):
    return unicodedata.normalize('NFC', s)


def chu(x):
    return nfc(re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip())


def so(x):
    d = re.sub(r'\D', '', x or '')
    return int(d) if d else None


def _mo(url, ctx=None):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'vi,en;q=0.8'})
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        return r.read().decode('utf-8', 'replace')


def tai(url):
    try:
        return _mo(url)
    except urllib.error.URLError as e:
        host = urllib.request.urlparse(url).hostname
        if not (isinstance(e.reason, ssl.SSLCertVerificationError) and 'local issuer' in str(e.reason) and host in AIA):
            raise
    # máy chủ thiếu chứng chỉ trung gian → bổ sung theo AIA (như trình duyệt), vẫn kiểm tra tới chứng chỉ gốc
    with urllib.request.urlopen(urllib.request.Request(AIA[host], headers={'User-Agent': UA}), timeout=60) as r:
        der = r.read()
    ctx = ssl.create_default_context()
    ctx.load_verify_locations(cadata=der)
    ctx.verify_flags &= ~getattr(ssl, 'VERIFY_X509_PARTIAL_CHAIN', 0)
    print(f'  ({host}: máy chủ thiếu chứng chỉ trung gian – đã bổ sung từ {AIA[host]}, vẫn kiểm tra đầy đủ)')
    return _mo(url, ctx)


class Bang(HTMLParser):
    """Gom mọi <table> thành danh sách dòng, mỗi dòng là danh sách chữ trong ô; kèm chữ đứng ngay trước bảng."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bang, self.cur, self.row, self.cell, self.truoc = [], None, None, None, []

    def handle_starttag(self, tag, a):
        if tag == 'table':
            self.cur = {'truoc': ' '.join(self.truoc[-40:]), 'dong': []}
        elif tag == 'tr' and self.cur is not None:
            self.row = []
        elif tag in ('td', 'th') and self.row is not None:
            self.cell = []

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None and self.row is not None:
            self.row.append(nfc(re.sub(r'\s+', ' ', ''.join(self.cell)).strip()))
            self.cell = None
        elif tag == 'tr' and self.row is not None and self.cur is not None:
            if self.row:
                self.cur['dong'].append(self.row)
            self.row = None
        elif tag == 'table' and self.cur is not None:
            self.bang.append(self.cur)
            self.cur = None

    def handle_data(self, d):
        if self.cell is not None:
            self.cell.append(d)
        elif d.strip():
            self.truoc.append(d.strip())


def bang_cua(h):
    p = Bang()
    p.feed(h)
    return p.bang


def cot_kg(dau):
    """dòng tiêu đề → {chỉ số cột: số kg}"""
    return {i: int(m.group(1)) for i, c in enumerate(dau) for m in [re.search(r'(\d+)\s*kg', c, re.I)] if m}


def ten_noi(s):
    s = nfc(s).strip()
    s = re.sub(r'^(TP\.?|Thành phố)\s*', '', s, flags=re.I)
    return s.lower()


def doc_bang_tinh(bang, can_tieu_de):
    """bảng có dòng tiêu đề chứa 'kg' → {tên nơi (chữ thường): {'ten': ..., 'gia': {kg: đ}, 'hieu_luc': ...}}"""
    for b in bang:
        if not re.search(can_tieu_de, nfc(b['truoc'][-200:]), re.I):
            continue
        dong = b['dong']
        if not dong:
            continue
        cot = cot_kg(dong[0])
        if not cot:
            continue
        hl = next((i for i, c in enumerate(dong[0]) if 'hiệu lực' in c.lower()), None)
        kq = {}
        for r in dong[1:]:
            if len(r) < len(dong[0]) or not r[0]:
                continue
            gia = {kg: so(r[i]) for i, kg in cot.items() if so(r[i])}
            if gia:
                kq[ten_noi(r[0])] = {'ten': r[0], 'gia': gia, 'chu_goc': ' | '.join(r),
                                     **({'hieu_luc': r[hl]} if hl is not None else {})}
        if kq:
            return kq
    return None


def lay_pgas():
    h = tai(PGAS)
    m = re.search(r'GIÁ GAS THÁNG\s*(\d{1,2})/(\d{4})', chu(h), re.I)
    tinh = doc_bang_tinh(bang_cua(h), r'GIÁ GAS THÁNG\s*\d{1,2}/\d{4}\s*$')
    if not (m and tinh):
        raise RuntimeError('không thấy bảng "GIÁ GAS THÁNG mm/yyyy"')
    return {'thang': [int(m.group(1)), int(m.group(2))], 'tieu_de': m.group(0), 'tinh': tinh, 'nguon': PGAS}


def lay_saigon():
    h = tai(SAIGON)
    gia, goc = {}, {}
    for ten, gt in re.findall(r'<span>\s*(Chai gas[^<]*?)\s*</span>\s*<span>\s*([\d.,]+\s*đ)\s*</span>', h, re.I):
        m = re.search(r'(\d+)\s*kg', ten, re.I)
        if m and int(m.group(1)) not in gia:
            gia[int(m.group(1))] = so(gt)
            goc[int(m.group(1))] = f'{chu(ten)}: {chu(gt)}'
    d = re.search(r'<option[^>]*selected[^>]*>\s*Ngày\s*(\d{1,2})\.(\d{1,2})\.(\d{4})', h)
    if not gia or not d:
        raise RuntimeError('không thấy "Giá bán lẻ gas" hoặc ngày hiệu lực')
    return {'gia': gia, 'chu_goc': goc, 'ngay': f'{int(d.group(1)):02d}/{int(d.group(2)):02d}/{d.group(3)}',
            'thang': [int(d.group(2)), int(d.group(3))], 'nguon': SAIGON}


def lay_pvgas():
    h = tai(PVGAS)
    m = re.search(r'GIÁ BÁN LẺ GAS THÁNG\s*(\d{1,2})/(\d{4})', chu(h), re.I)
    tinh = doc_bang_tinh(bang_cua(h), r'GIÁ BÁN LẺ GAS THÁNG\s*\d{1,2}/\d{4}\s*$')
    if not (m and tinh):
        raise RuntimeError('không thấy bảng "GIÁ BÁN LẺ GAS THÁNG mm/yyyy"')
    return {'thang': [int(m.group(1)), int(m.group(2))], 'tieu_de': m.group(0), 'tinh': tinh, 'nguon': PVGAS}


def lay_gplx():
    h = tai(GPLX)
    sp = re.findall(r'class="entry-title"><a[^>]*>([^<]+)</a></h2></li>\s*<li>\s*Giá:\s*([\d.]+)\s*VNĐ', h)
    if not sp:
        raise RuntimeError('không thấy giá sản phẩm')
    return {'san_pham': [[chu(t), so(g)] for t, g in sp], 'nguon': GPLX, 'khong_dung': 'trang đại lý, chỉ để đối chiếu'}


def main():
    ra = sys.argv[1] if len(sys.argv) > 1 else 'gia.json'
    kq, loi = {}, False
    for ma, ham, dung in (('pgas', lay_pgas, True), ('saigon', lay_saigon, True), ('pvgas', lay_pvgas, True),
                          ('gaspetrolimex', lay_gplx, False)):
        try:
            kq[ma] = ham()
        except Exception as e:
            kq[ma] = None
            loi = loi or dung
            print(f'{ma} KHÔNG ĐỌC ĐƯỢC ({str(e)[:160]})')
    json.dump(kq, open(ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda v: f'{v:,}'.replace(',', '.')
    for ma in ('pgas', 'pvgas'):
        v = kq[ma]
        if v:
            ds = [x for k, x in v['tinh'].items() if ma == 'pgas' or k in ('hà nội', 'hồ chí minh')]
            print(f'{ma}: {v["tieu_de"]} ({len(v["tinh"])} tỉnh/thành) – ' + '; '.join(
                f'{x["ten"]} ' + '/'.join(f'{k}kg {f(g)}' for k, g in x['gia'].items()) for x in ds))
    if kq['saigon']:
        print(f'saigon: từ {kq["saigon"]["ngay"]} – ' + '; '.join(kq['saigon']['chu_goc'].values()))
    if kq['gaspetrolimex']:
        print('gaspetrolimex (đối chiếu, không dùng): ' + '; '.join(f'{t} {f(g)}' for t, g in kq['gaspetrolimex']['san_pham'][:3]))
    print('→', ra)
    sys.exit(1 if loi else 0)


if __name__ == '__main__':
    main()

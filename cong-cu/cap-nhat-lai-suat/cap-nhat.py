#!/usr/bin/env python3
"""Cập nhật lãi suất hằng ngày cho 2 bài blog Techcombank (quy trình bản 3 – xem QUY-TRINH.md).

  python3 cap-nhat.py lay                      tải 2 bài Techcombank + VnExpress + Topi vào tam/
  python3 cap-nhat.py dung dd/mm/yyyy          dựng tam/bai1.min.html, tam/bai2.min.html (đã tô vàng) + tam/ket-qua.json
  python3 cap-nhat.py soat bai1 <export.json>  so file Google Docs (bản xuất HTML) với bản dựng
  python3 cap-nhat.py bao-cao dd/mm/yyyy <link bài 1> <link bài 2> ["ghi chú thêm" ...]
"""
import difflib, html, json, os, re, subprocess, sys, time

TAM = 'tam/'
BAI = {
    'bai1': {'url': 'https://techcombank.com/thong-tin/blog/lai-suat-tiet-kiem',
             'ten_file': 'Lãi suất tiết kiệm Techcombank', 'bang': ['quay', 'online']},
    'bai2': {'url': 'https://techcombank.com/thong-tin/blog/cach-tinh-lai-suat-tien-gui-tiet-kiem',
             'ten_file': 'Cách tính lãi suất tiền gửi tiết kiệm Techcombank', 'bang': ['online']},
}
VNE_URL = 'https://gw.vnexpress.net/th?types='          # API mà trang vnexpress.net/chu-de/lai-suat-ngan-hang-3210 dùng
TOPI_URL = 'https://topi.vn/lai-suat-tiet-kiem-ngan-hang-nao-cao-nhat.html'
KY_VNE = ['1', '3', '6', '9', '12']
KY_TOPI = ['18', '24', '36']
THU_TU = ['1', '3', '6', '9', '12', '18', '24', '36']
TEN_BANG = {'quay': 'Tại quầy', 'online': 'Online'}
# tên trong bài Techcombank -> (tên VnExpress, tên Topi); chỉ ghép những cặp chắc chắn
TEN = {
    'MBBank': ('MB', 'MB Bank'), 'PVcomBank': ('PVCombank', 'PVcomBank'), 'BAOVIET Bank': ('BaoVietBank', 'Bảo Việt'),
    'Viet Capital Bank (BVBANK)': ('BVBank', 'BVBank'), 'PG Bank': ('PGBank', 'PGBank'), 'BacABank': ('BacABank', 'Bắc Á'),
    'VCB Neo (CBBank)': ('VCBNeo', 'VCBNeo (CBBank)'), 'CBBank': ('VCBNeo', 'VCBNeo (CBBank)'),
    'OceanBank': ('MBV', 'MBV (OceanBank)'), 'Kienlongbank': ('Kienlongbank', 'Kiên Long'), 'VietBank': ('VietBank', 'Vietbank'),
    'NamABank': ('NamABank', 'Nam Á Bank'), 'Vikki Bank': ('Vikki Bank', 'Vikkibank (Đông Á)'),
}
VANG = 'background-color:#ffff00'
XANH = {'rgb(10,132,255)', 'rgb(66,133,244)', '#0a84ff', '#4285f4'}
DO = {'rgb(237,28,36)', 'rgb(255,0,0)', '#ed1c24', '#ff0000'}
TEN_MAU = {'xanh': 'xanh (cao nhất)', 'do': 'đỏ (thấp nhất)', 'thuong': 'chữ thường'}


def thay_o(row, i, o_moi):
    """Thay ô thứ i (tính cả cột tên) trong một dòng bảng, theo vị trí — không theo nội dung, vì nhiều ô giống hệt nhau."""
    phan = re.split(r'(<td[^>]*>.*?</td>)', row, flags=re.S)
    vt = [j for j, x in enumerate(phan) if x.startswith('<td')]
    phan[vt[i]] = o_moi
    return ''.join(phan)


def chu(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).replace('\xa0', ' ').strip()


def so(x):
    try:
        return float(str(x).strip().replace(',', '.'))
    except ValueError:
        return None


# ======================= LẤY NGUỒN =======================
def lay():
    os.makedirs(TAM, exist_ok=True)
    trang_thai = {}
    viec = [(f'{k}.html', v['url']) for k, v in BAI.items()] + [('topi.html', TOPI_URL)] + \
           [(f'vne-{t}.json', VNE_URL + 'bank_rate_' + t) for t in ['offline', 'online']]
    for f, u in viec:
      for lan in range(5):                  # Techcombank hay ngắt kết nối giữa chừng -> thử lại tối đa 5 lần
        r = subprocess.run(['curl', '-sS', '-L', '-m', '60', '--retry', '3', '-A', 'Mozilla/5.0',
                            '-o', TAM + f, '-w', '%{http_code}', u], capture_output=True, text=True)
        ok = r.returncode == 0 and r.stdout.strip() == '200' and os.path.getsize(TAM + f) > 1000
        trang_thai[f] = 'ok' if ok else f'lỗi ({r.stdout.strip()} {r.stderr.strip()[:80]})'
        if ok or '403' in r.stderr:           # 403 = bị tường lửa môi trường chặn, thử lại vô ích
            break
        time.sleep(3 * (lan + 1))
      print(f, trang_thai[f])
    json.dump(trang_thai, open(TAM + 'trang-thai-nguon.json', 'w'), ensure_ascii=False, indent=1)


def doc_vne():
    """{'quay'|'online': {tên: {kỳ: chuỗi hiển thị}}}, ngày cập nhật. Thiếu bảng nào thì bảng đó = None."""
    out, ngay = {}, None
    for key, t in [('quay', 'offline'), ('online', 'online')]:
        try:
            ds = json.load(open(f'{TAM}vne-{t}.json'))['data']['bank_rate_' + t]
            assert len(ds) > 10
        except Exception:
            out[key] = None
            continue
        bang = {}
        for r in ds:
            bang[r['bank'].strip()] = {k: hien_vne(r.get('rate_' + k)) for k in KY_VNE}
            if r.get('update') and not ngay:
                m, d, y = r['update'].split('/')
                ngay = f'{int(d):02d}/{int(m):02d}/{y}'
        out[key] = bang
    return out, ngay


def hien_vne(v):
    """Số như VnExpress hiển thị: tối thiểu 1 chữ số thập phân (7 -> 7.0, 4.75 -> 4.75). Không có số -> None."""
    f = so(v) if v not in (None, '', '-') else None
    if not f:
        return None
    s = ('%.4f' % f).rstrip('0')
    return s + '0' if s.endswith('.') else s


def doc_topi():
    try:
        s = open(TAM + 'topi.html', encoding='utf-8').read()
    except FileNotFoundError:
        return {'quay': None, 'online': None}, None, None
    t = chu(re.sub(r'<script.*?</script>|<style.*?</style>', '', s, flags=re.S))
    m = re.search(r'(\d{2}/\d{2}/\d{4})\s*Trang chủ\s*>\s*Blog', t)
    ngay = m.group(1) if m else None
    m = re.search(r'Ngân hàng và lãi suất (.{0,120}?\d{1,2}/\d{4})', t)
    tieu_de = m.group(1) if m else None
    out = {'quay': None, 'online': None}
    for m in re.finditer(r'<table.*?</table>', s, re.S):
        truoc = chu(s[max(0, m.start() - 800):m.start()])[-200:].lower()
        key = 'quay' if 'tại quầy' in truoc else 'online' if 'gửi online' in truoc else None
        if not key or out[key] is not None:
            continue
        rows = [[chu(c) for c in re.findall(r'<t[dh].*?</t[dh]>', r, re.S)] for r in re.findall(r'<tr.*?</tr>', m.group(0), re.S)]
        cot = [re.sub(r'\D', '', c).lstrip('0') or c for c in rows[0]]
        out[key] = {r[0]: {k: (r[cot.index(k)] if k in cot and r[cot.index(k)] not in ('', '-') else None)
                           for k in KY_TOPI} for r in rows[1:]}
    return out, ngay, tieu_de


# ======================= DỰNG FILE =======================
def kieu_so(moi, cu, hai_so_le):
    """Giữ kiểu ghi số của ô cũ: dòng đang ghi kiểu 2 chữ số thập phân (2.10, 5.90) -> số mới cũng 2 chữ số;
    còn lại ghi đúng như nguồn. Ô như 4.75 tự nhiên có 2 chữ số nên không tính là "kiểu 2 chữ số"."""
    moi = moi.replace(',', '.')
    if hai_so_le and re.fullmatch(r'\d+\.\d+', cu.strip()) and moi != '-':
        return '%.2f' % float(moi)
    return moi


def dung(hom_nay):
    tt = json.load(open(TAM + 'trang-thai-nguon.json'))
    vne, ngay_vne = doc_vne()
    topi, ngay_topi, tieu_de_topi = doc_topi()
    kq = {'hom_nay': hom_nay, 'nguon': {'vne_ngay': ngay_vne, 'topi_ngay': ngay_topi, 'topi_tieu_de': tieu_de_topi},
          'loi_nguon': [], 'bai': {}}
    for key in ['quay', 'online']:
        if vne[key] is None:
            kq['loi_nguon'].append(f'VnExpress (bảng {TEN_BANG[key]})')
        if topi[key] is None:
            kq['loi_nguon'].append(f'Topi (bảng {TEN_BANG[key]})')
    for ma, cfg in BAI.items():
        if tt.get(f'{ma}.html') != 'ok':
            kq['bai'][ma] = {'loi': f'Chưa cập nhật được bài do không truy cập được Techcombank ({cfg["url"]})'}
            continue
        kq['bai'][ma] = dung_bai(ma, cfg, hom_nay, vne, topi)
    json.dump(kq, open(TAM + 'ket-qua.json', 'w'), ensure_ascii=False, indent=1)
    for ma, b in kq['bai'].items():
        print(ma, b.get('loi') or f"{len(b['sua'])} ô sửa, {len(b['gan_nhat'])} ô theo kỳ hạn gần nhất, "
                                    f"{len(b['chinh_thuc'])} ô trường hợp B, đổi ngày/tháng: {b['doi_ngay']}")


def dung_bai(ma, cfg, hom_nay, vne, topi):
    thang_nay = hom_nay[3:]
    src = open(f'{TAM}{ma}.html', encoding='utf-8').read()
    ghi = {'doi_mau': [], 'sua': [], 'gan_nhat': [], 'gan_nhat_trung': [], 'chinh_thuc': [], 'gach': [], 'can_duyet': [], 'doi_ngay': []}

    def to_vang(x, dam=None):
        return f'<span style="{VANG}{";font-weight:400" if dam is False else ""}">{x}</span>'

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
    sapo = html.unescape(re.search(r'article-header-body--subTitle">(.*?)</p>', src, re.S).group(1)).strip()
    iso = re.search(r'article-header-body--date">(\d{4})-(\d{2})-(\d{2})', src)
    ngay_dang = f'{iso.group(3)}/{iso.group(2)}/{iso.group(1)}'
    # Docs không nhận nền xám của đoạn văn khi nhập HTML -> đặt phần đầu bài trong 1 ô bảng nền xám, không viền
    O = 'style="font-family:Arial;text-align:center;margin:0;font-size:11pt;font-weight:400;'
    head = ('<table style="border-collapse:collapse;width:100%"><tbody><tr>'
            '<td style="background-color:#f5f6f8;border:0pt solid #f5f6f8;padding:4pt">'
            f'<h1 {O}color:#000000;line-height:1.5"><span style="font-weight:400">{sua_ngay(h1, "Tiêu đề")}</span></h1>'
            f'<p {O}color:#8d8175;line-height:1.25">{sua_ngay(sapo, "Sapo")}</p>'
            f'<p {O}color:#a2a2a2;font-style:italic;line-height:1.5">{sua_ngay(ngay_dang, "Ngày đăng")}</p>'
            '</td></tr></tbody></table><p></p>').replace(VANG + '"', VANG + ';font-weight:400"')

    # ----- thân bài: các khối chữ của bài, tới hết phần liên hệ (bỏ công cụ tính, nút bấm, khối quảng cáo) -----
    khoi = re.findall(r'<div id="text-[0-9a-f]+" class="cmp-text">\s*<html><head></head><body>(.*?)</body></html>', src, re.S)
    khoi = khoi[:next(i for i, k in enumerate(khoi) if 'call_center' in k) + 1]
    body = '\n'.join(khoi)
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

    def sua_bang(m):
        key = loai_bang(m)
        if key not in cfg['bang']:
            return m.group(0)
        tb = m.group(0)
        hang = re.findall(r'<tr.*?</tr>', tb, re.S)
        cot = [re.sub(r'\D', '', chu(c)) for c in re.findall(r'<td[^>]*>.*?</td>', hang[0], re.S)]
        for j, row in enumerate(hang[1:], 1):
            cells = re.findall(r'<td[^>]*>.*?</td>', row, re.S)
            ten = chu(cells[0]).replace(' (', '(').replace('(', ' (')
            if ten != 'Techcombank':
                hang[j] = sua_dong(key, ten, cot, cells, row)
        phan = re.split(r'(<tr.*?</tr>)', tb, flags=re.S)
        vt = [j for j, x in enumerate(phan) if x.startswith('<tr')]
        for j, h in zip(vt, hang):
            phan[j] = h
        moi_tb = ''.join(phan)
        # bảng có chú thích "Màu xanh … cao nhất, màu đỏ … thấp nhất" ngay bên dưới -> tô lại màu theo số mới
        if 'Màu xanh' in chu(body[m.end():m.end() + 3000]):
            moi_tb = to_lai_mau(key, moi_tb)
        return moi_tb

    def mau_hien_tai(cell):
        """Màu chữ đang hiển thị của con số trong ô: 'xanh' / 'do' / 'thuong'."""
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
        if mau in XANH:
            return 'xanh'
        if mau in DO:
            return 'do'
        return 'thuong'

    def to_lai_mau(key, tb):
        hang = re.findall(r'<tr.*?</tr>', tb, re.S)
        cot = [re.sub(r'\D', '', chu(c)) for c in re.findall(r'<td[^>]*>.*?</td>', hang[0], re.S)]
        dong = []          # [chỉ số dòng trong bảng, tên, danh sách ô]
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
        # ghép lại bảng theo vị trí từng dòng
        phan = re.split(r'(<tr.*?</tr>)', tb, flags=re.S)
        vt = [j for j, x in enumerate(phan) if x.startswith('<tr')]
        for j, h in zip(vt, hang):
            phan[j] = h
        return ''.join(phan)

    def sua_dong(key, ten, cot, cells, row):
        tv, tt = TEN.get(ten, (ten, ten))
        rv = vne[key].get(tv) if vne[key] is not None else None
        rt = topi[key].get(tt) if topi[key] is not None else None
        bang = TEN_BANG[key]
        co_tren_web = rv is not None or rt is not None
        nguon_loi = vne[key] is None or topi[key] is None
        ky_bai = [k for k in THU_TU if k in cot]
        hai_so_le = any(re.fullmatch(r'\d+\.\d0', chu(c)) for c in cells[1:])
        moi = {}   # kỳ -> (chuỗi, nguồn, căn cứ)
        for k in ky_bai:
            if k in KY_VNE:
                if vne[key] is None:
                    moi[k] = ('giu', 'VnExpress lỗi', None)
                elif rv and rv.get(k):
                    moi[k] = (rv[k], 'VnExpress', None)
            else:
                if topi[key] is None:
                    moi[k] = ('giu', 'Topi lỗi', None)
                elif rt and rt.get(k):
                    moi[k] = (rt[k].replace(',', '.'), 'Topi', None)
        thieu = [k for k in ky_bai if k not in moi]
        if rt is None and topi[key] is not None and rv is not None:
            ghi['can_duyet'].append(f'Bảng {bang} – {ten}: Topi không có ngân hàng này ở bảng {bang.lower()} '
                                    f'→ kỳ hạn {", ".join(KY_TOPI)} tháng lấy theo kỳ hạn gần nhất.')
        if rv is None and vne[key] is not None and rt is not None:
            ghi['can_duyet'].append(f'Bảng {bang} – {ten}: VnExpress không có ngân hàng này ở tab {bang} '
                                    f'→ kỳ hạn ngắn lấy theo kỳ hạn gần nhất.')
        # số bất thường: kỳ hạn dài thấp hơn hẳn kỳ hạn ngắn liền trước (≥ 0,8 điểm) hoặc dưới 1%/năm
        co = [(k, so(moi[k][0])) for k in ky_bai if k in moi and moi[k][0] != 'giu']
        for (k1, v1), (k2, v2) in zip(co, co[1:]):
            if v1 is not None and v2 is not None and v1 - v2 >= 0.8:
                ghi['can_duyet'].append(f'Bảng {bang} – {ten}: {k2} tháng ({v2:g}, {moi[k2][1]}) thấp hơn hẳn '
                                        f'{k1} tháng ({v1:g}, {moi[k1][1]}) – số bất thường trên nguồn, vẫn điền theo nguồn.')
        for k, v in co:
            if v is not None and v < 1:
                ghi['can_duyet'].append(f'Bảng {bang} – {ten} – {k} tháng: nguồn ghi {v:g}, thấp bất thường.')
        if thieu and co_tren_web:                        # Trường hợp A: kỳ hạn gần nhất (số vừa lấy lần này)
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
            ghi['can_duyet'].append(f'Bảng {bang} – {ten}: không thấy trên nguồn còn truy cập được, nguồn kia lỗi → giữ nguyên.')
        elif thieu:                                       # Trường hợp B: chưa có link trang chính thức -> "-"
            for k in thieu:
                moi[k] = ('-', 'B', None)
        for k in ky_bai:
            gia_tri, nguon, can_cu = moi[k]
            if gia_tri == 'giu':
                continue
            cell = cells[cot.index(k)]
            cu = chu(cell)
            gt = kieu_so(gia_tri, cu, hai_so_le)
            if (so(cu) is not None and so(gt) is not None and so(cu) == so(gt)) or cu == gt:
                if nguon == 'A':
                    ghi['gan_nhat_trung'].append([bang, ten, k, cu, can_cu])
                continue
            m = re.search(r'>(\s*)' + re.escape(cu) + r'(\s*)<', cell)
            if not m:
                ghi['can_duyet'].append(f'Bảng {bang} – {ten} – {k} tháng: không thay được số trong ô (ô ghi "{cu}"), giữ nguyên.')
                continue
            cell2 = cell[:m.start()] + '>' + m.group(1) + to_vang(gt) + m.group(2) + '<' + cell[m.end():]
            row = thay_o(row, cot.index(k), cell2)
            cells[cot.index(k)] = cell2
            if nguon == 'A':
                ghi['gan_nhat'].append([bang, ten, k, cu, gt, can_cu])
            elif nguon == 'B':
                ghi['chinh_thuc'].append([bang, ten, k, cu, gt])
                ghi['gach'].append([bang, ten, k, cu])
            else:
                ghi['sua'].append([bang, ten, k, cu, gt, nguon])
        return row

    body = re.sub(r'<table.*?</table>', sua_bang, body, flags=re.S)

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

    # ngày/tháng trong đoạn văn (ngoài bảng)
    body = ''.join(p if p.startswith('<table') else sua_ngay(p, 'Đoạn văn')
                   for p in re.split(r'(<table.*?</table>)', body, flags=re.S))

    doc = ('<html><head><meta charset="utf-8"></head><body style="font-family:Arial;font-size:11pt">'
           + head + body + '</body></html>')
    open(f'{TAM}{ma}.full.html', 'w', encoding='utf-8').write(doc)
    # bản gọn để tải lên Drive
    g = re.sub(r'\s*\n\s*', ' ', doc).replace('&#61;', '=')
    g = re.sub(r'(</(?:p|td|tr|li|ul|table|h1|h2|h3|tbody)>) +(<)', r'\1\2', g)
    g = re.sub(r'(<(?:tr|td|tbody|ul|table)[^>]*>) +(<)', r'\1\2', g)
    g = re.sub(r' (?:class|id|rel|target)="[^"]*"', '', g).replace('style="text-align: center;"', 'align="center"')
    g = re.sub(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', lambda m: '#%02x%02x%02x' % tuple(int(x) for x in m.groups()), g)
    g = re.sub(r'style="([^"]*)"', lambda m: 'style="' + re.sub(r'\s*([:;])\s*', r'\1', m.group(1)).strip(' ;') + '"', g)
    open(f'{TAM}{ma}.min.html', 'w', encoding='utf-8').write(g)
    ghi['ten_file'] = f'{cfg["ten_file"]} – {hom_nay}'
    ghi['kich_thuoc'] = len(g)
    return ghi


# ======================= SOÁT =======================
def o_bang(h):
    out = []
    for tb in re.findall(r'<table.*?</table>', h, re.S):
        for tr in re.findall(r'<tr.*?</tr>', tb, re.S):
            out.append([(chu(td), VANG in td.replace(' ', '')) for td in re.findall(r'<td.*?</td>', tr, re.S)])
    return out


def soat(ma, duong_dan):
    import base64
    d = json.load(open(duong_dan))
    try:
        g = base64.b64decode(d['content']).decode('utf-8')
    except Exception:
        g = d['content']
    mau = open(f'{TAM}{ma}.min.html').read()
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
def bao_cao(hom_nay, links, them):
    kq = json.load(open(TAM + 'ket-qua.json'))
    n = kq['nguon']
    L = [f'# Báo cáo cập nhật lãi suất – {hom_nay}', '']
    for x in kq['loi_nguon']:
        L.append(f'> **Chưa cập nhật được từ {x} do không truy cập được.**')
    L += [f'> {x}' for x in them]
    for (ma, b), link in zip(kq['bai'].items(), links):
        L += ['', f'## {"BÀI 1" if ma == "bai1" else "BÀI 2"} – {BAI[ma]["url"]}', '']
        if 'loi' in b:
            L += [b['loi'], '']
            continue
        k = lambda x: f'{x} tháng'
        if not (b['sua'] or b['gan_nhat'] or b['chinh_thuc'] or b.get('doi_mau')):
            # Trang dặn: lãi suất không đổi thì chỉ cần báo không thay đổi
            L += [f'**Link file:** [{b["ten_file"]}]({link})', '', '**Không có thay đổi lãi suất.**', '']
            continue
        L += [f'**1. Link file:** [{b["ten_file"]}]({link})', '', '**2. Ngày tháng đã đổi:**', '']
        L += [f'- {x}' for x in b['doi_ngay']] or ['- Ngày, tháng trong bài đã đúng, không đổi.']
        if not any('tháng' in x and 'Tiêu đề' not in x for x in b['doi_ngay']):
            L.append('- Tháng trong các đoạn văn đã đúng tháng hiện tại (hoặc bài không ghi tháng) → giữ nguyên.')
        topi_td = f' – tiêu đề bài Topi: "{n["topi_tieu_de"]}"' if n['topi_tieu_de'] else ''
        L += ['', '**3. Ngày dữ liệu nguồn:**', '', f'- VnExpress: cập nhật đến {n["vne_ngay"] or "không đọc được"}',
              f'- Topi: {n["topi_ngay"] or "không đọc được"}{topi_td}',
              '- Biểu lãi suất ngân hàng (Bước 4.2): ' + ('không dùng.' if not b['chinh_thuc'] else 'chưa có link trong danh sách.'), '',
              f'**4. Ô đã sửa từ VnExpress và Topi ({len(b["sua"])} ô):**', '']
        L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} → {c[4]} (nguồn: {c[5]})' for c in b['sua']] or ['- Không có.']
        dm = b.get('doi_mau', [])
        L += ['', f'**4b. Ô đổi màu cao nhất / thấp nhất ({len(dm)} ô, đều tô vàng):**', '']
        L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} — {c[4]} → {c[5]}' for c in dm] or ['- Không có.']
        L += ['', f'**5. Ô lấy theo kỳ hạn gần nhất – Trường hợp A ({len(b["gan_nhat"])} ô):**', '']
        L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} → {c[4]} (lấy theo kỳ hạn {c[5]} tháng)' for c in b['gan_nhat']] or ['- Không có.']
        if b['gan_nhat_trung']:
            L += ['', 'Ô cũng lấy theo kỳ hạn gần nhất nhưng ra đúng số cũ (không sửa, không tô):', '']
            L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} (theo kỳ hạn {c[4]} tháng)' for c in b['gan_nhat_trung']]
        L += ['', '**6. Ô lấy từ trang chính thức – Trường hợp B:**', '', '- Không có.' if not b['chinh_thuc'] else
              '- Chưa có link trang chính thức trong danh sách → các ô ở mục 7.', '',
              '**7. Ô điền "-" do không có trên 2 website và chưa có link trang chính thức:**', '']
        L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} → -' for c in b['gach']] or ['- Không có.']
        L += ['', '**8. Trường hợp cần người duyệt kiểm tra:**', '']
        cu = []
        if n['vne_ngay']:
            from datetime import date
            d, m, y = map(int, n['vne_ngay'].split('/')); h = list(map(int, hom_nay.split('/')))
            tre = (date(h[2], h[1], h[0]) - date(y, m, d)).days
            if tre > 3:
                cu.append(f'Dữ liệu VnExpress cũ {tre} ngày (cập nhật đến {n["vne_ngay"]}); kỳ hạn ngắn có thể đã đổi mà VnExpress chưa cập nhật.')
        L += [f'- {x}' for x in cu + b['can_duyet'] + bat_thuong(b)] or ['- Không có.']
        L += ['', f'**9.** Có thay đổi: {len(b["sua"]) + len(b["gan_nhat"]) + len(b["chinh_thuc"])} ô lãi suất, {len(dm)} ô đổi màu.']
    p = f'bao-cao/{hom_nay[6:]}-{hom_nay[3:5]}-{hom_nay[:2]}.md'
    open(p, 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


def bat_thuong(b):
    """Ô đổi mạnh so với số cũ (chênh ≥ 0,8 điểm)."""
    ra = []
    for c in b['sua']:
        v = so(c[4])
        if v is not None and so(c[3]) is not None and abs(v - so(c[3])) >= 0.8:
            ra.append(f'Bảng {c[0]} – {c[1]} – {c[2]} tháng: đổi mạnh {c[3]} → {c[4]} (nguồn {c[5]}).')
    return ra


if __name__ == '__main__':
    lenh = sys.argv[1]
    if lenh == 'lay':
        lay()
    elif lenh == 'dung':
        dung(sys.argv[2])
    elif lenh == 'soat':
        sys.exit(0 if soat(sys.argv[2], sys.argv[3]) else 1)
    elif lenh == 'bao-cao':
        bao_cao(sys.argv[2], sys.argv[3:5], sys.argv[5:])

"""Lấy giá lúa gạo cho bài TCB "Giá lúa gạo hôm nay" → gia.json. Chỉ dùng thư viện có sẵn + curl.

Chạy: python3 -I lay_gia.py <gia.json>

Nguồn (mọi con số đều đọc từ trang tải về trong lần chạy này — không có số nào viết sẵn):
  bgns    https://banggianongsan.com/gia-lua-gao-hom-nay/ — bảng "Bảng giá lúa gạo mới nhất - dd/mm/yyyy"
          (Nông sản | Giá cũ | Giá mới | Thay đổi) → gạo, nếp, lúa trong nước.
  vietbao bài "Giá lúa gạo hôm nay <ngày>" mới nhất trên vietbao.vn (tìm qua trang tìm kiếm của vietbao, dự phòng: sitemap theo ngày)
          → chỉ lấy bảng giá gạo THẾ GIỚI (Thái Lan / Ấn Độ) nếu bài có bảng đó.
  vfa     https://vietfood.org.vn/thi-truong/gia-xuat-khau/ (Hiệp hội Lương thực Việt Nam, số liệu Oryza) — 2 bản tin
          "Giá gạo xuất khẩu của các nước trên thế giới ngày …" mới nhất (để tính thay đổi so với kỳ trước).
          Nguồn thay thế cho bảng thế giới khi vietbao không có; tắt bằng "the_gioi_vfa": false trong cau-hinh.json.
Nguồn lỗi → null + in "<nguồn> KHÔNG ĐỌC ĐƯỢC".
"""
import datetime, html, json, os, re, subprocess, sys, unicodedata
from html.parser import HTMLParser

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36'
BGNS = 'https://banggianongsan.com/gia-lua-gao-hom-nay/'
VB_TIM = 'https://vietbao.vn/tim-kiem.html?keyword=gi%C3%A1%20l%C3%BAa%20g%E1%BA%A1o%20h%C3%B4m%20nay'
VB_SITEMAP = 'https://vietbao.vn/sitemap/sitemap-articles-day-{}.xml'
VFA_DS = 'https://vietfood.org.vn/thi-truong/gia-xuat-khau/'
HOM_NAY = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=7)).date()


def tai(url):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '40', '--retry', '2', '-A', UA, '-w', '\n%{http_code}', url],
                       capture_output=True)
    body = r.stdout.decode('utf-8', 'replace')
    body, _, code = body.rpartition('\n')
    if r.returncode != 0 or code != '200':
        raise RuntimeError(f'tải {url} lỗi: curl {r.returncode}, HTTP {code} {r.stderr.decode()[:100]}')
    return body


def chu(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', html.unescape(s))).strip()


class Bang(HTMLParser):
    """Gom mọi <table> thành danh sách dòng, mỗi dòng là danh sách chữ trong ô."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bang, self.dong, self.o, self.sau = [], None, None, 0

    def handle_starttag(self, t, a):
        if t == 'table':
            self.sau += 1; self.bang.append([])
        elif t == 'tr' and self.sau:
            self.dong = []
        elif t in ('td', 'th') and self.dong is not None:
            self.o = []
        elif t == 'br' and self.o is not None:
            self.o.append(' ')

    def handle_endtag(self, t):
        if t in ('td', 'th') and self.o is not None and self.dong is not None:
            self.dong.append(chu(''.join(self.o))); self.o = None
        elif t == 'tr' and self.dong is not None:
            if any(self.dong):
                self.bang[-1].append(self.dong)
            self.dong = None
        elif t == 'table' and self.sau:
            self.sau -= 1

    def handle_data(self, d):
        if self.o is not None:
            self.o.append(d)


def cac_bang(s):
    p = Bang(); p.feed(s); return p.bang


def van_ban(s):
    s = re.sub(r'(?s)<(script|style)[^>]*>.*?</\1>', ' ', s)
    return chu(re.sub(r'<[^>]+>', ' ', s))


def khoang(s):
    """'8.900 – 9.000' → [8900, 9000]; '28.000' → [28000, 28000]; không có số → None"""
    so = [int(x.replace('.', '').replace(',', '')) for x in re.findall(r'\d[\d.,]*', s or '')]
    if not so or len(so) > 2:
        return None
    return [so[0], so[-1]]


def lay_bgns():
    s = tai(BGNS)
    t = van_ban(s)
    m = re.search(r'(\d{1,2}:\d{2}) (\d{1,2}/\d{1,2}/\d{4}) Bảng giá lúa gạo mới nhất - (\d{1,2}/\d{1,2}/\d{4})', t)
    if not m:
        raise RuntimeError('không thấy tiêu đề "Bảng giá lúa gạo mới nhất - dd/mm/yyyy"')
    for b in cac_bang(s):
        if b and 'Giá cũ' in ' '.join(b[0]) and 'Giá mới' in ' '.join(b[0]):
            dong = []
            for r in b[1:]:
                if len(r) < 4:
                    continue
                ten = re.sub(r'\s*\((đ|VND)/kg\)\s*$', '', r[0], flags=re.I)
                dong.append({'ten': ten, 'goc': ' | '.join(r[:4]), 'cu': khoang(r[1]), 'moi': khoang(r[2]),
                             'thay_doi': r[3]})
            if len(dong) < 10:
                raise RuntimeError(f'bảng giá chỉ có {len(dong)} dòng')
            return {'ngay_bang': m.group(3), 'dang_luc': f'{m.group(1)} {m.group(2)}', 'nguon': BGNS, 'dong': dong}
    raise RuntimeError('không thấy bảng "Giá cũ | Giá mới"')


def ngay_slug(u):
    m = re.search(r'gia-lua-gao-hom-nay-(\d{5,8})-', u)
    if not m:
        return None
    d = m.group(1)
    try:
        return datetime.date(int(d[-4:]), int(d[-6:-4]), int(d[:-6]))
    except ValueError:
        return None


def lay_vietbao():
    ds = set()
    try:
        ds |= set(re.findall(r'https://vietbao\.vn/gia-lua-gao-hom-nay-[\w-]+\.html', tai(VB_TIM)))
    except Exception as e:
        print('vietbao: trang tìm kiếm lỗi –', str(e)[:100], '→ thử sitemap')
    if not ds:
        for k in range(3):
            d = HOM_NAY - datetime.timedelta(days=k)
            try:
                ds |= set(re.findall(r'https://vietbao\.vn/gia-lua-gao-hom-nay-[\w-]+\.html', tai(VB_SITEMAP.format(d.isoformat()))))
            except Exception:
                pass
    bai = sorted(((ngay_slug(u), u) for u in ds if ngay_slug(u)), reverse=True)
    if not bai:
        raise RuntimeError('không tìm được bài "giá lúa gạo hôm nay" nào')
    moi_nhat = {'url': bai[0][1], 'ngay': bai[0][0].strftime('%d/%m/%Y')}
    # bảng thế giới: chỉ xét các bài trong 3 ngày gần nhất (cũ hơn không coi là giá hiện hành)
    for d, u in bai[:3]:
        if (HOM_NAY - d).days > 3:
            break
        s = tai(u)
        dong = []
        for b in cac_bang(s):
            for r in b:
                if len(r) >= 3 and re.match(r'^(Thái Lan|Ấn Độ|Pakistan)$', r[0]):
                    dong.append({'thi_truong': r[0], 'loai': r[1], 'goc': ' | '.join(r),
                                 'gia': khoang(r[2]), 'thay_doi': r[3] if len(r) > 3 else ''})
        if dong:
            m = re.search(r'(\d{1,2}:\d{2} \d{1,2}/\d{1,2}/\d{4})', van_ban(s))
            return dict(moi_nhat, the_gioi={'url': u, 'ngay': d.strftime('%d/%m/%Y'),
                                            'dang_luc': m.group(1) if m else '?', 'dong': dong})
    return dict(moi_nhat, the_gioi=None)


def bang_vfa(u):
    s = tai(u)
    dong, qg = [], None
    for b in cac_bang(s):
        if 'QUỐC GIA' not in ' '.join(' '.join(r) for r in b[:3]):
            continue
        for r in b:
            if len(r) == 4 and not r[2].replace('.', '').isdigit():
                continue
            if len(r) == 4:
                qg, r = r[0], r[1:]
            if len(r) == 3 and qg and re.fullmatch(r'[\d.]+', r[1]) and re.fullmatch(r'[\d.]+', r[2]):
                dong.append({'quoc_gia': qg, 'loai': r[0], 'goc': f'{qg} | ' + ' | '.join(r),
                             'gia': [int(r[1].replace('.', '')), int(r[2].replace('.', ''))]})
    if not dong:
        raise RuntimeError(f'không thấy bảng giá ở {u}')
    return dong


def lay_vfa():
    s = tai(VFA_DS)
    ds = set(re.findall(r'https://vietfood\.org\.vn/gia-gao-xuat-khau-cua-cac-nuoc-tren-the-gioi-ngay-(\d{1,2})-(\d{1,2})-(\d{4})/', s))
    bai = sorted({datetime.date(int(y), int(m), int(d)): f'https://vietfood.org.vn/gia-gao-xuat-khau-cua-cac-nuoc-tren-the-gioi-ngay-{d}-{m}-{y}/'
                  for d, m, y in ds}.items(), reverse=True)
    if len(bai) < 1:
        raise RuntimeError('không thấy bản tin giá gạo xuất khẩu nào')
    kq = {'ngay': bai[0][0].strftime('%d/%m/%Y'), 'url': bai[0][1], 'dong': bang_vfa(bai[0][1]), 'truoc': None}
    if len(bai) > 1:
        try:
            kq['truoc'] = {'ngay': bai[1][0].strftime('%d/%m/%Y'), 'url': bai[1][1], 'dong': bang_vfa(bai[1][1])}
        except Exception as e:
            print('vfa kỳ trước KHÔNG ĐỌC ĐƯỢC –', str(e)[:100])
    return kq


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'gia.json'
    try:
        ch = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cau-hinh.json'), encoding='utf-8'))
    except Exception:
        ch = {}
    viec = [('bgns', lay_bgns), ('vietbao', lay_vietbao)]
    if ch.get('the_gioi_vfa', True):
        viec.append(('vfa', lay_vfa))
    kq = {'chay_luc': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=7)).strftime('%H:%M %d/%m/%Y')}
    for ma, ham in viec:
        try:
            kq[ma] = ham()
        except Exception as e:
            kq[ma] = None
            print(ma, 'KHÔNG ĐỌC ĐƯỢC –', str(e)[:150])
    json.dump(kq, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if kq.get('bgns'):
        print(f"bgns    bảng {kq['bgns']['ngay_bang']} (đăng {kq['bgns']['dang_luc']}): {len(kq['bgns']['dong'])} dòng")
    if kq.get('vietbao'):
        v = kq['vietbao']; tg = v['the_gioi']
        print(f"vietbao bài mới nhất {v['ngay']}: {v['url']}")
        print('        bảng thế giới:', f"{len(tg['dong'])} dòng ({tg['ngay']})" if tg else 'không có trong các bài 3 ngày gần nhất')
    if kq.get('vfa'):
        v = kq['vfa']
        print(f"vfa     bản tin {v['ngay']}: {len(v['dong'])} dòng; kỳ trước: {v['truoc']['ngay'] if v['truoc'] else 'không có'}")
    print('→', out)


if __name__ == '__main__':
    main()

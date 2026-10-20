#!/usr/bin/env python3
"""Đối chiếu nội dung viết tay trong content.py với dữ liệu đã đo.

Bắt các trường hợp bịa số hoặc bịa tên. Không bắt được mọi thứ — phần còn lại là
trách nhiệm của người viết. Xem references/no-fabrication.md.

    python3 scripts/verify_claims.py --data data --content content.py
"""
import argparse, json, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(__file__))
from lib import clean, dom

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data')
ap.add_argument('--content', required=True)
ap.add_argument('--strict', action='store_true', help='thoát mã lỗi 1 nếu có cảnh báo')
a = ap.parse_args()

ME = json.load(open(f'{a.data}/meta.json'))['domain']
P = {clean(p['url']): p for p in json.load(open(f'{a.data}/pages.json'))}
CLU = json.load(open(f'{a.data}/clusters.json'))['clusters']
_sp = f'{a.data}/url_status.json'
STATUS = json.load(open(_sp)) if os.path.exists(_sp) else {}
KNOWN_DOM = {dom(u) for u in P}
BY_DOM = {}
for u, p in P.items():
    BY_DOM.setdefault(dom(u), []).append(p)

ns = {}
exec(open(a.content, encoding='utf-8').read(), ns)
C = ns.get('C', {})
NAMES = {c['name'] for c in CLU}

warn, info = [], []
def W(cl, msg): warn.append(f'[{cl}] {msg}')
def I(cl, msg): info.append(f'[{cl}] {msg}')


def nrm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', str(s))).strip().lower()


# 1. tên cụm phải khớp clusters.json
for k in C:
    if k.startswith('__'): continue
    if k not in NAMES:
        W(k, f'tên cụm không có trong clusters.json — báo cáo sẽ bỏ qua phần này')

# 2. mọi domain nhắc trong content phải nằm trong tập đã crawl
DOMRE = re.compile(r'\b([a-z0-9][a-z0-9-]{1,40}\.(?:com\.vn|net\.vn|org\.vn|edu\.vn|com|vn|net|org))\b')
for k, det in C.items():
    if not isinstance(det, dict): continue
    blob = json.dumps(det, ensure_ascii=False).lower()
    for d in set(DOMRE.findall(blob)):
        if d == ME or d in KNOWN_DOM: continue
        if d.endswith('.webp') or d.endswith('.html'): continue
        W(k, f'nhắc domain "{d}" nhưng domain này không có trong tập đã crawl')

# 3. title và description "hiện tại" trong meta phải khớp HTML đã crawl
def find_pages(det):
    """Đoán trang được nói tới: từ khoá page trong det, hoặc mọi trang của mình."""
    pg = str(det.get('page', ''))
    hit = [p for u, p in P.items() if ME in u and pg and pg.split()[0].rstrip(',') in u]
    return hit or [p for u, p in P.items() if ME in u]

for k, det in C.items():
    if not isinstance(det, dict) or 'meta' not in det: continue
    cands = find_pages(det)
    for row in det['meta']:
        if len(row) < 2: continue
        field, cur = str(row[0]).lower(), str(row[1])
        cur_txt = re.sub(r'\(\d+\s*ký tự\)', '', cur).strip()
        if len(cur_txt) < 12: continue
        if 'title' in field:
            def _match(t):
                a_, b_ = nrm(cur_txt), nrm(t)
                # khai là một phần của title thật thì chấp nhận; ngược lại title thật phải
                # phủ ít nhất 60% độ dài chuỗi khai, tránh title ngắn như "Dịch vụ" khớp bừa
                return a_ in b_ or (b_ in a_ and len(b_) >= 0.6 * len(a_))
            if not any(_match(p['title']) for p in cands if p.get('title')):
                W(k, f'title "hiện tại" không khớp title nào đã crawl: {cur_txt[:60]}')
        elif 'description' in field:
            if not any(nrm(cur_txt[:60]) in nrm(p['desc']) for p in cands if p.get('desc')):
                W(k, f'description "hiện tại" không khớp description nào đã crawl: {cur_txt[:60]}')
        # số ký tự khai trong ngoặc phải đúng
        m = re.search(r'\((\d+)\s*ký tự\)', cur)
        if m and abs(int(m.group(1)) - len(cur_txt)) > 3:
            W(k, f'khai {m.group(1)} ký tự nhưng chuỗi dài {len(cur_txt)}: {cur_txt[:50]}')

# 4. cột "hiện tại" của bảng ảnh phải khớp số đo được
NUMRE = re.compile(r'^(\d+)(?:\s*/\s*(\d+))?$')
for k, det in C.items():
    if not isinstance(det, dict) or 'media' not in det: continue
    cands = find_pages(det)
    keymap = {'ảnh nội dung': 'imgs_all', 'ảnh lazy-load': 'lazy', 'ảnh có srcset': 'srcset',
              'ảnh webp': 'webp', 'link nội bộ': 'ilinks', 'dung lượng html': 'kb'}
    for row in det['media']:
        if len(row) < 2: continue
        lab, cur = nrm(row[0]), str(row[1]).strip()
        fld = next((v for kk, v in keymap.items() if kk in lab), None)
        m = NUMRE.match(cur.replace('KB', '').strip())
        if not fld or not m: continue
        val = int(m.group(1))
        if not any(p.get(fld) == val for p in cands):
            got = sorted({p.get(fld) for p in cands})[:6]
            W(k, f'bảng ảnh ghi {row[0]} = {val} nhưng không trang nào của mình có giá trị đó '
                 f'(đo được: {got})')

# 4b. không đề xuất sửa trang đã hỏng
if not STATUS:
    info.append('[chung] chưa có url_status.json — chạy verify_urls.py trước, '
                'nếu không sẽ không bắt được đề xuất sửa trang 404 hay noindex')
else:
    def _bad(u):
        st = STATUS.get(u) or STATUS.get(u.rstrip('/')) or STATUS.get(u + '/')
        if not st: return None
        c = st.get('status')
        if c in (404, 410): return f'đang trả {c} — trang đã mất'
        if isinstance(c, int) and c >= 500: return f'đang trả {c} — lỗi máy chủ'
        if c in (301, 302, 303, 307, 308): return f'đang {c} chuyển hướng tới {st.get("target","")[:60]}'
        if st.get('noindex'): return 'đang gắn noindex, không thể lên top'
        if st.get('canonical') and clean(st['canonical']) != clean(u):
            return f'canonical trỏ sang {st["canonical"][:60]}'
        return None
    URLRE = re.compile(r'(/[a-z0-9\-/]{4,})')
    for k, det in C.items():
        if not isinstance(det, dict): continue
        blob = json.dumps(det, ensure_ascii=False)
        paths = {p.rstrip('.,;)') for p in URLRE.findall(blob) if not p.endswith(('.webp', '.jpg', '.png'))}
        for p in paths:
            for base in (f'https://www.{ME}{p}', f'https://{ME}{p}'):
                why = _bad(base)
                if why:
                    W(k, f'đề xuất động tới {p} nhưng URL này {why} — xử lý tình trạng trước, '
                         f'đừng viết việc tối ưu nội dung')
                    break

# 5. cụm từ mơ hồ — chỉ nhắc, không phải lỗi
VAGUE = ['khoảng chừng', 'ước chừng', 'có lẽ', 'chắc là', 'thường thì', 'nhìn chung là',
         'đa số đối thủ', 'hầu hết đối thủ']
for k, det in C.items():
    if not isinstance(det, dict): continue
    blob = nrm(json.dumps(det, ensure_ascii=False))
    for v in VAGUE:
        if v in blob:
            I(k, f'có cụm mơ hồ "{v}" — thay bằng số đo được')

print(f"Đối chiếu {len([k for k in C if not k.startswith('__')])} cụm trong {a.content}")
print(f"dữ liệu nền: {len(P)} trang đã crawl · {len(KNOWN_DOM)} domain\n")
if warn:
    print(f"CẢNH BÁO — {len(warn)} chỗ không truy được về dữ liệu, phải sửa:")
    for w in warn: print('  ', w)
else:
    print("Không có cảnh báo ở các trường kiểm được.")
if info:
    print(f"\nNhắc — {len(info)} chỗ nên viết chặt hơn:")
    for i in info: print('  ', i)
print("\nScript chỉ kiểm phần kiểm được: tên cụm, tên domain, title, description, bảng ảnh,")
print("và tình trạng URL được đề xuất động tới.")
print("Các nhận định còn lại phải tự đối chiếu dữ liệu, không viết từ trí nhớ.")
if a.strict and warn:
    sys.exit(1)

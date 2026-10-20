#!/usr/bin/env python3
"""Kiểm trạng thái lập chỉ mục thật của từng URL bằng URL Inspection API của Search Console.

KHÔNG dùng cú pháp site: trên Google. Lý do ở references/verify.md mục 3: Google chặn truy vấn
tự động, và số kết quả của site: vốn là ước lượng thô, không cho biết vì sao một URL không
được index. URL Inspection API là nguồn chính thống, trả về đúng thứ cần:

  verdict          PASS / NEUTRAL / FAIL
  coverageState    "Đã được gửi và lập chỉ mục", "Đã thu thập dữ liệu - hiện chưa lập chỉ mục"...
  googleCanonical  URL Google thực sự chọn — khác userCanonical là bằng chứng gộp trang
  lastCrawlTime    lần crawl gần nhất
  robotsTxtState · indexingState · pageFetchState · crawledAs

    python3 scripts/index_status.py --data data --site <property>

Quota: 2.000 URL mỗi ngày và 600 mỗi phút cho mỗi property. Script mặc định chỉ kiểm URL
của mình có trong file check top hoặc có hiển thị trên Search Console.
"""
import argparse, collections, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import clean

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data')
ap.add_argument('--site', help='property GSC; bỏ trống thì lấy từ data/gsc_meta.json')
ap.add_argument('--limit', type=int, default=300, help='số URL tối đa mỗi lần chạy, quota 2000/ngày')
ap.add_argument('--min-imp', type=int, default=0)
ap.add_argument('--cred')
ap.add_argument('--sleep', type=float, default=0.12, help='giãn cách giữa hai lần gọi')
a = ap.parse_args()

from auth import credential_candidates, load_credentials
from googleapiclient.discovery import build

META = json.load(open(f'{a.data}/meta.json'))
ME = META['domain']
SITE = a.site or (json.load(open(f'{a.data}/gsc_meta.json'))['site']
                  if os.path.exists(f'{a.data}/gsc_meta.json') else None)
if not SITE:
    sys.exit('Thiếu property. Truyền --site hoặc chạy gsc.py trước.')


def find_cred():
    if a.cred: return a.cred
    for p in credential_candidates():
        try:
            svc = build('searchconsole', 'v1', credentials=load_credentials(p), cache_discovery=False)
            if SITE in [s['siteUrl'] for s in svc.sites().list().execute().get('siteEntry', [])]:
                print(f'dùng credential: {os.path.basename(p)}')
                return p
        except Exception:
            continue
    sys.exit(f'Không credential nào có quyền với {SITE}. Đặt GSC_CREDENTIALS_DIR hoặc '
             f'GSC_CREDENTIALS_FILE, hoặc truyền --cred.')


svc = build('searchconsole', 'v1', credentials=load_credentials(find_cred()), cache_discovery=False)

KW = json.load(open(f'{a.data}/kw.json'))
urls = {clean(u) for r in KW for _, u in r['allmine']}
imp = collections.Counter()
if os.path.exists(f'{a.data}/gsc_qp.json'):
    for r in json.load(open(f'{a.data}/gsc_qp.json')):
        u = clean(r['keys'][1])
        if ME in u: imp[u] += r['impressions']
    urls |= {u for u, i in imp.items() if i >= a.min_imp}

path = f'{a.data}/index_status.json'
done = json.load(open(path)) if os.path.exists(path) else {}
todo = [u for u in sorted(urls, key=lambda x: -imp.get(x, 0)) if u not in done][:a.limit]
print(f'{len(urls)} URL của mình · đã có {len(done)} · kiểm thêm {len(todo)} lần này')

FIELDS = ('verdict', 'coverageState', 'robotsTxtState', 'indexingState', 'lastCrawlTime',
          'googleCanonical', 'userCanonical', 'pageFetchState', 'crawledAs')
for n, u in enumerate(todo, 1):
    try:
        r = svc.urlInspection().index().inspect(
            body={'inspectionUrl': u, 'siteUrl': SITE, 'languageCode': 'vi'}).execute()
        i = r['inspectionResult'].get('indexStatusResult', {})
        done[u] = {k: i.get(k) for k in FIELDS if i.get(k) is not None}
        done[u]['imp'] = imp.get(u, 0)
    except Exception as e:
        done[u] = {'error': str(e)[:120], 'imp': imp.get(u, 0)}
    if n % 25 == 0:
        print(f'  {n}/{len(todo)}', flush=True)
        json.dump(done, open(path, 'w'), ensure_ascii=False)
    time.sleep(a.sleep)
json.dump(done, open(path, 'w'), ensure_ascii=False)

R = list(done.values())
def cnt(f): return sum(1 for r in R if f(r))
indexed = [u for u, r in done.items() if r.get('verdict') == 'PASS']
_REDIR = ('chuyển hướng', 'redirect')
def _is_redir(r): return any(t in (r.get('coverageState') or '').lower() for t in _REDIR)
notidx = [(u, r) for u, r in done.items()
          if r.get('verdict') and r['verdict'] != 'PASS' and not _is_redir(r)]
redir = [(u, r) for u, r in done.items() if _is_redir(r)]
diffcan = [(u, r) for u, r in done.items()
           if r.get('googleCanonical') and r.get('userCanonical')
           and clean(r['googleCanonical']) != clean(r['userCanonical'])]
err = [(u, r) for u, r in done.items() if 'error' in r]

print(f"\n{'Tình trạng lập chỉ mục':44s}{'số URL':>8}")
print(f"{'đã được lập chỉ mục (verdict PASS)':44s}{len(indexed):>8}")
print(f"{'chưa index — cần xử lý':44s}{len(notidx):>8}")
print(f"{'không index vì đã chuyển hướng':44s}{len(redir):>8}")
print(f"{'Google chọn canonical khác trang khai báo':44s}{len(diffcan):>8}")
print(f"{'lỗi khi kiểm':44s}{len(err):>8}")

cov = collections.Counter(r.get('coverageState') for r in R if r.get('coverageState'))
print('\nPhân bố coverageState:')
for k, v in cov.most_common():
    print(f'   {v:4d}  {k}')

def sh(u): return u.replace(f'https://www.{ME}', '').replace(f'https://{ME}', '') or '/'
if redir:
    print('\n--- KHÔNG INDEX VÌ ĐÃ CHUYỂN HƯỚNG — bình thường nếu 301 có chủ đích ---')
    print('    Đối chiếu với url_status.json: trùng nhau nghĩa là hai nguồn độc lập cùng kết luận.')
    for u, r in sorted(redir, key=lambda x: -x[1].get('imp', 0))[:10]:
        print(f"   {r.get('imp',0):>7} hiển thị · {sh(u)}  [{r.get('coverageState','')}]")
if notidx:
    print('\n--- CHƯA ĐƯỢC LẬP CHỈ MỤC — không thể lên top, xử lý trước khi tối ưu nội dung ---')
    for u, r in sorted(notidx, key=lambda x: -x[1].get('imp', 0))[:20]:
        print(f"   {r.get('imp',0):>7} hiển thị · {sh(u)}")
        print(f"        {r.get('coverageState','')} · fetch {r.get('pageFetchState','')} · robots {r.get('robotsTxtState','')}")
if diffcan:
    print('\n--- GOOGLE CHỌN CANONICAL KHÁC — bằng chứng trực tiếp của gộp trang ---')
    for u, r in sorted(diffcan, key=lambda x: -x[1].get('imp', 0))[:20]:
        print(f"   {r.get('imp',0):>7} hiển thị · {sh(u)}")
        print(f"        Google gộp về: {sh(r['googleCanonical'])}")
if not diffcan and len(done) >= 20:
    print('\n--- Không URL nào có googleCanonical khác userCanonical ---')
    print('    Nghĩa là ăn thịt từ khoá ở site này KHÔNG phải dạng Google gộp trang,')
    print('    mà là dạng Google phân vân chọn URL nào để xếp hạng cho cùng một truy vấn.')
    print('    Hai dạng này cần cách xử lý khác nhau, xem references/verify.md mục 3.')
if err:
    print(f'\n--- LỖI KHI KIỂM ({len(err)}) ---')
    for u, r in err[:10]: print(f"   {sh(u)}  {r['error'][:80]}")

print(f"\nĐã lưu {path}. Còn {len(urls)-len(done)} URL chưa kiểm — chạy lại để tiếp tục.")
print("Không dùng cú pháp site: để thay cho bước này, xem references/verify.md mục 3.")

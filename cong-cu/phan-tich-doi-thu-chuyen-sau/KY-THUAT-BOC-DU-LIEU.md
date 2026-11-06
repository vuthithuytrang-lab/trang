# Kỹ thuật bóc dữ liệu từ website — bản đã chạy thật

Rút từ lần chạy osakar.com.vn ngày 25/09/2026: bóc 25 trang sản phẩm, 5 bài tin tức,
trang chính sách và 4 trang đối thủ.

---

## 1. Lấy sơ đồ trang trước tiên

Luôn bắt đầu từ đây. Có sơ đồ là có toàn bộ URL, không phải mò.

```bash
for u in sitemap.xml sitemap_index.xml product-sitemap.xml post-sitemap.xml; do
  curl -sL --http1.1 -o "s_$u" "https://TENMIEN/$u"
done
grep -o '<loc>[^<]*</loc>' s_*.xml | sed 's|</\?loc>||g' | grep -v image | sort -u
```

Sơ đồ WordPress do Yoast sinh thường có: `post-sitemap.xml`, `page-sitemap.xml`,
`product-sitemap.xml`, `category-sitemap.xml`.

## 2. Tải hàng loạt trang

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
while read u; do
  f="pages/$(echo "$u" | sed 's|https://TENMIEN/||; s|/$||; s|/|__|g').html"
  curl -sL --http1.1 -c cj.txt -b cj.txt -A "$UA" -o "$f" -w "%{http_code} $f\n" "$u"
done < products.txt
```

- `-c cj.txt -b cj.txt` giữ cookie — **gỡ được vòng lặp chuyển hướng 307**
  (đã gặp ở vietnix.vn)
- `--http1.1` tránh lỗi giao thức với một số máy chủ
- `-w "%{http_code}"` để biết trang nào hỏng ngay

## 3. Bóc tiêu đề, đề mục và bảng

```python
import re, html, sys
h = open(sys.argv[1], encoding='utf-8', errors='replace').read()
h = re.sub(r'(?is)<script.*?</script>', ' ', h)
h = re.sub(r'(?is)<style.*?</style>', ' ', h)
def tx(s):
    s = re.sub(r'(?s)<[^>]+>', ' ', s); s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

print('TITLE:', tx(re.search(r'(?is)<title>(.*?)</title>', h).group(1)))
for m in re.finditer(r'(?is)<(h[1-4])[^>]*>(.*?)</\1>', h):
    print(f'  [{m.group(1).upper()}] {tx(m.group(2))}')
for i, m in enumerate(re.finditer(r'(?is)<table.*?</table>', h)):
    print(f'  --- BẢNG {i+1} ---')
    for r in re.findall(r'(?is)<tr.*?</tr>', m.group(0)):
        cells = [tx(x) for x in re.findall(r'(?is)<t[dh][^>]*>(.*?)</t[dh]>', r)]
        if any(cells): print('    | ' + ' | '.join(c for c in cells if c))
```

## 4. Bóc giá cho đúng — cạm bẫy hay gặp

Một trang sản phẩm thường có **nhiều con số giá**: giá của chính nó, cộng thêm
giá của các sản phẩm gợi ý ở cuối trang. Lấy bừa là sai.

**Cách làm đúng: tìm con số đi kèm chuỗi đặc trưng của trang đó.**

```python
# Ở osakar.com.vn, giá thật luôn đi kèm "(Giá đã bao gồm VAT, 01 bộ sạc)"
g = re.search(r'([\d][\d\.]{5,})\s*VNĐ\s*\(\s*Giá đã bao gồm VAT', text)
```

Cách tìm chuỗi đặc trưng: in ra **ngữ cảnh quanh mỗi con số giá**, đọc bằng mắt
một trang rồi mới viết quy tắc.

```python
for m in re.finditer(r'[\d][\d\.,]{5,}\s*(?:đ|₫|VNĐ|VND)', text):
    print('...' + text[max(0,m.start()-220):m.end()+120] + '...')
```

Nếu site dùng WooCommerce, thử dữ liệu có cấu trúc trước:
`<script type="application/ld+json">` → `@type: Product` → `offers.price`.
Nhiều site Việt để trống trường này, lúc đó mới quay lại cách trên.

## 5. Lấy ảnh đại diện sản phẩm

Ảnh trong thân trang thường là ảnh màu sắc, ảnh chi tiết — không phải ảnh chính.
Ảnh chính nằm ở thẻ mạng xã hội:

```bash
grep -oE '<meta property="og:image" content="[^"]+"' trang.html | head -1
```

## 6. Khi bị chặn

| Biểu hiện | Thử gì |
|---|---|
| Vòng lặp chuyển hướng 307 | Thêm cookie jar `-c/-b` và `--http1.1` |
| 403 Forbidden | Đổi User-Agent sang điện thoại, thêm `Referer: https://www.google.com/`, thêm `Accept-Language` |
| 403 vẫn còn sau 3 cách | **Dừng. Báo rõ đã thử mấy cách. Không đoán nội dung.** |
| 522 / timeout | Máy chủ gốc lỗi, không phải mình. Thử lại sau, rồi báo thật |
| Cloudflare chặn hẳn | Không vượt được. Xin Trang chụp màn hình |

Lệnh thử lại với trình duyệt điện thoại:

```bash
curl -sL --http1.1 -m 40 \
  -H "Accept-Language: vi-VN,vi;q=0.9" \
  -H "Referer: https://www.google.com/" \
  -A "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1" \
  -o out.html -w "HTTP:%{http_code}\n" "URL"
```

**Tuyệt đối không tắt kiểm tra chứng chỉ, không bỏ biến proxy.**

## 7. Bóc toàn văn một bài để đọc

Bộ bóc đơn giản hay cắt mất phần sau. Dùng bản này, giữ nguyên thứ tự và đánh dấu đề mục:

```python
m = re.search(r'(?is)<div[^>]*class="[^"]*(?:entry-content|post-content)[^"]*".*?>(.*)', h)
seg = m.group(1) if m else h
seg = re.sub(r'(?is)<(h[1-6])[^>]*>', r'\n\n@@\1@@ ', seg)
seg = re.sub(r'(?is)</(h[1-6])>', '\n', seg)
seg = re.sub(r'(?is)<li[^>]*>', '\n- ', seg)
seg = re.sub(r'(?is)</(p|div|tr|table|ul|ol)>', '\n', seg)
seg = re.sub(r'(?is)</t[dh]>', ' | ', seg)
print(re.sub(r'\n\s*\n+', '\n', html.unescape(re.sub(r'(?s)<[^>]+>', '', seg))))
```

⚠️ **Đừng lọc trùng dòng** khi bóc toàn văn — bài dài sẽ bị cắt mất đoạn.

## 8. Soát file HTML trước khi giao

```python
# Thẻ có cân không
for t in ['div','table','tr','td','th','ul','li','p','h1','h2','h3','span']:
    o = len(re.findall(r'<%s[\s>]' % t, h)); c = len(re.findall(r'</%s>' % t, h))
    if o != c: print('LỆCH THẺ', t, o, c)
```

Soát tràn lề bằng Chromium không giao diện, chèn đoạn mã đo chiều rộng rồi đọc
tiêu đề trang:

```bash
CH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
for W in 390 768 1100; do
  "$CH" --headless --no-sandbox --disable-gpu --virtual-time-budget=2500 \
    --window-size=$W,900 --dump-dom "file:///duong/dan/test.html" 2>/dev/null \
    | grep -o '<title>[^<]*</title>'
done
```

Chụp ảnh để tự soát dấu tiếng Việt và bố cục:

```bash
"$CH" --headless --no-sandbox --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=900,1400 \
  --screenshot=/tmp/soat.png "file:///duong/dan/bai.html"
```

Muốn soi một mục ở giữa bài thì **cắt riêng mục đó ra file tạm** rồi chụp —
`scrollIntoView` không ăn với ảnh chụp không giao diện.

**Dọn hết ảnh nháp trước khi lưu vào kho.**

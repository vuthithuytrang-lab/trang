# WordPress.com REST API — Steps

Thao tác đăng bài lên WordPress.com bản free qua REST API công khai của nền tảng (`public-api.wordpress.com`), không dùng browser automation, không cần login UI. Mọi lệnh gọi HTTP dùng qua `scripts/wp-http.sh`, mọi xử lý JSON dùng qua `scripts/wp-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp, vì 2 script này đã được allowlist trong `.claude/settings.json` (domain hardcode sẵn trong script) để pipeline chạy không cần xác nhận thủ công từng lệnh.

## Contents

- Setup app & OAuth (1 lần / site)
- Lấy access token (authorization code grant)
- Upload ảnh
- Tạo & publish bài
- Xử lý trang nguồn bị chặn bot (JS cookie challenge)
- scripts/wp-http.sh — reference lệnh
- scripts/wp-json.js — reference lệnh
- Known limits

## Setup app & OAuth (1 lần / site)

1. Hướng dẫn user tạo app tại `https://developer.wordpress.com/apps/new/`, đăng nhập bằng tài khoản WordPress.com sở hữu site đích:
   - Name: bất kỳ (vd tên skill)
   - Website URL: URL site đích
   - Redirect URLs: `https://localhost/`
   - Type: Web
2. Sau khi tạo, trang hiển thị Client ID + Client Secret — lưu vào `wp-accounts.local.json` theo domain site (key là domain, vd `myblog.wordpress.com`).

## Lấy access token (authorization code grant — mặc định, token không hết hạn)

Dùng `response_type=code` (authorization code grant), KHÔNG dùng `response_type=token` (implicit grant) — implicit grant cấp token có hạn ~14 ngày và không có refresh token, phải lặp lại toàn bộ bước OAuth mỗi khi hết hạn. Authorization code grant cấp token KHÔNG hết hạn (response không có field `expires_in`), chỉ cần làm 1 lần/site.

1. Build authorize URL:
   `https://public-api.wordpress.com/oauth2/authorize?client_id=<CLIENT_ID>&redirect_uri=https%3A%2F%2Flocalhost%2F&response_type=code&scope=global`
2. Đưa link cho user mở trong trình duyệt họ đang đăng nhập WordPress.com, bấm Approve.
3. Trình duyệt redirect tới `https://localhost/?code=<CODE>&state=...` (code nằm ở query string, không phải fragment) — trang báo lỗi không tải được là bình thường, chỉ cần copy URL trên thanh địa chỉ.
4. User paste lại URL đó, trích giá trị `code`.
5. Đổi code lấy access token:
   ```
   bash scripts/wp-http.sh oauth-token <CLIENT_ID> <CLIENT_SECRET> https://localhost/ <CODE> <out-file>.json
   ```
6. Lưu response vào `wp-accounts.local.json`:
   ```
   node scripts/wp-json.js save-oauth-token wp-accounts.local.json <site-domain> <out-file>.json
   ```
   Lệnh này tự kiểm tra response có `access_token` không, ghi `access_token`/`token_type`/`token_scope`/`token_expires` (`false` nếu response không có `expires_in`, đúng như authorization code grant)/`obtained_at`.
7. Nếu API sau này trả 401 (token bị revoke thủ công từ phía user, hoặc app bị xoá) → lặp lại bước 1-6, KHÔNG tự đoán token khác.

### Legacy: implicit grant (không dùng làm mặc định)

`response_type=token` trả `access_token` trong URL fragment (`#access_token=...&expires_in=1209600...`) và hết hạn sau ~14 ngày, không có refresh token. Nếu vì lý do nào đó phải dùng lại luồng này: decode bằng `node scripts/wp-json.js decode-implicit-fragment "<fragment-string>"` — KHÔNG tách chuỗi bằng `&`/`=` thủ công vì token có thể chứa ký tự đặc biệt (`*`, `^`, `@`, `&`, `#`, `!`, `(`...) đã percent-encode.

## Upload ảnh

```
bash scripts/wp-http.sh upload-media <site-domain> <token> <local-image-path> <mime-type> <out-file>.json
node scripts/wp-json.js show-media-id <out-file>.json
```

`show-media-id` in ra `media[0].ID` — dùng ID này làm giá trị field `featured_image` khi tạo post ở bước sau. HTTP_STATUS in ra không phải 2xx → bỏ qua ảnh, tạo post không kèm `featured_image`.

## Tạo & publish bài

Content phải là Gutenberg block markup (không phải HTML thường) để bài hiển thị đúng dạng khối khi mở lại trong block editor:

```html
<!-- wp:paragraph -->
<p>Đoạn văn...</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Tiêu đề phụ</h2>
<!-- /wp:heading -->

<!-- wp:list {"ordered":true} -->
<ol>
<!-- wp:list-item -->
<li>Mục 1</li>
<!-- /wp:list-item -->
</ol>
<!-- /wp:list -->
```

Ghi content này ra 1 file tạm, rồi:

```
node scripts/wp-json.js build-post-payload <content-html-file> "<title>" "<slug>" "<media-id-hoặc-để-trống>" <payload-file>.json
bash scripts/wp-http.sh create-post <site-domain> <token> <payload-file>.json <out-file>.json
node scripts/wp-json.js show-post-result <out-file>.json
```

`show-post-result` in ra `ID`, `URL`, `status`, `title`, `slug`, `featured_image` — dùng để verify (Step 8 trong SKILL.md) và build Output format. Chỉ coi là thành công khi `status` đúng `"publish"`.

## Xử lý trang nguồn bị chặn bot (JS cookie challenge)

Một số site nguồn dùng WAF/CDN chặn request không chạy JS: response ban đầu rất ngắn, chỉ chứa 1 thẻ script dạng:

```html
<script>document.cookie="XXX=yyy...; expires=...; path=/";window.location.reload(true);</script>
```

Nếu gặp response dạng này (kiểm tra bằng cách đọc lại file `<out-file>` sau `fetch-source`, thấy size rất nhỏ và chỉ chứa script này):
1. Trích tên + giá trị cookie từ script đó.
2. Gọi lại `fetch-source` cùng URL, truyền thêm cookie ở tham số thứ 3:
   ```
   bash scripts/wp-http.sh fetch-source <url> <out-file> "XXX=yyy"
   ```
   Lần này sẽ trả về HTML đầy đủ của trang.

Đây là kiểu JS-redirect phổ biến ở nhiều CMS/CDN cho request đầu tiên, áp dụng cho trang public không yêu cầu đăng nhập — không phải bypass xác thực hay bảo mật.

## scripts/wp-http.sh — reference lệnh

Mọi HTTP call của skill này đi qua script này (gọi tới `public-api.wordpress.com` và đọc bài từ URL nguồn bất kỳ; script tự chặn các địa chỉ nội bộ như localhost / mạng riêng để tránh bị lợi dụng):

| Subcommand | Args | Dùng ở |
|---|---|---|
| `fetch-source` | `<url> <out-file> [cookie]` | Step 3 — đọc bài nguồn |
| `download-image` | `<url> <out-file> <cookie>` | Step 5 — tải ảnh đại diện |
| `check-site` | `<site-domain> <token>` | Step 2 — verify token còn dùng được |
| `oauth-token` | `<client_id> <client_secret> <redirect_uri> <code> <out-file>` | Step 2 — đổi code lấy access token |
| `upload-media` | `<site-domain> <token> <local-file> <mime-type> <out-file>` | Step 6 — upload ảnh |
| `create-post` | `<site-domain> <token> <payload-file> <out-file>` | Step 7 — tạo & publish bài |

## scripts/wp-json.js — reference lệnh

Mọi xử lý JSON/text của skill này đi qua script này:

| Subcommand | Args | Dùng ở |
|---|---|---|
| `get-account-field` | `<accounts-json-file> <site-domain> <field>` | Step 1-2 — đọc client_id/client_secret/access_token đã lưu |
| `save-oauth-token` | `<accounts-json-file> <site-domain> <token-response-file>` | Step 2 — lưu token mới lấy được |
| `decode-implicit-fragment` | `<fragment-string>` | Chỉ dùng khi buộc phải dùng legacy implicit grant |
| `build-post-payload` | `<content-html-file> <title> <slug> <media-id-or-empty> <out-file>` | Step 7 — build JSON body trước khi create-post |
| `word-count` | `<gutenberg-block-html-file>` | Step 4 — self-check độ dài bài viết lại |
| `show-media-id` | `<media-upload-response-file>` | Step 6 — lấy media ID sau upload |
| `show-post-result` | `<post-response-file>` | Step 8 — verify + lấy ID/URL/status/title/slug |

## Known limits

- WordPress.com free plan giới hạn tổng dung lượng media (thường 3GB/site) — ảnh quá lớn có thể bị từ chối ở bước upload, không phải do sai cú pháp request.
- `site_id=0` trong response OAuth với `scope=global` là bình thường — token dùng được cho mọi site của tài khoản, site đích được xác định qua domain trong URL request, không cần theo `site_id`.
- `wp-http.sh` chỉ chặn URL trỏ về địa chỉ nội bộ (localhost, 127.x, 10.x, 192.168.x...) — đọc bài nguồn ở domain công khai nào cũng được. Không tự ý gọi `curl` trực tiếp để lách qua script này (script này đã được cho phép sẵn trong `settings.json`).

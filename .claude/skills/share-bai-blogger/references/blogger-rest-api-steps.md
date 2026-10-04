# Blogger API v3 — Steps

Thao tác đăng bài lên Blogger qua Blogger API v3 (Google), không dùng browser automation, không cần login UI. Mọi lệnh gọi HTTP dùng qua `scripts/blogger-http.sh`, mọi xử lý JSON dùng qua `scripts/blogger-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp, vì 2 script này được allowlist trong `.claude/settings.json` (domain hardcode sẵn trong script) để pipeline chạy không cần xác nhận thủ công từng lệnh.

## Contents

- Setup OAuth app (1 lần / Google Cloud project)
- Lấy refresh_token (1 lần / blog)
- Refresh access_token (mỗi lần chạy, tự động)
- Tra blog ID từ blog URL (1 lần / blog)
- Nhúng ảnh vào bài (base64 data URI, KHÔNG hotlink)
- Tạo & publish bài
- Cập nhật bài đã đăng
- Xử lý trang nguồn bị chặn bot (JS cookie challenge)
- scripts/blogger-http.sh — reference lệnh
- scripts/blogger-json.js — reference lệnh
- Known limits

## Setup OAuth app (1 lần / Google Cloud project)

1. Hướng dẫn user tạo project tại `https://console.cloud.google.com/projectcreate` (nếu chưa có project).
2. Enable "Blogger API v3" tại `https://console.cloud.google.com/apis/library` (search đúng tên, bấm Enable).
3. Tạo OAuth consent screen tại `https://console.cloud.google.com/apis/credentials/consent`: User Type = External, điền email user, **thêm chính email user vào mục Test users** (bắt buộc, thiếu bước này sẽ bị lỗi "Access blocked" khi authorize).
4. Tạo OAuth Client ID tại `https://console.cloud.google.com/apis/credentials` → Create Credentials → OAuth client ID → Application type = **Desktop app**.
5. Lấy Client ID + Client Secret (hiện ngay sau khi tạo, hoặc bấm vào client vừa tạo để xem lại / Download JSON).
6. Lưu vào `blogger-accounts.local.json`:
   ```
   node scripts/blogger-json.js set-client blogger-accounts.local.json <blog-key> <client_id> <client_secret> <blog-url>
   ```
   `<blog-key>` là tên định danh blog (khuyến nghị dùng chính domain blog, vd `myblog.blogspot.com`).

## Lấy refresh_token (1 lần / blog)

1. Chạy:
   ```
   node scripts/google-oauth-server.js <client_id> <client_secret> <out-file>.json
   ```
   Script tự mở 1 local HTTP server tạm (mặc định port 8765) và in ra 1 authorize URL.
2. Đưa URL đó cho user mở trong trình duyệt, đăng nhập đúng tài khoản Google sở hữu blog, bấm Allow. KHÔNG cần copy-paste URL redirect thủ công — script tự bắt request redirect về `127.0.0.1:8765` và tự đổi code lấy token.
3. Script tự thoát (exit code 0) sau khi ghi response token vào `<out-file>.json`. Timeout 5 phút nếu user không thao tác.
4. Lưu vào `blogger-accounts.local.json`:
   ```
   node scripts/blogger-json.js save-tokens blogger-accounts.local.json <blog-key> <out-file>.json
   ```
   Lệnh này tự kiểm tra response có `refresh_token` không (bắt buộc phải có ở lần đầu — nếu thiếu, nghĩa là authorize URL thiếu `access_type=offline`/`prompt=consent`, chạy lại bước 1).

## Refresh access_token (mỗi lần chạy, tự động)

Access token của Google chỉ sống ~1 giờ, KHÔNG như WordPress access token là vĩnh viễn — phải refresh trước mỗi lần gọi Blogger API. Việc này KHÔNG cần user tương tác gì (silent), chỉ cần `refresh_token` còn hợp lệ:

```
bash scripts/blogger-http.sh refresh-token <client_id> <client_secret> <refresh_token> <out-file>.json
node scripts/blogger-json.js save-refreshed-access-token blogger-accounts.local.json <blog-key> <out-file>.json
```

Nếu response trả lỗi (thường do `refresh_token` bị revoke thủ công, hoặc project OAuth consent screen bị thu hồi quyền) → coi như mất token, quay lại mục "Lấy refresh_token" phía trên.

## Tra blog ID từ blog URL (1 lần / blog)

Blogger API cần `blog_id` (số), không nhận trực tiếp blog URL cho phần lớn endpoint. Tra 1 lần, lưu lại dùng mãi:

```
bash scripts/blogger-http.sh get-blog-by-url <access_token> <blog-url> <out-file>.json
node scripts/blogger-json.js save-blog-id blogger-accounts.local.json <blog-key> <out-file>.json
```

## Nhúng ảnh vào bài (base64 data URI, KHÔNG hotlink)

Blogger API không có "featured image" hay "media upload" riêng như WordPress, nên cách chèn ảnh là nhúng thẳng vào `content`. **KHÔNG** để `<img src="...">` trỏ thẳng về URL ảnh gốc trên site nguồn — đã gặp thực tế: site nguồn chặn hotlink (yêu cầu cookie/challenge như lúc fetch trang, hoặc chặn theo Referer), khiến `curl` tải ảnh về máy vẫn trả 200 OK bình thường (vì có cookie/User-Agent đúng) nhưng khi Blogger phục vụ ảnh đó cho người đọc thật thì bị vỡ (trình duyệt người đọc không có cookie đó, hoặc Referer là blogspot.com bị site nguồn chặn).

Cách đúng — nhúng ảnh base64 trực tiếp vào HTML, không phụ thuộc domain nguồn nữa:

```
node scripts/blogger-json.js embed-image-datauri <content-html-file> <image-file> <mime-type> <out-file>
```

Trong content viết ở bước rewrite, đặt sẵn 1 thẻ `<img src="PLACEHOLDER" alt="...">` — lệnh trên tìm thẻ `<img ...src="...">` đầu tiên và thay `src` bằng `data:<mime>;base64,<...>` từ file ảnh đã tải ở bước "Chuẩn bị ảnh". Không tìm thấy `<img>` nào trong content → lệnh báo lỗi và exit 1, coi như không có ảnh, bỏ qua bước này.

## Tạo & publish bài

Content là HTML thường (không phải Gutenberg block markup — đó là đặc thù riêng WordPress). Chuẩn bị content HTML (đã nhúng ảnh base64 nếu có) rồi:

```
node scripts/blogger-json.js build-post-payload <content-html-file> "<title>" <payload-file>.json
bash scripts/blogger-http.sh create-post <blog-id> <access_token> <payload-file>.json <out-file>.json
node scripts/blogger-json.js show-post-result <out-file>.json
```

Mặc định `POST .../posts/` publish bài NGAY (không phải draft) — không cần set thêm field nào để publish. `show-post-result` in ra `id`, `url`, `title`, `status`. Chỉ coi là thành công khi có `url` hợp lệ và `status` là `"LIVE"`.

## Cập nhật bài đã đăng

Nếu cần sửa lại 1 bài đã publish (vd: phát hiện ảnh vỡ sau khi đăng, cần build lại payload rồi update):

```
bash scripts/blogger-http.sh update-post <blog-id> <post-id> <access_token> <payload-file>.json <out-file>.json
```

`<post-id>` lấy từ field `id` trong response lúc `create-post` (hoặc `show-post-result`). URL bài viết giữ nguyên sau khi update.

## Xử lý trang nguồn bị chặn bot (JS cookie challenge)

Một số site nguồn dùng WAF/CDN chặn request không chạy JS: response ban đầu rất ngắn, chỉ chứa 1 thẻ script dạng:

```html
<script>document.cookie="XXX=yyy...; expires=...; path=/";window.location.reload(true);</script>
```

Nếu gặp response dạng này (kiểm tra bằng cách đọc lại file `<out-file>` sau `fetch-source`, thấy size rất nhỏ và chỉ chứa script này):
1. Trích tên + giá trị cookie từ script đó.
2. Gọi lại `fetch-source` cùng URL, truyền thêm cookie ở tham số thứ 3:
   ```
   bash scripts/blogger-http.sh fetch-source <url> <out-file> "XXX=yyy"
   ```
   Lần này sẽ trả về HTML đầy đủ của trang.

Đây là kiểu JS-redirect phổ biến ở nhiều CMS/CDN cho request đầu tiên, áp dụng cho trang public không yêu cầu đăng nhập — không phải bypass xác thực hay bảo mật.

## scripts/blogger-http.sh — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `fetch-source` | `<url> <out-file> [cookie]` | Đọc bài nguồn |
| `download-image` | `<url> <out-file> <cookie>` | Tải ảnh đại diện |
| `refresh-token` | `<client_id> <client_secret> <refresh_token> <out-file>` | Trước mỗi lần gọi Blogger API |
| `get-blog-by-url` | `<access_token> <blog-url> <out-file>` | Tra blog ID lần đầu |
| `create-post` | `<blog-id> <access_token> <payload-file> <out-file>` | Tạo & publish bài |
| `update-post` | `<blog-id> <post-id> <access_token> <payload-file> <out-file>` | Sửa lại bài đã đăng |

## scripts/blogger-json.js — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `get-account-field` | `<accounts-json-file> <blog-key> <field>` | Đọc client_id/client_secret/refresh_token/access_token/blog_id đã lưu |
| `set-client` | `<accounts-json-file> <blog-key> <client_id> <client_secret> <blog-url>` | Setup lần đầu |
| `save-tokens` | `<accounts-json-file> <blog-key> <token-response-file>` | Sau khi chạy `google-oauth-server.js` lần đầu |
| `save-refreshed-access-token` | `<accounts-json-file> <blog-key> <refresh-response-file>` | Sau mỗi lần `refresh-token` |
| `save-blog-id` | `<accounts-json-file> <blog-key> <blog-byurl-response-file>` | Sau `get-blog-by-url` |
| `build-post-payload` | `<content-html-file> <title> <out-file>` | Trước `create-post` |
| `embed-image-datauri` | `<content-html-file> <image-file> <mime-type> <out-file>` | Trước `build-post-payload`, nếu có ảnh |
| `word-count` | `<html-file>` | Self-check độ dài bài viết lại |
| `show-post-result` | `<post-response-file>` | Verify + lấy id/url/title/status |

## Known limits

- Access token Google sống ~1 giờ — BẮT BUỘC refresh trước mỗi lần gọi API tạo post/tra blog ID, không tái sử dụng access_token cũ quá lâu.
- `refresh_token` chỉ được cấp khi authorize URL có `access_type=offline`. Nếu user đã từng authorize app này trước đó mà không có `prompt=consent`, lần authorize sau có thể KHÔNG trả `refresh_token` mới — `google-oauth-server.js` đã set sẵn cả 2 param này nên không gặp vấn đề này.
- OAuth consent screen ở chế độ "Testing" (không publish) vẫn hoạt động bình thường cho tài khoản cá nhân, miễn email đã có trong Test users — không cần verify app với Google.
- Blogger API không có "featured image" hay "media upload" riêng — ảnh được nhúng vào `content` bằng thẻ `<img>` dạng base64 data URI (xem mục "Nhúng ảnh vào bài"), KHÔNG trỏ thẳng URL ảnh gốc vì nhiều site nguồn chặn hotlink khiến ảnh vỡ phía người đọc dù lúc tải về vẫn thành công.
- `data:` URI làm payload JSON phình to hơn (ảnh ~100KB thành ~130KB base64 text) — bình thường với Blogger, không cần lo giới hạn kích thước cho 1 ảnh đại diện.

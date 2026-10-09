# Đăng bài lên Mastodon qua API — Steps

Mastodon có REST API mở, tài liệu đầy đủ tại `docs.joinmastodon.org`. Xác thực bằng **access token tĩnh** tạo trực tiếp trong web UI (Preferences → Development) — KHÔNG có luồng OAuth qua trình duyệt như `share-bai-wp`/`share-bai-blogger`/`share-bai-ggr`/`share-bai-tumblr`, KHÔNG có `client_secret`/`refresh_token` nào cả. Gần giống `share-bai-wix` về độ đơn giản (1 token dùng mãi, không hết hạn), nhưng còn đơn giản hơn: không cần `site_id`/`account_id`/`member_id` riêng.

Mọi lệnh gọi HTTP dùng qua `scripts/mastodon-http.sh`, mọi xử lý JSON dùng qua `scripts/mastodon-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp, vì 2 script này được allowlist trong `.claude/settings.json` để pipeline chạy không cần xác nhận thủ công từng lệnh.

## Contents

- Setup access token (1 lần / tài khoản Mastodon)
- Giới hạn ký tự & cách Mastodon tính link
- Upload ảnh (2 bước: tải về + upload multipart)
- Tạo & đăng status
- Xử lý trang nguồn bị chặn bot
- scripts/mastodon-http.sh — reference lệnh
- scripts/mastodon-json.js — reference lệnh
- Known limits

## Setup access token (1 lần / tài khoản Mastodon)

1. Hướng dẫn user đăng nhập đúng tài khoản Mastodon đích trên trình duyệt, tại instance đích (vd `https://mastodon.social`).
2. Vào **Preferences** (Cài đặt) → **Development** (Phát triển, ở menu bên trái) → bấm **New application** (Ứng dụng mới).
3. Đặt tên ứng dụng bất kỳ (vd `share-bai-mastodon`). Ở phần **Scopes**, tích tối thiểu `write:statuses` và `write:media` (để giữ `read` mặc định cũng không sao, không cần bỏ).
4. Bấm **Submit**, sau đó bấm vào tên ứng dụng vừa tạo trong danh sách để mở chi tiết.
5. Copy giá trị **"Your access token"** — đây là giá trị DUY NHẤT cần lưu (KHÔNG phải "Client key"/"Client secret", hai giá trị đó chỉ dùng cho luồng OAuth authorization-code, không cần ở đây).
6. Lưu vào `mastodon-accounts.local.json`:
   ```
   node scripts/mastodon-json.js set-credentials mastodon-accounts.local.json <account-key> <access_token> <instance_url> [account_handle]
   ```
   `<account-key>` khuyến nghị dùng dạng `<username>@<instance-domain>` (vd `tenban@mastodon.social`) để không nhầm khi 1 người quản lý nhiều tài khoản/instance khác nhau. `<instance_url>` dạng đầy đủ có scheme (vd `https://mastodon.social`, không có dấu `/` cuối — script tự strip nếu có).

Có thể verify token còn hợp lệ bất kỳ lúc nào bằng:
```
bash scripts/mastodon-http.sh verify-token <instance_url> <access_token> <out-file>.json
```
Response có field `username` → token hợp lệ. HTTP 401 → token bị revoke, quay lại bước 1-6 lấy token mới.

## Giới hạn ký tự & cách Mastodon tính link

Xác nhận trực tiếp từ `configuration.statuses` trên endpoint public `<instance_url>/api/v1/instance` (không cần auth) của mastodon.social:

- `max_characters`: **500**
- `characters_reserved_per_url`: **23** — MỌI URL trong status, bất kể độ dài thật, được tính CỐ ĐỊNH 23 ký tự khi so với giới hạn 500 (tương tự cách Twitter rút gọn link qua t.co). Đây là hành vi thật của instance, không phải ước lượng.
- `max_media_attachments`: **4**

Vì lý do này, KHÔNG được tự đếm ký tự bằng `.length` thô của chuỗi — phải qua `node scripts/mastodon-json.js char-count <file>`, script này thay mỗi URL bằng 23 ký tự placeholder trước khi đếm, giống hệt cách Mastodon tính.

## Upload ảnh (2 bước: tải về + upload multipart)

Khác Tumblr/Wix (dùng thẳng URL ảnh ngoài, hoặc Wix tự fetch từ URL), Mastodon **bắt buộc phải upload bytes ảnh thật** qua multipart form — không nhận URL ảnh ngoài. Vì vậy phải tải ảnh về máy trước (giống `share-bai-wp`):

```
bash scripts/mastodon-http.sh download-image <image-url-nguồn> <local-file> <cookie>
bash scripts/mastodon-http.sh upload-media <instance_url> <access_token> <local-file> <mime-type> "<mô tả ảnh>" <out-file>.json
node scripts/mastodon-json.js show-media-result <out-file>.json
```

`<cookie>` để trống (`""`) nếu Step 3 (đọc bài nguồn) không cần cookie challenge. Giới hạn theo `configuration.media_attachments` của mastodon.social: ảnh ≤16MB (16777216 bytes), định dạng hỗ trợ JPEG/PNG/GIF/WebP/HEIC/HEIF/AVIF — đoán `mime-type` từ đuôi file URL nguồn (`.jpg`/`.jpeg` → `image/jpeg`, `.png` → `image/png`, `.webp` → `image/webp`, `.gif` → `image/gif`).

`show-media-result` in `id`/`type`/`url`/`preview_url`. Ảnh xử lý **đồng bộ** (response HTTP 200, có `url` ngay) trong tuyệt đại đa số trường hợp — chỉ video/gif lớn mới trả HTTP 202 với `url: null` (async). Nếu gặp `url: null` (hiếm với ảnh tĩnh), poll 1 lần:
```
bash scripts/mastodon-http.sh get-media <instance_url> <access_token> <media-id> <out-file>.json
```
Nếu vẫn `null` sau 1 lần poll → bỏ ảnh, đăng tiếp không ảnh (xem Recovery trong `SKILL.md`).

## Tạo & đăng status

```
node scripts/mastodon-json.js build-status-payload <status-text-file> <visibility> <out-file>.json [media_id...]
bash scripts/mastodon-http.sh create-status <instance_url> <access_token> <out-file>.json <status-response-file>.json
node scripts/mastodon-json.js show-post-result <status-response-file>.json
```

`build-status-payload` đọc file text toot (đã viết ở Step 4 theo `references/rewrite-guidelines.md`), bọc thành JSON body `{"status": "...", "visibility": "public", "media_ids": [...]}` — `media_ids` chỉ có khi Step 5 upload ảnh thành công (0-4 media id truyền vào cuối lệnh). `visibility` mặc định `"public"` (hiển thị trên federated timeline + hashtag search), có thể đổi `"unlisted"`/`"private"`/`"direct"` nếu user yêu cầu.

`show-post-result` in `id`/`url`/`uri`/`created_at`/`visibility`/`error`. `url` chính là link công khai của toot vừa đăng (dạng `https://<instance>/@<username>/<id>`). Response có field `error` (thay vì `id`) → đăng thất bại, đọc message cụ thể (thường do vượt 500 ký tự — HTTP 422 — hoặc token thiếu scope `write:statuses`).

## Xử lý trang nguồn bị chặn bot (JS cookie challenge)

Một số site nguồn dùng WAF/CDN chặn request không chạy JS: response ban đầu rất ngắn, chỉ chứa 1 thẻ script dạng:

```html
<script>document.cookie="XXX=yyy...; expires=...; path=/";window.location.reload(true);</script>
```

Nếu gặp response dạng này (kiểm tra bằng cách đọc lại file `<out-file>` sau `fetch-source`, thấy size rất nhỏ và chỉ chứa script này):
1. Trích tên + giá trị cookie từ script đó.
2. Gọi lại `fetch-source` cùng URL, truyền thêm cookie ở tham số thứ 3:
   ```
   bash scripts/mastodon-http.sh fetch-source <url> <out-file> "XXX=yyy"
   ```
   Lần này sẽ trả về HTML đầy đủ của trang.

Đây là kiểu JS-redirect phổ biến ở nhiều CMS/CDN cho request đầu tiên, áp dụng cho trang public không yêu cầu đăng nhập — không phải bypass xác thực hay bảo mật.

## scripts/mastodon-http.sh — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `fetch-source` | `<url> <out-file> [cookie]` | Step 3 — đọc bài nguồn |
| `download-image` | `<url> <out-file> <cookie>` | Step 5 — tải ảnh về trước khi upload |
| `verify-token` | `<instance_url> <access_token> <out-file>` | Step 2 — kiểm tra token còn hợp lệ |
| `upload-media` | `<instance_url> <access_token> <local-file> <mime-type> <description> <out-file>` | Step 5 — upload ảnh lấy media_id |
| `get-media` | `<instance_url> <access_token> <media-id> <out-file>` | Step 5 — poll nếu ảnh chưa xử lý xong (hiếm) |
| `create-status` | `<instance_url> <access_token> <payload-file> <out-file>` | Step 6 — đăng toot |

## scripts/mastodon-json.js — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `get-account-field` | `<accounts-json-file> <account-key> <field>` | Step 1-2 — đọc access_token/instance_url đã lưu |
| `set-credentials` | `<accounts-json-file> <account-key> <access_token> <instance_url> [account_handle]` | Setup lần đầu |
| `char-count` | `<status-text-file>` | Step 4 — đếm ký tự theo đúng cách Mastodon tính (link = 23 ký tự) |
| `build-status-payload` | `<status-text-file> <visibility> <out-file> [media_id...]` | Step 6 — trước `create-status` |
| `show-media-result` | `<media-upload-response-file>` | Step 5 — lấy media_id + kiểm tra đã xử lý xong chưa |
| `show-post-result` | `<status-response-file>` | Step 7 — verify + lấy id/url |

## Known limits

- Access token tạo qua Preferences → Development **không hết hạn** — không có bước refresh nào, khác 4 skill kia (`wp`/`blogger`/`ggr`/`tumblr`). Chỉ mất hiệu lực nếu user chủ động revoke ứng dụng trong Preferences → Development, hoặc đổi mật khẩu tài khoản (một số trường hợp).
- Giới hạn 500 ký tự và `characters_reserved_per_url: 23` là cấu hình CỦA TỪNG INSTANCE (đọc từ `/api/v1/instance`, không auth) — đã xác nhận với mastodon.social, nhưng nếu account đích chuyển sang 1 instance tự host khác, giá trị này CÓ THỂ khác (một số instance tăng `max_characters` lên vài nghìn). Nếu nghi ngờ, gọi `curl <instance_url>/api/v1/instance | grep max_characters` để xác nhận lại trước khi build content dựa cứng vào 500.
- Rate limit API chung: 300 requests/5 phút theo IP hoặc theo token (tùy endpoint) — hiếm khi chạm với tần suất đăng bài thông thường của skill này.
- Ảnh: tối đa 16MB (`image_size_limit`), tối đa 4 ảnh/status (`max_media_attachments`) — skill này chỉ dùng 0-1 ảnh nên không chạm giới hạn.
- Mastodon KHÔNG hỗ trợ rich text/Markdown trong status mặc định (content type `text/plain`) — chỉ URL/mention (`@user`)/hashtag (`#tag`) được auto-linkify, mọi cú pháp Markdown khác hiển thị nguyên văn ký tự thừa.

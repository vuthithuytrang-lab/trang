# Đăng bài lên Tumblr qua API v2 — Steps

Tumblr có REST API tạo bài trực tiếp (khác `share-bai-ggr` phải giả lập qua gửi email). Bài viết dùng **Neue Post Format (NPF)** — nội dung là 1 mảng "content blocks" (`{"type":"text",...}`, `{"type":"image",...}`), không phải HTML/Gutenberg.

Mọi lệnh gọi HTTP dùng qua `scripts/tumblr-http.sh`, mọi xử lý JSON/NPF dùng qua `scripts/tumblr-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp, vì 2 script này được allowlist trong `.claude/settings.json` (domain hardcode sẵn trong script) để pipeline chạy không cần xác nhận thủ công từng lệnh.

## Contents

- Setup OAuth app (1 lần / Tumblr account)
- Lấy refresh_token (1 lần / blog)
- Refresh access_token (mỗi lần chạy, tự động)
- Cấu trúc NPF content blocks
- Gắn link vào từ khóa chính (formatting offset)
- Ảnh trong bài (external URL — không cần bước upload riêng)
- Tạo & publish bài (Tumblr API `posts`)
- Xử lý trang nguồn bị chặn bot
- scripts/tumblr-http.sh — reference lệnh
- scripts/tumblr-json.js — reference lệnh
- Known limits

## Setup OAuth app (1 lần / Tumblr account)

1. Hướng dẫn user đăng ký app tại `https://www.tumblr.com/oauth/apps/register`, đăng nhập bằng tài khoản sở hữu blog đích. Các trường bắt buộc (đánh dấu `*`): Application Name, Application Website, Application Description (≤400 ký tự), Administrative contact email, Default callback URL, và (không đánh dấu `*` nhưng cần điền để OAuth2 hoạt động) OAuth2 redirect URLs.
2. **Default callback URL** và **OAuth2 redirect URLs**: dùng `http://localhost:8767/` — **KHÔNG dùng `http://127.0.0.1:8767/`**, Tumblr từ chối raw-IP domain lúc đăng ký ("This url's domain is not valid"), chỉ chấp nhận `localhost` hoặc domain thật.
3. Icons (128x128, 64x64, 44x44, 32x32, 16x16 PNG) không đánh dấu `*` trong form — có thể để trống.
4. Sau khi submit, trang app hiện **OAuth Consumer Key** + **Secret Key** — lưu vào `tumblr-accounts.local.json` theo blog identifier (key là domain dạng `<tên-blog>.tumblr.com`):
   ```
   node scripts/tumblr-json.js set-client tumblr-accounts.local.json <blog-key> <client_id> <client_secret> <blog_identifier>
   ```
   `<blog-key>` khuyến nghị dùng chính `<blog_identifier>`.

## Lấy refresh_token (1 lần / blog)

Tumblr hỗ trợ cả OAuth 1.0a (legacy) và OAuth2 — skill này dùng **OAuth2 authorization code grant** (đơn giản hơn OAuth 1.0a vì không cần request-signing HMAC-SHA1, và có refresh_token).

1. Chạy:
   ```
   node scripts/tumblr-oauth-server.js <client_id> <client_secret> <out-file>.json
   ```
   Script tự mở 1 local HTTP server tạm (mặc định port 8767, khớp với callback URL đã đăng ký ở bước Setup) và in ra 1 authorize URL, xin scope `write offline_access` (`write` để đăng bài, `offline_access` **bắt buộc** để nhận `refresh_token` — thiếu scope này Tumblr chỉ cấp access_token ngắn hạn không refresh được).
2. Đưa URL đó cho user mở trong trình duyệt, đăng nhập đúng tài khoản Tumblr **sở hữu blog đích**, bấm Allow. KHÔNG cần copy-paste URL redirect thủ công — script tự bắt request redirect về `localhost:8767` (kèm kiểm tra `state` khớp để chống CSRF) và tự đổi code lấy token.
3. Script tự thoát (exit code 0) sau khi ghi response token vào `<out-file>.json`. Timeout 5 phút nếu user không thao tác.
4. Lưu vào `tumblr-accounts.local.json`:
   ```
   node scripts/tumblr-json.js save-tokens tumblr-accounts.local.json <blog-key> <out-file>.json
   ```
   Lệnh này tự kiểm tra response có `refresh_token` không (bắt buộc phải có ở lần đầu — nếu thiếu, nghĩa là scope thiếu `offline_access`, chạy lại bước 1).

## Refresh access_token (mỗi lần chạy, tự động)

Access token Tumblr sống ngắn hạn — refresh trước mỗi lần gọi API tạo bài. Việc này KHÔNG cần user tương tác (silent), chỉ cần `refresh_token` còn hợp lệ:

```
bash scripts/tumblr-http.sh refresh-token <client_id> <client_secret> <refresh_token> <out-file>.json
node scripts/tumblr-json.js save-refreshed-access-token tumblr-accounts.local.json <blog-key> <out-file>.json
```

Response refresh có thể trả kèm `refresh_token` mới (rotating) hoặc không — `save-refreshed-access-token` tự xử lý cả 2 trường hợp, giữ token cũ nếu response không trả cái mới.

Nếu response trả lỗi (thường do `refresh_token` bị revoke thủ công, hoặc app OAuth bị xoá) → coi như mất token, quay lại mục "Lấy refresh_token" phía trên.

## Cấu trúc NPF content blocks

Nội dung bài là 1 mảng JSON các block, viết trực tiếp ra 1 file (vd `content-blocks.json`) bằng Write tool — KHÔNG cần helper script build từng block, vì cấu trúc JSON đơn giản và Claude viết trực tiếp chính xác hơn qua 1 script trung gian:

```json
[
  { "type": "text", "subtype": "heading1", "text": "Tiêu đề bài viết" },
  { "type": "text", "text": "Đoạn mở đầu chứa từ khóa chính..." },
  { "type": "image", "media": [{ "url": "https://.../anh.jpg", "type": "image/jpeg" }], "alt_text": "Mô tả ảnh" },
  { "type": "text", "subtype": "heading2", "text": "Heading phụ" },
  { "type": "text", "text": "Đoạn thân bài..." }
]
```

Subtype hợp lệ cho block text: `heading1` (dùng làm tiêu đề bài — Tumblr/NPF không có field `title` riêng), `heading2`, `quote`, `indented`, `chat`, `ordered-list-item`, `unordered-list-item`. Block đoạn văn thường thì bỏ `subtype`.

Giới hạn NPF: mỗi text block tối đa 4096 ký tự (đoạn văn thường không chạm ngưỡng này), tối đa 1000 block/bài, tối đa 30 image block/bài.

## Gắn link vào từ khóa chính (formatting offset)

NPF không dùng `<a href>` như HTML — phải thêm 1 entry vào mảng `formatting` của đúng block chứa từ khóa, với `start`/`end` là offset ký tự. Tính tay dễ sai lệch, dùng script:

```
node scripts/tumblr-json.js add-link-formatting <content-blocks-file> <block-index> "<từ khóa chính>" <source-url> <out-file>
```

`block-index` là vị trí (0-based) của block text chứa từ khóa trong mảng (thường là block 1 — đoạn mở đầu, ngay sau block 0 là heading1 tiêu đề). Script tự tìm offset, báo lỗi nếu không tìm thấy cụm từ, hoặc cụm từ xuất hiện >1 lần trong block đó (cần chọn cụm từ đủ dài để không ambiguous).

## Ảnh trong bài (external URL — không cần bước upload riêng)

Khác WordPress (phải upload lên media library lấy ID) và Google Groups/Gmail (phải nhúng `multipart/related` + `Content-ID` vì Gmail lột `data:` URI), NPF image block chấp nhận thẳng **URL công khai** trong field `media[].url` — Tumblr tự fetch và host lại ảnh khi tạo bài, không cần bước tải về + upload riêng:

```json
{ "type": "image", "media": [{ "url": "<url ảnh gốc từ bài nguồn>", "type": "image/jpeg" }], "alt_text": "..." }
```

Dùng thẳng URL `og:image`/ảnh đầu bài lấy được ở Step 3 — KHÔNG cần `download-image` như 3 skill kia. Nếu site nguồn chặn hotlink khiến Tumblr fetch ảnh thất bại lúc tạo bài (hiếm, và không đoán trước được), xem mục Recovery trong `SKILL.md` — bỏ block ảnh, đăng lại không ảnh.

## Tạo & publish bài (Tumblr API `posts`)

```
node scripts/tumblr-json.js build-post-payload <content-blocks-file> "<tag1,tag2>" <payload-file>.json <slug-ascii-kebab-case>
bash scripts/tumblr-http.sh create-post <blog_identifier> <access_token> <payload-file>.json <out-file>.json
node scripts/tumblr-json.js show-post-result <out-file>.json <blog_identifier>
```

`build-post-payload` bọc mảng content blocks thành body API đầy đủ (`content`, `tags`, `state: "published"`, `slug` nếu truyền tham số thứ 4). `show-post-result` in ra `id`/`state`/`post_url`/`meta` — `state` phải là `"published"` và `meta.status` phải `201` mới coi là thành công.

**Đã xác nhận qua thực tế chạy skill**: field `slug` được endpoint NPF chấp nhận dù không có trong ví dụ tài liệu chung — nếu không truyền, Tumblr tự sinh slug từ tiêu đề và percent-encode dấu tiếng Việt (vd `d%E1%BB%8Bch-vu-...`), ra URL khó đọc. Luôn truyền slug ASCII kebab-case đã tạo ở Step 4 để có URL sạch, giống quy ước `share-bai-wp`/`share-bai-blogger`.

**Đã xác nhận qua thực tế chạy skill**: response tạo bài của Tumblr CHỈ trả `id`/`state`/`display_text`, KHÔNG có `post_url` hay `blog_name` như một số ví dụ tài liệu NPF mô tả. `show-post-result` tự dựng permalink từ `blog_identifier` (tham số truyền vào) + `id`: `https://<blog_identifier>/post/<id>`.

**Đã xác nhận qua thực tế chạy skill**: field `tags` PHẢI là 1 chuỗi phân tách bởi dấu phẩy (`"tag1,tag2,tag3"`), KHÔNG phải mảng JSON (`["tag1","tag2"]`) như ví dụ trong tài liệu NPF chung mô tả — gửi dạng mảng khiến API trả `400 Bad Request` với message chung chung `"Posting failed. Please try again."` (code `8001`, không nêu rõ field nào sai, không phải lỗi liên quan content/ảnh). `build-post-payload` đã tự xử lý đúng (nhận input dạng `"tag1,tag2"`, tự join lại thành string trước khi gửi) — không tự sửa lại thành mảng.

## Xử lý trang nguồn bị chặn bot (JS cookie challenge)

Một số site nguồn dùng WAF/CDN chặn request không chạy JS: response ban đầu rất ngắn, chỉ chứa 1 thẻ script dạng:

```html
<script>document.cookie="XXX=yyy...; expires=...; path=/";window.location.reload(true);</script>
```

Nếu gặp response dạng này (kiểm tra bằng cách đọc lại file `<out-file>` sau `fetch-source`, thấy size rất nhỏ và chỉ chứa script này):
1. Trích tên + giá trị cookie từ script đó.
2. Gọi lại `fetch-source` cùng URL, truyền thêm cookie ở tham số thứ 3:
   ```
   bash scripts/tumblr-http.sh fetch-source <url> <out-file> "XXX=yyy"
   ```
   Lần này sẽ trả về HTML đầy đủ của trang.

Đây là kiểu JS-redirect phổ biến ở nhiều CMS/CDN cho request đầu tiên, áp dụng cho trang public không yêu cầu đăng nhập — không phải bypass xác thực hay bảo mật.

## scripts/tumblr-http.sh — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `fetch-source` | `<url> <out-file> [cookie]` | Step 3 — đọc bài nguồn |
| `refresh-token` | `<client_id> <client_secret> <refresh_token> <out-file>` | Step 2 — trước mỗi lần gọi API |
| `create-post` | `<blog_identifier> <access_token> <payload-file> <out-file>` | Step 6 — tạo & publish bài |
| `delete-post` | `<blog_identifier> <access_token> <post-id> <out-file>` | Dọn bài test/lỗi khi cần (không thuộc pipeline chính) |
| `exchange-code` | `<client_id> <client_secret> <redirect_uri> <code> <out-file>` | Fallback thủ công khi `tumblr-oauth-server.js` đã thoát nhưng code vẫn còn hiệu lực (code Tumblr hết hạn rất nhanh, ~1 phút, nên phải dùng ngay) |

## scripts/tumblr-json.js — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `get-account-field` | `<accounts-json-file> <blog-key> <field>` | Step 1-2 — đọc client_id/client_secret/access_token/blog_identifier đã lưu |
| `set-client` | `<accounts-json-file> <blog-key> <client_id> <client_secret> <blog_identifier>` | Setup lần đầu |
| `save-tokens` | `<accounts-json-file> <blog-key> <token-response-file>` | Sau khi chạy `tumblr-oauth-server.js` lần đầu |
| `save-refreshed-access-token` | `<accounts-json-file> <blog-key> <refresh-response-file>` | Sau mỗi lần `refresh-token` |
| `add-link-formatting` | `<content-blocks-file> <block-index> <link-text> <url> <out-file>` | Step 4 — gắn link từ khóa chính |
| `build-post-payload` | `<content-blocks-file> <tags-or-empty> <out-file> [slug]` | Step 6 — trước `create-post` |
| `word-count` | `<content-blocks-file>` | Step 4 — self-check độ dài bài viết lại |
| `show-post-result` | `<post-response-file> <blog_identifier>` | Step 7 — verify + lấy id/post_url (tự dựng)/state |

## Known limits

- Rate limit app mới đăng ký: 1.000 request/giờ, 5.000 request/ngày — dư cho nhu cầu đăng vài bài/lần; nếu cần nhiều hơn, Tumblr cho request gỡ giới hạn qua link trên trang app.
- NPF không có field `title` riêng — dùng text block đầu tiên với `subtype: "heading1"` làm tiêu đề, hiển thị đúng như tiêu đề bài trên Tumblr.
- Image block dùng external URL: Tumblr tự fetch và host lại lúc tạo bài — nếu site nguồn chặn hotlink với chính server Tumblr (khác với chặn browser thường), ảnh có thể fail dù URL vẫn mở được bình thường trên trình duyệt. **Đã xác nhận qua thực tế**: trường hợp này trả `400` với `errors[0].code: 0`, message `"Internet strangeness. Try again."` — khác hẳn lỗi cấu trúc payload thông thường (thường có `code` khác 0 và message mô tả rõ field sai). Gặp đúng dấu hiệu này → áp dụng Recovery ở Step 6 (bỏ ảnh, đăng lại). Không có cách kiểm tra trước.
- `refresh_token` không có thời hạn cố định công bố rõ như Google (7 ngày ở trạng thái Testing) — nếu bị revoke, lỗi trả về từ `refresh-token` sẽ rõ ràng (401/400), xử lý bằng cách quay lại "Lấy refresh_token".
- **Đã xác nhận qua thực tế (2026-09-18)**: text block với `subtype: "bullet-list-item"` (kể cả kèm `indent_level: 0`) khiến `/v2/blog/{id}/posts` trả `400` chung chung (`errors[].code: 0`, message ngẫu nhiên kiểu "Measly little error."/"Something goofed." — không nêu field sai, khác hẳn dấu hiệu lỗi ảnh ở trên). Đã bisect bằng payload tối thiểu (bỏ dần từng block) để xác nhận đúng `bullet-list-item` là nguyên nhân, không phải do slug/tags/formatting/Unicode. Cách né: không dùng subtype này — render danh sách thành các text block thường, mỗi dòng tự thêm tiền tố `"- "` (vẫn hiển thị được nội dung, chỉ mất style bullet thật của Tumblr).

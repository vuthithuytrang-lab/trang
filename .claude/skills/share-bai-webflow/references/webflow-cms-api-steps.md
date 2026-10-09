# Webflow CMS API — Steps

Đăng bài lên Webflow CMS qua REST API v2 chính thức (`api.webflow.com/v2`), không dùng browser automation. Mọi lệnh gọi HTTP dùng qua `scripts/webflow-http.sh`, mọi xử lý JSON dùng qua `scripts/webflow-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp, vì 2 script này đã được allowlist trong `.claude/settings.json` để pipeline chạy không cần xác nhận thủ công từng lệnh.

## Contents

- Setup Site Token (1 lần / site) — và cách phát hiện free plan không cho tạo token
- Xác định site_id, collection_id, field slug
- Upload ảnh (Assets API, 2 bước)
- Tạo & publish item
- Xây live URL từ site domain + collection slug + item slug
- Xử lý trang nguồn bị chặn bot (JS cookie challenge)
- scripts/webflow-http.sh — reference lệnh
- scripts/webflow-json.js — reference lệnh
- Known limits

## Setup Site Token (1 lần / site)

Webflow CMS API không dùng OAuth app cho use case cá nhân/nội bộ — dùng Site Token, tạo trực tiếp trong site settings, không hết hạn tới khi user tự thu hồi.

1. Hướng dẫn user vào Webflow Designer/Dashboard của site đích → **Site settings → Apps & Integrations → API access**.
2. Bấm **Generate API token**, chọn scope tối thiểu: `sites:read`, `cms:read`, `cms:write`, `assets:write`.
3. Copy token, lưu vào `webflow-accounts.local.json` qua `node scripts/webflow-json.js save-token <file> <site-key> <token>`.

**Phát hiện free plan không cho tạo token — KHÔNG đoán, kiểm tra trực tiếp:**

- Nếu user báo mục "API access" không hiện nút "Generate API token" (hoặc cả mục API access không xuất hiện trong Site settings) → đây là dấu hiệu site đang ở gói free (Starter). Dừng lại, báo rõ cho user: cần nâng cấp site lên gói trả phí (tối thiểu Basic Site plan) mới thấy mục này — KHÔNG hướng dẫn user thử cách khác để "lách" (không có cách nào khác, Webflow không có anonymous/public API cho CMS write).
- Nếu user đã tạo được token → luôn verify bằng lệnh thật (`list-sites`) trước khi tin token hợp lệ, đừng giả định free plan chắc chắn chặn hay chắc chắn không chặn — tài liệu chính thức Webflow không nói rõ ràng điều này, chỉ có thể xác nhận qua thao tác thật trên tài khoản user.

## Xác định site_id, collection_id, field slug

Sau khi có token:

```
bash scripts/webflow-http.sh list-sites <token> <out>.json
```

- HTTP 200 → đọc `out.json`, dùng `node scripts/webflow-json.js find-site-id <out>.json "<tên hoặc domain site>"` để lấy `id` (site_id). Không tìm thấy site khớp → liệt kê toàn bộ `sites[].displayName` cho user chọn.
- HTTP 401 → token sai hoặc bị thu hồi. Quay lại bước tạo token mới, KHÔNG tự đoán token khác.
- HTTP 403 → token hợp lệ nhưng bị từ chối quyền — nguyên nhân thường gặp nhất là site chưa ở gói đủ để dùng API (xem mục trên) hoặc thiếu scope lúc tạo token. Báo rõ 2 khả năng này cho user, không suy đoán thêm nguyên nhân khác.

Lấy collection đích:

```
bash scripts/webflow-http.sh list-collections <site_id> <token> <out>.json
node scripts/webflow-json.js find-collection-id <out>.json "<tên collection, vd Blog Posts>"
```

Không tìm thấy hoặc user không chỉ định tên → liệt kê toàn bộ `collections[].displayName` cho user chọn, KHÔNG tự ý chọn collection đầu tiên trong danh sách (site có thể có nhiều collection không liên quan tới blog).

Lấy field schema của collection đã chọn — Collection ở mỗi site Webflow có schema field TỰ ĐỊNH NGHĨA theo site, không cố định như slug tiêu chuẩn:

```
bash scripts/webflow-http.sh get-collection <collection_id> <token> <out>.json
node scripts/webflow-json.js find-field-slug <out>.json RichText
node scripts/webflow-json.js find-field-slug <out>.json Image
```

`find-field-slug` trả về slug của field đầu tiên khớp `type` (`RichText` cho nội dung thân bài, `Image` cho ảnh đại diện — có thể rỗng nếu collection không có field ảnh, khi đó bỏ qua ảnh). Field built-in `name` (tiêu đề) và `slug` (URL slug) luôn tồn tại, không cần tra.

Lưu toàn bộ vào `webflow-accounts.local.json`:

```
node scripts/webflow-json.js set-site <file> <site-key> <site_id> <collection_id> <field-body-slug> <field-image-slug-or-rỗng> <site-domain>
```

`<site-domain>` lấy từ `customDomains[0].url` hoặc `defaultDomain` (dạng `*.webflow.io`) trong response `list-sites` — dùng để build live URL ở bước cuối.

## Upload ảnh (Assets API, 2 bước)

Webflow không nhận file upload trực tiếp trong request tạo item — phải tạo asset metadata trước, upload binary lên URL S3 mà Webflow trả về, rồi dùng `hostedUrl` của asset đó làm giá trị field ảnh.

```
node scripts/webflow-json.js md5-file <local-image-file>
bash scripts/webflow-http.sh create-asset <site_id> <token> "<file-name.jpg>" "<md5-hash-vừa-tính>" <asset-meta>.json
```

Response chứa `uploadUrl` + `uploadDetails` (object nhiều field, dùng làm form field khi POST binary lên `uploadUrl`) và `hostedUrl` (URL cuối cùng để tham chiếu trong CMS item, có sẵn ngay cả trước khi upload xong).

```
bash scripts/webflow-http.sh upload-asset "<uploadUrl từ response trên>" <asset-meta>.json <local-image-file> <upload-result>.json
node scripts/webflow-json.js show-asset-hosted-url <asset-meta>.json
```

`upload-asset` đọc field trong `uploadDetails` động (không hardcode tên field) và forward nguyên vào request S3. Lỗi ở bước `create-asset` hoặc `upload-asset` (4xx/5xx) → bỏ qua ảnh, tiếp tục tạo item không có field ảnh. KHÔNG chặn pipeline chỉ vì ảnh.

## Tạo & publish item

```
node scripts/webflow-json.js build-item-payload <content-html-file> "<title>" "<slug-kebab-khong-dau>" <field-body-slug> <field-image-slug-hoac-rong> <hosted-url-hoac-rong> <payload>.json
bash scripts/webflow-http.sh create-item <collection_id> <token> <payload>.json <create-result>.json
```

Payload set sẵn `isDraft:false` — theo tài liệu Webflow, tạo item với `isDraft:false` publish ngay khi tạo. Để chắc chắn item thực sự lên live site (tránh trường hợp chỉ cập nhật staging), luôn gọi thêm bước publish tường minh:

```
node scripts/webflow-json.js show-item-result <create-result>.json
bash scripts/webflow-http.sh publish-item <collection_id> <token> "<item id từ create-result>" <publish-result>.json
```

`create-item` trả lỗi 4xx/5xx (vd field slug sai do schema đổi, thiếu field bắt buộc khác ngoài `name`/`slug`/body) → dừng, đọc message qua `node scripts/webflow-json.js show-error <create-result>.json`, báo cụ thể cho user, KHÔNG báo "đã đăng thành công".

## Xây live URL từ site domain + collection slug + item slug

Khác WordPress/Wix (API trả thẳng `URL`), Webflow response không trả live URL đầy đủ — tự ghép từ 3 phần:

```
https://<site-domain>/<collection-slug>/<item-slug>
```

- `site-domain` đã lưu ở bước set-site (Step 2).
- `collection-slug` lấy từ field `slug` trong response `list-collections` (khác `collection_id`).
- `item-slug` lấy từ `fieldData.slug` trong response `create-item`/`publish-item`.

Verify bằng `bash scripts/webflow-http.sh get-item <collection_id> <item_id> <token> <verify>.json`, kiểm tra `isDraft:false` và `lastPublished` có giá trị (không null) trước khi coi là publish thành công.

## Xử lý trang nguồn bị chặn bot (JS cookie challenge)

Một số site nguồn dùng WAF/CDN chặn request không chạy JS: response ban đầu rất ngắn, chỉ chứa 1 thẻ script dạng:

```html
<script>document.cookie="XXX=yyy...; expires=...; path=/";window.location.reload(true);</script>
```

Nếu gặp response dạng này (size rất nhỏ sau `fetch-source`):
1. Trích tên + giá trị cookie từ script đó.
2. Gọi lại `bash scripts/webflow-http.sh fetch-source <url> <out-file> "XXX=yyy"` — lần này trả về HTML đầy đủ.

## scripts/webflow-http.sh — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `fetch-source` | `<url> <out-file> [cookie]` | Step 3 — đọc bài nguồn |
| `download-image` | `<url> <out-file> <cookie>` | Step 5 — tải ảnh đại diện |
| `list-sites` | `<token> <out-file>` | Step 2 — verify token + lấy site_id/domain |
| `list-collections` | `<site_id> <token> <out-file>` | Step 2 — lấy collection_id + collection slug |
| `get-collection` | `<collection_id> <token> <out-file>` | Step 2 — lấy field schema (slug + type) |
| `create-asset` | `<site_id> <token> <file-name> <file-hash> <out-file>` | Step 6 — tạo asset metadata, lấy uploadUrl/hostedUrl |
| `upload-asset` | `<upload-url> <upload-details-file> <local-file> <out-file>` | Step 6 — upload binary lên S3 |
| `create-item` | `<collection_id> <token> <payload-file> <out-file>` | Step 7 — tạo item (isDraft:false) |
| `publish-item` | `<collection_id> <token> <item_id> <out-file>` | Step 7 — publish tường minh |
| `get-item` | `<collection_id> <item_id> <token> <out-file>` | Step 8 — verify đã live |

## scripts/webflow-json.js — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `get-account-field` | `<accounts-json-file> <site-key> <field>` | Step 1-2 — đọc token/site_id/collection_id đã lưu |
| `save-token` | `<accounts-json-file> <site-key> <token>` | Step 2 — lưu token mới |
| `set-site` | `<accounts-json-file> <site-key> <site_id> <collection_id> <field-body> <field-image> <site-domain>` | Step 2 — lưu cấu hình site |
| `md5-file` | `<local-file>` | Step 6 — tính fileHash cho create-asset |
| `find-site-id` | `<list-sites-response-file> <tên-hoặc-domain>` | Step 2 |
| `find-collection-id` | `<list-collections-response-file> <tên-collection>` | Step 2 |
| `find-field-slug` | `<collection-schema-file> <field-type>` | Step 2 |
| `build-item-payload` | `<content-html-file> <title> <slug> <field-body> <field-image> <image-url> <out-file>` | Step 7 |
| `word-count` | `<rich-text-html-file>` | Step 4 — self-check độ dài |
| `show-asset-hosted-url` | `<create-asset-response-file>` | Step 6 |
| `show-item-result` | `<create-or-publish-response-file>` | Step 7, 8 |
| `show-error` | `<response-json-file>` | Mọi bước gọi API lỗi |

## Known limits

- **Đã test live end-to-end thành công** (site thật `my-site.webflow.io`, free plan Starter, bài "Trung tâm giám sát an toàn không gian mạng là gì?"): tạo Site Token trên free plan, verify token qua `list-sites`, lấy collection "Blog Posts" + field slug `post-body`/`main-image` qua `get-collection`, upload ảnh 2 bước (`create-asset` → `upload-asset`, ETag S3 khớp đúng md5 hash), `create-item` với `isDraft:false`, `publish-item` tường minh, verify qua `get-item` (`isDraft:false` + `lastPublished` có giá trị), và xác nhận live URL trả HTTP 200 đúng nội dung. Toàn bộ cơ chế ở các mục trên đã xác nhận hoạt động thật, không còn là suy đoán.
- **Free plan (Starter) CÓ cho tạo Site Token** — đã xác nhận thật trên tài khoản free, dialog "Generate an API Token" hiện đầy đủ trong Site settings → Apps & Integrations → API access, không cần nâng cấp gói trả phí để lấy token cơ bản (scope `sites:read`/`cms:read`/`cms:write`/`assets:write` đều dùng được). Vẫn giữ hướng dẫn phát hiện lỗi 401/403 ở Step 2 cho trường hợp site khác có giới hạn khác (workspace/plan cấu hình riêng).
- Bug đã gặp và sửa: `upload-asset` lúc đầu đọc nhầm toàn bộ response `create-asset` thay vì object `uploadDetails` lồng bên trong, khiến S3 báo lỗi thiếu field `key`. Đã sửa trong `scripts/webflow-http.sh` — script hiện đọc đúng `r.uploadDetails`.
- Collection schema khác nhau giữa các site — field slug cho nội dung/ảnh KHÔNG cố định, luôn tra qua `get-collection` mỗi khi setup site mới, không tái dùng slug từ site khác.
- Rate limit API Webflow theo phút, thấp hơn đáng kể ở gói self-serve so với gói Enterprise/Team — nếu gặp HTTP 429, dừng, báo user, không tự retry liên tục.

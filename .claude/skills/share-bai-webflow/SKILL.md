---
name: share-bai-webflow
description: This skill should be used when the user runs "/share-bai-webflow" with a main keyword and a source URL, or asks to "đăng bài lên Webflow", "share bài viết lên Webflow CMS", "viết lại bài từ URL này rồi đăng Webflow", "auto-post to Webflow", or "publish this article to my Webflow CMS collection". Reads the source article at the given URL, rewrites it in Vietnamese (~1000 words, no duplication, keeps the original meaning and facts, contains the main keyword hyperlinked to the source), then publishes it as a new Collection Item via the Webflow CMS API v2 (Site Token auth) — title, rich-text body, cover image if the collection has an image field — publishes the item, and returns the live post URL after verifying it.
argument-hint: [từ khóa chính], [URL nguồn], [site Webflow - tuỳ chọn]
---

# share-bai-webflow

Đăng bài tự động lên Webflow CMS: đọc 1 bài viết nguồn từ URL, viết lại theo từ khóa chính cho trước, rồi publish qua Webflow CMS API v2 (REST, Site Token).

## Khi nào dùng

User gõ:

- `/share-bai-webflow [từ khóa chính], [URL nguồn]`
- `/share-bai-webflow [từ khóa chính], [URL nguồn], [site Webflow khác site mặc định]`

KHÔNG dùng skill này khi:

- User muốn đăng lên nền tảng khác Webflow (WordPress, Wix, Blogger...) — đó là skill riêng khác (`share-bai-wp`, `share-bai-wix`, `share-bai-blogger`).
- User chỉ muốn tóm tắt/review bài viết, không cần đăng lên đâu cả.
- Site đích chưa có Collection nào đóng vai trò blog (CMS Collection với ít nhất field Rich Text) — skill này ghi vào 1 Collection Item, không tạo static page.

## Tiền điều kiện

- [ ] Site Webflow đích có mục "API access" trong Site settings → Apps & Integrations (đã xác nhận free plan Starter cũng có mục này — không bắt buộc gói trả phí). Nếu một site cụ thể không thấy nút "Generate API token", xem `references/webflow-cms-api-steps.md` mục "Setup Site Token" để phát hiện nguyên nhân qua thao tác thật thay vì đoán.
- [ ] File `webflow-accounts.local.json` nằm ngay trong thư mục skill này (`.claude/skills/share-bai-webflow/webflow-accounts.local.json`, cùng cấp với `scripts/`, `references/`) — lưu `token`/`site_id`/`collection_id`/`field_body`/`field_image`/`site_domain` từng site. Nếu chưa có, Step 2 sẽ tạo.
- [ ] Site đích đã có ít nhất 1 CMS Collection dùng làm blog, có field kiểu Rich Text cho thân bài.
- [ ] Mọi lệnh HTTP/JSON trong pipeline BẮT BUỘC gọi qua `scripts/webflow-http.sh` và `scripts/webflow-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp. Hai script này cần được allowlist trong `.claude/settings.json` để chạy không cần xác nhận thủ công.

> ⚠️ **Checklist nội dung bắt buộc:** `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md` — đọc ở bước viết lại bài, cùng với `references/rewrite-guidelines.md`.

## Default settings

| Setting | Default | Override khi |
|---|---|---|
| Độ dài bài viết lại | 900-1100 từ | — (cố định, xem `references/rewrite-guidelines.md`) |
| Ảnh bắt buộc | **Có, tối thiểu 3 ảnh/bài ~1000 chữ** (Mastodon: 1 ảnh) — theo `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md` mục 5: ảnh lấy từ trang nguồn/website doanh nghiệp (ưu tiên `og:image`, ảnh trong nội dung, ảnh sản phẩm; bỏ logo/icon/ảnh <300px), liên quan đoạn văn xung quanh, căn giữa, chú thích in nghiêng <70 ký tự có từ khóa. Nguồn chỉ có 1–2 ảnh → dùng hết và báo "thiếu ảnh: có X/3"; **không có ảnh nào → dừng, không đăng**. Quy tắc này ghi đè mọi chỗ "thiếu ảnh vẫn đăng" / "1 ảnh" ở các bước bên dưới | — |
| Xác nhận trước Publish | Không hỏi — auto-publish ngay sau khi tạo item | User yêu cầu skill dừng lại chờ xác nhận trước khi publish |
| Site đích khi không chỉ định | Site duy nhất có trong `webflow-accounts.local.json` | Nhiều site trong file → hỏi user chọn |
| Collection đích khi không chỉ định | Hỏi user chọn từ danh sách collection của site (Step 2) | Site key đã cấu hình sẵn `collection_id` từ lần chạy trước |

## Pipeline — 9 bước

Theo thứ tự, không skip.

### Step 1 — Parse input

Tách 3 phần từ input, cách nhau bởi dấu phẩy: từ khóa chính, URL nguồn, site Webflow đích (tuỳ chọn). URL nguồn luôn bắt đầu bằng `http`, dùng mốc đó để tách đúng phần từ khóa khi từ khóa tự nó chứa dấu phẩy.

- Thiếu từ khóa hoặc URL nguồn → hỏi lại user, KHÔNG đoán.
- Không có site đích trong input → dùng site duy nhất trong `webflow-accounts.local.json` nếu file chỉ có 1 entry; nhiều entry hoặc rỗng → hỏi user chọn/khai báo site.

**Exit condition**: có đủ từ khóa chính, URL nguồn, và xác định được site-key đích.

### Step 2 — Đảm bảo có Site Token + site_id + collection_id + field slug

Đọc `references/webflow-cms-api-steps.md` mục "Setup Site Token" và "Xác định site_id, collection_id, field slug".

- Chưa có `token` cho site-key → hướng dẫn user tạo Site Token tại Site settings → Apps & Integrations → API access. Nếu user báo không thấy nút "Generate API token" → dừng, báo rõ site cần nâng cấp gói trả phí, KHÔNG tìm cách khác để lấy token.
- Có `token` nhưng chưa có `site_id`/`collection_id`/`field_body` → gọi `list-sites`, `list-collections`, `get-collection` theo thứ tự, hỏi user chọn site/collection nếu có nhiều lựa chọn hoặc không khớp tên rõ ràng, lưu bằng `node scripts/webflow-json.js set-site`.
- Đã có đủ `token`/`site_id`/`collection_id`/`field_body` → dùng thẳng, không hỏi lại.

**Decision point**: API trả 401 → token sai/bị thu hồi, quay lại hướng dẫn tạo token mới. API trả 403 → báo 2 khả năng (site chưa đủ gói, hoặc token thiếu scope), không tự đoán thêm. KHÔNG tự bịa `site_id`/`collection_id` khi response không khớp tên user cung cấp.

### Step 3 — Đọc bài viết nguồn

Gọi `bash scripts/webflow-http.sh fetch-source <url> <out-file>` để tải trang nguồn, rồi đọc file đó và trích: tiêu đề, nội dung chính, ảnh đại diện (`og:image`/`twitter:image`); nếu không có meta ảnh thì lấy ảnh `<img>` đầu tiên trong nội dung bài. Gặp JS cookie challenge (response ngắn, chỉ chứa script set cookie rồi reload) → xem `references/webflow-cms-api-steps.md` mục "Xử lý trang nguồn bị chặn bot".

**Exit condition**: có đủ text để viết lại. URL không truy cập được → dừng pipeline, báo lỗi cụ thể, KHÔNG bịa nội dung.

### Step 4 — Viết lại bài viết

Đọc `references/rewrite-guidelines.md`. Viết lại ~1000 từ tiếng Việt: giữ nghĩa & thông tin chính xác như bài gốc, không copy nguyên câu, chứa từ khóa chính, gắn hyperlink vào đúng 1 lần xuất hiện của từ khóa chính trỏ về URL nguồn. Đặt tiêu đề (chứa từ khóa chính) và tạo slug kebab-case không dấu. Ghi nội dung dưới dạng 1 chuỗi HTML dùng tập thẻ cơ bản (`<p>`, `<h2>`, `<ul>/<li>`, `<a>`...) mà Rich Text field của Webflow hỗ trợ — xem mẫu trong `references/rewrite-guidelines.md` mục "Định dạng content".

**Exit condition**: bài đạt 900-1100 từ (`node scripts/webflow-json.js word-count`), đúng 1 link ở từ khóa chính, không đoạn nào trùng nguyên văn >1 câu với bài gốc.

### Step 5 — Chuẩn bị ảnh

Nếu Step 3 lấy được ảnh đại diện hoặc ảnh đầu bài, VÀ site đã có `field_image` (từ Step 2) → gọi `bash scripts/webflow-http.sh download-image <url> <out-file> [cookie]` để tải ảnh về thư mục tạm.

Không có ảnh khả dụng, tải lỗi, hoặc collection không có field ảnh → bỏ qua, tiếp tục không ảnh. KHÔNG chặn pipeline chỉ vì thiếu ảnh.

### Step 6 — Upload ảnh lên Webflow Assets

Nếu Step 5 có ảnh, đọc `references/webflow-cms-api-steps.md` mục "Upload ảnh (Assets API, 2 bước)". Tính `fileHash` bằng `node scripts/webflow-json.js md5-file`, gọi `create-asset` rồi `upload-asset`, lấy `hostedUrl` bằng `node scripts/webflow-json.js show-asset-hosted-url`.

Lỗi ở bước nào (4xx/5xx) → bỏ qua ảnh, tiếp tục Step 7 không có field ảnh. KHÔNG chặn pipeline.

### Step 7 — Tạo & publish item

Đọc `references/webflow-cms-api-steps.md` mục "Tạo & publish item". Gọi `node scripts/webflow-json.js build-item-payload` để tạo file JSON body (`isDraft:false`), rồi `bash scripts/webflow-http.sh create-item`. Gọi thêm `bash scripts/webflow-http.sh publish-item` tường minh ngay sau đó để đảm bảo item thật sự lên live site. KHÔNG dừng lại hỏi user xác nhận trước khi publish — user đã yêu cầu skill này tự publish luôn sau khi soạn xong.

**Exit condition**: `create-item` trả về `id` + `fieldData.slug`, `publish-item` không lỗi.

### Step 8 — Verify

Đọc `references/webflow-cms-api-steps.md` mục "Xây live URL". Gọi `get-item`, kiểm tra `isDraft:false` và `lastPublished` có giá trị. Ghép live URL từ `site_domain` (đã lưu Step 2) + `collection slug` (từ `list-collections`) + `item slug` (từ `create-item`). Response lỗi, hoặc `isDraft` vẫn `true`, hoặc `lastPublished` rỗng → báo cụ thể cho user, KHÔNG báo thành công.

### Step 9 — Report

Output theo format ở mục Output.

## Decision points

| Step | Hỏi user khi | Auto-proceed khi |
|---|---|---|
| 1 | Thiếu từ khóa hoặc URL nguồn; site đích không xác định được | Input đủ từ khóa + URL, site đích rõ ràng |
| 2 | Chưa có Site Token; nhiều site/collection khớp mơ hồ; API access không khả dụng (free plan) | Đã có đủ token/site_id/collection_id/field_body trong `webflow-accounts.local.json` |
| 3 | — (không hỏi, dừng luôn nếu không qua được challenge) | URL nguồn fetch thành công |
| 7 | — (không hỏi, auto-publish theo yêu cầu user) | Luôn tự gọi create-item + publish-item ngay sau Step 4-6 |

## Recovery

- URL nguồn lỗi/không truy cập được → dừng, báo user, không bịa nội dung.
- API trả 401 ở bất kỳ bước nào (token bị thu hồi) → dừng, hướng dẫn user tạo Site Token mới theo `references/webflow-cms-api-steps.md`, không tự đoán token khác.
- API trả 403 → báo rõ 2 khả năng (site chưa đủ gói trả phí, hoặc token thiếu scope `sites:read`/`cms:read`/`cms:write`/`assets:write`), không tự đoán nguyên nhân khác.
- Upload ảnh lỗi ở Step 6 (create-asset hoặc upload-asset) → bỏ qua ảnh, tiếp tục Step 7 không có field ảnh.
- `create-item` trả lỗi 4xx/5xx (thường do field slug sai vì schema site đổi, hoặc thiếu field bắt buộc khác) → dừng, đọc message qua `node scripts/webflow-json.js show-error`, báo rõ cho user, KHÔNG báo "đã đăng thành công".
- HTTP 429 (rate limit) → dừng, báo user, KHÔNG tự retry liên tục.

## Output format

```
Đã đăng bài thành công.

Site: <site domain>
Collection: <collection displayName>
Tiêu đề: <title>
Từ khóa chính: <keyword> (link về: <source URL>)
Link bài đã đăng: <live URL ghép từ site domain + collection slug + item slug>
```

Fetch lỗi ở Step 3, thiếu Site Token/site_id/collection_id ở Step 2, hoặc API lỗi ở Step 7-8, thì báo rõ bước nào fail và lý do thay vì trả Output format trên.

## Anti-patterns

- KHÔNG copy nguyên văn nhiều câu liên tiếp từ bài gốc (vd: giữ nguyên cả đoạn mở đầu của bài gốc, chỉ đổi vài từ — đây vẫn là đạo văn).
- KHÔNG bịa thông tin/số liệu không có trong bài gốc.
- KHÔNG lưu `token` dạng plaintext trong SKILL.md, chat log, hay file được commit — chỉ lưu trong `webflow-accounts.local.json` (trong thư mục skill), thêm vào `.gitignore` nếu có.
- KHÔNG tự ý đăng lên site/collection khác site user đã chỉ định.
- KHÔNG báo "đăng thành công" khi `isDraft` vẫn `true` hoặc `lastPublished` rỗng sau Step 8 — verify response thật trước khi report, không suy đoán từ HTTP 200 chung chung của `create-item`.
- KHÔNG khẳng định chắc chắn free plan Webflow có hay không cho tạo Site Token khi chưa kiểm tra thật trên tài khoản user — Step 2 luôn detect qua thao tác thật (xem `references/webflow-cms-api-steps.md`), không trả lời từ suy đoán.

## Skill files

| File | Purpose | Load when |
|---|---|---|
| `references/rewrite-guidelines.md` | Quy tắc viết lại bài: độ dài, giữ nghĩa, gắn từ khóa + link, định dạng HTML cho Rich Text field | Step 4 |
| `references/webflow-cms-api-steps.md` | Chi tiết Site Token/free-plan detection, xác định site_id/collection_id/field slug, upload ảnh 2 bước, tạo & publish item, xây live URL, xử lý bot challenge | Step 2, 3, 5, 6, 7, 8 |
| `scripts/webflow-http.sh` | Thực thi mọi lệnh HTTP (fetch source, download image, list-sites, list-collections, get-collection, create-asset, upload-asset, create-item, publish-item, get-item) — allowlisted trong `.claude/settings.json` | Step 2, 3, 5, 6, 7, 8 |
| `scripts/webflow-json.js` | Thực thi mọi xử lý JSON (đọc/lưu credential, tìm site/collection/field, tính md5, build payload, đếm từ, đọc kết quả/lỗi) — allowlisted trong `.claude/settings.json` | Step 1, 2, 4, 6, 7, 8 |
| `webflow-accounts.local.json` | Credential từng site (`token`/`site_id`/`collection_id`/`field_body`/`field_image`/`site_domain`) — KHÔNG commit, chỉ đọc/ghi qua `scripts/webflow-json.js` | Step 2, 6, 7, 8 |

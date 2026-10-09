---
name: share-bai-wp
description: This skill should be used when the user runs "/share-bai-wp" with a main keyword and a source URL, or asks to "đăng bài lên WordPress", "share bài viết lên WP", "viết lại bài từ URL này rồi đăng WordPress", "auto-post to WordPress", or "publish this article to my WordPress site". Reads the source article at the given URL, rewrites it in Vietnamese (~1000 words, no duplication, keeps the original meaning and facts, contains the main keyword hyperlinked to the source), then publishes it to a WordPress.com free-plan site via the WordPress.com REST API (OAuth token) as native block content with title/slug/featured image, and returns the live post URL.
argument-hint: [từ khóa chính], [URL nguồn], [site WP - tuỳ chọn]
---

# share-bai-wp

Đăng bài tự động lên WordPress.com bản free (block editor): đọc 1 bài viết nguồn từ URL, viết lại theo từ khóa chính cho trước, rồi publish qua WordPress.com REST API.

## Khi nào dùng

User gõ:

- `/share-bai-wp [từ khóa chính], [URL nguồn]`
- `/share-bai-wp [từ khóa chính], [URL nguồn], [site WP khác site mặc định]`

KHÔNG dùng skill này khi:

- User muốn đăng lên nền tảng khác WordPress (Blogger, Facebook...) — đó là skill riêng khác (vd `share-bai-blogger`).
- User chỉ muốn tóm tắt/review bài viết, không cần đăng lên đâu cả.
- Site đích là WordPress tự host (self-hosted, không phải `*.wordpress.com`) — skill này gọi WordPress.com REST API (`public-api.wordpress.com`), chỉ hoạt động với site trên nền tảng WordPress.com.

## Tiền điều kiện

- [ ] Đã tạo 1 OAuth app tại `developer.wordpress.com/apps` cho site đích (làm 1 lần/site) — Step 2 hướng dẫn nếu chưa có.
- [ ] File `wp-accounts.local.json` nằm ngay trong thư mục skill này (`.claude/skills/share-bai-wp/wp-accounts.local.json`, cùng cấp với `scripts/`, `references/`) — lưu `client_id`/`client_secret`/`access_token` từng site. Nếu chưa có, Step 2 sẽ tạo.
- [ ] Site đích dùng WordPress.com bản free với block editor mặc định.
- [ ] Mọi lệnh HTTP/JSON trong pipeline (Step 2-3, 5-8) BẮT BUỘC gọi qua `scripts/wp-http.sh` và `scripts/wp-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp. Hai script này đã được allowlist trong `.claude/settings.json` để chạy không cần xác nhận thủ công; gọi `curl`/`node -e` trực tiếp sẽ vẫn bị hỏi xác nhận mỗi lần.

## Default settings

| Setting | Default | Override khi |
|---|---|---|
| Độ dài bài viết lại | 900-1100 từ | — (cố định, xem `references/rewrite-guidelines.md`) |
| Ảnh bắt buộc | Không — thiếu ảnh vẫn đăng bình thường | User yêu cầu bắt buộc phải có ảnh mới đăng |
| Xác nhận trước Publish | Không hỏi — auto-publish ngay sau Step 7 | User yêu cầu skill dừng lại chờ xác nhận trước khi publish |
| Site đích khi không chỉ định | Site duy nhất có trong `wp-accounts.local.json` | Nhiều site trong file → hỏi user chọn |
| Loại OAuth grant | Authorization code (`response_type=code`) — token không hết hạn | — (KHÔNG dùng implicit `response_type=token`, token loại đó hết hạn ~14 ngày) |

## Pipeline — 9 bước

Theo thứ tự, không skip.

### Step 1 — Parse input

Tách 3 phần từ input, cách nhau bởi dấu phẩy: từ khóa chính, URL nguồn, site WP đích (tuỳ chọn). URL nguồn luôn bắt đầu bằng `http`, dùng mốc đó để tách đúng phần từ khóa khi từ khóa tự nó chứa dấu phẩy.

- Thiếu từ khóa hoặc URL nguồn → hỏi lại user, KHÔNG đoán.
- Không có site đích trong input → dùng site duy nhất trong `wp-accounts.local.json` nếu file chỉ có 1 entry; nếu file có nhiều entry hoặc rỗng → hỏi user chọn/khai báo site.

**Exit condition**: có đủ từ khóa chính, URL nguồn, và xác định được domain site đích.

### Step 2 — Đảm bảo có OAuth app + access token hợp lệ

Đọc `references/wordpress-rest-api-steps.md` mục "Setup app & OAuth" và "Lấy / làm mới access token". Tra `wp-accounts.local.json` theo domain site đích.

- Chưa có entry (chưa tạo app) → hướng dẫn user tạo app tại `developer.wordpress.com/apps/new/`, lấy Client ID + Client Secret, lưu vào file (`node scripts/wp-json.js save-oauth-token` hoặc chỉnh trực tiếp).
- Có `client_id`/`client_secret` nhưng chưa có `access_token` → đưa user link authorize dùng `response_type=code` (authorization code grant — token không hết hạn, KHÔNG dùng `response_type=token`), nhận URL redirect user paste lại (code nằm ở query string), đổi code lấy access token qua `bash scripts/wp-http.sh oauth-token`, lưu bằng `node scripts/wp-json.js save-oauth-token`.
- Đã có `access_token` → dùng luôn, không hỏi lại (token loại này không hết hạn). Đọc bằng `node scripts/wp-json.js get-account-field`.

**Decision point**: luôn hỏi/hướng dẫn khi thiếu app hoặc thiếu access token cho đúng site đích. KHÔNG tự bịa token hoặc dùng token của site khác. Nếu API trả 401 (token bị revoke) → coi như chưa có token, quay lại hướng dẫn lấy token mới.

### Step 3 — Đọc bài viết nguồn

Gọi `bash scripts/wp-http.sh fetch-source <url> <out-file>` để tải trang nguồn, rồi đọc file đó và trích: tiêu đề, nội dung chính, ảnh đại diện (`og:image`/`twitter:image`); nếu không có meta ảnh thì lấy ảnh `<img>` đầu tiên trong nội dung bài. Nếu response ban đầu chỉ chứa 1 đoạn script set cookie rồi reload (JS challenge của WAF/CDN), xem `references/wordpress-rest-api-steps.md` mục "Xử lý trang nguồn bị chặn bot" để lấy nội dung thật.

**Exit condition**: có đủ text để viết lại. URL không truy cập được (404, timeout, chặn hẳn không qua được challenge...) → dừng pipeline, báo lỗi cụ thể cho user, KHÔNG bịa nội dung thay thế.

### Step 4 — Viết lại bài viết

Đọc `references/rewrite-guidelines.md`. Viết lại ~1000 từ tiếng Việt theo guideline đó: giữ nghĩa & thông tin chính xác như bài gốc, không copy nguyên câu, chứa từ khóa chính, gắn hyperlink vào đúng 1 lần xuất hiện của từ khóa chính trỏ về URL nguồn. Đặt tiêu đề (chứa từ khóa chính) và tạo slug kebab-case không dấu. Chuyển nội dung sang Gutenberg block markup (`<!-- wp:paragraph -->`, `<!-- wp:heading -->`, `<!-- wp:list -->`...) theo mẫu trong `references/wordpress-rest-api-steps.md` mục "Tạo & publish bài" — đây là điều kiện để bài hiển thị đúng dạng khối khi mở lại trong block editor.

**Exit condition**: bài đạt 900-1100 từ, đúng 1 link ở từ khóa chính, không đoạn nào trùng nguyên văn >1 câu với bài gốc (theo self-check trong guideline).

### Step 5 — Chuẩn bị ảnh

Nếu Step 3 lấy được ảnh đại diện hoặc ảnh đầu bài → gọi `bash scripts/wp-http.sh download-image <url> <out-file> [cookie]` để tải ảnh về thư mục tạm, dùng cho Step 6.

Nếu không tìm được ảnh nào khả dụng → bỏ qua, đăng bài không ảnh. KHÔNG chặn pipeline chỉ vì thiếu ảnh.

### Step 6 — Upload ảnh lên media library

Nếu Step 5 có ảnh, đọc `references/wordpress-rest-api-steps.md` mục "Upload ảnh". Gọi `bash scripts/wp-http.sh upload-media <site-domain> <token> <local-file> <mime-type> <out-file>` rồi `node scripts/wp-json.js show-media-id <out-file>` để lấy media ID.

Upload lỗi (4xx/5xx) → bỏ qua ảnh, tiếp tục Step 7 không có `featured_image`. KHÔNG chặn pipeline.

### Step 7 — Tạo & publish bài

Đọc `references/wordpress-rest-api-steps.md` mục "Tạo & publish bài". Gọi `node scripts/wp-json.js build-post-payload` để tạo file JSON body (`title`, `content` là Gutenberg block markup từ Step 4, `slug`, `featured_image` là media ID từ Step 6 nếu có), rồi `bash scripts/wp-http.sh create-post <site-domain> <token> <payload-file> <out-file>`. KHÔNG dừng lại hỏi user xác nhận trước khi gọi — user đã yêu cầu skill này tự publish luôn sau khi soạn xong.

**Exit condition**: response trả về `status: "publish"` kèm `ID` và `URL`.

### Step 8 — Verify

Gọi `node scripts/wp-json.js show-post-result <out-file>` để đọc `ID`/`status`/`URL`/`title`/`slug`/`featured_image`. Kiểm tra có `URL` hợp lệ và `status` đúng `publish`. Response lỗi (4xx/5xx, hoặc `status` khác `publish`) → báo cụ thể lỗi cho user, KHÔNG báo thành công.

### Step 9 — Report

Output theo format ở mục Output.

## Decision points

| Step | Hỏi user khi | Auto-proceed khi |
|---|---|---|
| 1 | Thiếu từ khóa hoặc URL nguồn; site đích không xác định được | Input đủ từ khóa + URL, site đích rõ ràng |
| 2 | Chưa có OAuth app, hoặc chưa có access token cho site đích | Đã có access token trong `wp-accounts.local.json` |
| 3 | — (không hỏi, dừng luôn nếu không qua được challenge) | URL nguồn fetch thành công (trực tiếp hoặc sau khi xử lý cookie challenge) |
| 7 | — (không hỏi, auto-publish theo yêu cầu user) | Luôn tự gọi API publish ngay sau khi soạn xong Step 4-6 |

## Recovery

- URL nguồn lỗi/không truy cập được, hoặc bị chặn bot không xử lý được bằng cookie challenge → dừng, báo user, không bịa nội dung.
- Access token bị revoke (API trả 401 dù đã lưu token — hiếm khi xảy ra với authorization code grant vì token không tự hết hạn) → dừng, hướng dẫn user lấy lại token theo `references/wordpress-rest-api-steps.md`, không tự đoán token khác.
- Upload ảnh lỗi ở Step 6 → bỏ qua ảnh, tiếp tục publish không `featured_image`.
- API tạo post trả lỗi (4xx/5xx) ở Step 7 → dừng, báo rõ mã lỗi + message từ response, không báo "đã đăng thành công".

## Output format

```
Đã đăng bài thành công.

Site: <site domain>
Tiêu đề: <title>
Từ khóa chính: <keyword> (link về: <source URL>)
Link bài đã đăng: <published URL>
```

Fetch lỗi ở Step 3, thiếu OAuth app/token ở Step 2, hoặc API lỗi ở Step 7, thì báo rõ bước nào fail và lý do thay vì trả Output format trên.

## Anti-patterns

- KHÔNG copy nguyên văn nhiều câu liên tiếp từ bài gốc (vd: giữ nguyên cả đoạn mở đầu của bài gốc, chỉ đổi vài từ — đây vẫn là đạo văn).
- KHÔNG bịa thông tin/số liệu không có trong bài gốc (vd: bài gốc không nêu con số cụ thể nhưng tự thêm "theo thống kê, 90% website từng bị tấn công DDoS").
- KHÔNG dùng các từ xếp hạng tuyệt đối như "nhất", "duy nhất", "số 1", "hàng đầu", "tốt nhất"... khi không có tài liệu/số liệu trong bài gốc chứng minh cho khẳng định đó — xem chi tiết ở `references/rewrite-guidelines.md`.
- KHÔNG lưu client_secret/access_token dạng plaintext trong SKILL.md, chat log, hay file được commit (vd: paste token vào Output format để "báo cáo lại cho user") — chỉ lưu trong `wp-accounts.local.json` (trong thư mục skill), thêm vào `.gitignore` nếu có.
- KHÔNG tự ý đăng lên site khác site user đã chỉ định (vd: user gõ site đích là `mysite2.wordpress.com` nhưng chỉ có token site A sẵn có trong `wp-accounts.local.json` → không được lặng lẽ đăng vào site A thay thế).
- KHÔNG báo "đăng thành công" khi response API không trả `status: "publish"` — verify response thật trước khi report (Step 8), không suy đoán từ HTTP 200 chung chung.

## Skill files

| File | Purpose | Load when |
|---|---|---|
| `references/rewrite-guidelines.md` | Quy tắc viết lại bài: độ dài, giữ nghĩa, gắn từ khóa + link, cấu trúc, self-check | Step 4 |
| `references/wordpress-rest-api-steps.md` | Chi tiết OAuth app/token, upload ảnh, tạo & publish bài qua REST API, xử lý bot challenge | Step 2, 3, 6, 7 |
| `scripts/wp-http.sh` | Thực thi mọi lệnh HTTP (fetch source, download image, oauth-token, upload-media, create-post) — allowlisted trong `.claude/settings.json` | Step 2, 3, 5, 6, 7 |
| `scripts/wp-json.js` | Thực thi mọi xử lý JSON (đọc/lưu credential, build payload, đếm từ, đọc kết quả) — allowlisted trong `.claude/settings.json` | Step 1, 2, 4, 6, 7, 8 |
| `wp-accounts.local.json` | Credential từng site (`client_id`/`client_secret`/`access_token`) — KHÔNG commit, chỉ đọc/ghi qua `scripts/wp-json.js` | Step 2, 6, 7 |

---
name: share-bai-blogger
description: This skill should be used when the user runs "/share-bai-blogger" with a main keyword and a source URL, or asks to "đăng bài lên Blogger", "share bài viết lên Blogspot", "viết lại bài từ URL này rồi đăng Blogger", "auto-post to Blogger", or "publish this article to my Blogspot". Reads the source article at the given URL, rewrites it in Vietnamese (~1000 words, no duplication, keeps the original meaning and facts, contains the main keyword hyperlinked to the source), then publishes it to a Blogger blog via the Blogger API v3 (Google OAuth), including an inline image when available, and returns the live post URL.
argument-hint: [từ khóa chính], [URL nguồn], [blog Blogger đích - tuỳ chọn]
---

# share-bai-blogger

Đăng bài tự động lên Blogger: đọc 1 bài viết nguồn từ URL, viết lại theo từ khóa chính cho trước, rồi publish qua Blogger API v3. Kiến trúc tương tự skill `share-bai-wp` (cùng nhóm skill đăng bài tự động, khác nền tảng đích).

## Khi nào dùng

User gõ:

- `/share-bai-blogger [từ khóa chính], [URL nguồn]`
- `/share-bai-blogger [từ khóa chính], [URL nguồn], [blog Blogger khác blog mặc định]`

KHÔNG dùng skill này khi:

- User muốn đăng lên nền tảng khác Blogger (WordPress, Facebook...) — đó là skill riêng khác (vd `share-bai-wp`).
- User chỉ muốn tóm tắt/review bài viết, không cần đăng lên đâu cả.
- User muốn đăng ở dạng draft (bản nháp) — skill này auto-publish luôn, không hỗ trợ chế độ draft.

## Tiền điều kiện

- [ ] Đã tạo 1 Google Cloud project, enable "Blogger API v3", tạo OAuth Client ID (Desktop app), thêm email user vào Test users của OAuth consent screen — Step 2 hướng dẫn nếu chưa có.
- [ ] File `blogger-accounts.local.json` nằm ngay trong thư mục skill này (`.claude/skills/share-bai-blogger/blogger-accounts.local.json`, cùng cấp với `scripts/`, `references/`) — lưu `client_id`/`client_secret`/`refresh_token`/`access_token`/`blog_id` từng blog. Nếu chưa có, Step 2 sẽ tạo.
- [ ] Mọi lệnh HTTP/JSON trong pipeline BẮT BUỘC gọi qua `scripts/blogger-http.sh`, `scripts/blogger-json.js`, và `scripts/google-oauth-server.js` — KHÔNG gọi `curl`/`node -e` trực tiếp. 2 script đầu đã được allowlist trong `.claude/settings.json` để chạy không cần xác nhận thủ công.

> ⚠️ **Checklist nội dung bắt buộc:** `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md` — đọc ở bước viết lại bài, cùng với `references/rewrite-guidelines.md`.

## Default settings

| Setting | Default | Override khi |
|---|---|---|
| Độ dài bài viết lại | 900-1100 từ | — (cố định, xem `references/rewrite-guidelines.md`) |
| Ảnh bắt buộc | **Có, tối thiểu 3 ảnh/bài ~1000 chữ** (Mastodon: 1 ảnh) — theo `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md` mục 5: ảnh lấy từ trang nguồn/website doanh nghiệp (ưu tiên `og:image`, ảnh trong nội dung, ảnh sản phẩm; bỏ logo/icon/ảnh <300px), liên quan đoạn văn xung quanh, căn giữa, chú thích in nghiêng <70 ký tự có từ khóa. Nguồn chỉ có 1–2 ảnh → dùng hết và báo "thiếu ảnh: có X/3"; **không có ảnh nào → dừng, không đăng**. Quy tắc này ghi đè mọi chỗ "thiếu ảnh vẫn đăng" / "1 ảnh" ở các bước bên dưới | — |
| Xác nhận trước Publish | Không hỏi — auto-publish ngay sau khi soạn xong | User yêu cầu skill dừng lại chờ xác nhận trước khi publish |
| Blog đích khi không chỉ định | Blog duy nhất có trong `blogger-accounts.local.json` | Nhiều blog trong file → hỏi user chọn |
| Định dạng content | HTML thường (`<p>`, `<h2>`, `<ul>`...) | — (Blogger không dùng Gutenberg block markup như WordPress) |
| Ảnh trong bài | Nhúng thẳng `<img src="...">` trỏ URL ảnh gốc từ bài nguồn | — (Blogger API không có upload media/featured image riêng) |

## Pipeline — 9 bước

Theo thứ tự, không skip.

### Step 1 — Parse input

Tách 3 phần từ input, cách nhau bởi dấu phẩy: từ khóa chính, URL nguồn, blog Blogger đích (tuỳ chọn). URL nguồn luôn bắt đầu bằng `http`, dùng mốc đó để tách đúng phần từ khóa khi từ khóa tự nó chứa dấu phẩy.

- Thiếu từ khóa hoặc URL nguồn → hỏi lại user, KHÔNG đoán.
- Không có blog đích trong input → dùng blog duy nhất trong `blogger-accounts.local.json` nếu file chỉ có 1 entry; nếu file có nhiều entry hoặc rỗng → hỏi user chọn/khai báo blog.

**Exit condition**: có đủ từ khóa chính, URL nguồn, và xác định được blog đích.

### Step 2 — Đảm bảo có OAuth client + token hợp lệ

Đọc `references/blogger-rest-api-steps.md` mục "Setup OAuth app", "Lấy refresh_token", "Refresh access_token", "Tra blog ID".

- Chưa có entry (chưa tạo OAuth client) → hướng dẫn user tạo project + enable Blogger API v3 + tạo Client ID tại Google Cloud Console, lưu bằng `node scripts/blogger-json.js set-client`.
- Có `client_id`/`client_secret` nhưng chưa có `refresh_token` → chạy `node scripts/google-oauth-server.js`, đưa user authorize URL script in ra, đợi script tự bắt code và đổi token, lưu bằng `node scripts/blogger-json.js save-tokens`.
- Có `refresh_token` nhưng chưa có `blog_id` → gọi `bash scripts/blogger-http.sh refresh-token` lấy access_token tạm, rồi `bash scripts/blogger-http.sh get-blog-by-url` + `node scripts/blogger-json.js save-blog-id`.
- Đã có đủ `refresh_token` + `blog_id` → gọi `bash scripts/blogger-http.sh refresh-token` lấy access_token mới (Google access_token chỉ sống ~1 giờ, PHẢI refresh mỗi lần chạy, việc này silent không cần user tương tác) rồi `node scripts/blogger-json.js save-refreshed-access-token`.

**Decision point**: luôn hỏi/hướng dẫn khi thiếu OAuth client hoặc thiếu refresh_token cho đúng blog đích. KHÔNG tự bịa token hoặc dùng token của blog khác. Nếu refresh-token API trả lỗi (refresh_token bị revoke) → coi như mất token, quay lại hướng dẫn lấy refresh_token mới.

### Step 3 — Đọc bài viết nguồn

Gọi `bash scripts/blogger-http.sh fetch-source <url> <out-file>` để tải trang nguồn, rồi đọc file đó và trích: tiêu đề, nội dung chính, ảnh đại diện (`og:image`/`twitter:image`); nếu không có meta ảnh thì lấy ảnh `<img>` đầu tiên trong nội dung bài. Nếu response ban đầu chỉ chứa 1 đoạn script set cookie rồi reload (JS challenge của WAF/CDN), xem `references/blogger-rest-api-steps.md` mục "Xử lý trang nguồn bị chặn bot" để lấy nội dung thật.

**Exit condition**: có đủ text để viết lại. URL không truy cập được (404, timeout, chặn hẳn không qua được challenge...) → dừng pipeline, báo lỗi cụ thể cho user, KHÔNG bịa nội dung thay thế.

### Step 4 — Viết lại bài viết

Đọc `references/rewrite-guidelines.md`. Viết lại ~1000 từ tiếng Việt theo guideline đó: giữ nghĩa & thông tin chính xác như bài gốc, không copy nguyên câu, chứa từ khóa chính, gắn hyperlink vào đúng 1 lần xuất hiện của từ khóa chính trỏ về URL nguồn. Đặt tiêu đề (chứa từ khóa chính). Viết content dạng HTML thường (`<p>`, `<h2>`, `<ul><li>`...) — KHÔNG dùng Gutenberg block markup (đó là đặc thù WordPress).

**Exit condition**: bài đạt 900-1100 từ (`node scripts/blogger-json.js word-count`), đúng 1 link ở từ khóa chính, không đoạn nào trùng nguyên văn >1 câu với bài gốc (theo self-check trong guideline).

### Step 5 — Chuẩn bị ảnh

Nếu Step 3 lấy được ảnh đại diện hoặc ảnh đầu bài → gọi `bash scripts/blogger-http.sh download-image <url> <out-file> [cookie]` để tải ảnh về thư mục tạm.

Nếu không tìm được ảnh nào khả dụng, hoặc tải lỗi → bỏ qua, đăng bài không ảnh. KHÔNG chặn pipeline chỉ vì thiếu ảnh.

### Step 6 — Chèn ảnh vào content

Nếu Step 5 có ảnh, đặt tạm thẻ `<img src="PLACEHOLDER" alt="...">` vào content HTML lúc viết ở Step 4 (thường ở đầu bài, sau đoạn mở đầu), rồi chạy `node scripts/blogger-json.js embed-image-datauri <content-html-file> <image-file> <mime-type> <out-file>` để thay `src` bằng base64 data URI từ file ảnh đã tải ở Step 5. Nhiều ảnh (checklist: ≥3 ảnh) → đặt nhiều thẻ `PLACEHOLDER` theo đúng thứ tự, gọi lệnh này 1 lần cho mỗi ảnh (lệnh tự bỏ qua thẻ đã nhúng), mỗi ảnh kèm chú thích `<em>` dưới 70 ký tự, căn giữa.

**KHÔNG trỏ `src` thẳng về URL ảnh gốc trên site nguồn** — nhiều site chặn hotlink (chỉ cho phép tải ảnh từ chính domain đó, hoặc yêu cầu cookie/challenge như khi fetch trang), ảnh sẽ vỡ khi Blogger hiển thị cho người đọc dù response tải ảnh lúc build vẫn 200 OK. Base64 data URI nhúng thẳng ảnh vào bài, không phụ thuộc domain nguồn còn cho phép hotlink hay không.

Nếu không có ảnh → bỏ qua bước này, content không có `<img>`.

### Step 7 — Tạo & publish bài

Đọc `references/blogger-rest-api-steps.md` mục "Tạo & publish bài". Gọi `node scripts/blogger-json.js build-post-payload` để tạo file JSON body (`title`, `content` là HTML từ Step 4-6), rồi `bash scripts/blogger-http.sh create-post <blog-id> <access_token> <payload-file> <out-file>`. KHÔNG dừng lại hỏi user xác nhận trước khi gọi — user đã yêu cầu skill này tự publish luôn sau khi soạn xong.

**Exit condition**: response trả về `status: "LIVE"` kèm `id` và `url`.

### Step 8 — Verify

Gọi `node scripts/blogger-json.js show-post-result <out-file>` để đọc `id`/`url`/`title`/`status`. Kiểm tra có `url` hợp lệ và `status` đúng `LIVE`. Response lỗi (4xx/5xx, hoặc `status` khác `LIVE`) → báo cụ thể lỗi cho user, KHÔNG báo thành công.

### Step 9 — Report

Output theo format ở mục Output.

## Decision points

| Step | Hỏi user khi | Auto-proceed khi |
|---|---|---|
| 1 | Thiếu từ khóa hoặc URL nguồn; blog đích không xác định được | Input đủ từ khóa + URL, blog đích rõ ràng |
| 2 | Chưa có OAuth client, hoặc chưa có refresh_token cho blog đích | Đã có refresh_token + blog_id trong `blogger-accounts.local.json` (access_token tự refresh silent) |
| 3 | — (không hỏi, dừng luôn nếu không qua được challenge) | URL nguồn fetch thành công (trực tiếp hoặc sau khi xử lý cookie challenge) |
| 7 | — (không hỏi, auto-publish theo yêu cầu user) | Luôn tự gọi API publish ngay sau khi soạn xong Step 4-6 |

## Recovery

- URL nguồn lỗi/không truy cập được, hoặc bị chặn bot không xử lý được bằng cookie challenge → dừng, báo user, không bịa nội dung.
- `refresh-token` API trả lỗi (refresh_token bị revoke, hoặc OAuth consent screen bị thu hồi quyền) → dừng, hướng dẫn user lấy lại refresh_token theo `references/blogger-rest-api-steps.md`, không tự đoán token khác.
- Tải ảnh lỗi ở Step 5, hoặc `embed-image-datauri` báo không tìm thấy `<img>` để thay ở Step 6 → bỏ qua ảnh, tiếp tục publish không có `<img>`.
- API tạo post trả lỗi (4xx/5xx) ở Step 7 → dừng, báo rõ mã lỗi + message từ response, không báo "đã đăng thành công".

## Output format

```
Đã đăng bài thành công.

Blog: <blog url>
Tiêu đề: <title>
Từ khóa chính: <keyword> (link về: <source URL>)
Link bài đã đăng: <published URL>
```

Fetch lỗi ở Step 3, thiếu OAuth client/token ở Step 2, hoặc API lỗi ở Step 7, thì báo rõ bước nào fail và lý do thay vì trả Output format trên.

## Anti-patterns

- KHÔNG copy nguyên văn nhiều câu liên tiếp từ bài gốc (vd: giữ nguyên cả đoạn mở đầu của bài gốc, chỉ đổi vài từ — đây vẫn là đạo văn).
- KHÔNG bịa thông tin/số liệu không có trong bài gốc (vd: bài gốc không nêu con số cụ thể nhưng tự thêm "theo thống kê, 90% website từng bị tấn công DDoS").
- KHÔNG lưu client_secret/refresh_token/access_token dạng plaintext trong SKILL.md, chat log, hay file được commit (vd: paste token vào Output format để "báo cáo lại cho user") — chỉ lưu trong `blogger-accounts.local.json` (trong thư mục skill), thêm vào `.gitignore` nếu có.
- KHÔNG tự ý đăng lên blog khác blog user đã chỉ định (vd: user gõ blog đích là `blog2.blogspot.com` nhưng chỉ có token blog A sẵn có trong `blogger-accounts.local.json` → không được lặng lẽ đăng vào blog A thay thế).
- KHÔNG dùng access_token cũ quá 1 giờ mà không refresh (vd: tái sử dụng access_token đã lưu từ lần chạy trước mà không kiểm tra `obtained_at`) — access_token Google hết hạn nhanh hơn nhiều so với WordPress, luôn refresh ở Step 2 trước khi gọi API tạo post.
- KHÔNG báo "đăng thành công" khi response API không trả `status: "LIVE"` — verify response thật trước khi report (Step 8), không suy đoán từ HTTP 200 chung chung.
- KHÔNG trỏ `<img src="...">` thẳng về URL ảnh gốc trên site nguồn (vd: giữ nguyên `src="https://site-nguon.com/anh.jpg"` trong content gửi lên Blogger) — nhiều site chặn hotlink nên ảnh hiển thị vỡ với người đọc dù lúc build không báo lỗi gì; luôn dùng `embed-image-datauri` để nhúng base64.

## Skill files

| File | Purpose | Load when |
|---|---|---|
| `references/rewrite-guidelines.md` | Quy tắc viết lại bài: độ dài, giữ nghĩa, gắn từ khóa + link, cấu trúc, self-check | Step 4 |
| `references/blogger-rest-api-steps.md` | Chi tiết OAuth client/token, refresh token, tra blog ID, tạo & publish bài qua Blogger API, xử lý bot challenge | Step 2, 3, 7 |
| `scripts/blogger-http.sh` | Thực thi mọi lệnh HTTP (fetch source, download image, refresh-token, get-blog-by-url, create-post, update-post) — allowlisted trong `.claude/settings.json` | Step 2, 3, 5, 7 |
| `scripts/blogger-json.js` | Thực thi mọi xử lý JSON (đọc/lưu credential, build payload, embed ảnh base64, đếm từ, đọc kết quả) — allowlisted trong `.claude/settings.json` | Step 1, 2, 4, 6, 7, 8 |
| `scripts/google-oauth-server.js` | Chạy OAuth flow lần đầu: mở local server tạm bắt redirect code, đổi lấy token — không cần copy-paste URL thủ công | Step 2 (chỉ lần đầu/blog) |
| `blogger-accounts.local.json` | Credential từng blog (`client_id`/`client_secret`/`refresh_token`/`access_token`/`blog_id`) — KHÔNG commit, chỉ đọc/ghi qua `scripts/blogger-json.js` | Step 2, 7 |

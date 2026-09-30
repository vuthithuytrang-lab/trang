---
name: share-bai-tumblr
description: This skill should be used when the user asks to "đăng bài lên Tumblr", "share bài lên Tumblr", "chia sẻ bài lên Tumblr", "đăng blog Tumblr", "/share-bai-tumblr [từ khóa], [URL]", "post to Tumblr blog", or wants to auto-publish a rewritten article to a Tumblr blog. Reads 1 source article from a URL, rewrites it around a given primary keyword, then publishes via the Tumblr API v2 (Neue Post Format, OAuth2). Same skill family as share-bai-wp/share-bai-blogger/share-bai-ggr — different target platform and publish mechanism (real REST API, not email).
---

# share-bai-tumblr

Đăng bài tự động lên Tumblr: đọc 1 bài viết nguồn từ URL, viết lại theo từ khóa chính cho trước, rồi publish qua Tumblr API v2 (Neue Post Format — NPF). Kiến trúc tương tự `share-bai-wp`/`share-bai-blogger`/`share-bai-ggr` (cùng nhóm skill đăng bài tự động, khác nền tảng đích và định dạng nội dung). Khác `share-bai-ggr`: Tumblr có REST API tạo bài thật (không phải gửi email), nội dung là mảng NPF content blocks thay vì HTML/Gutenberg.

## Khi nào dùng

User gõ:

- `/share-bai-tumblr [từ khóa chính], [URL nguồn]`
- `/share-bai-tumblr [từ khóa chính], [URL nguồn], [blog Tumblr khác blog mặc định]`

KHÔNG dùng skill này khi:

- User muốn đăng lên nền tảng khác Tumblr (WordPress, Blogger, Google Group...) — đó là skill riêng khác (`share-bai-wp`, `share-bai-blogger`, `share-bai-ggr`).
- User chỉ muốn tóm tắt/review bài viết, không cần đăng lên đâu cả.

## Tiền điều kiện

- [ ] Đã đăng ký 1 OAuth app tại `tumblr.com/oauth/apps` (làm 1 lần/tài khoản Tumblr), có Consumer Key + Consumer Secret, callback URL đăng ký là `http://localhost:8767/` (KHÔNG dùng `127.0.0.1` — Tumblr từ chối raw-IP domain lúc đăng ký) — Step 2 hướng dẫn nếu chưa có.
- [ ] File `tumblr-accounts.local.json` nằm ngay trong thư mục skill này (`.claude/skills/share-bai-tumblr/tumblr-accounts.local.json`, cùng cấp với `scripts/`, `references/`) — lưu `client_id`/`client_secret`/`access_token`/`refresh_token`/`blog_identifier` từng blog. Nếu chưa có, Step 2 sẽ tạo.
- [ ] Tài khoản Tumblr dùng để authorize đã là chủ sở hữu (hoặc member có quyền đăng) của blog đích.
- [ ] Mọi lệnh HTTP/JSON trong pipeline BẮT BUỘC gọi qua `scripts/tumblr-http.sh` và `scripts/tumblr-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp. 2 script này cần được allowlist trong `.claude/settings.json` để chạy không cần xác nhận thủ công.

> ⚠️ **Checklist nội dung bắt buộc:** `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md` — đọc ở bước viết lại bài, cùng với `references/rewrite-guidelines.md`.

## Default settings

| Setting | Default | Override khi |
|---|---|---|
| Độ dài bài viết lại | 900-1100 từ | — (cố định, xem `references/rewrite-guidelines.md`) |
| Ảnh bắt buộc | **Có, tối thiểu 3 ảnh/bài ~1000 chữ** (Mastodon: 1 ảnh) — theo `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md` mục 5: ảnh lấy từ trang nguồn/website doanh nghiệp (ưu tiên `og:image`, ảnh trong nội dung, ảnh sản phẩm; bỏ logo/icon/ảnh <300px), liên quan đoạn văn xung quanh, căn giữa, chú thích in nghiêng <70 ký tự có từ khóa. Nguồn chỉ có 1–2 ảnh → dùng hết và báo "thiếu ảnh: có X/3"; **không có ảnh nào → dừng, không đăng**. Quy tắc này ghi đè mọi chỗ "thiếu ảnh vẫn đăng" / "1 ảnh" ở các bước bên dưới | — |
| Xác nhận trước khi đăng | Không hỏi — auto-publish ngay sau khi soạn xong | User yêu cầu skill dừng lại chờ xác nhận trước khi đăng |
| Blog đích khi không chỉ định | Blog duy nhất có trong `tumblr-accounts.local.json` | Nhiều blog trong file → hỏi user chọn |
| Định dạng nội dung | NPF content blocks (`text`/`image`), ảnh qua external URL trực tiếp trong `media[].url` | — (KHÔNG cần bước upload ảnh riêng như WordPress) |
| Access token | Tự refresh mỗi lần chạy bằng `refresh_token` đã lưu (silent, không hỏi user) | — (access_token Tumblr sống ngắn hạn) |

## Pipeline — 9 bước

Theo thứ tự, không skip.

### Step 1 — Parse input

Tách 3 phần từ input, cách nhau bởi dấu phẩy: từ khóa chính, URL nguồn, blog Tumblr đích (tuỳ chọn). URL nguồn luôn bắt đầu bằng `http`, dùng mốc đó để tách đúng phần từ khóa khi từ khóa tự nó chứa dấu phẩy.

- Thiếu từ khóa hoặc URL nguồn → hỏi lại user, KHÔNG đoán.
- Không có blog đích trong input → dùng blog duy nhất trong `tumblr-accounts.local.json` nếu file chỉ có 1 entry; nếu file có nhiều entry hoặc rỗng → hỏi user chọn/khai báo blog (dạng `<tên-blog>.tumblr.com`).

**Exit condition**: có đủ từ khóa chính, URL nguồn, và xác định được `blog_identifier` đích.

### Step 2 — Đảm bảo có OAuth client + token hợp lệ

Đọc `references/tumblr-api-steps.md` mục "Setup OAuth app", "Lấy refresh_token", "Refresh access_token".

- Chưa có entry (chưa tạo OAuth app) → hướng dẫn user đăng ký app tại `tumblr.com/oauth/apps/register`, callback URL `http://localhost:8767/`, lấy Consumer Key + Secret Key, lưu bằng `node scripts/tumblr-json.js set-client`.
- Có `client_id`/`client_secret` nhưng chưa có `refresh_token` → chạy `node scripts/tumblr-oauth-server.js`, đưa user authorize URL script in ra, đợi script tự bắt code và đổi token, lưu bằng `node scripts/tumblr-json.js save-tokens`.
- Đã có `refresh_token` → gọi `bash scripts/tumblr-http.sh refresh-token` lấy access_token mới (PHẢI refresh mỗi lần chạy, silent không cần user tương tác) rồi `node scripts/tumblr-json.js save-refreshed-access-token`.

**Decision point**: luôn hỏi/hướng dẫn khi thiếu OAuth app hoặc thiếu refresh_token cho đúng blog đích. KHÔNG tự bịa token hoặc dùng token của blog khác. Nếu `refresh-token` trả lỗi (refresh_token bị revoke) → coi như mất token, quay lại hướng dẫn lấy refresh_token mới.

### Step 3 — Đọc bài viết nguồn

Gọi `bash scripts/tumblr-http.sh fetch-source <url> <out-file>` để tải trang nguồn, rồi đọc file đó và trích: tiêu đề, nội dung chính, URL ảnh đại diện (`og:image`/`twitter:image`); nếu không có meta ảnh thì lấy URL ảnh `<img>` đầu tiên trong nội dung bài. Nếu response ban đầu chỉ chứa 1 đoạn script set cookie rồi reload (JS challenge của WAF/CDN), xem `references/tumblr-api-steps.md` mục "Xử lý trang nguồn bị chặn bot" để lấy nội dung thật.

**Exit condition**: có đủ text để viết lại. URL không truy cập được (404, timeout, chặn hẳn không qua được challenge...) → dừng pipeline, báo lỗi cụ thể cho user, KHÔNG bịa nội dung thay thế.

### Step 4 — Viết lại bài viết thành NPF content blocks

Đọc `references/rewrite-guidelines.md`. Viết lại ~1000 từ tiếng Việt theo guideline đó: giữ nghĩa & thông tin chính xác như bài gốc, không copy nguyên câu, chứa từ khóa chính. Ghi trực tiếp ra 1 file JSON mảng content blocks theo cấu trúc NPF (`references/tumblr-api-steps.md` mục "Cấu trúc NPF content blocks") — block đầu tiên `{"type":"text","subtype":"heading1","text":"<tiêu đề>"}` (NPF không có field `title` riêng), tiếp theo là các block `text`/`image` xen kẽ.

Đồng thời tạo 1 slug kebab-case KHÔNG DẤU từ tiêu đề (giống quy ước ở `share-bai-wp`/`share-bai-blogger`) để truyền vào `build-post-payload` ở Step 6 — không truyền slug thì Tumblr tự sinh slug từ tiêu đề và percent-encode dấu tiếng Việt, ra URL dạng `...d%E1%BB%8Bch-vu-...` khó đọc/khó chia sẻ.

Gắn hyperlink vào ĐÚNG 1 lần xuất hiện của từ khóa chính bằng:
```
node scripts/tumblr-json.js add-link-formatting <content-blocks-file> <block-index> "<từ khóa chính>" <source-url> <out-file>
```

**Exit condition**: `node scripts/tumblr-json.js word-count <content-blocks-file>` trả về 900-1100, đúng 1 link ở từ khóa chính (verify qua `add-link-formatting` chạy thành công không lỗi), không đoạn nào trùng nguyên văn >1 câu với bài gốc (theo self-check trong guideline).

### Step 5 — Chèn ảnh (nếu có)

Nếu Step 3 lấy được URL ảnh đại diện hoặc ảnh đầu bài → thêm 1 block `{"type":"image","media":[{"url":"<url ảnh>","type":"<mime đoán từ đuôi file>"}],"alt_text":"..."}` vào vị trí phù hợp trong mảng content blocks (thường ngay sau đoạn mở đầu) — dùng thẳng URL từ bài nguồn, KHÔNG cần tải về/upload riêng (xem `references/tumblr-api-steps.md` mục "Ảnh trong bài").

Nếu không tìm được ảnh nào khả dụng → bỏ qua, đăng bài không ảnh. KHÔNG chặn pipeline chỉ vì thiếu ảnh.

### Step 6 — Tạo & publish bài

Đọc `references/tumblr-api-steps.md` mục "Tạo & publish bài". Gọi `node scripts/tumblr-json.js build-post-payload <content-blocks-file> <tags> <payload-file> <slug>` (slug ASCII đã tạo ở Step 4) để bọc content blocks thành payload API, rồi `bash scripts/tumblr-http.sh create-post <blog_identifier> <access_token> <payload-file> <out-file>`. KHÔNG dừng lại hỏi user xác nhận trước khi gọi — user đã yêu cầu skill này tự publish luôn sau khi soạn xong.

**Exit condition**: response có `meta.status` = `201` và `response.state` = `"published"`.

Nếu response lỗi cụ thể do block ảnh (media fetch thất bại phía Tumblr) → thử lại 1 lần: bỏ block ảnh khỏi content, build lại payload, gọi lại `create-post` không ảnh.

### Step 7 — Verify

Gọi `node scripts/tumblr-json.js show-post-result <out-file> <blog_identifier>` để đọc `id`/`state`/`post_url`/`meta` — response API gốc của Tumblr KHÔNG trả `post_url`, script tự dựng URL từ `blog_identifier` + `id` (dạng `https://<blog_identifier>/post/<id>`). Kiểm tra `state` đúng `"published"`. Response lỗi (4xx/5xx, hoặc `state` khác `"published"`) → báo cụ thể lỗi cho user, KHÔNG báo thành công.

### Step 8 — Report

Output theo format ở mục Output.

## Decision points

| Step | Hỏi user khi | Auto-proceed khi |
|---|---|---|
| 1 | Thiếu từ khóa hoặc URL nguồn; blog đích không xác định được | Input đủ từ khóa + URL, blog đích rõ ràng |
| 2 | Chưa có OAuth app, hoặc chưa có refresh_token cho blog đích | Đã có refresh_token trong `tumblr-accounts.local.json` (access_token tự refresh silent) |
| 3 | — (không hỏi, dừng luôn nếu không qua được challenge) | URL nguồn fetch thành công (trực tiếp hoặc sau khi xử lý cookie challenge) |
| 6 | — (không hỏi, auto-publish theo yêu cầu user) | Luôn tự gọi API publish ngay sau khi soạn xong Step 4-5 |

## Recovery

- URL nguồn lỗi/không truy cập được, hoặc bị chặn bot không xử lý được bằng cookie challenge → dừng, báo user, không bịa nội dung.
- `refresh-token` trả lỗi (refresh_token bị revoke, hoặc app OAuth bị xoá) → dừng, hướng dẫn user lấy lại refresh_token theo `references/tumblr-api-steps.md`, không tự đoán token khác.
- `add-link-formatting` báo lỗi không tìm thấy/ambiguous cụm từ khóa → viết lại câu chứa từ khóa cho rõ ràng, unique hơn trong block đó, chạy lại.
- Block ảnh khiến `create-post` lỗi ở Step 6 → bỏ ảnh, đăng lại không `image` block (xem chi tiết Step 6).
- API tạo post trả lỗi (4xx/5xx) không liên quan ảnh → dừng, báo rõ mã lỗi + message từ response, không báo "đã đăng thành công".

## Output format

```
Đã đăng bài thành công lên Tumblr.

Blog: <blog_identifier>
Tiêu đề: <title>
Từ khóa chính: <keyword> (link về: <source URL>)
Link bài đã đăng: <post_url>
```

Fetch lỗi ở Step 3, thiếu OAuth app/token ở Step 2, hoặc API lỗi ở Step 6, thì báo rõ bước nào fail và lý do thay vì trả Output format trên.

## Anti-patterns

- KHÔNG copy nguyên văn nhiều câu liên tiếp từ bài gốc (vd: giữ nguyên cả đoạn mở đầu của bài gốc, chỉ đổi vài từ — đây vẫn là đạo văn).
- KHÔNG bịa thông tin/số liệu không có trong bài gốc (vd: bài gốc không nêu con số cụ thể nhưng tự thêm "theo thống kê, 90% website từng bị tấn công DDoS").
- KHÔNG dùng các từ xếp hạng tuyệt đối như "nhất", "duy nhất", "số 1", "hàng đầu", "tốt nhất"... khi không có tài liệu/số liệu trong bài gốc chứng minh cho khẳng định đó — xem chi tiết ở `references/rewrite-guidelines.md`.
- KHÔNG lưu client_secret/access_token/refresh_token dạng plaintext trong SKILL.md, chat log, hay file được commit — chỉ lưu trong `tumblr-accounts.local.json` (trong thư mục skill), thêm vào `.gitignore` nếu có.
- KHÔNG tự ý đăng lên blog khác blog user đã chỉ định (vd: user gõ blog đích là `blog2.tumblr.com` nhưng chỉ có token blog A sẵn có trong `tumblr-accounts.local.json` → không được lặng lẽ đăng vào blog A thay thế).
- KHÔNG tự tính offset `start`/`end` cho `formatting` bằng tay — luôn qua `add-link-formatting` để tránh lệch offset khiến link trỏ sai vị trí hoặc lỗi ký tự.
- KHÔNG báo "đăng thành công" khi response không có `meta.status: 201` và `response.state: "published"` — verify response thật trước khi report (Step 7).

## Skill files

| File | Purpose | Load when |
|---|---|---|
| `references/rewrite-guidelines.md` | Quy tắc viết lại bài: độ dài, giữ nghĩa, gắn từ khóa + link, cấu trúc, self-check | Step 4 |
| `references/tumblr-api-steps.md` | Chi tiết OAuth app/token, cấu trúc NPF, gắn link offset, ảnh, tạo & publish bài, xử lý bot challenge | Step 2, 3, 4, 5, 6, 7 |
| `scripts/tumblr-http.sh` | Thực thi mọi lệnh HTTP (fetch source, refresh-token, create-post) — allowlisted trong `.claude/settings.json` | Step 2, 3, 6 |
| `scripts/tumblr-json.js` | Thực thi mọi xử lý JSON/NPF (đọc/lưu credential, gắn link offset, build payload, đếm từ, đọc kết quả) — allowlisted trong `.claude/settings.json` | Step 1, 2, 4, 6, 7 |
| `scripts/tumblr-oauth-server.js` | Chạy OAuth2 flow lần đầu: mở local server tạm bắt redirect code, đổi lấy token — không cần copy-paste URL thủ công | Step 2 (chỉ lần đầu/blog) |
| `tumblr-accounts.local.json` | Credential từng blog (`client_id`/`client_secret`/`access_token`/`refresh_token`/`blog_identifier`) — KHÔNG commit, chỉ đọc/ghi qua `scripts/tumblr-json.js` | Step 2, 6, 7 |

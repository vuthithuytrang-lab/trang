---
name: share-bai-ggr
description: This skill should be used when the user runs "/share-bai-ggr" with a main keyword and a source URL, or asks to "đăng bài lên Google Group", "share bài viết lên Google Groups", "viết lại bài từ URL này rồi đăng lên Google Group", "auto-post to Google Group", or "gửi bài lên nhóm Google Groups". Reads the source article at the given URL, rewrites it in Vietnamese (~1000 words, no duplication, keeps the original meaning and facts, contains the main keyword hyperlinked to the source), then posts it as a new topic to a Google Group by sending an HTML email via the Gmail API (OAuth, gmail.send + gmail.metadata scopes) to the group's posting address — embedding an inline image when available — reads back the real Message-Id Gmail assigned, and returns the topic's Google Groups permalink built from it.
argument-hint: [từ khóa chính], [URL nguồn], [Google Group đích - tuỳ chọn]
---

# share-bai-ggr

Đăng bài tự động lên Google Group: đọc 1 bài viết nguồn từ URL, viết lại theo từ khóa chính cho trước, rồi "đăng" bằng cách gửi 1 email HTML qua Gmail API tới địa chỉ posting của group (Google Groups không có REST API tạo bài trực tiếp — cơ chế thật của nó là nhận bài qua email). Kiến trúc tương tự skill `share-bai-wp`/`share-bai-blogger` (cùng nhóm skill đăng bài tự động, khác nền tảng đích và cơ chế publish).

## Khi nào dùng

User gõ:

- `/share-bai-ggr [từ khóa chính], [URL nguồn]`
- `/share-bai-ggr [từ khóa chính], [URL nguồn], [Google Group khác group mặc định]`

KHÔNG dùng skill này khi:

- User muốn đăng lên nền tảng khác Google Groups (WordPress, Blogger, Google Sites...) — đó là skill riêng khác (`share-bai-wp`, `share-bai-blogger`, `share-bai-google-site`).
- User chỉ muốn tóm tắt/review bài viết, không cần đăng lên đâu cả.
- User muốn skill tự xác nhận bài đã "duyệt"/hiển thị công khai trên group — skill này chỉ verify được đến mức Gmail đã nhận gửi email thành công, không verify được trạng thái duyệt bài phía Google Groups (xem Known limits trong `references/google-groups-api-steps.md`).

## Tiền điều kiện

- [ ] Đã tạo 1 Google Cloud project, enable "Gmail API", tạo OAuth Client ID (Desktop app), thêm email user vào Test users của OAuth consent screen (scope xin gồm `gmail.send` + `gmail.metadata`), và (khuyến nghị) Publish App sang "In production" để `refresh_token` không tự hết hạn sau 7 ngày — Step 2 hướng dẫn nếu chưa có.
- [ ] File `ggr-accounts.local.json` nằm ngay trong thư mục skill này (`.claude/skills/share-bai-ggr/ggr-accounts.local.json`, cùng cấp với `scripts/`, `references/`) — lưu `client_id`/`client_secret`/`refresh_token`/`access_token`/`group_email` từng group. Nếu chưa có, Step 2 sẽ tạo.
- [ ] Tài khoản Google dùng để authorize (nhận OAuth) đã là **thành viên của Google Group đích**, và group cho phép member đăng bài không cần duyệt (moderation) — nếu group bắt buộc duyệt, email vẫn gửi thành công qua Gmail API nhưng bài có thể chưa hiển thị công khai ngay.
- [ ] Mọi lệnh HTTP/JSON trong pipeline BẮT BUỘC gọi qua `scripts/ggr-http.sh` và `scripts/ggr-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp. 2 script này cần được allowlist trong `.claude/settings.json` để chạy không cần xác nhận thủ công.

## Default settings

| Setting | Default | Override khi |
|---|---|---|
| Độ dài bài viết lại | 900-1100 từ | — (cố định, xem `references/rewrite-guidelines.md`) |
| Ảnh bắt buộc | Không — thiếu ảnh vẫn đăng bình thường | User yêu cầu bắt buộc phải có ảnh mới đăng |
| Xác nhận trước khi gửi | Không hỏi — auto-send ngay sau khi soạn xong | User yêu cầu skill dừng lại chờ xác nhận trước khi gửi |
| Group đích khi không chỉ định | Group duy nhất có trong `ggr-accounts.local.json` | Nhiều group trong file → hỏi user chọn |
| Định dạng nội dung | HTML email (`multipart/related` khi có ảnh inline qua `cid:`, `text/html` đơn giản khi không có ảnh) | — (KHÔNG dùng `<img src="data:...">` — Gmail lột bỏ data URI khỏi email nhận, khác Blogger/WordPress render web bình thường) |
| Access token | Tự refresh mỗi lần chạy bằng `refresh_token` đã lưu (silent, không hỏi user) | — (Google access_token chỉ sống ~1 giờ, không như WordPress) |

## Pipeline — 9 bước

Theo thứ tự, không skip.

### Step 1 — Parse input

Tách 3 phần từ input, cách nhau bởi dấu phẩy: từ khóa chính, URL nguồn, Google Group đích (tuỳ chọn). URL nguồn luôn bắt đầu bằng `http`, dùng mốc đó để tách đúng phần từ khóa khi từ khóa tự nó chứa dấu phẩy.

- Thiếu từ khóa hoặc URL nguồn → hỏi lại user, KHÔNG đoán.
- Không có group đích trong input → dùng group duy nhất trong `ggr-accounts.local.json` nếu file chỉ có 1 entry; nếu file có nhiều entry hoặc rỗng → hỏi user chọn/khai báo group (địa chỉ dạng `<tên-group>@googlegroups.com`).

**Exit condition**: có đủ từ khóa chính, URL nguồn, và xác định được `group_email` đích.

### Step 2 — Đảm bảo có OAuth client + token hợp lệ

Đọc `references/google-groups-api-steps.md` mục "Setup OAuth app", "Lấy refresh_token", "Refresh access_token".

- Chưa có entry (chưa tạo OAuth client) → hướng dẫn user tạo project + enable Gmail API + tạo Client ID tại Google Cloud Console, lưu bằng `node scripts/ggr-json.js set-client`.
- Có `client_id`/`client_secret` nhưng chưa có `refresh_token` → chạy `node scripts/ggr-oauth-server.js`, đưa user authorize URL script in ra, đợi script tự bắt code và đổi token, lưu bằng `node scripts/ggr-json.js save-tokens`.
- Đã có `refresh_token` → gọi `bash scripts/ggr-http.sh refresh-token` lấy access_token mới (Google access_token chỉ sống ~1 giờ, PHẢI refresh mỗi lần chạy, việc này silent không cần user tương tác) rồi `node scripts/ggr-json.js save-refreshed-access-token`.

**Decision point**: luôn hỏi/hướng dẫn khi thiếu OAuth client hoặc thiếu refresh_token cho đúng group đích. KHÔNG tự bịa token hoặc dùng token của group khác. Nếu `refresh-token` trả lỗi (refresh_token bị revoke, hoặc hết hạn 7 ngày do consent screen còn ở "Testing") → coi như mất token, quay lại hướng dẫn lấy refresh_token mới.

### Step 3 — Đọc bài viết nguồn

Gọi `bash scripts/ggr-http.sh fetch-source <url> <out-file>` để tải trang nguồn, rồi đọc file đó và trích: tiêu đề, nội dung chính, ảnh đại diện (`og:image`/`twitter:image`); nếu không có meta ảnh thì lấy ảnh `<img>` đầu tiên trong nội dung bài. Nếu response ban đầu chỉ chứa 1 đoạn script set cookie rồi reload (JS challenge của WAF/CDN), xem `references/google-groups-api-steps.md` mục "Xử lý trang nguồn bị chặn bot" để lấy nội dung thật.

**Exit condition**: có đủ text để viết lại. URL không truy cập được (404, timeout, chặn hẳn không qua được challenge...) → dừng pipeline, báo lỗi cụ thể cho user, KHÔNG bịa nội dung thay thế.

### Step 4 — Viết lại bài viết

Đọc `references/rewrite-guidelines.md`. Viết lại ~1000 từ tiếng Việt theo guideline đó: giữ nghĩa & thông tin chính xác như bài gốc, không copy nguyên câu, chứa từ khóa chính, gắn hyperlink vào đúng 1 lần xuất hiện của từ khóa chính trỏ về URL nguồn. Đặt tiêu đề (chứa từ khóa chính, dùng làm Subject của email). Viết content dạng HTML thường (`<p>`, `<h2>`, `<ul><li>`...). Nếu Step 5 có ảnh, chèn sẵn `<img src="cid:ggr-inline-image" alt="...">` ở vị trí mong muốn (thường sau đoạn mở đầu) — `cid:` này khớp với `Content-ID` mà `build-mime-message` sẽ gắn ở Step 6.

**Exit condition**: bài đạt 900-1100 từ (`node scripts/ggr-json.js word-count`), đúng 1 link ở từ khóa chính, không đoạn nào trùng nguyên văn >1 câu với bài gốc (theo self-check trong guideline).

### Step 5 — Chuẩn bị ảnh

Nếu Step 3 lấy được ảnh đại diện hoặc ảnh đầu bài → gọi `bash scripts/ggr-http.sh download-image <url> <out-file> [cookie]` để tải ảnh về thư mục tạm, dùng cho Step 6.

Nếu không tìm được ảnh nào khả dụng, hoặc tải lỗi → bỏ qua, gửi bài không ảnh (không chèn thẻ `<img>` ở Step 4). KHÔNG chặn pipeline chỉ vì thiếu ảnh.

### Step 6 — Build email (MIME)

Đọc `references/google-groups-api-steps.md` mục "Build & gửi email". Build raw email:

```
node scripts/ggr-json.js build-mime-message <content-html-file> "<title>" <group_email> <payload-file>.json [image-file] [image-mime]
```

Ảnh (nếu có ở Step 5) đi vào dưới dạng `multipart/related` + `Content-ID`, KHÔNG dùng data URI (xem lý do trong reference — Gmail lột bỏ `data:` URI khỏi email nhận, khác Blogger/WordPress render trang web bình thường).

KHÔNG tự đặt header `Message-ID` — Gmail không giữ nguyên giá trị tự sinh khi gửi qua API (đã xác nhận thực tế: build permalink từ 1 Message-ID tự sinh trước khi gửi trỏ sai bài), nên `build-mime-message` không nhận tham số này nữa. Message-ID thật sẽ được đọc lại ở Step 8, sau khi gửi.

### Step 7 — Gửi (= publish)

```
bash scripts/ggr-http.sh gmail-send <access_token> <payload-file>.json <out-file>.json
node scripts/ggr-json.js show-send-result <out-file>.json
```

KHÔNG dừng lại hỏi user xác nhận trước khi gọi — user đã yêu cầu skill này tự gửi luôn sau khi soạn xong.

**Exit condition**: HTTP_STATUS 2xx và response có `id` (Gmail message ID).

### Step 8 — Verify + lấy permalink

Response Gmail 4xx/5xx, hoặc không có `id` → dừng, báo lỗi cụ thể, KHÔNG báo thành công. Ngược lại, đọc lại header `Message-Id` THẬT mà Gmail đã gán cho message vừa gửi (dùng `id` từ `show-send-result`), rồi mới build permalink từ giá trị đó:

```
bash scripts/ggr-http.sh gmail-get-message <access_token> <message-id-tra-ve-tu-step-7> <out-file>.json
node scripts/ggr-json.js extract-message-id <out-file>.json
node scripts/ggr-json.js build-permalink <group_email> "<message-id-that-vua-doc-duoc>"
```

KHÔNG build permalink từ 1 Message-ID tự đoán/tự sinh trước khi gửi — đã xác nhận thực tế Gmail tự thay Message-ID khi gửi qua API, permalink build từ giá trị đoán trước sẽ trỏ sai bài (404 hoặc redirect nhầm).

Lưu ý: đây là mức verify "Gmail đã nhận gửi email thành công", KHÔNG phải "bài đã LIVE công khai trên group" — Gmail API không cho biết trạng thái duyệt bài phía Google Groups (xem Known limits).

### Step 9 — Report

Output theo format ở mục Output.

## Decision points

| Step | Hỏi user khi | Auto-proceed khi |
|---|---|---|
| 1 | Thiếu từ khóa hoặc URL nguồn; group đích không xác định được | Input đủ từ khóa + URL, group đích rõ ràng |
| 2 | Chưa có OAuth client, hoặc chưa có refresh_token cho group đích | Đã có refresh_token trong `ggr-accounts.local.json` (access_token tự refresh silent) |
| 3 | — (không hỏi, dừng luôn nếu không qua được challenge) | URL nguồn fetch thành công (trực tiếp hoặc sau khi xử lý cookie challenge) |
| 7 | — (không hỏi, auto-send theo yêu cầu user) | Luôn tự gọi Gmail API gửi ngay sau khi soạn xong Step 4-6 |

## Recovery

- URL nguồn lỗi/không truy cập được, hoặc bị chặn bot không xử lý được bằng cookie challenge → dừng, báo user, không bịa nội dung.
- `refresh-token` trả lỗi (refresh_token bị revoke, hoặc hết hạn 7 ngày do consent screen còn "Testing") → dừng, hướng dẫn user lấy lại refresh_token theo `references/google-groups-api-steps.md`, không tự đoán token khác.
- Tải ảnh lỗi ở Step 5 → bỏ qua ảnh, tiếp tục gửi không có `<img>`.
- Gmail API trả lỗi (4xx/5xx) ở Step 7 → dừng, báo rõ mã lỗi + message từ response, không báo "đã đăng thành công".
- `gmail-get-message`/`extract-message-id` ở Step 8 lỗi hoặc không tìm thấy header `Message-Id` (hiếm, có thể do thiếu scope `gmail.metadata` — access_token cũ chỉ có `gmail.send`) → báo user cần re-authorize theo `references/google-groups-api-steps.md` để cấp thêm scope; KHÔNG tự bịa permalink từ giá trị đoán.
- Permalink Step 8 chưa load được ngay khi user vừa bấm thử → không phải lỗi, Google Groups cần vài phút index bài mới; nhắc user thử lại sau, không báo lỗi ngay lập tức.

## Output format

```
Đã gửi bài lên Google Group.

Group: <group_email>
Tiêu đề: <title>
Từ khóa chính: <keyword> (link về: <source URL>)
Link bài đã đăng: <permalink>

Lưu ý: link có thể mất vài phút để hiển thị do Google Groups cần index bài mới. Nếu group bật duyệt bài cho thành viên, bài sẽ chờ moderator duyệt trước khi công khai.
```

Fetch lỗi ở Step 3, thiếu OAuth client/token ở Step 2, hoặc Gmail API lỗi ở Step 7, thì báo rõ bước nào fail và lý do thay vì trả Output format trên.

## Anti-patterns

- KHÔNG copy nguyên văn nhiều câu liên tiếp từ bài gốc (vd: giữ nguyên cả đoạn mở đầu của bài gốc, chỉ đổi vài từ — đây vẫn là đạo văn).
- KHÔNG bịa thông tin/số liệu không có trong bài gốc (vd: bài gốc không nêu con số cụ thể nhưng tự thêm "theo thống kê, 90% website từng bị tấn công DDoS").
- KHÔNG lưu client_secret/refresh_token/access_token dạng plaintext trong SKILL.md, chat log, hay file được commit (vd: paste token vào Output format để "báo cáo lại cho user") — chỉ lưu trong `ggr-accounts.local.json` (trong thư mục skill), thêm vào `.gitignore` nếu có.
- KHÔNG tự ý gửi lên group khác group user đã chỉ định (vd: user gõ group đích là `group2@googlegroups.com` nhưng chỉ có token group A sẵn có trong `ggr-accounts.local.json` → không được lặng lẽ gửi vào group A thay thế).
- KHÔNG dùng access_token cũ quá 1 giờ mà không refresh — luôn refresh ở Step 2 trước khi gọi `gmail-send`.
- KHÔNG dùng `<img src="data:...">` để nhúng ảnh trong email — Gmail và phần lớn mail client lột bỏ data URI khỏi email nhận (khác render trang web của Blogger/WordPress); luôn dùng `cid:` + `multipart/related` qua `build-mime-message`.
- KHÔNG báo "đã đăng thành công lên group" khi chỉ mới xác nhận được Gmail API nhận gửi (HTTP 200 + `id`) — nói rõ mức verify thực tế (Gmail đã gửi, bài có thể chờ duyệt) thay vì khẳng định "đã LIVE" như WP/Blogger, vì skill này không có cách xác minh trạng thái duyệt bài phía Google Groups.

## Skill files

| File | Purpose | Load when |
|---|---|---|
| `references/rewrite-guidelines.md` | Quy tắc viết lại bài: độ dài, giữ nghĩa, gắn từ khóa + link, cấu trúc, self-check | Step 4 |
| `references/google-groups-api-steps.md` | Chi tiết OAuth client/token, build MIME email, nhúng ảnh inline, gửi qua Gmail API, build permalink, xử lý bot challenge | Step 2, 3, 5, 6, 7, 8 |
| `scripts/ggr-http.sh` | Thực thi mọi lệnh HTTP (fetch source, download image, refresh-token, gmail-send, gmail-get-message) — allowlisted trong `.claude/settings.json` | Step 2, 3, 5, 7, 8 |
| `scripts/ggr-json.js` | Thực thi mọi xử lý JSON/MIME (đọc/lưu credential, build email raw, đếm từ, đọc Message-ID thật, build permalink, đọc kết quả) — allowlisted trong `.claude/settings.json` | Step 1, 2, 4, 6, 7, 8 |
| `scripts/ggr-oauth-server.js` | Chạy OAuth flow lần đầu: mở local server tạm bắt redirect code, đổi lấy token — không cần copy-paste URL thủ công | Step 2 (chỉ lần đầu/group) |
| `ggr-accounts.local.json` | Credential từng group (`client_id`/`client_secret`/`refresh_token`/`access_token`/`group_email`) — KHÔNG commit, chỉ đọc/ghi qua `scripts/ggr-json.js` | Step 2, 6, 7, 8 |

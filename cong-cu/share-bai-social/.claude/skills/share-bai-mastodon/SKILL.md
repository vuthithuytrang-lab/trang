---
name: share-bai-mastodon
description: This skill should be used when the user asks to "đăng bài lên Mastodon", "share bài lên Mastodon", "chia sẻ bài lên Mastodon", "đăng toot", "/share-bai-mastodon [từ khóa], [URL]", "post to Mastodon", or wants to auto-publish a rewritten article as a short Mastodon status (toot). Reads 1 source article from a URL, rewrites it into a short status (≤500 characters) around a given primary keyword, then publishes via the Mastodon REST API (POST /api/v1/statuses, static access token — no OAuth browser flow). Same skill family as share-bai-wp/share-bai-blogger/share-bai-ggr/share-bai-tumblr/share-bai-wix/share-bai-instagram — different target platform; short microblog post instead of a long article, clickable link allowed (unlike Instagram), auth is a non-expiring personal access token (like share-bai-wix) instead of full OAuth.
---

# share-bai-mastodon

Đăng bài tự động lên Mastodon (status/toot ngắn): đọc 1 bài viết nguồn từ URL, viết lại thành 1 toot ngắn (≤500 ký tự) theo từ khóa chính cho trước, rồi publish qua Mastodon REST API (`POST /api/v1/statuses`). Kiến trúc tương tự các skill `share-bai-*` khác, khác biệt chính: nội dung là 1 status ngắn (không phải bài ~1000 từ), Mastodon CHO PHÉP link clickable + tự tạo preview card (khác Instagram), và xác thực bằng **access token tĩnh** tạo trực tiếp trong web UI — không có luồng OAuth qua trình duyệt, không có client_secret/refresh_token.

## Khi nào dùng

User gõ:

- `/share-bai-mastodon [từ khóa chính], [URL nguồn]`
- `/share-bai-mastodon [từ khóa chính], [URL nguồn], [tài khoản Mastodon khác mặc định]`

KHÔNG dùng skill này khi:

- User muốn đăng lên nền tảng khác Mastodon (WordPress, Blogger, Google Group, Tumblr, Wix, Instagram...) — đó là skill riêng khác.
- User chỉ muốn tóm tắt/review bài viết, không cần đăng lên đâu cả.
- User muốn đăng 1 bài dài đầy đủ (~1000 từ) lên Mastodon — nền tảng giới hạn 500 ký tự/status, không phù hợp cho nội dung dài; skill này chỉ tạo được toot ngắn kèm link về bài gốc.

## Tiền điều kiện

- [ ] User (chủ tài khoản Mastodon đích) đã tạo 1 access token tại Preferences → Development → New application trên instance đích (vd `mastodon.social`), scope tối thiểu `write:statuses` + `write:media` — Step 2 hướng dẫn nếu chưa có.
- [ ] File `mastodon-accounts.local.json` nằm ngay trong thư mục skill này (`.claude/skills/share-bai-mastodon/mastodon-accounts.local.json`, cùng cấp với `scripts/`, `references/`) — lưu `access_token`/`instance_url`/`account_handle` từng tài khoản. Đã có sẵn 1 entry rỗng token cho `tenban@mastodon.social`; Step 2 sẽ điền token khi user cung cấp.
- [ ] Mọi lệnh HTTP/JSON trong pipeline BẮT BUỘC gọi qua `scripts/mastodon-http.sh` và `scripts/mastodon-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp. 2 script này cần được allowlist trong `.claude/settings.json` để chạy không cần xác nhận thủ công.

## Default settings

| Setting | Default | Override khi |
|---|---|---|
| Độ dài toot | ≤500 ký tự (đo qua `char-count`, xem `references/rewrite-guidelines.md`) | — (giới hạn cứng của instance, không override được) |
| Ảnh bắt buộc | Không — thiếu ảnh vẫn đăng bình thường | User yêu cầu bắt buộc phải có ảnh mới đăng |
| Xác nhận trước khi đăng | Không hỏi — auto-publish ngay sau khi soạn xong | User yêu cầu skill dừng lại chờ xác nhận trước khi đăng |
| Tài khoản đích khi không chỉ định | Tài khoản duy nhất có trong `mastodon-accounts.local.json` | Nhiều tài khoản trong file → hỏi user chọn |
| Visibility | `public` (hiện trên federated timeline + hashtag search) | User yêu cầu `unlisted`/`private`/`direct` |
| Link trong toot | URL trần (plain text), Mastodon tự linkify + tạo preview card | — (KHÔNG bọc Markdown/HTML, Mastodon không parse) |
| Access token | Không hết hạn, dùng thẳng mọi lần chạy, không cần refresh | — (khác OAuth access_token của `wp`/`blogger`/`ggr`/`tumblr`) |

## Pipeline — 8 bước

Theo thứ tự, không skip.

### Step 1 — Parse input

Tách 3 phần từ input, cách nhau bởi dấu phẩy: từ khóa chính, URL nguồn, tài khoản Mastodon đích (tuỳ chọn). URL nguồn luôn bắt đầu bằng `http`, dùng mốc đó để tách đúng phần từ khóa khi từ khóa tự nó chứa dấu phẩy.

- Thiếu từ khóa hoặc URL nguồn → hỏi lại user, KHÔNG đoán.
- Không có tài khoản đích trong input → dùng tài khoản duy nhất trong `mastodon-accounts.local.json` nếu file chỉ có 1 entry (mặc định: `tenban@mastodon.social`); nếu file có nhiều entry → hỏi user chọn/khai báo tài khoản.

**Exit condition**: có đủ từ khóa chính, URL nguồn, và xác định được account-key đích.

### Step 2 — Đảm bảo có access token hợp lệ

Đọc `references/mastodon-api-steps.md` mục "Setup access token".

- Entry chưa có `access_token` (rỗng hoặc thiếu) → hướng dẫn user tạo token tại `<instance_url>` → Preferences → Development → New application, scope `write:statuses` + `write:media`, lưu bằng `node scripts/mastodon-json.js set-credentials`.
- Đã có `access_token` → verify còn hợp lệ bằng `bash scripts/mastodon-http.sh verify-token <instance_url> <access_token> <out-file>`; response có `username` → dùng thẳng, không hỏi lại. HTTP 401 → coi như mất token, quay lại hướng dẫn tạo token mới.

**Decision point**: luôn hỏi/hướng dẫn khi thiếu token cho đúng tài khoản đích. KHÔNG tự bịa token hoặc dùng token của tài khoản khác.

### Step 3 — Đọc bài viết nguồn

Gọi `bash scripts/mastodon-http.sh fetch-source <url> <out-file>` để tải trang nguồn, rồi đọc file đó và trích: nội dung chính (ý/số liệu nổi bật nhất để tóm tắt), URL ảnh đại diện (`og:image`/`twitter:image`); nếu không có meta ảnh thì lấy URL ảnh `<img>` đầu tiên trong nội dung bài. Nếu response ban đầu chỉ chứa 1 đoạn script set cookie rồi reload (JS challenge của WAF/CDN), xem `references/mastodon-api-steps.md` mục "Xử lý trang nguồn bị chặn bot" để lấy nội dung thật.

**Exit condition**: có đủ ý để tóm tắt thành toot ngắn. URL không truy cập được (404, timeout, chặn hẳn không qua được challenge...) → dừng pipeline, báo lỗi cụ thể cho user, KHÔNG bịa nội dung thay thế.

### Step 4 — Viết toot

Đọc `references/rewrite-guidelines.md`. Viết 1-2 câu tiếng Việt tóm tắt ý chính, chứa từ khóa chính tự nhiên ở câu đầu, thêm dòng link URL nguồn trần ở cuối (và hashtag liên quan nếu phù hợp, tối đa 4). Ghi ra 1 file text.

**Exit condition**: `node scripts/mastodon-json.js char-count <file>` trả về ≤500, từ khóa chính xuất hiện tự nhiên, đúng 1 URL trần (không Markdown/HTML), không câu nào copy nguyên văn >1 câu so với bài gốc (theo self-check trong guideline). Vượt 500 → cắt bớt câu bổ sung/hashtag, giữ nguyên câu mở + link.

### Step 5 — Chuẩn bị & upload ảnh (nếu có)

Nếu Step 3 lấy được URL ảnh đại diện hoặc ảnh đầu bài, đọc `references/mastodon-api-steps.md` mục "Upload ảnh":
```
bash scripts/mastodon-http.sh download-image <image-url> <local-file> <cookie>
bash scripts/mastodon-http.sh upload-media <instance_url> <access_token> <local-file> <mime-type> "<mô tả ảnh>" <out-file>
node scripts/mastodon-json.js show-media-result <out-file>
```
Lấy `id` từ response làm `media_id` cho Step 6.

Nếu không tìm được ảnh nào khả dụng, tải ảnh lỗi, hoặc upload lỗi → bỏ qua, đăng toot không ảnh. KHÔNG chặn pipeline chỉ vì thiếu ảnh.

### Step 6 — Đăng toot

Đọc `references/mastodon-api-steps.md` mục "Tạo & đăng status". Gọi `node scripts/mastodon-json.js build-status-payload <status-text-file> public <payload-file> [media_id]` rồi `bash scripts/mastodon-http.sh create-status <instance_url> <access_token> <payload-file> <out-file>`. KHÔNG dừng lại hỏi user xác nhận trước khi gọi — user đã yêu cầu skill này tự publish luôn sau khi soạn xong.

**Exit condition**: response có `id` và `url`, không có field `error`.

Nếu response lỗi 422 do vượt 500 ký tự (hiếm nếu đã check ở Step 4, nhưng có thể lệch nếu instance đích khác mastodon.social có `characters_reserved_per_url` khác) → cắt ngắn nội dung, giữ câu mở + link, gọi lại.

### Step 7 — Verify

Gọi `node scripts/mastodon-json.js show-post-result <out-file>` để đọc `id`/`url`/`uri`/`visibility`/`error`. Kiểm tra có `url` hợp lệ và KHÔNG có field `error`. Response lỗi (4xx/5xx, hoặc có `error`) → báo cụ thể lỗi cho user, KHÔNG báo thành công.

### Step 8 — Report

Output theo format ở mục Output.

## Decision points

| Step | Hỏi user khi | Auto-proceed khi |
|---|---|---|
| 1 | Thiếu từ khóa hoặc URL nguồn; tài khoản đích không xác định được | Input đủ từ khóa + URL, tài khoản đích rõ ràng |
| 2 | Chưa có access token, hoặc token verify trả 401 | Đã có access_token hợp lệ trong `mastodon-accounts.local.json` |
| 3 | — (không hỏi, dừng luôn nếu không qua được challenge) | URL nguồn fetch thành công (trực tiếp hoặc sau khi xử lý cookie challenge) |
| 6 | — (không hỏi, auto-publish theo yêu cầu user) | Luôn tự gọi API đăng ngay sau khi soạn xong Step 4-5 |

## Recovery

- URL nguồn lỗi/không truy cập được, hoặc bị chặn bot không xử lý được bằng cookie challenge → dừng, báo user, không bịa nội dung.
- `verify-token` trả 401 (token bị revoke) → dừng, hướng dẫn user tạo lại token theo `references/mastodon-api-steps.md`, không tự đoán token khác.
- Download/upload ảnh lỗi ở Step 5 → bỏ ảnh, tiếp tục Step 6 không có `media_ids`.
- `upload-media` trả `url: null` (processing) → poll `get-media` 1 lần; vẫn `null` → bỏ ảnh, đăng tiếp không ảnh.
- API đăng status trả lỗi 422 do vượt ký tự → cắt ngắn nội dung (giữ câu mở + link), gọi lại đúng 1 lần; vẫn lỗi → báo user, không tự ý cắt xén tới mức mất nghĩa.
- API đăng status trả lỗi khác (4xx/5xx không liên quan ký tự) → dừng, báo rõ mã lỗi + message từ response, không báo "đã đăng thành công".

## Output format

```
Đã đăng bài thành công lên Mastodon.

Tài khoản: <account-key>
Nội dung toot: <status text>
Từ khóa chính: <keyword> (link về: <source URL>)
Link toot đã đăng: <post url>
```

Fetch lỗi ở Step 3, thiếu access token ở Step 2, hoặc API lỗi ở Step 6, thì báo rõ bước nào fail và lý do thay vì trả Output format trên.

## Anti-patterns

- KHÔNG copy nguyên văn câu dài từ bài gốc vào toot — phải cô đọng, diễn đạt lại bằng câu chữ ngắn gọn riêng.
- KHÔNG bịa thông tin/số liệu không có trong bài gốc.
- KHÔNG dùng các từ xếp hạng tuyệt đối như "nhất", "duy nhất", "số 1", "hàng đầu", "tốt nhất"... khi không có tài liệu/số liệu trong bài gốc chứng minh cho khẳng định đó.
- KHÔNG tự đếm ký tự bằng mắt hoặc `.length` thô — luôn qua `node scripts/mastodon-json.js char-count`, vì Mastodon tính link cố định 23 ký tự bất kể độ dài thật, đếm tay sẽ sai và gây lỗi 422 lúc đăng.
- KHÔNG bọc link nguồn bằng Markdown `[text](url)` hay HTML `<a>` — Mastodon không parse, hiển thị nguyên ký tự thừa. Luôn dùng URL trần, Mastodon tự linkify.
- KHÔNG lưu access_token dạng plaintext trong SKILL.md, chat log, hay file được commit — chỉ lưu trong `mastodon-accounts.local.json` (trong thư mục skill), thêm vào `.gitignore` nếu có.
- KHÔNG tự ý đăng lên tài khoản Mastodon khác tài khoản user đã chỉ định (vd user gõ tài khoản đích khác nhưng chỉ có token tài khoản A sẵn có trong `mastodon-accounts.local.json` → không được lặng lẽ đăng vào tài khoản A thay thế).
- KHÔNG báo "đăng thành công" khi response có field `error` hoặc thiếu `url` — verify response thật trước khi report (Step 7).

## Skill files

| File | Purpose | Load when |
|---|---|---|
| `references/rewrite-guidelines.md` | Quy tắc viết toot ngắn: độ dài, cách Mastodon tính link, hashtag, self-check | Step 4 |
| `references/mastodon-api-steps.md` | Chi tiết setup access token, giới hạn ký tự, upload ảnh, tạo & đăng status, xử lý bot challenge | Step 2, 3, 5, 6, 7 |
| `scripts/mastodon-http.sh` | Thực thi mọi lệnh HTTP (fetch source, download image, verify token, upload media, create status) — allowlisted trong `.claude/settings.json` | Step 2, 3, 5, 6 |
| `scripts/mastodon-json.js` | Thực thi mọi xử lý JSON (đọc/lưu credential, đếm ký tự, build payload, đọc kết quả) — allowlisted trong `.claude/settings.json` | Step 1, 2, 4, 5, 6, 7 |
| `mastodon-accounts.local.json` | Credential từng tài khoản (`access_token`/`instance_url`/`account_handle`) — KHÔNG commit, chỉ đọc/ghi qua `scripts/mastodon-json.js` | Step 2, 5, 6, 7 |

---
name: share-bai-wix
description: This skill should be used when the user asks to "đăng bài lên Wix", "share bài lên Wixsite", "chia sẻ bài lên Wix blog", "đăng blog Wix", "/share-bai-wix [từ khóa], [URL]", "post to Wix blog", or wants to auto-publish a rewritten article to a Wix site's blog. Reads 1 source article from a URL, rewrites it around a given primary keyword, then publishes via the Wix Blog API (Draft Posts API, Ricos rich content, API Key auth). Same skill family as share-bai-wp/share-bai-blogger/share-bai-ggr/share-bai-tumblr — different target platform; auth is a non-expiring API Key instead of OAuth.
---

# share-bai-wix

Đăng bài tự động lên Wix Blog: đọc 1 bài viết nguồn từ URL, viết lại theo từ khóa chính cho trước, rồi publish qua Wix Blog API (Draft Posts API, định dạng nội dung Ricos). Kiến trúc tương tự `share-bai-wp` (cùng nhóm skill đăng bài tự động, khác nền tảng đích và cơ chế auth). Khác biệt chính: Wix xác thực bằng **API Key** không hết hạn (account owner tự tạo tại `manage.wix.com`), KHÔNG có luồng OAuth qua trình duyệt như `share-bai-wp`/`share-bai-blogger`/`share-bai-ggr`/`share-bai-tumblr`.

## Khi nào dùng

User gõ:

- `/share-bai-wix [từ khóa chính], [URL nguồn]`
- `/share-bai-wix [từ khóa chính], [URL nguồn], [site Wix khác site mặc định]`

KHÔNG dùng skill này khi:

- User muốn đăng lên nền tảng khác Wix (WordPress, Blogger, Google Group, Tumblr...) — đó là skill riêng khác (`share-bai-wp`, `share-bai-blogger`, `share-bai-ggr`, `share-bai-tumblr`).
- User chỉ muốn tóm tắt/review bài viết, không cần đăng lên đâu cả.
- Site đích không dùng Wix Blog app (site Wix không có blog, hoặc dùng blog bên thứ ba nhúng vào) — skill này chỉ gọi được Wix Blog API.

## Tiền điều kiện

- [ ] User (account owner hoặc co-owner của tài khoản Wix — bắt buộc, collaborator thường không tạo được key) đã tạo 1 API Key tại `manage.wix.com/account/api-keys`, phạm vi "Specific sites" trỏ đúng site đích, gán quyền quản lý Blog + đọc Members — Step 2 hướng dẫn nếu chưa có.
- [ ] File `wix-accounts.local.json` nằm ngay trong thư mục skill này (`.claude/skills/share-bai-wix/wix-accounts.local.json`, cùng cấp với `scripts/`, `references/`) — lưu `api_key`/`account_id`/`site_id`/`member_id` từng site. Nếu chưa có, Step 2 sẽ tạo.
- [ ] Site đích đã cài Wix Blog app (site mới tạo trên Wix thường có sẵn).
- [ ] Mọi lệnh HTTP/JSON trong pipeline BẮT BUỘC gọi qua `scripts/wix-http.sh` và `scripts/wix-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp. 2 script này cần được allowlist trong `.claude/settings.json` để chạy không cần xác nhận thủ công.

> ⚠️ **Checklist nội dung bắt buộc:** `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md` — đọc ở bước viết lại bài, cùng với `references/rewrite-guidelines.md`.

## Default settings

| Setting | Default | Override khi |
|---|---|---|
| Độ dài bài viết lại | 900-1100 từ | — (cố định, xem `references/rewrite-guidelines.md`) |
| Ảnh bắt buộc | **Có, tối thiểu 3 ảnh/bài ~1000 chữ** (Mastodon: 1 ảnh) — theo `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md` mục 5: ảnh lấy từ trang nguồn/website doanh nghiệp (ưu tiên `og:image`, ảnh trong nội dung, ảnh sản phẩm; bỏ logo/icon/ảnh <300px), liên quan đoạn văn xung quanh, căn giữa, chú thích in nghiêng <70 ký tự có từ khóa. Nguồn chỉ có 1–2 ảnh → dùng hết và báo "thiếu ảnh: có X/3"; **không có ảnh nào → dừng, không đăng**. Quy tắc này ghi đè mọi chỗ "thiếu ảnh vẫn đăng" / "1 ảnh" ở các bước bên dưới | — |
| Xác nhận trước khi đăng | Không hỏi — auto-publish ngay sau khi soạn xong | User yêu cầu skill dừng lại chờ xác nhận trước khi đăng |
| Site đích khi không chỉ định | Site duy nhất có trong `wix-accounts.local.json` | Nhiều site trong file → hỏi user chọn |
| Định dạng nội dung | Ricos content nodes (`heading`/`paragraph`/`image`), ảnh PHẢI import qua Wix Media trước khi dùng | — (KHÔNG dùng thẳng URL ảnh nguồn như Tumblr — Wix không hiển thị được) |
| API Key | Không hết hạn, dùng thẳng mọi lần chạy, không cần refresh | — (khác OAuth access_token của 4 skill kia) |

## Pipeline — 8 bước

Theo thứ tự, không skip.

### Step 1 — Parse input

Tách 3 phần từ input, cách nhau bởi dấu phẩy: từ khóa chính, URL nguồn, site Wix đích (tuỳ chọn). URL nguồn luôn bắt đầu bằng `http`, dùng mốc đó để tách đúng phần từ khóa khi từ khóa tự nó chứa dấu phẩy.

- Thiếu từ khóa hoặc URL nguồn → hỏi lại user, KHÔNG đoán.
- Không có site đích trong input → dùng site duy nhất trong `wix-accounts.local.json` nếu file chỉ có 1 entry; nếu file có nhiều entry hoặc rỗng → hỏi user chọn/khai báo site.

**Exit condition**: có đủ từ khóa chính, URL nguồn, và xác định được site-key đích.

### Step 2 — Đảm bảo có API Key + site_id + member_id

Đọc `references/wix-api-steps.md` mục "Setup API Key", "Lấy site_id, account_id", "Lấy member_id".

- Chưa có entry (chưa có API Key) → hướng dẫn user tạo key tại `manage.wix.com/account/api-keys` (chỉ account owner/co-owner làm được), phạm vi Specific sites, lấy site_id (từ URL dashboard hoặc `query-sites`) và account_id (cùng trang API Keys Manager), lưu bằng `node scripts/wix-json.js set-credentials`.
- Có `api_key`/`site_id` nhưng chưa có `member_id` → gọi `bash scripts/wix-http.sh get-members`, lưu bằng `node scripts/wix-json.js save-member-id` (chỉ cần làm 1 lần/site, không lặp lại các lần sau).
- Đã có đủ `api_key`/`site_id`/`member_id` → dùng thẳng, không cần refresh gì (API Key Wix không hết hạn).

**Decision point**: luôn hỏi/hướng dẫn khi thiếu API Key hoặc site_id/member_id cho đúng site đích. KHÔNG tự bịa key hoặc dùng key của site khác. Nếu API trả 401/403 (key bị revoke, hoặc thiếu quyền) → coi như mất key, quay lại hướng dẫn tạo key mới.

### Step 3 — Đọc bài viết nguồn

Gọi `bash scripts/wix-http.sh fetch-source <url> <out-file>` để tải trang nguồn, rồi đọc file đó và trích: tiêu đề, nội dung chính, URL ảnh đại diện (`og:image`/`twitter:image`); nếu không có meta ảnh thì lấy URL ảnh `<img>` đầu tiên trong nội dung bài. Nếu response ban đầu chỉ chứa 1 đoạn script set cookie rồi reload (JS challenge của WAF/CDN), xem `references/wix-api-steps.md` mục "Xử lý trang nguồn bị chặn bot" để lấy nội dung thật.

**Exit condition**: có đủ text để viết lại. URL không truy cập được (404, timeout, chặn hẳn không qua được challenge...) → dừng pipeline, báo lỗi cụ thể cho user, KHÔNG bịa nội dung thay thế.

### Step 4 — Viết lại bài viết thành cấu trúc Ricos

Đọc `references/rewrite-guidelines.md`. Viết lại ~1000 từ tiếng Việt theo guideline đó: giữ nghĩa & thông tin chính xác như bài gốc, không copy nguyên câu, chứa từ khóa chính. Ghi ra 1 file JSON mảng cấu trúc rút gọn (`references/wix-api-steps.md` mục "Cấu trúc Ricos content nodes") gồm các block `paragraph`/`heading`/`image` xen kẽ.

KHÔNG thêm block `heading` level 1 chứa lại tiêu đề ở đầu mảng — Wix tự hiển thị `draftPost.title` (Step 6) thành 1 heading lớn riêng phía trên nội dung, thêm heading level 1 trùng nội dung sẽ khiến tiêu đề hiển thị LẶP 2 LẦN trên trang. Block đầu tiên nên là `paragraph` (đoạn mở đầu) hoặc `heading` level 2 trở lên nếu cần chia mục ngay từ đầu. Convert sang Ricos node thật bằng `node scripts/wix-json.js build-content-nodes`.

Đồng thời tạo 1 slug kebab-case KHÔNG DẤU từ tiêu đề (giống quy ước ở `share-bai-wp`/`share-bai-blogger`/`share-bai-tumblr`) — dùng ở Step 6 để sửa lại URL bài đăng, vì Wix không cho đặt slug tùy chỉnh lúc tạo bài (chỉ tự sinh từ tiêu đề, percent-encode dấu tiếng Việt thành URL khó đọc).

Gắn hyperlink vào ĐÚNG 1 lần xuất hiện của từ khóa chính bằng:
```
node scripts/wix-json.js add-link-decoration <content-nodes-file> <node-index> "<từ khóa chính>" <source-url> <out-file>
```
Lệnh này tự tách node text thành 3 phần (trước/link/sau) để link chỉ áp dụng đúng cụm từ khóa — KHÔNG dùng offset `start`/`end` trên 1 node duy nhất (xem lý do trong `references/wix-api-steps.md` mục "Gắn link vào từ khóa chính").

**Exit condition**: `node scripts/wix-json.js word-count <content-nodes-file>` trả về 900-1100, đúng 1 link ở từ khóa chính (verify qua `add-link-decoration` chạy thành công không lỗi), không đoạn nào trùng nguyên văn >1 câu với bài gốc (theo self-check trong guideline).

### Step 5 — Import ảnh (nếu có)

Nếu Step 3 lấy được URL ảnh đại diện hoặc ảnh đầu bài → import vào Wix Media trước khi dùng (KHÔNG dùng thẳng URL ảnh nguồn — Wix không hiển thị được):
```
bash scripts/wix-http.sh import-media <api_key> <site_id> <image-url-nguồn> <mime-type> <display-name> <out-file>
node scripts/wix-json.js show-import-result <out-file>
```
Dùng URL `wixstatic.com` trả về (không phải URL gốc) làm giá trị `url` cho block `image` trong cấu trúc ở Step 4, đặt sau đoạn mở đầu.

Import lỗi, hoặc `operationStatus` không chuyển `READY` → bỏ ảnh, tiếp tục đăng bài không ảnh. KHÔNG chặn pipeline chỉ vì thiếu ảnh.

### Step 6 — Tạo & publish bài

Đọc `references/wix-api-steps.md` mục "Tạo & publish bài". Gọi `node scripts/wix-json.js build-post-payload <content-nodes-file> "<tiêu đề>" <member_id> <payload-file>` rồi `bash scripts/wix-http.sh create-draft-post <api_key> <site_id> <payload-file> <out-file>`. KHÔNG dừng lại hỏi user xác nhận trước khi gọi — user đã yêu cầu skill này tự publish luôn sau khi soạn xong (`build-post-payload` đã đặt sẵn `publish: true`).

**Exit condition**: response có `draftPost.status` = `"PUBLISHED"`.

Nếu lỗi cụ thể liên quan ảnh (import chưa `READY` khi tạo bài) → thử lại 1 lần: bỏ node ảnh khỏi content, build lại payload, gọi lại `create-draft-post` không ảnh.

Sau khi tạo thành công, sửa lại slug sang bản ASCII đã chuẩn bị ở Step 4 (CreateDraftPost không nhận field slug tùy chỉnh, luôn tự sinh slug có dấu từ tiêu đề):
```
node scripts/wix-json.js build-slug-update-payload <post-id-từ-response-vừa-tạo> <slug-ascii> <slug-payload-file>
bash scripts/wix-http.sh update-draft-post <api_key> <site_id> <post-id> <slug-payload-file> <out-file>
```

### Step 7 — Verify

Gọi `node scripts/wix-json.js show-post-result <out-file> <site-domain>` để đọc `id`/`title`/`status`/`post_url`. Kiểm tra `status` đúng `"PUBLISHED"` và có `post_url`. Response lỗi (4xx/5xx, hoặc `status` khác `"PUBLISHED"`) → báo cụ thể lỗi cho user, KHÔNG báo thành công.

### Step 8 — Report

Output theo format ở mục Output.

## Decision points

| Step | Hỏi user khi | Auto-proceed khi |
|---|---|---|
| 1 | Thiếu từ khóa hoặc URL nguồn; site đích không xác định được | Input đủ từ khóa + URL, site đích rõ ràng |
| 2 | Chưa có API Key, hoặc chưa có site_id/member_id cho site đích | Đã có đủ api_key/site_id/member_id trong `wix-accounts.local.json` |
| 3 | — (không hỏi, dừng luôn nếu không qua được challenge) | URL nguồn fetch thành công (trực tiếp hoặc sau khi xử lý cookie challenge) |
| 6 | — (không hỏi, auto-publish theo yêu cầu user) | Luôn tự gọi API publish ngay sau khi soạn xong Step 4-5 |

## Recovery

- URL nguồn lỗi/không truy cập được, hoặc bị chặn bot không xử lý được bằng cookie challenge → dừng, báo user, không bịa nội dung.
- API trả 401/403 (API Key bị revoke, hoặc thiếu quyền Blog/Members) → dừng, hướng dẫn user tạo lại key theo `references/wix-api-steps.md`, không tự đoán key khác.
- `add-link-decoration` báo lỗi không tìm thấy/ambiguous cụm từ khóa → viết lại câu chứa từ khóa cho rõ ràng, unique hơn trong node đó, chạy lại.
- Import ảnh lỗi hoặc `operationStatus` không `READY` ở Step 5 → bỏ ảnh, tiếp tục Step 6 không có node ảnh.
- API tạo bài trả lỗi (4xx/5xx) không liên quan ảnh → dừng, báo rõ mã lỗi + message từ response, không báo "đã đăng thành công".

## Output format

```
Đã đăng bài thành công lên Wix.

Site: <site-key>
Tiêu đề: <title>
Từ khóa chính: <keyword> (link về: <source URL>)
Link bài đã đăng: <post_url>
```

Fetch lỗi ở Step 3, thiếu API Key/site_id/member_id ở Step 2, hoặc API lỗi ở Step 6, thì báo rõ bước nào fail và lý do thay vì trả Output format trên.

## Anti-patterns

- KHÔNG copy nguyên văn nhiều câu liên tiếp từ bài gốc (vd: giữ nguyên cả đoạn mở đầu của bài gốc, chỉ đổi vài từ — đây vẫn là đạo văn).
- KHÔNG bịa thông tin/số liệu không có trong bài gốc (vd: bài gốc không nêu con số cụ thể nhưng tự thêm "theo thống kê, 90% website từng bị tấn công DDoS").
- KHÔNG dùng các từ xếp hạng tuyệt đối như "nhất", "duy nhất", "số 1", "hàng đầu", "tốt nhất"... khi không có tài liệu/số liệu trong bài gốc chứng minh cho khẳng định đó — xem chi tiết ở `references/rewrite-guidelines.md`.
- KHÔNG lưu api_key dạng plaintext trong SKILL.md, chat log, hay file được commit (vd: paste key vào Output format để "báo cáo lại cho user") — chỉ lưu trong `wix-accounts.local.json` (trong thư mục skill), thêm vào `.gitignore` nếu có.
- KHÔNG tự ý đăng lên site khác site user đã chỉ định (vd: user gõ site đích là `site2.wixsite.com/site2` nhưng chỉ có key site A sẵn có trong `wix-accounts.local.json` → không được lặng lẽ đăng vào site A thay thế).
- KHÔNG dùng thẳng URL ảnh nguồn trong node `image` — luôn qua `import-media` trước để lấy URL `wixstatic.com`, nếu không ảnh sẽ không hiển thị được trên bài đăng.
- KHÔNG tự viết decoration `LINK` kèm offset `start`/`end` trên 1 node TEXT duy nhất — Wix's Ricos renderer KHÔNG tôn trọng offset này, sẽ biến cả node (cả đoạn văn) thành link thay vì chỉ đúng cụm từ khóa (lỗi đã xảy ra thật, xem `references/wix-api-steps.md`). Luôn dùng `add-link-decoration` (tự tách node thành 3 phần trước/link/sau).
- KHÔNG thêm block `heading` level 1 chứa lại tiêu đề ở đầu content — Wix tự hiển thị `draftPost.title` thành heading riêng phía trên, thêm heading trùng sẽ khiến tiêu đề hiển thị lặp lại 2 lần trên bài đã publish (lỗi đã xảy ra thật).
- KHÔNG báo "đăng thành công" khi response không có `draftPost.status: "PUBLISHED"` — verify response thật trước khi report (Step 7).

## Skill files

| File | Purpose | Load when |
|---|---|---|
| `references/rewrite-guidelines.md` | Quy tắc viết lại bài: độ dài, giữ nghĩa, gắn từ khóa + link, cấu trúc, self-check | Step 4 |
| `references/wix-api-steps.md` | Chi tiết API Key/site_id/member_id, cấu trúc Ricos, gắn link offset, import ảnh, tạo & publish bài, xử lý bot challenge | Step 2, 3, 4, 5, 6, 7 |
| `scripts/wix-http.sh` | Thực thi mọi lệnh HTTP (fetch source, query-sites, get-members, import-media, create-draft-post) — allowlisted trong `.claude/settings.json` | Step 2, 3, 5, 6 |
| `scripts/wix-json.js` | Thực thi mọi xử lý JSON/Ricos (đọc/lưu credential, build content nodes, gắn link offset, build payload, đếm từ, đọc kết quả) — allowlisted trong `.claude/settings.json` | Step 1, 2, 4, 5, 6, 7 |
| `wix-accounts.local.json` | Credential từng site (`api_key`/`account_id`/`site_id`/`member_id`) — KHÔNG commit, chỉ đọc/ghi qua `scripts/wix-json.js` | Step 2, 5, 6, 7 |

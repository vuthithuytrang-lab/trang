# Đăng bài lên Wix Blog qua API — Steps

Wix có REST API tạo bài blog thật (Draft Posts API), xác thực bằng **API Key** thay vì luồng OAuth qua trình duyệt — khác hẳn `share-bai-wp`/`share-bai-blogger`/`share-bai-ggr`/`share-bai-tumblr`. Không có `client_secret`, không có `access_token`/`refresh_token`, không có bước authorize/Allow nào cả — chủ tài khoản Wix tự tạo 1 API Key dùng mãi mãi (không hết hạn).

Mọi lệnh gọi HTTP dùng qua `scripts/wix-http.sh`, mọi xử lý JSON/Ricos dùng qua `scripts/wix-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp, vì 2 script này được allowlist trong `.claude/settings.json` (domain hardcode sẵn trong script) để pipeline chạy không cần xác nhận thủ công từng lệnh.

## Contents

- Setup API Key (1 lần / tài khoản Wix)
- Lấy site_id, account_id
- Lấy member_id (1 lần / site)
- Cấu trúc Ricos content nodes
- Gắn link vào từ khóa chính (decoration offset)
- Import ảnh (bắt buộc trước khi dùng trong content)
- Tạo & publish bài (Draft Posts API)
- Xử lý trang nguồn bị chặn bot
- scripts/wix-http.sh — reference lệnh
- scripts/wix-json.js — reference lệnh
- Known limits

## Setup API Key (1 lần / tài khoản Wix)

1. Hướng dẫn user (phải là **account owner hoặc co-owner** — member/collaborator thường không tạo được key) vào `https://manage.wix.com/account/api-keys`.
2. Bấm tạo key mới. Ở phần **Site access**, chọn **Specific sites** rồi chọn đúng site đích (tránh chọn "All sites" nếu không cần — nguyên tắc least privilege). Gán quyền (permissions) tối thiểu cần cho skill: quyền quản lý Blog (tạo/publish post) và quyền đọc Members (`Read Members`).
3. Wix có thể yêu cầu xác minh 2 bước qua SMS lúc tạo key — nếu không nhận được mã, đó là vấn đề phía tài khoản Wix của user, không phải lỗi API.
4. Sau khi tạo, trang hiển thị **API Key** (chuỗi dài) — đây là giá trị duy nhất cần lưu, không có secret thứ hai đi kèm.
5. Cùng trang **API Keys Manager** cũng hiển thị **Account ID** của tài khoản — lấy luôn giá trị này.
6. Lưu vào `wix-accounts.local.json`:
   ```
   node scripts/wix-json.js set-credentials wix-accounts.local.json <site-key> <api_key> <account_id> <site_id>
   ```
   `<site-key>` khuyến nghị dùng domain site (vd `mysite.wixsite.com/mysite` hoặc domain riêng nếu đã custom). `site_id` lấy theo mục dưới.

## Lấy site_id, account_id

- **site_id**: cách nhanh nhất là lấy từ URL dashboard của site trong trình duyệt — phần ngay sau `/dashboard/`, dạng `https://manage.wix.com/dashboard/<SITE_ID>/home`. Nếu user không tự tìm được, dùng account-level API key (đã có ở bước Setup) để liệt kê site:
  ```
  bash scripts/wix-http.sh query-sites <api_key> <account_id> <out-file>.json
  ```
  Đọc field `id` của site khớp tên/domain user muốn trong response.
- **account_id**: lấy trực tiếp trên trang `manage.wix.com/account/api-keys` (hiển thị cùng chỗ với API key vừa tạo).

## Lấy member_id (1 lần / site)

Draft Posts API bắt buộc field `memberId` (chủ bài viết) khi gọi từ bên thứ ba. Lấy 1 lần đầu, không cần lấy lại mỗi lần đăng bài:

```
bash scripts/wix-http.sh get-members <api_key> <site_id> <out-file>.json
node scripts/wix-json.js save-member-id wix-accounts.local.json <site-key> <out-file>.json
```

`save-member-id` mặc định lấy member đầu tiên trong danh sách trả về (thường là site owner với site mới, ít member). Nếu site có nhiều member và cần chỉ định đúng người viết bài, đọc trực tiếp response JSON (field `members[].profile.nickname`) để xác định đúng member trước khi lưu tay bằng `set-credentials` với tham số `member_id`.

## Cấu trúc Ricos content nodes

Nội dung bài dùng **Ricos** — 1 cây JSON node, khác hẳn HTML/Gutenberg. Viết ra 1 file cấu trúc rút gọn trước, rồi convert bằng script (viết tay Ricos node đầy đủ rất dễ sai vì lồng nhau `nodes`/`textData`/`imageData`):

```json
[
  { "type": "paragraph", "text": "Đoạn mở đầu chứa từ khóa chính..." },
  { "type": "image", "url": "<wixstatic URL từ bước import ảnh>", "altText": "Mô tả ảnh" },
  { "type": "heading", "level": 2, "text": "Heading phụ" },
  { "type": "paragraph", "text": "Đoạn thân bài..." }
]
```

Convert sang Ricos node thật:

```
node scripts/wix-json.js build-content-nodes <structure-file> <out-file>
```

**Đã xác nhận qua thực tế chạy skill (2026-08-01): KHÔNG thêm block `heading` level 1 chứa lại tiêu đề ở đầu mảng.** Wix tự hiển thị `draftPost.title` (field riêng, xem mục "Tạo & publish bài") thành 1 heading lớn ngay phía trên nội dung — thêm heading level 1 trùng chữ trong content sẽ khiến tiêu đề hiển thị lặp lại 2 lần trên trang đã publish. Block đầu tiên nên là `paragraph` (đoạn mở đầu), heading phụ trong content chỉ nên dùng level 2 trở lên.

## Gắn link vào từ khóa chính

Ricos không dùng `<a href>`. Dùng script để gắn link, KHÔNG tự viết tay:

```
node scripts/wix-json.js add-link-decoration <content-nodes-file> <node-index> "<từ khóa chính>" <source-url> <out-file>
```

`node-index` là vị trí (0-based) của node `paragraph`/`heading` chứa từ khóa trong mảng đã convert (thường là node 0 — đoạn mở đầu, vì không còn heading tiêu đề trùng lặp ở đầu mảng như trước).

**Đã xác nhận qua thực tế chạy skill (2026-08-01) — lỗi đã từng xảy ra thật, không phải giả định**: cách làm ban đầu (gắn 1 decoration `LINK` kèm offset `start`/`end` lên MỘT node TEXT duy nhất) bị Wix's Ricos renderer BỎ QUA offset và áp decoration lên TOÀN BỘ text của node đó — khiến cả đoạn văn dài trở thành 1 link, thay vì chỉ đúng cụm từ khóa. Cách đúng, script hiện đang dùng: **tách node TEXT gốc thành 3 node con liền kề** — (1) text trước cụm từ khóa (không decoration), (2) text đúng bằng cụm từ khóa với `decorations: [{"type":"LINK","linkData":{"link":{"url":...}}}]` áp cho TOÀN BỘ text của riêng node này (không có `start`/`end`), (3) text sau cụm từ khóa (không decoration). Ghép 3 phần lại đúng bằng văn bản gốc, không thừa/thiếu ký tự. Script tự báo lỗi nếu không tìm thấy cụm từ, hoặc cụm từ xuất hiện >1 lần trong node đó (chọn cụm đủ dài để không ambiguous).

## Import ảnh (bắt buộc trước khi dùng trong content)

Khác Tumblr (nhận thẳng URL ảnh ngoài), Wix **bắt buộc** phải import ảnh vào Wix Media Manager trước, lấy về URL `wixstatic.com`, rồi mới dùng URL đó trong node `image` — dùng thẳng URL ảnh gốc từ site nguồn sẽ không hiển thị được:

```
bash scripts/wix-http.sh import-media <api_key> <site_id> <image-url-nguồn> <mime-type> <display-name> <out-file>.json
node scripts/wix-json.js show-import-result <out-file>.json
```

`show-import-result` in ra `id`/`url`/`operationStatus`. Wix tự tải ảnh từ URL nguồn (không cần script này tự tải về máy trước) — nếu site nguồn chặn hotlink với server Wix, bước import sẽ lỗi hoặc `operationStatus` không chuyển sang `READY`; xử lý theo Recovery trong `SKILL.md` (bỏ ảnh, đăng tiếp không ảnh). Dùng giá trị `url` trả về (không phải URL gốc) làm `url` cho block `image` ở bước build-content-nodes.

## Tạo & publish bài (Draft Posts API)

```
node scripts/wix-json.js build-post-payload <content-nodes-file> "<tiêu đề>" <member_id> <out-file>.json
bash scripts/wix-http.sh create-draft-post <api_key> <site_id> <out-file>.json <post-response-file>.json
node scripts/wix-json.js show-post-result <post-response-file>.json <site-domain>
```

`build-post-payload` bọc content nodes thành body API đầy đủ (`draftPost.title`, `draftPost.memberId`, `draftPost.richContent`, `publish: true` để đăng ngay không cần gọi API publish riêng). `create-draft-post` tự thêm `fieldsets=URL` vào query string — thiếu tham số này response sẽ không trả field `url`, khiến không lấy được link bài thật. `show-post-result` in ra `id`/`title`/`status`/`post_url` — `status` phải là `"PUBLISHED"` mới coi là thành công.

**Đã xác nhận qua thực tế chạy skill**: `CreateDraftPost` KHÔNG nhận field `seoSlug` tùy chỉnh trong request — Wix luôn tự sinh slug từ tiêu đề, giữ nguyên dấu tiếng Việt và percent-encode khi hiển thị trên URL (vd `...post/trung-tâm-giám-sát-...`), khó đọc/khó chia sẻ. Fix bằng 1 lệnh `UpdateDraftPost` (PATCH) ngay sau khi tạo, dùng `id` bài vừa nhận được:

```
node scripts/wix-json.js build-slug-update-payload <post-id> <slug-ascii-kebab-case> <out-file>.json
bash scripts/wix-http.sh update-draft-post <api_key> <site_id> <post-id> <out-file>.json <update-response-file>.json
```

Payload PATCH phải kèm `"action": "UPDATE_PUBLICATION"` (script tự thêm) — vì bài đã ở trạng thái `PUBLISHED`, action mặc định `"UPDATE"` chỉ sửa bản draft chứ không áp dụng lên bản đã publish. Response trả về `url.path` đã chứa slug ASCII mới.

## Xử lý trang nguồn bị chặn bot (JS cookie challenge)

Một số site nguồn dùng WAF/CDN chặn request không chạy JS: response ban đầu rất ngắn, chỉ chứa 1 thẻ script dạng:

```html
<script>document.cookie="XXX=yyy...; expires=...; path=/";window.location.reload(true);</script>
```

Nếu gặp response dạng này (kiểm tra bằng cách đọc lại file `<out-file>` sau `fetch-source`, thấy size rất nhỏ và chỉ chứa script này):
1. Trích tên + giá trị cookie từ script đó.
2. Gọi lại `fetch-source` cùng URL, truyền thêm cookie ở tham số thứ 3:
   ```
   bash scripts/wix-http.sh fetch-source <url> <out-file> "XXX=yyy"
   ```
   Lần này sẽ trả về HTML đầy đủ của trang.

Đây là kiểu JS-redirect phổ biến ở nhiều CMS/CDN cho request đầu tiên, áp dụng cho trang public không yêu cầu đăng nhập — không phải bypass xác thực hay bảo mật.

## scripts/wix-http.sh — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `fetch-source` | `<url> <out-file> [cookie]` | Step 3 — đọc bài nguồn |
| `query-sites` | `<api_key> <account_id> <out-file>` | Step 2 — liệt kê site nếu user không tự tìm được site_id |
| `get-members` | `<api_key> <site_id> <out-file>` | Step 2 — lấy member_id (chỉ 1 lần/site) |
| `import-media` | `<api_key> <site_id> <image-url> <mime-type> <display-name> <out-file>` | Step 5 — import ảnh trước khi dùng trong content |
| `create-draft-post` | `<api_key> <site_id> <payload-file> <out-file>` | Step 6 — tạo & publish bài |
| `update-draft-post` | `<api_key> <site_id> <post-id> <payload-file> <out-file>` | Step 6 — sửa slug sang ASCII sau khi tạo |
| `get-draft-post` | `<api_key> <site_id> <post-id> <out-file>` | Debug/verify — đọc lại title/richContent thật đã lưu trên Wix |

## scripts/wix-json.js — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `get-account-field` | `<accounts-json-file> <site-key> <field>` | Step 1-2 — đọc api_key/account_id/site_id/member_id đã lưu |
| `set-credentials` | `<accounts-json-file> <site-key> <api_key> <account_id> <site_id> [member_id]` | Setup lần đầu |
| `save-member-id` | `<accounts-json-file> <site-key> <members-response-file>` | Step 2 — sau `get-members`, chỉ 1 lần/site |
| `build-content-nodes` | `<structure-file> <out-file>` | Step 4 — convert cấu trúc rút gọn sang Ricos nodes thật |
| `add-link-decoration` | `<content-nodes-file> <node-index> <link-text> <url> <out-file>` | Step 4 — gắn link từ khóa chính |
| `build-post-payload` | `<content-nodes-file> <title> <member_id> <out-file>` | Step 6 — trước `create-draft-post` |
| `build-slug-update-payload` | `<post-id> <slug-ascii> <out-file>` | Step 6 — trước `update-draft-post` |
| `word-count` | `<content-nodes-file>` | Step 4 — self-check độ dài bài viết lại |
| `show-import-result` | `<import-media-response-file>` | Step 5 — lấy URL wixstatic.com của ảnh đã import |
| `show-post-result` | `<post-response-file> <site-domain>` | Step 7 — verify + lấy id/status/post_url |

## Known limits

- API Key **không hết hạn** — không có bước refresh nào, khác 4 skill kia. Chỉ mất hiệu lực nếu account owner chủ động xoá/revoke key trong API Keys Manager.
- API Key chỉ tạo được bởi account owner/co-owner, không phải collaborator/blog writer thường — nếu user không có quyền này, cần nhờ đúng người sở hữu tài khoản Wix tạo key.
- Site-level API call (Draft Posts, Members, Media Import) yêu cầu header `wix-site-id`; account-level call (Query Sites) yêu cầu header `wix-account-id` — không dùng lẫn 2 header cho cùng 1 request.
- `fieldsets=URL` bắt buộc trên query string của `create-draft-post` để có field `url` trong response — thiếu tham số này response vẫn `status: "PUBLISHED"` nhưng không có link bài để báo cho user.
- Import ảnh qua URL: Wix tự fetch từ site nguồn, `operationStatus` chuyển `PENDING` → `READY` có thể mất vài giây; nếu site nguồn chặn hotlink với server Wix, import có thể lỗi hoặc kẹt ở `PENDING` — không có cách kiểm tra trước, xử lý theo Recovery trong `SKILL.md` (bỏ ảnh, đăng tiếp).
- Giới hạn kích thước 1 bài viết: 400KB (áp dụng cho toàn bộ `richContent`, hiếm khi chạm ngưỡng với bài ~1000 từ).

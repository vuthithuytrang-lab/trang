# Đăng bài lên Google Group qua Gmail API — Steps

Google Groups **không có REST API để tạo bài viết trực tiếp** (không như WordPress.com hay Blogger API v3). Cách hoạt động thật của Google Groups là: mỗi topic/reply là 1 email gửi tới địa chỉ đăng bài của group (`<tên-group>@googlegroups.com`). Vì vậy skill này "đăng bài" bằng cách gửi 1 email HTML qua **Gmail API** (`gmail.send` + `gmail.metadata`, OAuth) tới địa chỉ đó — không dùng browser automation, không cần login UI Google Groups.

Mọi lệnh gọi HTTP dùng qua `scripts/ggr-http.sh`, mọi xử lý JSON/MIME dùng qua `scripts/ggr-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp, vì 2 script này được allowlist trong `.claude/settings.json` (domain hardcode sẵn trong script) để pipeline chạy không cần xác nhận thủ công từng lệnh.

## Contents

- Setup OAuth app (1 lần / Google Cloud project)
- Lấy refresh_token (1 lần / group)
- Refresh access_token (mỗi lần chạy, tự động)
- Nhúng ảnh vào bài (multipart/related + Content-ID, KHÔNG data URI)
- Build & gửi email (Gmail API `messages.send`)
- Lấy permalink Google Group (đọc lại Message-Id thật)
- Xử lý trang nguồn bị chặn bot (JS cookie challenge)
- scripts/ggr-http.sh — reference lệnh
- scripts/ggr-json.js — reference lệnh
- Known limits

## Setup OAuth app (1 lần / Google Cloud project)

1. Hướng dẫn user tạo project tại `https://console.cloud.google.com/projectcreate` (nếu chưa có project, có thể dùng chung project đã tạo cho `share-bai-blogger` — cùng Google Cloud project được, không bắt buộc tách riêng).
2. Enable "Gmail API" tại `https://console.cloud.google.com/apis/library` (search đúng tên, bấm Enable).
3. Tạo OAuth consent screen tại `https://console.cloud.google.com/apis/credentials/consent`: User Type = External, điền email user, **thêm chính email user vào mục Test users** (bắt buộc, thiếu bước này sẽ bị lỗi "Access blocked" khi authorize).
   - Khuyến nghị: sau khi tạo xong, bấm **"PUBLISH APP"** để chuyển Publishing status từ "Testing" sang "In production". App vẫn ở trạng thái **chưa verify** (Google chỉ hiện 1 màn cảnh báo "Google hasn't verified this app" lúc authorize, bấm Advanced → Go to app là qua) — nhưng đổi sang "In production" giúp `refresh_token` không bị giới hạn hết hạn sau 7 ngày mà "Testing" áp dụng cho các app dùng scope nhạy cảm (`gmail.send`/`gmail.metadata` thuộc nhóm này). Không làm bước này thì skill vẫn chạy được, chỉ là có thể phải làm lại OAuth mỗi ~7 ngày.
4. Tạo OAuth Client ID tại `https://console.cloud.google.com/apis/credentials` → Create Credentials → OAuth client ID → Application type = **Desktop app**.
5. Lấy Client ID + Client Secret (hiện ngay sau khi tạo, hoặc bấm vào client vừa tạo để xem lại / Download JSON).
6. Lưu vào `ggr-accounts.local.json`:
   ```
   node scripts/ggr-json.js set-client ggr-accounts.local.json <group-key> <client_id> <client_secret> <group-email>
   ```
   `<group-key>` là tên định danh group (khuyến nghị dùng chính địa chỉ email group, vd `mygroup@googlegroups.com`). `<group-email>` là địa chỉ đăng bài của group, dạng `<tên-group>@googlegroups.com`.

## Lấy refresh_token (1 lần / group)

1. Chạy:
   ```
   node scripts/ggr-oauth-server.js <client_id> <client_secret> <out-file>.json
   ```
   Script tự mở 1 local HTTP server tạm (mặc định port 8766) và in ra 1 authorize URL, xin 2 scope: `gmail.send` (gửi email) và `gmail.metadata` (đọc header email, KHÔNG đọc nội dung/body hộp thư — dùng để lấy lại `Message-Id` thật ở bước verify, xem mục "Lấy permalink Google Group" bên dưới).
2. Đưa URL đó cho user mở trong trình duyệt, đăng nhập đúng tài khoản Google **là thành viên của group đích** (xem Known limits về quyền đăng bài), bấm Allow. KHÔNG cần copy-paste URL redirect thủ công — script tự bắt request redirect về `127.0.0.1:8766` và tự đổi code lấy token.
3. Script tự thoát (exit code 0) sau khi ghi response token vào `<out-file>.json`. Timeout 5 phút nếu user không thao tác.
4. Lưu vào `ggr-accounts.local.json`:
   ```
   node scripts/ggr-json.js save-tokens ggr-accounts.local.json <group-key> <out-file>.json
   ```
   Lệnh này tự kiểm tra response có `refresh_token` không (bắt buộc phải có ở lần đầu — nếu thiếu, nghĩa là authorize URL thiếu `access_type=offline`/`prompt=consent`, chạy lại bước 1).

Nếu 1 group đã từng authorize trước đó CHỈ với scope `gmail.send` (bản cũ của skill) → `access_token`/`refresh_token` đang lưu không có quyền `gmail.metadata`, gọi `gmail-get-message` ở bước verify sẽ trả lỗi thiếu scope. Chạy lại đúng 4 bước trên (`prompt=consent` sẽ buộc Google hỏi lại quyền, kể cả khi user đã từng Allow trước đó) để có token mới đủ cả 2 scope.

## Refresh access_token (mỗi lần chạy, tự động)

Access token của Google chỉ sống ~1 giờ — phải refresh trước mỗi lần gọi Gmail API. Việc này KHÔNG cần user tương tác gì (silent), chỉ cần `refresh_token` còn hợp lệ:

```
bash scripts/ggr-http.sh refresh-token <client_id> <client_secret> <refresh_token> <out-file>.json
node scripts/ggr-json.js save-refreshed-access-token ggr-accounts.local.json <group-key> <out-file>.json
```

Nếu response trả lỗi (thường do `refresh_token` bị revoke thủ công, project OAuth consent screen bị thu hồi quyền, hoặc — nếu Publishing status vẫn còn "Testing" — refresh_token đã tự hết hạn sau 7 ngày) → coi như mất token, quay lại mục "Lấy refresh_token" phía trên.

## Nhúng ảnh vào bài (multipart/related + Content-ID, KHÔNG data URI)

Khác với Blogger/WordPress (render như trang web, data URI hiển thị bình thường), **email HTML thì Gmail và phần lớn mail client chặn/lột bỏ `<img src="data:...">`** vì lý do bảo mật. Vì vậy ảnh phải đi kèm dưới dạng 1 phần MIME riêng (`multipart/related`), tham chiếu qua `Content-ID`, KHÔNG dùng base64 data URI như 2 skill kia.

`scripts/ggr-json.js build-mime-message` tự lo việc này — trong content HTML viết ở bước rewrite, chèn ảnh bằng đúng tag:

```html
<img src="cid:ggr-inline-image" alt="...">
```

rồi gọi (xem chi tiết ở mục "Build & gửi email" bên dưới) kèm tham số `<image-file>`/`<image-mime>` — script tự build phần MIME ảnh với `Content-ID: <ggr-inline-image>` khớp với `cid:` trong HTML.

Không có ảnh → gọi `build-mime-message` KHÔNG kèm 2 tham số cuối, HTML gửi nguyên dạng `text/html` đơn giản (không multipart).

## Build & gửi email (Gmail API `messages.send`)

1. Build raw email (base64url, đã bọc sẵn `{"raw": "..."}`):
   ```
   node scripts/ggr-json.js build-mime-message <content-html-file> "<title>" <group-email> <payload-file>.json [image-file] [image-mime]
   ```
   Không cần tự đặt `Message-ID` — xem lý do ở mục kế tiếp.
2. Gửi:
   ```
   bash scripts/ggr-http.sh gmail-send <access_token> <payload-file>.json <out-file>.json
   node scripts/ggr-json.js show-send-result <out-file>.json
   ```
   `show-send-result` in ra `id`/`threadId` — `id` này dùng ở bước verify tiếp theo để đọc lại `Message-Id` thật. HTTP_STATUS khác 2xx hoặc response không có `id` → coi là gửi thất bại, KHÔNG báo thành công.

## Lấy permalink Google Group (đọc lại Message-Id thật)

**Đã xác nhận qua thực tế chạy skill**: Gmail API **không giữ nguyên** một header `Message-ID` tự đặt trong `raw` MIME khi gửi — Gmail tự sinh và gán `Message-Id` riêng của nó (dạng `<...@mail.gmail.com>`), khác hoàn toàn với bất kỳ giá trị nào script tự tạo trước khi gửi. Một permalink build từ Message-ID tự đoán trước sẽ trỏ SAI bài (không load được, hoặc redirect nhầm topic).

Cách đúng — đọc lại header thật SAU KHI gửi, rồi mới build permalink:

```
bash scripts/ggr-http.sh gmail-get-message <access_token> <message-id-tu-buoc-gmail-send> <out-file>.json
node scripts/ggr-json.js extract-message-id <out-file>.json
node scripts/ggr-json.js build-permalink <group-email> "<message-id-vua-doc-duoc>"
```

`gmail-get-message` gọi `GET .../messages/<id>?format=metadata&metadataHeaders=Message-Id` — chỉ đọc 1 header, không đọc nội dung/body hộp thư, dùng đúng phạm vi scope `gmail.metadata` đã xin. `extract-message-id` parse header đó ra giá trị (dạng `<xxx@mail.gmail.com>`). `build-permalink` in ra `https://groups.google.com/d/msgid/<tên-group>/<message-id-đã-encode>` — đã verify thực tế link này redirect (HTTP 302) đúng tới trang topic thật trên Google Groups (`https://groups.google.com/g/<group>/c/<topic-id>`).

Permalink có thể mất vài phút mới load được do Google Groups cần thời gian index bài mới — xem Known limits.

## Xử lý trang nguồn bị chặn bot (JS cookie challenge)

Một số site nguồn dùng WAF/CDN chặn request không chạy JS: response ban đầu rất ngắn, chỉ chứa 1 thẻ script dạng:

```html
<script>document.cookie="XXX=yyy...; expires=...; path=/";window.location.reload(true);</script>
```

Nếu gặp response dạng này (kiểm tra bằng cách đọc lại file `<out-file>` sau `fetch-source`, thấy size rất nhỏ và chỉ chứa script này):
1. Trích tên + giá trị cookie từ script đó.
2. Gọi lại `fetch-source` cùng URL, truyền thêm cookie ở tham số thứ 3:
   ```
   bash scripts/ggr-http.sh fetch-source <url> <out-file> "XXX=yyy"
   ```
   Lần này sẽ trả về HTML đầy đủ của trang.

Đây là kiểu JS-redirect phổ biến ở nhiều CMS/CDN cho request đầu tiên, áp dụng cho trang public không yêu cầu đăng nhập — không phải bypass xác thực hay bảo mật.

## scripts/ggr-http.sh — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `fetch-source` | `<url> <out-file> [cookie]` | Đọc bài nguồn |
| `download-image` | `<url> <out-file> <cookie>` | Tải ảnh đại diện |
| `refresh-token` | `<client_id> <client_secret> <refresh_token> <out-file>` | Trước mỗi lần gọi Gmail API |
| `gmail-send` | `<access_token> <payload-file> <out-file>` | Gửi email = đăng bài lên group |
| `gmail-get-message` | `<access_token> <message-id> <out-file>` | Sau `gmail-send`, đọc lại header `Message-Id` thật để build permalink |

## scripts/ggr-json.js — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `get-account-field` | `<accounts-json-file> <group-key> <field>` | Đọc client_id/client_secret/refresh_token/access_token/group_email đã lưu |
| `set-client` | `<accounts-json-file> <group-key> <client_id> <client_secret> <group-email>` | Setup lần đầu |
| `save-tokens` | `<accounts-json-file> <group-key> <token-response-file>` | Sau khi chạy `ggr-oauth-server.js` lần đầu (hoặc re-authorize để thêm scope) |
| `save-refreshed-access-token` | `<accounts-json-file> <group-key> <refresh-response-file>` | Sau mỗi lần `refresh-token` |
| `build-mime-message` | `<content-html-file> <subject> <to-email> <out-file> [image-file] [image-mime]` | Trước `gmail-send` |
| `extract-message-id` | `<gmail-get-message-response-file>` | Sau `gmail-get-message`, trước `build-permalink` |
| `build-permalink` | `<group-email> <message-id>` | Sau `extract-message-id` |
| `word-count` | `<html-file>` | Self-check độ dài bài viết lại |
| `show-send-result` | `<send-response-file>` | Lấy `id`/`threadId` của Gmail sau khi gửi |

## Known limits

- **Tài khoản OAuth phải là thành viên của group, và group nên cho phép member đăng bài không cần duyệt.** Gmail API `messages.send` trả `200` + `id` nghĩa là email đã được Gmail chấp nhận gửi đi — KHÔNG đồng nghĩa bài đã hiển thị công khai ngay trên group. Nếu group bật chế độ duyệt bài (moderation) cho thành viên, hoặc tài khoản gửi không phải thành viên, email vẫn "gửi thành công" theo Gmail API nhưng có thể nằm chờ duyệt, hoặc bị group từ chối âm thầm — không có cách nào phát hiện qua Gmail API (Gmail API chỉ biết email đã rời hộp thư đi, không biết chuyện gì xảy ra phía nhận). Skill chỉ verify được đến mức "Gmail đã nhận gửi", không verify được "đã LIVE trên group" như WP/Blogger verify `status`.
- Gmail **không giữ nguyên** header `Message-ID` tự đặt khi gửi qua API — nó luôn tự sinh `Message-Id` riêng. Vì vậy permalink Google Groups BẮT BUỘC phải build từ giá trị đọc lại qua `gmail-get-message` + `extract-message-id` (Step 8 trong SKILL.md), không được đoán trước.
- Permalink `https://groups.google.com/d/msgid/<group>/<message-id>` có thể mất vài phút mới load được do Google Groups cần thời gian index bài mới — nếu user bấm link ngay mà báo không tìm thấy, thử lại sau 1-2 phút trước khi coi là lỗi thật.
- Access token Google sống ~1 giờ — BẮT BUỘC refresh trước mỗi lần gọi `gmail-send`/`gmail-get-message`, không tái sử dụng access_token cũ quá lâu.
- `refresh_token` chỉ được cấp khi authorize URL có `access_type=offline`. `ggr-oauth-server.js` đã set sẵn cả `access_type=offline` và `prompt=consent` nên không gặp vấn đề thiếu refresh_token.
- OAuth consent screen ở "Testing" (chưa Publish App) khiến `refresh_token` tự hết hạn sau 7 ngày với scope nhạy cảm như `gmail.send`/`gmail.metadata` — chuyển Publishing status sang "In production" (vẫn không cần verify app với Google, chỉ hiện cảnh báo unverified 1 lần lúc authorize) để tránh phải làm lại OAuth định kỳ.
- Scope xin `gmail.send` (gửi email) + `gmail.metadata` (đọc HEADER email, không đọc body/nội dung hộp thư) — không xin `gmail.readonly`/`gmail.modify` vì skill không cần đọc nội dung mailbox, chỉ cần đọc lại đúng 1 header (`Message-Id`) của message vừa tự gửi.

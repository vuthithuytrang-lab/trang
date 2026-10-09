---
name: google-sheets-social
description: This skill should be used when the user or an agent needs to read or write a Google Sheet used for content-distribution tracking — reading header cells (including their hyperlinks, not just display text), row data, checkbox state, or writing a single cell's value (e.g. a published post URL) back. Trigger phrases: "đọc sheet chia sẻ bài", "ghi link vào sheet", "connect Google Sheets for the sharing sheet", or being invoked by the share-bai-social agent. Read-only or single-cell-write Sheets I/O via Google Sheets API v4 — does not write article content, does not rewrite text, does not publish to any platform itself.
---

# google-sheets-social

Đọc/ghi 1 Google Sheet dùng cho việc theo dõi chia sẻ bài (content-distribution tracking sheet) qua Google Sheets API v4. Skill hạ tầng thuần túy — KHÔNG viết lại nội dung, KHÔNG đăng bài lên bất kỳ nền tảng nào; agent `share-bai-social` dùng skill này để đọc cấu trúc cột/dòng của sheet rồi tự quyết định gọi skill `share-bai-*` nào, sau đó dùng lại skill này để ghi link kết quả về sheet.

## Khi nào dùng

- Agent `share-bai-social` gọi qua Skill tool để đọc sheet trước khi xử lý, và ghi lại link sau khi publish xong 1 platform.
- User trực tiếp yêu cầu "đọc sheet chia sẻ bài", "kiểm tra cột nào đã tích", "ghi link X vào ô Y trong sheet".

KHÔNG dùng skill này khi:

- User muốn viết lại nội dung bài hoặc đăng bài lên 1 nền tảng cụ thể — đó là các skill `share-bai-*`.
- User muốn thao tác Google Sheets không liên quan sheet chia sẻ bài (vd tạo sheet mới, format cell, chart...) — ngoài phạm vi skill này.

## Tiền điều kiện

- [ ] Đã có 1 OAuth client **RIÊNG** cho skill này (KHÔNG dùng chung client_id với `share-bai-blogger`/`share-bai-ggr` hay skill khác — xem lý do trong "Known limits") đã bật **Google Sheets API**, và đã lấy được `refresh_token` cho đúng tài khoản Google có quyền sửa sheet đích — Step 2 hướng dẫn nếu chưa có.
- [ ] File `sheets-accounts.local.json` nằm ngay trong thư mục skill này (`.claude/skills/google-sheets-social/sheets-accounts.local.json`) — lưu `client_id`/`client_secret`/`access_token`/`refresh_token`/`spreadsheet_id`/`sheet_name` từng sheet. Nếu chưa có, Step 2 sẽ tạo.
- [ ] Mọi lệnh HTTP/JSON BẮT BUỘC gọi qua `scripts/sheets-http.sh` và `scripts/sheets-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp. 2 script này cần allowlist trong `.claude/settings.json` để agent `share-bai-social` (chạy nền) không bị treo vì permission prompt.

## Default settings

| Setting | Default | Override khi |
|---|---|---|
| Sheet đích khi không chỉ định | Sheet duy nhất có trong `sheets-accounts.local.json` | Nhiều sheet trong file → hỏi user chọn |
| Nguồn xác định nền tảng của 1 cột | Hyperlink thật gắn trên header cell | Header không có hyperlink → fallback text, cảnh báo caller có thể nhầm |
| Access token | Tự refresh mỗi lần chạy bằng `refresh_token` đã lưu (silent, không hỏi user) | — |
| Ghi cell | Luôn ghi đúng 1 ô/lần gọi (`valueInputOption=USER_ENTERED`) | — (API không hỗ trợ batch trong skill này) |

## Pipeline — 4 bước

### Step 1 — Xác định sheet đích

Parse spreadsheet_id từ URL sheet user cung cấp (đoạn giữa `/d/` và `/edit`), và tên tab (`sheet_name`, thấy trên URL param `gid` hoặc user cho biết trực tiếp tên tab). Không có sheet-key nào khớp trong `sheets-accounts.local.json` → coi là sheet mới, sang Step 2.

**Exit condition**: có `spreadsheet_id` + `sheet_name` + xác định được sheet-key.

### Step 2 — Đảm bảo có OAuth client + token hợp lệ

Đọc `references/sheets-api-steps.md` toàn bộ.

- Chưa có entry → hướng dẫn user tạo 1 OAuth Client ID RIÊNG cho skill này (mục "Setup OAuth" — mặc định KHÔNG tái sử dụng client_id của skill khác, trừ khi user chủ động yêu cầu và chấp nhận rủi ro 50-token-cap), lưu bằng `set-client`.
- Có `client_id`/`client_secret` nhưng chưa có `refresh_token` → chạy `sheets-oauth-server.js`, lưu bằng `save-tokens`.
- Đã có `refresh_token` → gọi `refresh-token` lấy access_token mới, lưu bằng `save-refreshed-access-token`.

**Decision point**: mặc định luôn đề xuất Client ID riêng, không tự ý dùng chung client với skill khác. API trả lỗi permission/token hết hạn → coi như mất token, quay lại bước tương ứng.

### Step 3 — Đọc sheet

```
bash scripts/sheets-http.sh get-sheet-data <access_token> <spreadsheet_id> <sheet_name> <out-file>
node scripts/sheets-json.js parse-sheet-data <out-file> <parsed-file>
```

**Exit condition**: `parsed-file` có `headers` và `rows` non-empty. `checkboxHeaderText` là `null` (không nhận diện được cột checkbox) → báo caller rõ ràng, không đoán cột nào là checkbox.

### Step 4 — Ghi 1 cell

```
node scripts/sheets-json.js build-a1-range "<sheet_name>" <column-index-hoặc-chữ> <row-number>
node scripts/sheets-json.js build-update-cell-body "<value>" <payload-file>
bash scripts/sheets-http.sh update-cell <access_token> <spreadsheet_id> "<a1-range>" <payload-file> <out-file>
node scripts/sheets-json.js show-update-result <out-file>
```

**Exit condition**: response có `updatedCells: 1`, không có `error`.

## Decision points

| Step | Hỏi user khi | Auto-proceed khi |
|---|---|---|
| 1 | Không xác định được spreadsheet_id/sheet_name | URL sheet hợp lệ, tab rõ ràng |
| 2 | Chưa có OAuth client, hoặc chưa có refresh_token — hướng dẫn tạo Client ID riêng, không tự dùng chung | Đã có đủ access_token cho sheet-key đích |
| 3-4 | — (không hỏi, dừng nếu không đọc/ghi được) | Đọc/ghi thành công |

## Recovery

- `parse-sheet-data` báo `checkboxHeaderText: null` → dừng, báo caller tên các header thực tế để user xác nhận cột nào là checkbox, không tự đoán.
- API trả 401/403 → access_token hết hạn hoặc thiếu quyền — refresh lại theo Step 2; nếu vẫn lỗi, `refresh_token` có thể đã bị revoke, quay lại lấy refresh_token mới.
- `update-cell` trả lỗi range không hợp lệ (sai tên tab, cell ngoài phạm vi) → kiểm tra lại `sheet_name` và `rowIndex`/cột dùng từ đúng dữ liệu Step 3 trả về, không tự bịa toạ độ.

## Output format

Khi đọc xong, trả nguyên văn nội dung file JSON từ `parse-sheet-data` cho caller (agent/user) tự xử lý tiếp. Khi ghi xong, trả kết quả từ `show-update-result`:
```
Đã ghi <value> vào <a1-range>.
```
Ghi lỗi → báo rõ mã lỗi + message, không báo "đã ghi thành công".

## Anti-patterns

- KHÔNG dùng text hiển thị của header để xác định nền tảng — luôn ưu tiên `hyperlink`, vì các tên hiển thị có thể giống nhau nhưng trỏ domain khác (2 instance Mastodon khác nhau là ví dụ thật đã gặp).
- KHÔNG tự đoán cột nào là checkbox khi `checkboxHeaderText` trả về `null` — dừng và hỏi thay vì đoán.
- KHÔNG lưu client_secret/access_token/refresh_token dạng plaintext trong SKILL.md, chat log, hay file được commit — chỉ lưu trong `sheets-accounts.local.json`, thêm vào `.gitignore` nếu có.
- KHÔNG ghi đè 1 cell đã có giá trị mà không được caller xác nhận — skill này chỉ thực thi lệnh ghi được yêu cầu, việc kiểm tra "cell đã có link chưa" là trách nhiệm của caller (vd agent `share-bai-social`) trước khi gọi `update-cell`.
- KHÔNG tự ý dùng chung 1 OAuth client_id với `share-bai-blogger`/`share-bai-ggr` hay skill khác — mỗi mục đích cần Client ID riêng để tránh chạm giới hạn 50 refresh_token/cặp (client, tài khoản) của Google (xem "Known limits").

## Skill files

| File | Purpose | Load when |
|---|---|---|
| `references/sheets-api-steps.md` | Chi tiết OAuth, đọc sheet, ghi cell, A1 notation, xử lý sheet name có dấu cách | Step 2, 3, 4 |
| `scripts/sheets-http.sh` | Thực thi mọi lệnh HTTP (refresh-token, get-sheet-data, update-cell) — allowlisted trong `.claude/settings.json` | Step 2, 3, 4 |
| `scripts/sheets-json.js` | Thực thi mọi xử lý JSON (đọc/lưu credential, parse sheet, build A1 range, build payload, đọc kết quả) — allowlisted trong `.claude/settings.json` | Step 1, 2, 3, 4 |
| `scripts/sheets-oauth-server.js` | Chạy OAuth flow lần đầu: mở local server tạm bắt redirect code, đổi lấy token | Step 2 (chỉ lần đầu/sheet) |
| `sheets-accounts.local.json` | Credential từng sheet (`client_id`/`client_secret`/`access_token`/`refresh_token`/`spreadsheet_id`/`sheet_name`) — KHÔNG commit, chỉ đọc/ghi qua `scripts/sheets-json.js` | Step 2, 3, 4 |

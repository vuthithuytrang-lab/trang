# Đọc/ghi Google Sheets qua Sheets API v4 — Steps

Skill hạ tầng thuần túy — đọc/ghi Google Sheets, không rewrite nội dung, không đăng bài. Được gọi bởi agent `share-bai-social` (hoặc trực tiếp bởi user/Claude khi cần đọc/ghi 1 sheet chia sẻ bài) qua Skill tool.

Mọi lệnh gọi HTTP dùng qua `scripts/sheets-http.sh`, mọi xử lý JSON dùng qua `scripts/sheets-json.js` — KHÔNG gọi `curl`/`node -e` trực tiếp, vì 2 script này được allowlist trong `.claude/settings.json` (domain hardcode sẵn trong script) để pipeline chạy không cần xác nhận thủ công từng lệnh — điều kiện bắt buộc để agent `share-bai-social` chạy nền (background) không bị treo vì permission prompt.

## Contents

- Setup OAuth (1 lần/sheet — Client ID riêng, không dùng chung)
- Lấy refresh_token (1 lần/sheet)
- Refresh access_token (mỗi lần chạy, tự động)
- Đọc sheet (headers + hyperlink + rows + checkbox)
- Ghi 1 cell (A1 notation)
- scripts/sheets-http.sh — reference lệnh
- scripts/sheets-json.js — reference lệnh
- Known limits

## Setup OAuth (1 lần/sheet — Client ID riêng, không dùng chung)

Scope cần: `https://www.googleapis.com/auth/spreadsheets` (đọc + ghi).

**Mặc định: LUÔN tạo 1 OAuth Client ID RIÊNG cho skill này — KHÔNG tái sử dụng client_id đã dùng cho `share-bai-blogger`/`share-bai-ggr` hay bất kỳ skill nào khác.**

**Đã xác nhận qua sự cố thật (2026-08-02):** Google giới hạn cứng tối đa **50 refresh_token còn hiệu lực cho mỗi cặp (client_id, tài khoản Google)** — vượt quá, token cũ nhất bị vô hiệu hoá silent, không cảnh báo. Dùng chung 1 client_id giữa `google-sheets-social` và `share-bai-blogger`/`share-bai-ggr` từng khiến refresh_token của Blogger bị revoke ngay sau khi authorize thêm cho Sheets trên cùng client. Mỗi mục đích cần 1 Client ID riêng để có "ngân sách" 50-token độc lập, không bao giờ cạnh tranh nhau.

Có thể dùng chung 1 Google Cloud **project** đã có sẵn (đỡ phải tạo project mới, chỉ cần bật thêm **Google Sheets API** cho project đó tại `console.cloud.google.com/apis/library` nếu chưa bật) — nhưng bên trong project đó, vào `console.cloud.google.com/apis/credentials` → Create Credentials → OAuth client ID → **Desktop app**, tạo 1 Client ID hoàn toàn mới, không lấy lại client_id đã ghi trong `blogger-accounts.local.json`/`ggr-accounts.local.json`.

Chỉ tái sử dụng client_id có sẵn khi user **chủ động** yêu cầu và đã hiểu rõ rủi ro 50-token-cap ở trên — không tự đề xuất phương án này như lựa chọn ngang hàng.

Sau khi có `client_id`/`client_secret`, lưu:
```
node scripts/sheets-json.js set-client sheets-accounts.local.json <sheet-key> <client_id> <client_secret> <spreadsheet_id> <sheet_name>
```
`<sheet-key>` khuyến nghị dùng tên gợi nhớ dự án (vd `ten-du-an-share-social`). `<spreadsheet_id>` lấy từ URL sheet (đoạn giữa `/d/` và `/edit`). `<sheet_name>` là tên tab (vd `Share social`).

## Lấy refresh_token (1 lần/sheet)

1. Chạy:
   ```
   node scripts/sheets-oauth-server.js <client_id> <client_secret> <out-file>.json
   ```
   Script mở 1 local HTTP server tạm (mặc định port 8769) và in ra authorize URL, xin scope `spreadsheets`.
2. Đưa URL cho user mở trong trình duyệt, đăng nhập đúng tài khoản Google **có quyền chỉnh sửa sheet đích**, bấm Allow.
3. Script tự bắt code redirect, đổi lấy token, ghi vào `<out-file>.json`.
4. Lưu:
   ```
   node scripts/sheets-json.js save-tokens sheets-accounts.local.json <sheet-key> <out-file>.json
   ```

## Refresh access_token (mỗi lần chạy, tự động)

Access token Google sống ~1 giờ — refresh trước mỗi lần đọc/ghi sheet:
```
bash scripts/sheets-http.sh refresh-token <client_id> <client_secret> <refresh_token> <out-file>.json
node scripts/sheets-json.js save-refreshed-access-token sheets-accounts.local.json <sheet-key> <out-file>.json
```

## Đọc sheet (headers + hyperlink + rows + checkbox)

```
bash scripts/sheets-http.sh get-sheet-data <access_token> <spreadsheet_id> <sheet_name> <out-file>.json
node scripts/sheets-json.js parse-sheet-data <out-file>.json <parsed-file>.json
```

**Đã xác nhận qua thực tế chạy skill**: `get-sheet-data` tự bọc `sheet_name` trong dấu nháy đơn nếu tên tab có ký tự ngoài `[A-Za-z0-9_]` (dấu cách, gạch ngang, dấu tiếng Việt...) — API từ chối range không bọc nháy với lỗi `"Unable to parse range"`. Gọi lệnh với `sheet_name` thô (không tự bọc nháy tay), script tự xử lý.

`parse-sheet-data` trả về JSON gọn:
```json
{
  "sheetTitle": "Share social",
  "headers": [{"index":0,"text":"STT","hyperlink":null}, {"index":4,"text":"Wordpress","hyperlink":"https://myblog.wordpress.com/"}, ...],
  "checkboxHeaderText": "Duyệt share",
  "rows": [
    {"rowIndex": 3, "checked": true, "values": {"STT":"1","Key chính":"...", "Wordpress":"", ...}}
  ]
}
```

`hyperlink` lấy từ link THẬT gắn trên cell header — dùng field này để xác định domain nền tảng, KHÔNG dùng `text` hiển thị (2 nền tảng có thể tên giống nhau nhưng domain khác, vd 2 instance Mastodon khác nhau). `rowIndex` là số dòng thật trên sheet (1-based, tính cả header) — dùng lại đúng số này khi ghi cell để không bị lệch dòng.

`checkboxHeaderText` được tự nhận diện bằng cách so khớp mờ (regex `/duyệt|duyet|approve|publish/i`) trên text header — nếu sheet dùng tên cột checkbox khác hẳn (không chứa các từ này), field này trả về `null` và mọi `row.checked` cũng `null`; báo lỗi cho caller thay vì đoán mò.

## Ghi 1 cell (A1 notation)

```
node scripts/sheets-json.js build-a1-range "<sheet_name>" <column-letter-or-0-based-index> <row-number>
node scripts/sheets-json.js build-update-cell-body "<value>" <payload-file>.json
bash scripts/sheets-http.sh update-cell <access_token> <spreadsheet_id> "<a1-range-vừa-build>" <payload-file>.json <out-file>.json
node scripts/sheets-json.js show-update-result <out-file>.json
```

`build-a1-range` tự bọc tên sheet trong dấu nháy đơn nếu có ký tự đặc biệt/dấu cách (A1 notation yêu cầu — vd `'Share social'!F5`), và tự convert cột dạng index 0-based (lấy từ `headers[].index` ở bước đọc) sang chữ cái cột (F, G, AA...). `show-update-result` in ra `updatedRange`/`updatedCells` — không có `error` và `updatedCells` = 1 mới coi là ghi thành công.

## scripts/sheets-http.sh — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `refresh-token` | `<client_id> <client_secret> <refresh_token> <out-file>` | Trước mỗi lần đọc/ghi |
| `get-sheet-data` | `<access_token> <spreadsheet_id> <sheet_name> <out-file>` | Đọc toàn bộ sheet |
| `update-cell` | `<access_token> <spreadsheet_id> <a1_range> <payload-file> <out-file>` | Ghi 1 cell |

## scripts/sheets-json.js — reference lệnh

| Subcommand | Args | Dùng ở |
|---|---|---|
| `get-account-field` | `<accounts-json-file> <sheet-key> <field>` | Đọc client_id/client_secret/access_token/spreadsheet_id/sheet_name đã lưu |
| `set-client` | `<accounts-json-file> <sheet-key> <client_id> <client_secret> <spreadsheet_id> <sheet_name>` | Setup lần đầu |
| `save-tokens` | `<accounts-json-file> <sheet-key> <token-response-file>` | Sau OAuth lần đầu |
| `save-refreshed-access-token` | `<accounts-json-file> <sheet-key> <refresh-response-file>` | Sau mỗi lần `refresh-token` |
| `parse-sheet-data` | `<get-sheet-data-response-file> <out-file>` | Sau `get-sheet-data` |
| `build-a1-range` | `<sheet_name> <column-letter-or-index> <row-number>` | Trước `update-cell` |
| `build-update-cell-body` | `<value> <out-file>` | Trước `update-cell` |
| `show-update-result` | `<update-response-file>` | Verify sau khi ghi |

## Known limits

- `get-sheet-data` đọc TOÀN BỘ tab (`ranges=<sheet_name>`) — sheet rất lớn (hàng nghìn dòng) sẽ trả response nặng; nếu cần, có thể thu hẹp bằng cách truyền `sheet_name` kèm range cụ thể (vd `Share social!A1:Z200`) thay vì cả tab.
- Không hỗ trợ ghi nhiều cell cùng lúc (batchUpdate) — mỗi lần gọi `update-cell` chỉ ghi đúng 1 ô. Cần ghi nhiều ô thì gọi lặp lại.
- `checkboxHeaderText` dựa vào regex tên cột tiếng Việt/Anh phổ biến — sheet dùng tên cột khác hẳn (không chứa "duyệt"/"approve"/"publish") sẽ không tự nhận diện được, cần user đặt lại tên cột hoặc sửa regex trong `sheets-json.js`.
- access_token không tự refresh lặp lại được nếu `refresh_token` bị revoke (user thu hồi quyền truy cập, hoặc app OAuth bị xoá) — phải chạy lại toàn bộ mục "Lấy refresh_token".
- **Google giới hạn cứng tối đa 50 refresh_token còn hiệu lực cho mỗi cặp (client_id, tài khoản Google)** — vượt quá, token cũ nhất bị vô hiệu hoá silent. Đây là lý do bắt buộc dùng Client ID riêng cho skill này (xem mục "Setup OAuth") — đã xảy ra thật ngày 2026-08-02: dùng chung client với `share-bai-blogger` khiến refresh_token Blogger bị revoke ngay sau khi authorize Sheets.

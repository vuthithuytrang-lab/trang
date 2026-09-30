# Pinterest API v5 — Steps

Mọi HTTP qua `scripts/pinterest-http.sh`, mọi JSON qua `scripts/pinterest-json.js`.

## Tạo app (1 lần / tài khoản)

1. Tài khoản phải là **Business** (Settings → Account management → Convert to business).
2. `https://developers.pinterest.com/apps/` → Connect app. Use case: **Pin creation & scheduling**; Audience: **Businesses**; Reads Pins/Boards: **Yes, mine**; cần link Privacy policy (dùng trang chính sách của doanh nghiệp).
3. App mới ở mức **Trial access** (có thể phải chờ duyệt). Trong trang app → thêm Redirect URI `https://localhost/` → Save.
4. Lưu:
   ```
   node scripts/pinterest-json.js set-app pinterest-accounts.local.json <account-key> <app_id> <app_secret> https://localhost/ sandbox
   ```

## Trial vs Standard access

- **Trial:** Pin tạo ra chỉ tồn tại trong **sandbox** (`api-sandbox.pinterest.com`) — chỉ chủ tài khoản thấy. Dùng `env = sandbox`.
- **Standard:** cần gửi yêu cầu nâng cấp trong trang app, kèm **video quay màn hình** cảnh app thực hiện đăng Pin qua API (bắt buộc cả với app nội bộ). Pinterest duyệt theo đợt. Được duyệt → `set-field ... env prod`.
- Token sandbox: nếu API sandbox từ chối token OAuth thường, trang app có nút tạo **sandbox token** (30 ngày) — lưu vào `access_token` và bỏ qua refresh cho tới khi lên prod.

## Lấy token (authorization code, 1 lần)

1. Authorize URL (scope đủ 5 quyền để khỏi xin lại):
   `https://www.pinterest.com/oauth/?client_id=<APP_ID>&redirect_uri=https%3A%2F%2Flocalhost%2F&response_type=code&scope=boards:read,boards:write,pins:read,pins:write,user_accounts:read`
2. User mở link bằng đúng tài khoản, bấm **Give access** → trình duyệt về `https://localhost/?code=...` (trang lỗi là bình thường) → user dán lại URL.
3. Đổi code (hết hạn nhanh, dùng ngay):
   ```
   bash scripts/pinterest-http.sh oauth-token <app_id> <app_secret> https://localhost/ <code> <out>.json
   node scripts/pinterest-json.js save-tokens pinterest-accounts.local.json <account-key> <out>.json
   ```
   `continuous_refresh=true` → refresh token 60 ngày, gia hạn mỗi lần refresh.

## Refresh (mỗi lần chạy)

```
bash scripts/pinterest-http.sh refresh-token <app_id> <app_secret> <refresh_token> <out>.json
node scripts/pinterest-json.js save-tokens pinterest-accounts.local.json <account-key> <out>.json
```
Không chạy quá 60 ngày → refresh token hết hạn → phải authorize lại.

## Kiểm tra tài khoản & board

```
bash scripts/pinterest-http.sh get-user <env> <token> <out>.json && node scripts/pinterest-json.js show-user <out>.json
bash scripts/pinterest-http.sh list-boards <env> <token> <out>.json && node scripts/pinterest-json.js show-boards <out>.json
node scripts/pinterest-json.js set-field pinterest-accounts.local.json <account-key> board_id <id>
```
Tạo board (chỉ khi user đồng ý): `build-board-payload "<tên>" "<mô tả>" <p>.json` → `create-board <env> <token> <p>.json <out>.json`.

## Tạo Pin

```
node scripts/pinterest-json.js build-pin-payload <board_id> "<title>" "<description>" <source_url> "<alt>" <image-file> image/jpeg <payload>.json
bash scripts/pinterest-http.sh create-pin <env> <token> <payload>.json <out>.json
node scripts/pinterest-json.js show-pin-result <out>.json
bash scripts/pinterest-http.sh get-pin <env> <token> <pin_id> <out2>.json
```
Ảnh gửi dạng base64 (không hotlink). Giới hạn: title 100, description 500, alt 500 ký tự — `build-pin-payload` tự chặn nếu vượt.

## Known limits

- Trial → Pin không công khai; link `pinterest.com/pin/<id>` có thể không mở được với người khác.
- API trả 401 → refresh; vẫn 401 → authorize lại.
- 429 → quá giới hạn gọi, chờ rồi thử lại, không lặp liên tục.

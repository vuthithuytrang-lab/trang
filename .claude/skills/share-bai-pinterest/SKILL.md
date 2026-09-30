---
name: share-bai-pinterest
description: This skill should be used when the user asks to "đăng Pin lên Pinterest", "share bài lên Pinterest", "ghim bài lên Pinterest", "/share-bai-pinterest [từ khóa], [URL]", "post to Pinterest", or when the share-bai-social agent dispatches a Pinterest column. Reads 1 source article from a URL, picks a real image from that page, writes a Pin title + description + alt text around the primary keyword (following the shared content checklist), and publishes the Pin via the Pinterest API v5 (OAuth2, continuous refresh token), linking back to the source URL. Same skill family as share-bai-wp/share-bai-blogger/share-bai-mastodon — different target platform; a Pin is 1 image + short text, not a long article.
---

# share-bai-pinterest

Đăng 1 Pin lên Pinterest: đọc bài nguồn → chọn 1 ảnh thật trên trang nguồn → viết tiêu đề, mô tả, alt theo từ khóa chính → đăng Pin qua Pinterest API v5 → trả link Pin.

> ⚠️ **Checklist nội dung bắt buộc:** `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md` — với Pin chỉ áp dụng các mục ghi ở `references/rewrite-guidelines.md`.

## Khi nào dùng

- `/share-bai-pinterest [từ khóa chính], [URL nguồn]` hoặc `... , [account-key]`
- Agent `share-bai-social` gọi cho cột Pinterest (domain `pinterest.com`).

KHÔNG dùng khi user muốn đăng bài dài (dùng skill blog tương ứng) hoặc chạy quảng cáo Pinterest.

## Tiền điều kiện

- [ ] Tài khoản Pinterest **Business**, đã tạo app tại developers.pinterest.com, redirect URI `https://localhost/`.
- [ ] `pinterest-accounts.local.json` trong thư mục skill này có `app_id`, `app_secret`, `refresh_token`, `env`, `board_id` cho account đích — Step 2 hướng dẫn nếu thiếu. KHÔNG commit file này.
- [ ] Mọi lệnh HTTP/JSON gọi qua `scripts/pinterest-http.sh` và `scripts/pinterest-json.js` (đã allowlist trong `.claude/settings.json`).

## Default settings

| Setting | Default | Override khi |
|---|---|---|
| Môi trường (`env`) | Theo `env` trong accounts file: `sandbox` khi app mới có **Trial access** (Pin chỉ chủ tài khoản thấy), `prod` khi đã có **Standard access** | Pinterest duyệt Standard → `set-field ... env prod` |
| Ảnh | **Bắt buộc 1 ảnh** lấy từ trang nguồn (ưu tiên `og:image` → ảnh sản phẩm/ảnh nội dung; bỏ logo/icon/ảnh <300px). Không có ảnh → **dừng, không đăng** | — |
| Board | `board_id` lưu trong accounts file | User chỉ định board khác |
| Link của Pin | URL bài nguồn | — |
| Xác nhận trước khi đăng | Không hỏi — auto-publish | User yêu cầu duyệt trước |

## Pipeline — 8 bước

### Step 1 — Parse input
Từ khóa chính, URL nguồn (mốc `http`), account-key (tuỳ chọn — mặc định account duy nhất trong file; nhiều account → theo hồ sơ dự án, không đoán).

### Step 2 — Đảm bảo token hợp lệ
Đọc `references/pinterest-api-steps.md`.
- Chưa có app → hướng dẫn tạo app, lưu bằng `set-app`.
- Có app, chưa có `refresh_token` → đưa authorize URL, user dán lại URL `https://localhost/?code=...`, đổi bằng `oauth-token`, lưu bằng `save-tokens`.
- Đã có `refresh_token` → **luôn** `refresh-token` + `save-tokens` trước khi gọi API (access token sống 30 ngày, refresh token liên tục 60 ngày — mỗi lần refresh sẽ gia hạn).
- Chưa có `board_id` → `list-boards` → chọn board theo hồ sơ dự án; không có board phù hợp → hỏi user (hoặc tạo bằng `create-board` nếu user đồng ý), lưu bằng `set-field ... board_id`.

### Step 3 — Đọc trang nguồn
`fetch-source`. Trích tiêu đề, nội dung chính, danh sách ảnh (`og:image`, `<img>` trong nội dung). Không đọc được → dừng, không bịa.

### Step 4 — Chọn & tải ảnh
Chọn 1 ảnh liên quan nhất tới từ khóa/nội dung, `download-image`, kiểm tra đúng JPEG/PNG, chiều ngang ≥300px. Không có ảnh dùng được → dừng, báo "thiếu ảnh".

### Step 5 — Viết nội dung Pin
Theo `references/rewrite-guidelines.md`: tiêu đề ≤100 ký tự, mô tả ≤500 ký tự, alt ≤500 ký tự. Không bịa, không "nhất/số 1".

### Step 6 — Đăng Pin
`build-pin-payload` (kiểm tra giới hạn ký tự) → `create-pin <env>`.

### Step 7 — Verify
`show-pin-result` phải có `id`; `get-pin` trả 200. Lỗi → báo mã lỗi + message, không báo thành công.

### Step 8 — Report
```
Đã đăng Pin thành công.
Tài khoản: <account-key> (<env>)
Board: <board name>
Tiêu đề: <title>
Link Pin: https://www.pinterest.com/pin/<id>/
Link về: <source URL>
```
`env = sandbox` → ghi rõ: "Pin đang ở chế độ dùng thử — chỉ chủ tài khoản thấy, chưa công khai".

## Anti-patterns

- KHÔNG đăng Pin không ảnh, KHÔNG dùng ảnh ngoài trang nguồn/website doanh nghiệp.
- KHÔNG báo Pin "công khai" khi đang `sandbox`.
- KHÔNG in `app_secret`/token ra chat hay commit.
- KHÔNG dùng lại access token cũ mà không refresh.

## Skill files

| File | Purpose |
|---|---|
| `references/pinterest-api-steps.md` | Tạo app, OAuth, refresh, board, tạo Pin, sandbox vs prod |
| `references/rewrite-guidelines.md` | Quy tắc viết tiêu đề/mô tả/alt cho Pin |
| `scripts/pinterest-http.sh` | Mọi lệnh HTTP |
| `scripts/pinterest-json.js` | Mọi xử lý JSON/credential |
| `pinterest-accounts.local.example.json` | Mẫu cấu trúc file credential |

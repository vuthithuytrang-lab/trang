# Bản ghi DNS cần gắn cho `seongon.com` — để gửi email qua Resend

Đưa nguyên trang này cho người quản lý tên miền (IT). Chỉ cần thêm **3 bản ghi**, không xóa gì.

> ⚠️ Ba bản ghi này **chỉ thêm mới**, không đụng tới bản ghi đang có.
> Website và email hiện tại của công ty **không bị ảnh hưởng**.

## Bản ghi 1 — DKIM (chữ ký xác thực thư)

| Trường | Giá trị |
|---|---|
| **Type** | `TXT` |
| **Name / Host** | `resend._domainkey` |
| **Value** | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBb7pherCAXBFoyuoqbf/ZxeIHWOpzlWTpcfQjDmI+TBszkhex/5eLWjdjk8b2wh1/z+PRHS+7J16fEfkc8S7UsSz56JIc34gR2lAZIRcEIMyy1dYDwEFpxWDV787jOv9Ko4jvR9gUUOyOlbSpXVZLjE7lCklao9AlMK98Mry1sQIDAQAB` |
| **TTL** | Auto (hoặc 3600) |

## Bản ghi 2 — MX (nhận phản hồi từ nhà mạng)

| Trường | Giá trị |
|---|---|
| **Type** | `MX` |
| **Name / Host** | `send` |
| **Value** | `feedback-smtp.us-east-1.amazonses.com` |
| **Priority** | `10` |
| **TTL** | Auto (hoặc 3600) |

## Bản ghi 3 — SPF (cho phép Resend gửi thay mặt tên miền)

| Trường | Giá trị |
|---|---|
| **Type** | `TXT` |
| **Name / Host** | `send` |
| **Value** | `v=spf1 include:amazonses.com ~all` |
| **TTL** | Auto (hoặc 3600) |

---

## Lưu ý cho người gắn

- Một số nơi quản lý DNS tự thêm đuôi tên miền. Nếu ô Name đã có sẵn `.seongon.com`
  thì chỉ gõ `resend._domainkey` và `send`, **đừng gõ** `resend._domainkey.seongon.com`.
- Bản ghi 2 và 3 cùng tên `send` nhưng **khác loại** (MX và TXT) — đây là bình thường,
  gắn cả hai.
- Giá trị DKIM rất dài, phải **copy nguyên khối**, không được xuống dòng hay thêm dấu cách.

## Sau khi gắn xong

Vào https://resend.com/domains → bấm **Verify** ở dòng `seongon.com`.
Thường xanh sau vài phút, chậm nhất là vài tiếng.

Xanh rồi thì:
- Gửi được cho **khách thật**, không còn giới hạn chỉ gửi về email đăng ký
- Địa chỉ người gửi đổi từ `onboarding@resend.dev` thành email `@seongon.com`
- Thư ít rơi vào hộp thư rác hơn hẳn

---

*Thông tin lấy trực tiếp từ Resend ngày 08/09/2026, tên miền `seongon.com`
(mã `7befdd0f-94f1-4bc6-93bc-172779792784`), vùng máy chủ us-east-1.*

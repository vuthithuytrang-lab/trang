# Trang đích ShopOne — đã lên mạng

## Địa chỉ

| Trang | Đường dẫn |
|---|---|
| **Trang đích (chạy quảng cáo)** | https://shopone-landing.trangvtt.workers.dev/dang-ky |
| **Kho lead** (xem khách để lại thông tin) | https://shopone-landing.trangvtt.workers.dev/leads |
| Cửa đọc lại cho máy chấm | `/api/lead/moi-nhat?token=<mã>` |

Gắn nguồn quảng cáo vào link để biết khách đến từ đâu:
`...workers.dev/dang-ky?nguon=fb-ads` · `?nguon=google` · `?nguon=zalo`

## Hạ tầng — toàn bộ miễn phí

| Thành phần | Dùng gì | Chi phí |
|---|---|---|
| Máy chủ chạy trang | Cloudflare Workers | 0đ (100.000 lượt/ngày) |
| Kho lưu lead | Cloudflare D1 | 0đ |
| Gửi mail cảm ơn | Resend | 0đ (3.000 mail/tháng) |
| Tên miền | `*.workers.dev` | 0đ |

## Sửa nội dung ưu đãi

Mở `src/index.js`, sửa đúng dòng `const UU_DAI = ...` ở đầu file. Rồi chạy lại:

```
npx wrangler deploy
```

## Lệnh hay dùng

```
npx wrangler deploy                 # đưa bản mới lên
npx wrangler tail                   # xem nhật ký chạy trực tiếp
npx wrangler d1 execute shopone-leads --remote --command "SELECT * FROM leads ORDER BY id DESC LIMIT 20"
```

Cần biến môi trường: `CLOUDFLARE_API_KEY` + `CLOUDFLARE_EMAIL` (hoặc `CLOUDFLARE_API_TOKEN`).

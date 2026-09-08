# Trang báo cáo gửi sếp — đã lên mạng

## Địa chỉ gửi sếp

```
https://bao-cao-hanh-trinh.trangvtt.workers.dev
```

Mở lúc nào cũng được, không cần đăng nhập. Trang đặt cờ `noindex` nên **không hiện trên Google** —
chỉ ai có link mới vào được.

## Sườn 6 phần

| Phần | Nội dung |
|---|---|
| 1 | Trước đây việc này làm thế nào — title/meta làm tay, 7 tiêu chí, 22 bài · 635 từ khoá |
| 2 | Đã tự làm được gì — công cụ Title/Meta + hệ thống marketing 6 việc, kèm 3 ảnh chụp màn hình |
| 3 | Hiệu quả đo được — số thật, kèm 2 lỗi công cụ bắt được |
| 4 | Năng lực có thêm — bảng trước / giờ, 6 dòng |
| 5 | Định dùng tiếp thế nào — 5 việc cụ thể |
| **6** | **Đề xuất — CHƯA ĐƯA VÀO.** Trang chưa quyết. Muốn thêm thì báo Agent |

## Chỗ còn trống

**Số giờ tiết kiệm mỗi tuần chưa có.** Trang chưa bấm giờ đối chiếu trước — sau nên chưa có con số đủ
chắc. Trang hiện ghi thẳng điều đó thay vì ước lượng bừa. Có số thật thì báo Agent, sửa mất một phút,
**địa chỉ web giữ nguyên**.

## Sửa nội dung rồi đưa lên lại

```
npx wrangler deploy
```

Cần biến môi trường `CLOUDFLARE_EMAIL` + `CLOUDFLARE_API_KEY`.

## Thiết kế

Theo `cong-cu/nhan-dien-thuong-hieu/CAM-NANG-THUONG-HIEU.md`: nền chuyển navy → xanh, nhấn mint
`#07EF9C`, **logo nhúng đúng file gốc, không vẽ lại**. Ảnh chụp màn hình nhúng thẳng vào trang nên
không phụ thuộc đường dẫn ngoài.

Chi phí: **0đ** — Cloudflare Workers gói miễn phí.

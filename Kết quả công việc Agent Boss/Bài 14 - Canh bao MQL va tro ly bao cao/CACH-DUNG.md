# Bài 14 — Cảnh báo MQL qua Telegram + trợ lý báo cáo tự chạy

> Viết cho Trang đọc, không cần biết kỹ thuật.

## 1. Có khách "xịn" là Telegram kêu ngay

Khi ai đó điền form trên trang đích và **đạt chuẩn MQL**
(có số điện thoại từ 9 chữ số + có ghi nhu cầu), bot
[@ban_tin_marketing_bot](https://t.me/ban_tin_marketing_bot) nhắn ngay cho người lọc lead:

```
🔥 MQL mới

👤 Nguyễn Văn A
📞 0912345678
📝 Cần phần mềm bán hàng cho 3 cửa hàng
📣 Nguồn: fb-ads

Không phải khách thật? Bấm nút bên dưới để loại khỏi MQL.

        [ ❌ Không đủ điều kiện ]
```

Bấm nút đó thì:

- Lead **rút khỏi danh sách MQL** — con số MQL trên bảng điều khiển **giảm 1** ngay.
- Lead **vẫn nằm trong kho**, không mất đi. Chỉ là không còn được tính là khách chất lượng.
- Tin nhắn tự đổi thành "❌ Đã loại khỏi MQL" để biết đã xử lý rồi, khỏi bấm nhầm hai lần.

**Lúc học Trang đóng cả hai vai** (vừa marketing vừa người lọc) nên cả hai loại tin đều về
Telegram của Trang. Khi giao thật cho bạn Sales: bảo bạn ấy mở bot và bấm **/start**,
rồi báo Agent đổi người nhận — sửa một dòng, mất một phút.

## 2. Trợ lý tự gửi báo cáo cuối ngày

**18h00 mỗi ngày (giờ Việt Nam)** trợ lý tự chạy, không cần ai bấm gì:

```
📊 BÁO CÁO CUỐI NGÀY — ShopOne

👀 Lượt vào trang: 22
📝 Lead thu được: 3
⭐ MQL sau khi lọc: 2 (đã loại 1)
📈 Tỷ lệ chuyển đổi: 13,64%

💰 Tiền quảng cáo: chưa nối tài khoản quảng cáo
💵 Chi phí mỗi lead: chưa tính được

🤖 Nhận định
<1–2 câu AI viết: hôm nay đáng chú ý gì, nên làm gì tiếp>
```

Đổi giờ: sửa dòng `crons` trong `wrangler.toml` rồi chạy lại `npx wrangler deploy`.
Giờ ghi theo giờ quốc tế (UTC), **lấy giờ Việt Nam trừ đi 7**.

| Muốn nhận lúc | Ghi là |
|---|---|
| 8h00 sáng | `0 1 * * *` |
| 12h00 trưa | `0 5 * * *` |
| 18h00 chiều *(đang dùng)* | `0 11 * * *` |
| 21h00 tối | `0 14 * * *` |

## 3. Hai ô còn trống — và vì sao

| Ô | Vì sao trống |
|---|---|
| 💰 Tiền quảng cáo | Chưa nối tài khoản Facebook Ads / Google Ads. Hệ thống **không tự biết** đã tiêu bao nhiêu, nên để trống chứ không bịa số. |
| 💵 Chi phí mỗi lead | Là *tiền đã tiêu ÷ số lead*. Chưa có vế tiền thì không tính được. |

Nối được quảng cáo là hai ô này tự có số.

## 4. Muốn xem báo cáo ngay, không đợi 18h

Báo Agent: *"gửi báo cáo ShopOne ngay bây giờ"*. Agent gọi một cửa riêng có khoá
(`POST /bao-cao-ngay`, mật khẩu gửi trong header — không bao giờ nằm trên đường link).

## 5. An toàn

- Chìa bot Telegram và mật khẩu webhook **nằm trong két của Cloudflare**, không có trong mã nguồn, không lên GitHub.
- Cửa nhận tin từ Telegram kiểm tra mật khẩu trước; người lạ gọi vào bị chặn (đã thử: sai mật khẩu → **403 Không được phép**).

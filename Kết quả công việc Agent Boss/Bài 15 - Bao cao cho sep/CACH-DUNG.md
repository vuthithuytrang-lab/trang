# Bài 15 — Trang báo cáo gửi sếp

> Viết cho Trang đọc, không cần biết kỹ thuật.

## Địa chỉ

| Trang | Đường dẫn |
|---|---|
| **Báo cáo cho sếp** *(gửi link này)* | https://shopone-landing.trangvtt.workers.dev/bao-cao |
| Xem tháng khác | `…/bao-cao?ky=2026-08` |
| Bản số thô (cho máy đọc) | `…/api/bao-cao?ky=2026-09` |

Trên bảng điều khiển cũng đã có link **"→ Báo cáo cho sếp"** ở cuối trang.

## Trang có gì

1. **Bốn ô số lớn** — lượt vào trang · lead thu được · MQL · chi phí mỗi lead
2. **Phễu** — vào trang → để lại thông tin → đủ điều kiện, kèm tỷ lệ rơi từng bước
3. **Bảng nguồn** — nguồn nào mang về nhiều lead và nhiều MQL nhất, có dòng "Cộng lại"
4. **Phần Tiền** — chi phí mỗi lead và mỗi MQL, ghi rõ phép chia bên cạnh
5. **Nút gửi cho sếp** — bấm một cái, link báo cáo bay thẳng qua Telegram
6. **Mục "Số này tính thế nào"** — giải thích từng con số, để sếp hỏi là trả lời được ngay

## Số ở đây tính kiểu gì

**Chỉ đếm và chia. Không có AI đụng vào con số.**

| Con số | Cách tính |
|---|---|
| Lượt vào trang | Đếm số lần trang được mở trong tháng |
| Lead | Đếm số dòng trong kho có ngày tạo thuộc tháng đó |
| MQL | Trong số lead đó, đếm dòng đạt chuẩn (điện thoại ≥ 9 số + có ghi nhu cầu). Lead bị bấm "Không đủ điều kiện" thì thôi không tính |
| Chi phí mỗi lead | Tiền quảng cáo ÷ số lead |
| Bảng nguồn | Gom lead theo nguồn. **Cộng các nguồn luôn đúng bằng tổng lead** — không dòng nào lọt hay đếm hai lần |

AI chỉ viết một hai câu nhận xét **bằng lời** trong báo cáo Telegram cuối ngày (Bài 14). Nó không được phép chạm vào bất kỳ con số nào.

## Dữ liệu mẫu — và cách xoá

Hiện báo cáo có **32 lead mẫu + 412 lượt vào mẫu + 6.000.000đ tiền quảng cáo mẫu**, để sếp thấy trước
báo cáo trông ra sao. Mọi dòng mẫu đều gắn cờ riêng và tên bắt đầu bằng `MAU-`, trên trang có
nhãn vàng **"số mẫu"** nên không lẫn được với số thật.

Muốn xoá sạch mẫu, báo Agent một câu — hoặc chạy:

```
npx wrangler d1 execute shopone-leads --remote --command "DELETE FROM leads WHERE la_mau = 1"
npx wrangler d1 execute shopone-leads --remote --command "DELETE FROM bo_dem WHERE ten = 'traffic_mau'"
```

Số thật không hề bị đụng tới.

## Đưa tiền quảng cáo thật vào

Đang dùng 6.000.000đ là **số mẫu**. Có số thật rồi thì đặt vào két Cloudflare:

```
npx wrangler secret put NGAN_SACH_THANG
```

Đặt xong, nhãn "số mẫu" tự biến mất và hai dòng chi phí tự tính lại. Báo Agent một câu là xong.

## Gửi cho ai

Nút hiện gửi về Telegram của Trang. Muốn gửi thẳng cho sếp: bảo sếp mở bot
[@ban_tin_marketing_bot](https://t.me/ban_tin_marketing_bot) bấm **/start**, rồi báo Agent đặt
`CHAT_SEP` — mất một phút.

Nút này chỉ gửi đúng một đường link cố định về đúng một Telegram đã cài sẵn, **không nhận nội dung
tự do từ người bấm**, nên người lạ có bấm cũng không lợi dụng được gì.

## Mã tốt nghiệp

Trang bấm **"Cấp mã"** trên trang bài học → được mã dạng `NV15-XXXXXX` → đưa Agent →
Agent cất vào két Cloudflare (`NV_MA_TOT_NGHIEP`). Mã **không** nằm trong mã nguồn, **không** lên GitHub.

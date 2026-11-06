# Công thức: cập nhật bài "Giá Niken hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-niken — đóng gói 06/11/2026. Trang tích ô trong Sheet "Update" hoặc nhắn
*"Update bài giá niken"* — **không hỏi gì thêm**. Chạy được không cần Claude: `bash cong-cu/tu-dong/chay.sh gia-niken <thư mục ra>`
(khung chung `*)` của `chay.sh`; không cần Chromium, chỉ cần `curl` + python3).

## 1. Nguồn đã chọn

| | |
|---|---|
| Nguồn chính | **Westmetall** — bảng giá LME Nickel hằng ngày: https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Ni_cash (HTML thường, `curl` đọc được, không vượt chặn) |
| Chuỗi giá dùng | Cột **"LME Nickel 3-month"** (USD/tấn) — giá chính thức LME kỳ hạn 3 tháng, giá tham chiếu của thị trường |
| Nguồn đối chiếu | TradingView scanner (`LME:NIX2026`…, hợp đồng LME Nickel gần nhất, chỉ có giá mới nhất) — chỉ để soát lệch, **không ghi vào bài** |
| Đã thử, bỏ | LME.com, investing (bị chặn); thitruonghanghoa.com/gia-kim-loai và tradingeconomics.com chỉ có giá đang chạy, không có lịch sử từng phiên (dùng để soát tay: 06/11/2026 ≈ 16,255 và 16,215) |

Vì sao Westmetall: là nguồn duy nhất đọc được bằng `curl` có đủ lịch sử từng phiên (10 phiên gần nhất lưu trong `gia.json`).
Westmetall chốt giá chậm 1–2 ngày so với hôm nay (06/11 mới có phiên 05/11).

**Chuỗi nào khớp số cũ trong bài?** So 4 dòng cũ của bài với Westmetall: 22/10 bài 16,017.50 (3M 16,135 · cash 15,935), 21/10 bài 16,284.25
(3M 16,040 · cash 15,830), 20/10 bài 15,743.25 (3M 15,570 · cash 15,350), 19/10 bài 15,537.75 (3M 15,490 · cash 15,275). Không chuỗi nào trùng
đúng: số cũ có lẻ .25/.75 là **giá đóng cửa hợp đồng tương lai** (từ một sàn dữ liệu khác, không đọc được ở đây). **3-month** gần số cũ hơn cash
(lệch 48–244 so với 82–454 USD/tấn) nên chọn 3-month. Mức thay đổi của bài cũ không khớp với của Westmetall (vd 21/10 bài +541.00, nguồn +470) → luôn ghi mục cần duyệt.

**Đối chiếu giá mới nhất (06/11/2026):** Westmetall 05/11 = 16,265.00; TradingView LME Nickel (Nov 2026) đang chạy = 16,154.93 → lệch 0.68% (dung sai 3%).
Soát tay: thitruonghanghoa 16,255, tradingeconomics 16,215 — cùng mức. Lệch quá 3% → tự ghi cần duyệt.

## 2. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Bảng "Ngày giao dịch \| Giá đóng cửa \| Thay đổi so với phiên trước" | N dòng = N phiên **mới nhất** trên Westmetall (dòng 1 = mới nhất): ngày `dd/mm/yyyy`, giá `16,265.00` (dấu nghìn ",", 2 số lẻ), thay đổi `+590.00` / `-125.00` (có dấu) = giá phiên đó trừ giá phiên liền trước trên nguồn. Nhận bảng theo tiêu đề cột; chịu được ô sai dạng như `16.162.00` và dòng bị gộp thành 1 dòng chữ |
| Câu "… đóng cửa ở mức X USD/tấn, giảm Y USD/tấn, tương đương Z% so với phiên trước" | X = giá phiên mới nhất (bài ghi số nguyên → `16,265`), Y = mức thay đổi (`590.00`), chữ **tăng/giảm** theo dấu của Y (+ cần duyệt), Z = \|Y\| / giá phiên trước × 100 (**số tính ra**, tự ghi cần duyệt; công thức này cho đúng 1.07% với số cũ của bài) |
| Tỷ lệ % khác (Indonesia ~67% theo USGS) | Không phải giá → giữ nguyên + 1 mục cần duyệt |
| Số giá còn sót | Số giá nào còn lại mà không phải số nguồn → cần duyệt `SỐ GIÁ CHƯA CẬP NHẬT …` |
| Ngày trong tiêu đề, sapo, đoạn văn | Do bước `dung` của khung chung đổi sang ngày hôm sau; công thức không đụng |
| Nguồn lỗi | `lay_gia.py` in `Westmetall KHÔNG ĐỌC ĐƯỢC …`, ghi `null`; `tao_sua.py` giữ nguyên toàn bộ bảng + câu giá, ghi cần duyệt |
| Không bịa số | Mọi số viết vào bài là số trên Westmetall trong lần chạy (`ly_do` chép nguyên dòng nguồn, khóa `chu_nguon` trong `gia.json`) |

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung (không có nguồn tham khảo kiểu bài) |
| `lay_gia.py` | `python3 -I lay_gia.py cap-nhat/gia.json` — đọc Westmetall (có năm trước nếu đầu năm) + TradingView → `gia.json` (`westmetall.lich_su`, `tradingview`, `doi_chieu`, kèm nguồn + ngày dữ liệu) |
| `tao_sua.py` | `--xem … --gia … --goc … --ra sua.json` lập danh sách sửa + cần duyệt; `--kiem` soát lại ("Soát: khớp hết") |

## 4. Lưu ý đã gặp (06/11/2026)

Bước cuối của `chay.sh` (`doi_ngay_bai.py`) đổi mọi ngày trong 3 ngày gần đây sang ngày mai, kể cả ngày trong bảng nếu ô đó **không bị tô vàng
từng phần** (vd dòng 1 giữ nguyên 05/11 → bị đổi thành 07/11 sau bước "Soát"). Cần sửa `doi_ngay_bai.py` bỏ qua ô trong bảng; công thức này không tự chặn được.

# Báo cáo phân tích thứ hạng HR2B — mốc 18/09/2026

## Ba file Google Sheet (xem và sửa được)

| File | Nội dung | Link |
|---|---|---|
| **1/3** | Tổng quan, chủ đề, nhóm từ khóa, kết luận, phương án | https://docs.google.com/spreadsheets/d/1VQ1ljsEgSFMu8DRg2LniQB7aXKkmuLw0DG585Eo1BBE/edit |
| **2/3** | Chi tiết 109 từ khóa | https://docs.google.com/spreadsheets/d/1vbQsgPquF5epriZlg9s0Ls1iJEaRrI5JSjEyOyO3JbM/edit |
| **3/3** | Biến động đối thủ top 10 | https://docs.google.com/spreadsheets/d/1Rp8JfBDvEOzdP8TYGuJkini0Y-6r_CysMvlmF4J5YME/edit |

Bản gộp 1 file cũ (ngày 18/09, trước khi tách): 
https://docs.google.com/spreadsheets/d/1lvi3EtYzpnu2JdxfJ6G5GZJt5kssedJDYiu_ws9z60E/edit

Các file `.csv` trong thư mục này là bản gốc đã dùng để tạo Google Sheet.

## Cột "LÚC CAO NHẤT"

Thêm ngày 18/09 theo yêu cầu. Nghĩa là **mức tốt nhất đạt được trong 11 mốc đo tin cậy**
(đã loại 27/8 và 28/8 vì công cụ quét lỗi), kèm **ngày đạt mức đó** và **chênh lệch so với 18/9**.

- File 1: đỉnh của từng chỉ số tổng (Top 3/5/10/20/30, vị trí TB) và của từng chủ đề, từng nhóm.
- File 2: vị trí tốt nhất từng từ khóa từng đạt + ngày đạt + số bậc đã mất so với lúc đó.
  Ô ghi `MẤT HẲN` = từ khóa từng có thứ hạng nhưng ngày 18/9 không còn.
- File 3: số ô top 10 cao nhất từng đối thủ từng chiếm + ngày đạt + % còn lại so với đỉnh.

## Nguồn dữ liệu
- `lịch sử top.csv` — 109 từ khóa × 13 mốc ngày (01/08 → 18/09/2026)
- `serprobot_serps_export_5102689_2026-09-18.csv` — top 10 URL mỗi ngày, 1.253 bản ghi
- Google Sheet nhóm từ khóa của HR2B — 3 chủ đề, 41 nhóm

## Ba kết luận chính
1. **Ngày tụt thật sự không phải 18/9.** Cú tụt xảy ra khoảng **29/8 → 11/9**:
   từ khóa top 10 rơi 55 → 44; số ô top 10 HR2B chiếm trên SERP rơi 69 → 58.
   Từ 11/9 tới 18/9 đi ngang (44 → 43).
   **So với đỉnh 21/8 (62 từ khóa top 10), hôm nay còn 43 — mất 19, tức mất 31%.**
2. **Mình tụt, không phải thị trường tụt.** Trong cửa sổ đó HR2B là site duy nhất
   mất nhiều ô top 10 (−11), trong khi LinkedIn +9, joblinks.vn +5, manpower +5,
   easyhrm +5, Facebook +4, hrchannels +4, talentnetgroup +3.
   Tính từ đỉnh riêng của từng bên, HR2B mất −17 ô, nặng nhất bảng.
3. **Tụt theo cụm trang, không phải toàn site.** Cụm "Nhân sự – tư vấn & dịch vụ
   nhân sự" bay khỏi bảng gần như trọn cụm; cụm tiếng Anh "outsource recruitment"
   mất sạch.

## Khớp với bản kiểm tra kỹ thuật cùng ngày
Không một trang dịch vụ nào (`/vi/dich-vu/...`) nằm trong sitemap, kể cả trang chủ
tiếng Việt `/vi/`. Đó là 17 từ khóa đang nhắm vào những trang Google không được mời vào.
Xem thêm: `../Viec that - Kiem tra ky thuat hr2b.com/`

## Lưu ý về độ tin cậy
- Hai ngày **27/8 và 28/8** công cụ quét lỗi (chỉ lấy được 4 và 55 từ khóa) —
  đã loại khỏi mọi so sánh và khỏi phép tính đỉnh.
- File serprobot chỉ ghi **10 URL đầu** mỗi ngày, nên phần đối thủ chỉ nhìn được top 10;
  từ khóa đứng từ vị trí 11 trở xuống không có URL trong file đó.

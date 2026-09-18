# Báo cáo phân tích thứ hạng HR2B — mốc 18/09/2026

## 👉 FILE CHÍNH — MỘT FILE, SÁU TAB (xem và sửa được)

**https://docs.google.com/spreadsheets/d/1oxOXGI1zX3MUNEhjt2JrcxtGlnnzbsuXtpM-2fkTV_M/edit**

Toàn bộ báo cáo nằm trong một file duy nhất, mỗi phần là một tab ở đáy màn hình:

| Tab | Nội dung |
|---|---|
| 0. Đọc trước | Hướng dẫn đọc, 4 kết luận nhanh, lưu ý độ tin cậy, phần còn thiếu |
| 1. Tổng quan | Số key vào top theo chủ đề và nhóm từ khóa, tỷ lệ, top 3/5/10, cột LÚC CAO NHẤT, kết luận, 2 phương án |
| 2. Chi tiết 109 từ khóa | Vị trí từng ngày, vị trí TB, thời gian giữ top, khả năng giữ top, URL hay bắt, URL bắt top cao nhất |
| 3. Đối thủ | Bảng A tỷ lệ vào top + chủ đề mạnh nhất · Bảng B biến động qua 11 ngày check · Bảng C top 10 hiện tại từng key |
| 4. Vào-ra top 01.08 → 29.08 | Ai vào / ai ra top 10 ở từng từ khóa, từng chặng ngày — giai đoạn trước khi tụt |
| 5. Vào-ra top 29.08 → 18.09 | Như trên, đúng cửa sổ mình tụt |

Bản gốc nằm trong thư mục này: `HR2B-bao-cao-gop-tat-ca.xlsx`.
Đã tải file trên Drive về và đối chiếu từng ô với bản gốc — khớp 100%.

Vì file gộp phải nén rất mạnh mới gửi lên được, các số thập phân đã làm tròn
về 1 chữ số (ví dụ vị trí trung bình 4.76 thành 4.8). Muốn xem số đầy đủ thì
mở các file lẻ bên dưới.

## File bổ sung — lọc từng key theo ngày

**https://docs.google.com/spreadsheets/d/1rj5UXn6SpO0h1QH5BCmq6FNE0u4CiaPf4zr7QtPdjKE/edit**

109 từ khóa, mỗi dòng một key: vị trí ngày 21/8, 14/9, 16/9, 17/9, 18/9; chênh lệch
của 18/9 so với từng mốc; và hai cặp cột đối thủ nào lên top 10 / ai bật khỏi top 10
(so với 21/8, và so với ngày liền trước 17/9). Bản gốc: `4-loc-tung-key-18-09-vs-21-08.csv`.

Quy ước dấu: **+ là lên hạng** (số vị trí nhỏ đi), **- là tụt hạng**.

Kết quả so với 21/8: mất hẳn 15 key · tụt mạnh 10 · tụt nhẹ 22 · đứng yên 22 ·
lên nhẹ 13 · lên mạnh 3 · mới có 7 · cả hai mốc ngoài bảng 17.

Chưa đưa được vào file gộp 6 tab vì file đó đã chạm trần dung lượng mỗi lần tải lên.

## Các file lẻ trước đây (vẫn giữ để đối chiếu)

| File | Nội dung | Link |
|---|---|---|
| **1/3** | Tổng quan, chủ đề, nhóm từ khóa, kết luận, phương án | https://docs.google.com/spreadsheets/d/1VQ1ljsEgSFMu8DRg2LniQB7aXKkmuLw0DG585Eo1BBE/edit |
| **2/3** | Chi tiết 109 từ khóa | https://docs.google.com/spreadsheets/d/1vbQsgPquF5epriZlg9s0Ls1iJEaRrI5JSjEyOyO3JbM/edit |
| **3B** | Đối thủ: tỷ lệ vào top, chủ đề mạnh nhất, ai lên ai xuống, top 10 hiện tại | https://docs.google.com/spreadsheets/d/1LnHjyo6r1nRqCkQ1EuOJWQPcvMCyAVA4_RiS51tg3Og/edit |
| **3C** | Ai vào / ai ra top 10 từng từ khóa · 01/08 → 29/08 | https://docs.google.com/spreadsheets/d/1zNR_HJxJw3Rx6OvZSTPn8l66gBLfT6x8fPClxoOwf2E/edit |
| **3D** | Ai vào / ai ra top 10 từng từ khóa · 29/08 → 18/09 (cửa sổ tụt) | https://docs.google.com/spreadsheets/d/1gUZyCeRav2qbVoscZ7LXgALGYGSTtLR0Sfc5i9wawjU/edit |

Hai bản cũ vẫn giữ lại để đối chiếu, không dùng nữa:
- Bản đối thủ cũ (3/3): https://docs.google.com/spreadsheets/d/1Rp8JfBDvEOzdP8TYGuJkini0Y-6r_CysMvlmF4J5YME/edit
- Bản gộp 1 file (trước khi tách): https://docs.google.com/spreadsheets/d/1lvi3EtYzpnu2JdxfJ6G5GZJt5kssedJDYiu_ws9z60E/edit

## ⚠️ Đổi cách đếm ở phần đối thủ (từ FILE 3B trở đi)

Bản đối thủ **cũ** đếm theo **số ô** trên trang kết quả: một tên miền chiếm 2 vị trí
trong cùng một top 10 thì tính là 2. Vì vậy HR2B ngày 18/9 hiện lên là **59**.

Bản **mới** đếm theo **số từ khóa**: một tên miền có mặt trong top 10 của một từ khóa
tính là **1**, dù chiếm mấy ô. Vì vậy HR2B ngày 18/9 là **43** — khớp đúng với dòng
"Top 10" ở FILE 1. Con số khác nhau nhưng không mâu thuẫn, chỉ là hai thước đo khác nhau;
từ nay dùng thước "số từ khóa" cho thống nhất.

Các file `.csv` trong thư mục này là bản gốc đã dùng để tạo Google Sheet.

## Cột "LÚC CAO NHẤT"

Thêm ngày 18/09 theo yêu cầu. Nghĩa là **mức tốt nhất đạt được trong 11 mốc đo tin cậy**
(đã loại 27/8 và 28/8 vì công cụ quét lỗi), kèm **ngày đạt mức đó** và **chênh lệch so với 18/9**.

- File 1: đỉnh của từng chỉ số tổng (Top 3/5/10/20/30, vị trí TB) và của từng chủ đề, từng nhóm.
- File 2: vị trí tốt nhất từng từ khóa từng đạt + ngày đạt + số bậc đã mất so với lúc đó.
  Ô ghi `MẤT HẲN` = từ khóa từng có thứ hạng nhưng ngày 18/9 không còn.
- File 3B: số từ khóa top 10 cao nhất từng đối thủ từng đạt + ngày đạt + % còn lại so với đỉnh.

## Phần đối thủ có thêm gì (FILE 3B / 3C / 3D)

**FILE 3B — Bảng A:** với bộ 109 từ khóa, mỗi đối thủ có tỷ lệ vào top là bao nhiêu,
chủ đề nào họ mạnh nhất, và chiếm bao nhiêu phần trăm cụm chủ đề đó.
- talentnetgroup.com 90/109 = **82,6%** — mạnh nhất ở **Nhân sự** (67 key = 84,8% cụm)
- hr2b.com 76/109 = **69,7%** — mạnh nhất ở **Nhân sự** (60 key = 75,9% cụm)
- hrchannels.com chỉ 48/109 nhưng ôm **96% cụm Headhunter** (24/25 từ khóa)
- careerviet.vn 76% cụm Headhunter · glints.com 72% cụm Headhunter dù tổng chỉ 21 key

**FILE 3B — Bảng B:** số từ khóa trong top 10 và vị trí trung bình của từng đối thủ
qua cả 11 ngày check, kèm cột xu hướng (Đang lên / Đi ngang / Đang xuống).
Cộng dồn 10 chặng: **hr2b.com vào 53 lượt, rời 65 lượt → ròng −12, xấu nhất bảng.**
topcv.vn −10, talentnetgroup −8, careerviet −5. Ngược lại aniday +9, easyhrm +6,
glints +5, steco +5, ckhrconsulting +5.

**FILE 3B — Bảng C:** top 10 hiện tại (18/09) của từng từ khóa, xếp theo thứ tự 1→10.

**FILE 3C và 3D:** ai vào / ai ra top 10 ở **từng từ khóa, từng chặng ngày**.
3C là giai đoạn 01/08 → 29/08 (trước khi tụt), 3D là 29/08 → 18/09 (cửa sổ tụt).
Tách hai file vì mỗi file đã hơn 400 dòng.

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

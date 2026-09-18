# Báo cáo phân tích thứ hạng HR2B — mốc 18/09/2026

**Bản Google Sheet (xem và sửa được):**
https://docs.google.com/spreadsheets/d/1lvi3EtYzpnu2JdxfJ6G5GZJt5kssedJDYiu_ws9z60E/edit

File `.csv` trong thư mục này là bản gốc đã dùng để tạo Google Sheet.

## Nguồn dữ liệu
- `lịch sử top.csv` — 109 từ khóa × 13 mốc ngày (01/08 → 18/09/2026)
- `serprobot_serps_export_5102689_2026-09-18.csv` — top 10 URL mỗi ngày, 1.253 bản ghi
- Google Sheet nhóm từ khóa của HR2B — 3 chủ đề, 41 nhóm

## Ba kết luận chính
1. **Ngày tụt thật sự không phải 18/9.** Cú tụt xảy ra khoảng **29/8 → 11/9**:
   từ khóa top 10 rơi 55 → 44; số ô top 10 HR2B chiếm trên SERP rơi 69 → 58.
   Từ 11/9 tới 18/9 đi ngang (44 → 43).
2. **Mình tụt, không phải thị trường tụt.** Trong cửa sổ đó HR2B là site duy nhất
   mất nhiều ô top 10 (−11), trong khi LinkedIn +9, joblinks.vn +5, manpower +5,
   easyhrm +5, Facebook +4, hrchannels +4, talentnetgroup +3.
3. **Tụt theo cụm trang, không phải toàn site.** Cụm "Nhân sự – tư vấn & dịch vụ
   nhân sự" bay khỏi bảng gần như trọn cụm; cụm tiếng Anh "outsource recruitment"
   mất sạch.

## Khớp với bản kiểm tra kỹ thuật cùng ngày
Không một trang dịch vụ nào (`/vi/dich-vu/...`) nằm trong sitemap, kể cả trang chủ
tiếng Việt `/vi/`. Đó là 17 từ khóa đang nhắm vào những trang Google không được mời vào.
Xem thêm: `../Viec that - Kiem tra ky thuat hr2b.com/`

## Lưu ý về độ tin cậy
- Hai ngày **27/8 và 28/8** công cụ quét lỗi (chỉ lấy được 4 và 55 từ khóa) —
  đã loại khỏi mọi so sánh.
- File serprobot chỉ ghi **10 URL đầu** mỗi ngày, nên phần đối thủ chỉ nhìn được top 10;
  từ khóa đứng từ vị trí 11 trở xuống không có URL trong file đó.

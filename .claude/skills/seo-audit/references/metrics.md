# Bộ chỉ số và ngưỡng

## 1. Chỉ số nội dung, đo cho mọi trang trong SERP

Số từ nội dung chính · số ảnh · ảnh lazy · ảnh srcset · ảnh WebP · dung lượng HTML ·
số H2 · số H3 · toàn bộ heading · FAQ hiển thị · FAQPage schema · danh sách schema ·
dateModified · link nội bộ · form · link gọi điện · title · description · H1.

Nội dung chính = phần bài viết, loại menu, chân trang, thanh bên. Nếu sau khi lọc còn dưới
30% số từ ban đầu thì trả lại bản chỉ bỏ thẻ khung — tránh cắt nhầm.

## 2. Chỉ số kỹ thuật, đo cho trang của mình và trang top của mỗi cụm

TTFB tải HTML · ảnh thiếu alt · số thẻ H1 · độ dài title · độ dài description ·
số chỗ nhảy cấp heading · script ngoài · script nội tuyến · CSS ngoài · thẻ og · canonical · robots.

## 3. Ngưỡng lọt top

Ngưỡng lấy trên **toàn bộ cohort đang nằm trong mốc đó**, không lấy riêng nhóm ở biên:

| Mục tiêu | Lấy trung vị của các trang đang ở vị trí |
|---|---|
| Top 10 | 1 đến 10 |
| Top 5 | 1 đến 5 |
| Top 3 | 1 đến 3 |

Lý do: câu hỏi cần trả lời là "một trang nằm trong top N trông như thế nào", không phải
"mức tối thiểu để chen vào chỗ cuối". Lấy nhóm biên cho ngưỡng thấp giả tạo và cỡ mẫu nhỏ.

Tính riêng cho từng cụm. Cần tối thiểu 5 trang mới đủ mẫu, dưới mức đó thì bỏ qua mốc đó.

Đo thật trên bộ 302 từ khoá, 19 cụm của một dự án nội thất văn phòng: đổi từ nhóm biên sang
toàn dải làm ngưỡng số từ dịch +32 từ (2.684 lên 2.716) — gần như không đổi — nhưng số cụm
đủ mẫu để có ngưỡng riêng ở mốc top 5 tăng từ 15/19 lên 19/19. Lợi ích chính là cỡ mẫu,
không phải mức ngưỡng.

## 4. Bốn phép đo cấu trúc

| Phép đo | Cách tính | Mức tham chiếu |
|---|---|---|
| Trang dịch vụ so với blog | Tỷ lệ lượt top 3 của đối thủ nằm trên URL cấp gốc; vị trí trung vị và tỷ lệ top 3 của từ khoá do trang gốc gánh so với blog gánh | Lần chạy tham chiếu: 93% lượt top 3 của đối thủ là trang cấp gốc; trang gốc trung vị 6 và 38% top 3, blog trung vị 14 và 13% top 3 |
| Độ phân tán URL | Số từ khoá chia số URL dùng; và số từ khoá top 3 chia số URL có top 3 | Đối thủ dẫn đầu 18–22 kw/URL, dự án tham chiếu 6,3 |
| Ăn thịt từ khoá | Đếm hai nguồn: số từ khoá có từ 2 URL nội bộ trong SERP, và số truy vấn có từ 2 URL nhận hiển thị trên GSC | GSC luôn cao hơn vì thấy cả trang ngoài top |
| Schema thực thể | Tỷ lệ trang có Organization, LocalBusiness, PostalAddress, GeoCoordinates, ContactPoint, AggregateRating | Lần chạy tham chiếu: mình 0%, top 3 là 69% |

## 5. Tính khả thi — mục tiêu đặt trước

Bắt đầu từ mục tiêu, tính ngược:

```
cần thêm = mục tiêu × tổng số từ khoá − số từ khoá hiện đạt
kho khả dụng = số từ khoá ở các tầng dưới mốc đó
tỷ lệ chuyển đổi cần thiết = cần thêm / kho khả dụng
```

Sau đó đối chiếu với ba mức tham chiếu để đánh giá tỷ lệ cần thiết có thực tế không:

| Tầng nguồn | Thận trọng | Cơ sở | Triệt để |
|---|---|---|---|
| 11–20 lên top 10 | 75% | 85% | 92% |
| 21–50 lên top 10 | 45% | 55% | 68% |
| Ngoài 50 lên top 10 | 25% | 35% | 45% |
| 6–10 lên top 5 | 45% | 60% | 72% |
| 11–20 lên top 5 | 18% | 28% | 38% |
| 4–5 lên top 3 | 45% | 60% | 72% |
| 6–10 lên top 3 | 20% | 30% | 40% |
| 11–20 lên top 3 | 6% | 11% | 16% |

Nếu tỷ lệ cần thiết vượt cột "triệt để" thì mục tiêu không đạt được bằng on-page.
Nói thẳng con số thiếu, đừng làm mềm.

Trừ khỏi kho: các từ khoá đã xác định lệch ý định tìm kiếm — SERP toàn trang bán sản phẩm
trong khi mình bán dịch vụ, hoặc ngược lại. Ghi rõ danh sách đã trừ.

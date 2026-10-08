# Nhật ký: Domain Research — 3 báo tài chính (chạy ngày 08/10/2026)

Kết quả đã ghi vào sheet *Kịch bản traffic Techcombank | 2026*:
- tab **Domain Research**, cột C, dòng 20–22 (mỗi báo 1 ô)
- tab **Domain Research - Chi tiết**, dòng 92–136 (45 dòng, mỗi chủ đề 1 dòng, đủ điểm A/B/C, lý do, URL đối chiếu)

> Repo này để công khai, nên file này chỉ ghi cách làm và số đếm.
> Không chép dữ liệu nội bộ của Techcombank (Content Plan, Danh sách chi tiết…) vào đây.

## 1. Nguồn và khung thời gian

| Báo | Địa chỉ thật | Cách lấy danh sách bài | Bài trong khung 08/07–08/10 |
|---|---|---|---|
| thitruongtaichinhtiente.vn | giữ nguyên (http → https) | sitemap theo ngày `sitemap-article-YYYY-MM-DD.xml` | 2.051 |
| thoibaotaichinhvietnam.vn | giữ nguyên (http → https) | sitemap theo tháng `sitemap-month-2026-{7..10}.xml` | 3.603 |
| tapchitaichinh.vn | **đã chuyển sang tapchikinhtetaichinh.vn** | không có sitemap/RSS → đi trang chuyên mục, bấm "Xem thêm" (tham số `BRSR`) | 3.177 |

Mỗi bài chỉ lấy tiêu đề, sapo, chuyên mục, ngày đăng, thẻ. Không lưu toàn văn.

## 2. Lọc chuyên mục (bước 1)

Bỏ các chuyên mục: Thời sự, Xã hội, Tin hội viên, Hiệp hội ngành nghề, Nhìn ra thế giới / Tài chính quốc tế,
Kết nối, Văn hóa, Thư giãn, Sống đẹp, Góc sinh viên, Xây dựng Đảng, Đưa nghị quyết vào cuộc sống, Học tập làm theo…,
Trang thông tin Bộ trưởng, Sự kiện doanh nghiệp, Khu công nghiệp, Infographic/eMagazine/Ảnh, Môi trường, Giảm nghèo.

| Báo | Bài còn lại sau lọc chuyên mục | Bài quy được về chủ đề | Bài bị loại ở bước 4 (vĩ mô, hội nghị, học thuật, tin DN lẻ) |
|---|---|---|---|
| thitruongtaichinhtiente.vn | 1.468 | 411 | 1.057 |
| thoibaotaichinhvietnam.vn | 3.139 | 1.079 | 2.060 |
| tapchitaichinh.vn | 2.456 | 429 | 2.027 |

## 3. Gom chủ đề và chấm điểm

- Có 36 chủ đề ứng viên, gom bằng từ khoá trong tiêu đề. Mỗi chủ đề được chấm theo 3 trục A/B/C của spec.
- Chủ đề phải có **ít nhất 3 bài trên chính báo đó** mới được xét cho báo ấy.
- Thứ tự xếp: "Phù hợp" đứng trước "Cân nhắc". Trong cùng nhóm, xếp theo điểm A+B rồi đến số bài.
- **Trùng chéo**: tiêu đề giống nhau ≥ 75% và đăng cách nhau ≤ 3 ngày trên 2 báo thì tính là 1 tin (thường là cùng một thông cáo). Số tin trùng ghi ở cột cuối tab Chi tiết.
- Xu hướng theo tháng so T9 với T8, vì T7 và T10 chỉ có một phần tháng (đánh dấu `*`).

### Chủ đề "Cân nhắc" có đủ bài nhưng không vào ô C (vì mỗi báo đã đủ 15 chủ đề "Phù hợp")

Giá cà phê / hồ tiêu / cao su / heo hơi / lúa gạo hôm nay (Thời báo Tài chính ra mỗi ngày, trên 90 bài mỗi loại),
VN-Index hôm nay, nâng hạng thị trường chứng khoán, lãi suất trái phiếu chính phủ, tài sản mã hóa là gì,
chính sách mới có hiệu lực tháng 10/2026. Lý do: chỉ gắn được lời mời hành động (CTA) chung về app, tức điểm B = 1.

### Chủ đề loại hẳn

- "Nợ xấu ngân hàng": tin tiêu cực về ngân hàng, B = 0.
- Sửa Luật Bảo hiểm xã hội: còn là dự thảo, rủi ro tuân thủ Cao.
- "Hạn mức bảo hiểm tiền gửi": đã có trong cột **Chốt bỏ** (tab Cào từ khoá mới).

## 4. Điểm cần người duyệt xem lại

- "Giảm 30% thuế" trên Thị trường Tài chính Tiền tệ chỉ có 3 bài, cả 3 đều ở giai đoạn đề xuất (tháng 8).
  Các báo khác đã đưa tin chính thức nên chủ đề vẫn giữ, nhưng nên dẫn đúng văn bản cuối cùng.
- "Thẻ tín dụng miễn phí thường niên": bài nguồn chủ yếu là PR của ngân hàng khác. Khi viết, không nhắc tên đối thủ.
- "Điều kiện mua nhà ở xã hội": cần thẩm định lời mời hành động, vì gói vay nhà ở xã hội chủ yếu đi qua Ngân hàng Chính sách xã hội.
- Trạng thái "Đã có trong scope, chưa viết" được ghi là **[Mới]** ở cột C, vì spec chỉ cho 4 nhãn. Tab Chi tiết vẫn ghi đúng tên tab scope.

## 5. Chạy lại lần sau

Các script nằm trong thư mục `cong-cu/`:
1. `list_tapchi.py`: lấy danh sách bài của tapchikinhtetaichinh.vn.
2. `fetch_meta.py`: lấy tiêu đề, sapo, chuyên mục, ngày và thẻ của từng bài (8 luồng, có thử lại).
3. `build.py`: gom chủ đề, chấm điểm, xếp hạng và xuất kết quả. Danh mục chủ đề (`topics.py`) không đưa lên đây vì có chứa ghi chú đối chiếu nội bộ.

# Không bịa thông tin — quy tắc số một

Mọi con số, mọi nhận định, mọi đề xuất trong báo cáo phải truy được về một trong ba nguồn:

| Nguồn | Cho biết gì | File dữ liệu |
|---|---|---|
| File check top | Thứ hạng, URL nào của mình đang xếp hạng, SERP của đối thủ | `data/kw.json` |
| Search Console | Lượt hiển thị, click, tỷ lệ nhấp, URL nội bộ tranh nhau, trang ngoài top | `data/gsc_qp.json` |
| HTML đã crawl | Số từ, ảnh, heading, schema, title, mật độ cụm từ, chỉ số kỹ thuật | `data/pages.json`, `data/tech.json` |

Không có nguồn thì không viết. Đây là quy tắc đứng trên mọi quy tắc khác trong skill này.

## Áp dụng cho file giao ra

**Mọi thông tin xuất ra file output bắt buộc là thật**, tổng hợp từ đúng ba nguồn trên và các
nguồn đó phải đã được chứng thực trước khi dùng:

| Nguồn | Chứng thực nghĩa là |
|---|---|
| File check top | Đã đọc bằng `parse_ranktracker.py`, biết rõ độ sâu SERP và hai mốc ngày |
| Search Console | Đã lấy bằng credential có quyền với property, đã ghi kỳ đo vào `gsc_meta.json` |
| HTML đã crawl | Đã đo trực tiếp bằng `crawl.py`, đã loại trang render JavaScript, và URL nội bộ đã qua `verify_urls.py` nên biết đang 200, 404, 301 hay noindex |

Kéo theo ba điều cấm ở khâu xuất báo cáo:

1. **Cấm văn bản mẫu.** Không có câu chữ điền sẵn, không có số ví dụ, không có tên đối thủ
   minh hoạ. Mọi khối trong `overview.py` và `blocks.py` chỉ in ra khi có dữ liệu thật.
2. **Thiếu nguồn thì nói thẳng thiếu nguồn nào.** Khối không đủ dữ liệu in đúng một dòng
   ghi rõ thiếu gì và chạy lệnh nào để có — không im lặng bỏ mục, không lấp bằng câu chung chung.
3. **Ước tính phải gắn nhãn ước tính** kèm hệ số đã dùng và nguồn của hệ số. Hiện chỉ có hai
   chỗ được phép ước tính: cột kỳ vọng và trần ở mục 1, cột dư địa kỳ vọng ở mục 4 của file
   tổng hợp — cả hai đều lấy kho từ khoá thật nhân với mức tham chiếu ở `references/metrics.md` mục 5,
   và đều in kèm dòng nói rõ đó là ước tính.

---

## Cấm tuyệt đối

**Cấm bịa số.** Không viết "khoảng 5.000 từ", "chừng 100 ảnh", "đối thủ thường có FAQ".
Số phải là số đo được, ghi đúng như dữ liệu trả về.

**Cấm bịa tên đối thủ hoặc URL.** Chỉ nhắc domain và URL có trong `data/pages.json`.
Không viết tên một đối thủ vì "ngành này thường có" hay vì nhớ từ dự án khác.

**Cấm bịa nội dung trang đối thủ.** Chỉ mô tả mục nội dung có trong `headings` đã crawl.
Không suy đoán "chắc họ có mục báo giá".

**Cấm đề xuất cho trang chưa biết tình trạng.** Trước khi viết bất cứ việc gì cho một URL,
phải biết URL đó đang 200, 404, 301 hay noindex. Chạy `scripts/verify_urls.py` và đọc
`references/verify.md` mục 2.

**Cấm bịa trạng thái kỹ thuật.** Không viết "trang tải chậm" khi chưa đo. Chỉ viết cái đo được:
số ảnh, số lazy, dung lượng HTML, TTFB.

**Cấm bịa lịch sử.** Không viết "trang này mới xuất bản" hay "Google vừa cập nhật thuật toán"
nếu không có dữ liệu chứng minh trong tay.

**Cấm suy diễn nhân quả không kiểm chứng được.** "Thiếu backlink nên không lên top" là suy diễn
nếu chưa đo backlink. Viết đúng cái biết: on-page không phân biệt được giữa các tầng vị trí,
nên nguyên nhân nằm ngoài on-page — và ghi rõ chưa đo được yếu tố nào.

**Cấm dùng số của dự án khác làm chuẩn.** Các con số tham chiếu trong `references/metrics.md`
là kết quả của một lần chạy cụ thể, dùng để so sánh phương pháp, không phải chuẩn ngành.
Khi viết báo cáo cho dự án mới thì dùng số đo được của chính dự án đó.

---

## Bắt buộc

**Mỗi nhận định đi kèm số và nguồn.** "Ảnh chưa tối ưu" là câu vô giá trị.
"71 ảnh, 0 ảnh WebP, trong khi doithu-a.vn có 9 ảnh WebP trên trang cùng nhóm" mới là nhận định.

**Ghi rõ ngày và phạm vi đo.** Ngày crawl, kỳ Search Console, độ sâu SERP, vị trí địa lý đo.

**Ghi rõ cái không đo được.** Nếu thiếu backlink, thiếu dữ liệu tốc độ trường, thiếu lượng
tìm kiếm — nói thẳng là chưa đo, đừng lấp bằng phỏng đoán.

**Ghi rõ mẫu nhỏ.** Kết luận từ dưới 5 trang hoặc dưới 100 lượt hiển thị phải nêu kèm cỡ mẫu.
Vị trí trung bình Search Console trên 18 lượt hiển thị không phải bằng chứng.

**Trang đối thủ không crawl được thì ghi rõ**, không bỏ qua im lặng. Ba trên tám trang chặn crawl
thì bảng so sánh chỉ còn năm dòng, và phải nói điều đó.

---

## Được phép, nhưng phải gắn nhãn

| Loại | Cách viết đúng |
|---|---|
| Mục tiêu số lượng cho việc cần làm | "Nâng cụm chính từ 8 lên 25–30 lần" — số 8 là đo được, 25–30 là mục tiêu đề ra dựa trên mức 27 của đối thủ đang đứng trên |
| Ước tính số từ khoá thu về | Phải nêu rõ là ước tính, kèm hệ số chuyển đổi đã dùng và nguồn của hệ số |
| Đề xuất nội dung mới | Ghi rõ dựa trên mục nào của đối thủ nào, hoặc là gap không ai có |
| Dải giá, số liệu ngành trong FAQ | Chỉ nêu hướng trả lời, không tự điền số. Người viết bài lấy số thật từ doanh nghiệp |

---

## Kiểm tra trước khi giao

```bash
python3 scripts/verify_claims.py --data data --content content.py
```

Script đối chiếu các tuyên bố có cấu trúc trong `content.py` với dữ liệu đã đo:
title và description hiện tại, các số ở cột "hiện tại" của bảng ảnh, tên domain đối thủ.
Có cảnh báo thì sửa, đừng bỏ qua.

Script không bắt được mọi trường hợp — nó kiểm phần kiểm được. Phần còn lại là trách nhiệm
của người viết: **mở dữ liệu ra đối chiếu, đừng viết từ trí nhớ.**

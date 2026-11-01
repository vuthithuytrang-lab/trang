# 7c — Sapo và kết bài: vùng chứa nhiều key (Trang bổ sung 01/11/2026, nguyên văn)

## Nguyên tắc
Sapo và kết bài là hai vùng duy nhất được phép chứa đồng thời key chính và nhiều key phụ. Lý do: đây là hai đoạn có chức năng khái quát toàn bài, nên việc điểm qua các nhóm nội dung là tự nhiên, không phải nhồi key.

Các vùng còn lại giữ nguyên quy tắc 5b: **mỗi câu tối đa 1 key**.

## Cách chèn
Chỉ **1–2 key được phép khớp CHÍNH XÁC trong mỗi đoạn**. Các key còn lại phải chèn dưới dạng MỞ RỘNG hoặc PHÂN TÁN, bằng cách tách phần định danh chung và liệt kê phần phân biệt.

Ví dụ với bộ key: thủ tục thành lập doanh nghiệp / quy trình thành lập doanh nghiệp / hồ sơ thành lập doanh nghiệp / các bước thành lập doanh nghiệp

SAI (spam — 4 lần lặp cụm "thành lập doanh nghiệp"):
"Bài viết hướng dẫn thủ tục thành lập doanh nghiệp, quy trình thành lập doanh nghiệp, hồ sơ thành lập doanh nghiệp và các bước thành lập doanh nghiệp."

ĐÚNG (1 key chính xác + 3 key phân tán):
"Nắm rõ thủ tục thành lập doanh nghiệp, từ hồ sơ và quy trình đến các bước đăng ký, sẽ giúp bạn tiết kiệm thời gian."

## Điều kiện bắt buộc
1. Chuỗi liệt kê phải phản ánh đúng các mục có thật trong bài. Không nêu nội dung bài không có.
2. Mỗi thành phần trong chuỗi phải là một ý riêng, không trùng nghĩa nhau. "quy trình" và "các bước" là một thứ — chỉ chọn một nếu bài không tách thành hai mục riêng.
3. Chuỗi tối đa 3 thành phần. Dài hơn sẽ thành danh sách, mất chất văn xuôi của sapo/kết bài.
4. Câu chứa chuỗi liệt kê phải có mệnh đề chính mang thông tin, không phải câu chỉ để liệt kê.
5. Sapo và kết bài không dùng cùng một cấu trúc liệt kê. Nếu sapo đã dùng "từ A và B đến C", kết bài phải đổi cách diễn đạt khác.

## Kiểm tra trước khi xuất
- Đọc to cả đoạn: có cụm nào lặp 2 lần trong 2 câu liền nhau?
- Bỏ hết phần in đậm đi, câu còn đọc xuôi không?
- Chuỗi liệt kê có khớp với các H2 thật của bài không?
- Sapo có hứa nội dung nào bài không có không?

## Báo cáo
Trong phần tổng kết, nêu riêng:
- Sapo: liệt kê key đạt, ghi rõ loại khớp của từng key (chính xác / mở rộng / phân tán)
- Kết bài: tương tự
- Nếu một key chỉ xuất hiện ở sapo/kết bài mà không có trong thân bài, phải cảnh báo: key đó có thể lệch chủ đề bài.

# Công thức: bài "Giá nhôm hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-nhom — chạy lần đầu 15/10/2026, Trang chưa duyệt nguồn.

| Việc | Cách làm |
|---|---|
| Bảng thế giới (10 hợp đồng ALI…) | Giá chốt phiên trên barchart.com (nhôm COMEX `ALI`), từng hợp đồng — `lay_gia_barchart.js`. Hợp đồng chưa chốt thì % tính từ giá chốt hôm trước (Yahoo Finance), đánh `tinh_toan` |
| Cách viết số | Làm tròn tới đơn vị như bài (`3,086`), % kiểu `-0.02%` |
| Bảng trong nước | https://www.phelieuquangphong.com/thu-mua-phe-lieu-nhom/ (không ghi ngày) — giữ khi trùng |
| Kỳ hạn | Hợp đồng tháng gần nhất đáo hạn cuối tháng → cuộn lên |
| Script | `tao_sua.py` (có `--kiem`), `lay_gia_barchart.js` |
Mẫu kết quả: `cap-nhat-bai-tcb/2026-10-16-gia-nhom/`.

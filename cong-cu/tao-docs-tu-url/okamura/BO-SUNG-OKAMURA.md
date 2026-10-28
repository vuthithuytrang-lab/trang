# Bổ sung cho dự án Okamura (đọc SAU HUONG-DAN-WORKER.md, phần này thắng khi khác nhau)

- Site: https://www.okamura.com.vn (Wix). Nội thất văn phòng Nhật Bản (bàn, ghế, cabin, tủ). Không có cặp tỷ giá:
  F/G/I trống → bỏ qua mọi thứ về `tygia`; mọi anchor nằm trong `pairs`.
- Tải bài: `bash $D/fetch.sh <url> <file>` (UA trình duyệt). Dựng: `cd /home/user/trang/cong-cu/tao-docs-tu-url &&
  SP=$D/ BASE=https://www.okamura.com.vn SEL='[data-hook="post-description"]' python3 build.py`. KHÔNG chạy prep.py.
  Trang sản phẩm (/san-pham/...) build in ra `product` — VẪN LÀM (khác Techcombank): chèn vào các đoạn mô tả có sẵn.
  Nếu trang sản phẩm gần như không có chữ (< ~5 đoạn) → báo `error: "trang ít nội dung"`, không bịa nội dung.
- Giọng văn: chuyên gia nội thất văn phòng, xưng "bạn" (hoặc "doanh nghiệp" nếu bài dùng vậy), giọng tư vấn, không quảng cáo lố.
  Không bịa kích thước, giá, bảo hành, chất liệu, chứng nhận — chỉ dùng thông tin có trong bài gốc hoặc trang đích.
- Thay ví dụ ngân hàng trong brief bằng ngữ cảnh nội thất: VD anchor "kích thước ghế văn phòng" đặt ở đoạn đang bàn về chọn ghế hợp vóc dáng.
- Anchor có chữ "2026", "hiện nay", "top", "tổng hợp", "các mẫu" phải giữ NGUYÊN VĂN → hợp nhất là dòng `xemthem`
  (">>> Xem thêm: <anchor> ..." hoặc câu dẫn ngắn) hoặc `vietlai` khéo; đừng nhét gượng vào giữa câu.
- Nhiều bài trỏ link sang nhau theo chuỗi; bài gốc có thể ĐÃ có link tới URL đích → dùng `dacolink`/`chuyenlink` đúng quy tắc.
- Tên file (title): đúng cột "Từ khoá chính" của dòng (có trong rows.json là `kw`), viết hoa chữ đầu. VD "Sắp xếp bàn ghế văn phòng".
- `miss` trong rows.json = URL đích sheet có nhưng THIẾU anchor → KHÔNG chèn, chỉ ghi vào notes.

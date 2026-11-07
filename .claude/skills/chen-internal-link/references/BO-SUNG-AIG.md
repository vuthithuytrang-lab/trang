# Bổ sung dự án AIG (Asia Ingredients Group) — thắng HUONG-DAN-WORKER khi khác nhau

- Sheet `1os17NKJgF6ME4MdYwUoACnAjZAK4MBevxWd0yBJus9E`, tab **"5. Internal Link chuẩn"**, **hàng tiêu đề = hàng 11**, dữ liệu từ hàng 12.
  Cột: D Từ khoá chính · **I Landingpage chính xác (bài cần chèn link vào)** · Q/R/S Anchor 1/URL 1/Đã chèn AC1 · T/U/V cặp 2 · W/X/Y cặp 3 ·
  Z Tình trạng · **AB Blog = nơi ghi đề xuất** · AC Note. Cột S/V/Y ("Đã chèn") chỉ để tham khảo — luôn kiểm tra bài thật trên web.
- **Chế độ RÀ SOÁT + ĐỀ XUẤT (Trang chốt 07/11/2026):** KHÔNG tạo/sửa file. Đọc bài đã đăng, với từng anchor:
  đã có link đúng URL + chữ link đúng anchor + câu tự nhiên → bỏ qua; có nhưng gượng/sai chữ/sai chỗ → đề xuất sửa; chưa có → tìm chỗ và đề xuất.
  Ghi đề xuất vào ô AB (chỉ ô trống) theo mẫu:
  ```
  Anchor 3: nhà cung cấp nguyên liệu thực phẩm
  Trước khi chèn: (dòng mới) sau đoạn "Việc sử dụng trái cây đông lạnh…"
  Đề xuất: >>> Bên cạnh trái cây đông lạnh, AIG còn là nhà cung cấp nguyên liệu thực phẩm …
  ```
  Viết lại câu có sẵn thì "Trước khi chèn:" = câu gốc nguyên văn. Các anchor cách nhau 1 dòng trống. Bài đủ và tự nhiên → "Đã đủ x/x anchor, chèn tự nhiên — không cần sửa."
- Site WordPress: tải `bash D/fetch.sh <url> <file>`; dựng `SP=D/ BASE=https://asiagroup-vn.com SEL='section.main_content_post' python3 -I D/build.py`.
- Giọng: B2B, nhà cung cấp nguyên liệu thực phẩm/đồ uống/dược cho **doanh nghiệp**; xưng "doanh nghiệp", nhắc "AIG" vừa phải. Không bịa chứng nhận, công suất, số liệu.
- Anchor có "là gì", "2026", "3 nhóm", "11 nhóm", "(…)" → hợp dạng dòng ">>> Xem thêm: …" hoặc viết lại khéo; giữ nguyên văn kể cả ngoặc.

- **Luôn chạy 1 vòng biên tập lại** (6 tiêu chí: anchor nguyên văn · đúng ngữ cảnh trang đích · câu nối mạch, ≤35 chữ, không lặp "AIG còn là…" · không ý ngoài bài/trang đích · vị trí ≥25% · trích câu gốc chính xác) trước khi ghi vào sheet — lượt đầu 16/21 bài phải viết lại.

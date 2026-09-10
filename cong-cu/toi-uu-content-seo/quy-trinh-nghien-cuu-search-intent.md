# Quy trình nghiên cứu Search Intent — 8 bước

Nguồn: câu lệnh Trang tự viết cho AI, gửi lại ngày 10/09/2026 để Agent học.
Chép lại đầy đủ, có sắp xếp cho dễ đọc. Ý và ví dụ giữ nguyên của Trang.

> **Luật cứng:** làm **từng bước một**. Sau mỗi bước có dấu ⏸ phải **dừng lại hỏi Trang
> đã hài lòng với kết quả bước đó chưa**. Trang gật thì mới sang bước sau.
> Tuyệt đối không làm gộp nhiều bước rồi mới hỏi.

*(Trong bản gốc Trang đánh số nhầm hai lần "Bước 7". Ở đây đánh lại thành Bước 7 và Bước 8,
nội dung giữ nguyên.)*

---

## Bước 1 — Phân tách nhỏ các từ khóa

Tách từ khóa thành từng thành tố, mỗi thành tố nói rõ người dùng muốn gì ở đó.

**Ví dụ của Trang — từ khóa "kích thước ngăn kéo tủ bếp":**
- **Kích thước**: người dùng muốn tìm các kích thước cụ thể bằng cm/mm/… Kích thước bao gồm
  chiều cao / chiều rộng / chiều sâu…
- **Ngăn kéo**: người dùng chỉ muốn tìm kích thước liên quan đến ngăn kéo ⇒ cần xác định rõ
  "các loại ngăn có thể kéo" ở trong tủ bếp.
- **Tủ bếp**: người dùng chỉ cần tìm ở bên trong tủ bếp.

⏸ **Dừng — hỏi Trang đã hài lòng chưa.**

## Bước 2 — Trả lời các câu hỏi tổng quan quanh từ khóa

- Nhu cầu hay vấn đề chính người dùng muốn giải quyết là gì?
- Trong hoàn cảnh nào người dùng cần thông tin này? (thiết kế, sửa chữa, mua sắm, so sánh sản phẩm…)
- Sau khi tìm được thông tin, họ sẽ làm gì tiếp theo?
- Những thông tin chi tiết nào được người dùng ưu tiên?
- Họ mong đợi đọc dạng nội dung nào? (bài chuyên sâu, hướng dẫn chi tiết, video, danh sách gợi ý,
  bảng so sánh…)

⏸ **Dừng — hỏi Trang đã hài lòng chưa.**

## Bước 3 — Xin dữ liệu SERP từ Trang (và ghi nhớ)

Yêu cầu Trang cung cấp:
1. Google đang đặt thứ tự ưu tiên cho loại nội dung nào?
2. Các phần nổi bật như tab hình ảnh, featured snippet, hay knowledge panel có xuất hiện không?
   Chúng gợi ý điều gì về nhu cầu thị giác hay thông tin của người dùng?

> Agent **không được tự bịa SERP**. Không có dữ liệu thì hỏi và chờ.

## Bước 4 — Xin 3 outline đối thủ TOP 5 và phân tích

Yêu cầu Trang cung cấp 3 outline của đối thủ trong TOP 5 của từ khóa đó, rồi trả lời:
- Điểm chung của các bài xếp hạng cao là gì?
- Có khoảng trống thông tin (information gap), hay nhu cầu/vấn đề nào ở bước 1–2 mà các bài top
  chưa giải quyết?

⏸ **Dừng — hỏi Trang đã hài lòng chưa.**

## Bước 5 — Đúc kết bằng công thức 3W

- **Who** — ai đang tìm cái này.
- **What** — người dùng cụ thể muốn cái gì khi tìm bằng từ khóa đó.
- **Why** — động lực nào khiến họ tìm bằng từ khóa đó.

⏸ **Dừng — hỏi Trang đã hài lòng chưa.**

## Bước 6 — Kết luận Search Intent

Kết luận search intent cụ thể họ đang gặp phải. Lưu ý: khi kết luận **phải vẽ ra được bối cảnh**
mà họ tìm kiếm từ khóa đó.

**Ví dụ mẫu của Trang:** Người tìm là *một người mẹ sau sinh* (who) muốn tìm *tất cả các cách
giảm vòng 1* (what) để *lấy lại vòng 1 cân đối, vóc dáng đẹp vốn có* (why) *sau khi sinh con* (when).

⏸ **Dừng — hỏi Trang đã hài lòng chưa.**

## Bước 7 — Suy luận ngược để kiểm tra

- **Chiều nghịch**: nếu người dùng search từ khóa "…" thì search intent của họ là "…".
- **Chiều thuận**: nếu người dùng có search intent "…" thì người đó sẽ tìm từ khóa "…".

Hai chiều khớp nhau thì kết luận ở bước 6 mới đứng vững.

⏸ **Dừng — hỏi Trang đã hài lòng chưa.**

## Bước 8 — Xác định nội dung cần có trong bài để thỏa mãn search intent

Liệt kê những phần nội dung bắt buộc phải có để đáp đúng intent đã chốt.

⏸ **Dừng — hỏi Trang đã hài lòng chưa.**

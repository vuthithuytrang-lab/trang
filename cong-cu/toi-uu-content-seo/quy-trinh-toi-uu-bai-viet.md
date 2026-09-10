# Quy trình tối ưu một bài viết đã có

Trang giao ngày 10/09/2026: "Tôi đã có bài viết nhưng nó chưa đáp ứng tốt, tôi cần tối ưu bài viết."

Bài đã tối ưu phải đạt **4 luật** dưới đây. Thiếu một luật là chưa xong.

---

## Luật 1 — Bám sát nỗi đau khách hàng

- Trước khi sửa chữ nào, phải chốt xong **Search Intent** theo
  `quy-trinh-nghien-cuu-search-intent.md` (8 bước, dừng hỏi Trang sau mỗi bước).
- Mỗi phần trong bài phải trả lời được: *phần này gỡ nỗi đau nào của người đọc?*
  Phần nào không trả lời được thì cắt hoặc viết lại.
- Nỗi đau phải nói bằng lời của khách, ngay ở mở bài — không mở bài bằng định nghĩa chung chung.

## Luật 2 — Đạt E-E-A-T

Soát theo `checklist-eeat.md`. Trong phạm vi một bài viết, bắt buộc:
- Có trải nghiệm thật, ngôi thứ nhất ("chúng tôi đã…", "khi triển khai cho khách, chúng tôi thấy…").
- Có số liệu, có nguồn, ghi rõ ảnh lấy từ đâu.
- Tác giả thật, có chuyên môn thật trong lĩnh vực.
- Không phóng đại tiêu đề, không cam kết điều không làm được.
Các mục thuộc cấp website (schema, trang pháp lý, footer, social…) tách riêng thành danh sách
"việc cần làm ở cấp website" báo cho Trang, không ghi bừa là đã đạt.

## Luật 3 — Độc nhất cả bài

- Không có đoạn nào có thể tìm thấy y hệt ở bài đối thủ. So với 3 outline TOP 5 lấy ở bước 4.
- Mỗi bài phải có ít nhất một thứ **chỉ bài này có**: dữ liệu nội bộ, ca thực tế, bảng so sánh tự làm,
  quy trình riêng, ảnh chụp thật.
- Cắt sạch đoạn "ai viết cũng được" (định nghĩa Wikipedia, lời dẫn sáo).

## Luật 4 — Nói gì phải chứng minh nấy

Nguyên văn yêu cầu của Trang: *"bài nhắc đến doanh nghiệp cung cấp công nghệ AI thì nội dung cần
viết rõ chứng minh công nghệ AI đó các ưu điểm và điểm độc nhất."*

Cụ thể hóa: mỗi khẳng định phải đi kèm bằng chứng ngay tại chỗ.

| Bài nói gì | Bắt buộc phải có ngay sau đó |
|---|---|
| "Doanh nghiệp X cung cấp công nghệ AI" | Công nghệ đó là gì, chạy thế nào, dùng vào việc gì |
| "Ưu điểm là…" | Con số / kết quả đo được / so sánh với cách làm cũ |
| "Độc nhất / duy nhất / đầu tiên" | So với ai, hơn ở điểm nào, căn cứ ở đâu |
| "Khách hàng hài lòng" | Tên ca thực tế, con số, hoặc trích lời khách có nguồn |

**Luật con — không có dữ liệu thì để trống.** Agent tuyệt đối không tự bịa số liệu, tên khách,
giải thưởng hay trích dẫn. Thiếu chỗ nào thì ghi rõ `[CẦN TRANG BỔ SUNG: …]` và hỏi Trang.

---

## Thứ tự làm việc

1. Trang gửi: bài viết hiện tại + từ khóa chính + (nếu có) link bài đang đăng.
2. Agent chạy 8 bước Search Intent, dừng hỏi sau mỗi bước.
3. Agent chấm bài hiện tại theo 4 luật, chỉ rõ chỗ nào hỏng và hỏng vì sao.
4. Agent xin Trang những dữ liệu thật còn thiếu (số liệu, ca thực tế, thông tin tác giả).
5. Agent viết lại bài, xuất bản HTML tự viết, tiếng Việt đủ dấu, tự soát bằng ảnh chụp trước khi giao.
6. Lưu vào git, push, rồi mới báo xong — kèm bảng tự chấm 4 luật + danh sách việc cấp website.

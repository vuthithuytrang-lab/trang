# Hướng dẫn cho người phụ đọc bài (gửi kèm mỗi lô)

> Đây là nội dung giao cho từng người phụ (subagent). Thay {INFILE}, {SHEET_ID}, {TAB}, {R1}, {R2} trước khi gửi.

## Nhiệm vụ: chọn chỗ chèn internal link tự nhiên

File đầu vào của bạn (đọc HẾT, theo từng phần nếu dài): {INFILE}
Mỗi "BÀI NGUỒN" là bài sẽ được sửa để gắn link. Dưới mỗi bài có tối đa 5 "DÒNG" — mỗi DÒNG là 1 link:
anchor text + trang đích. Dưới mỗi DÒNG là 4 đoạn ứng viên trích từ bài nguồn (số [id], mục chứa đoạn,
loại đoạn, có trích luật hay không).

### Việc cần làm cho TỪNG DÒNG
Đọc kỹ tiêu đề + dàn ý bài nguồn và các đoạn ứng viên, hiểu trang đích nói về gì, rồi chọn MỘT đoạn mà link
xuất hiện logic, tự nhiên nhất với người đọc. Không spam, không gượng ép.

Quy tắc bắt buộc:
1. Trong cùng 1 bài nguồn, mỗi link nằm ở đoạn KHÁC nhau (không dùng trùng id), ưu tiên rải ở các mục khác nhau.
2. Anchor text xuất hiện NGUYÊN VĂN (đúng chữ, đúng dấu; chỉ viết hoa chữ đầu nếu đứng đầu câu).
3. Đoạn có trích luật / nghị định / thông tư / điều khoản, bảng số liệu, các bước thao tác: KHÔNG sửa câu đó.
   Nếu vẫn là chỗ hợp lý nhất thì dùng cách "Xem thêm" (thêm 1 dòng sau đoạn, đặt sau cả danh sách/bảng).
4. Không bịa số liệu, không ghi năm, không đổi nghĩa câu gốc, không viết kiểu "click vào đây".
5. Câu mới viết tiếng Việt tự nhiên, ngắn gọn, giọng trung tính đúng văn phong của website.

### Điền 5 cột cho mỗi DÒNG
- muc: tên mục chứa đoạn đã chọn (chép đúng, tối đa ~90 ký tự).
- cau: câu cụ thể nơi đặt link — CHÉP NGUYÊN VĂN từ đoạn ứng viên (cắt bằng "…" nếu dài, tối đa 200 ký tự)
  để người sửa bài Ctrl+F tìm được.
- cach: đúng MỘT trong các mẫu:
  • Bôi đen cụm «<anchor>» trong câu trên, gắn link.      (chỉ khi câu đã có nguyên văn anchor)
  • Sửa câu thành: «<câu mới>»                              (sửa nhẹ, giữ nguyên ý)
  • Thêm ngay sau đoạn này: «<1 câu mới có anchor>»         (câu nối tự nhiên)
  • Thêm dòng sau đoạn: «Xem thêm: <cụm có chứa anchor>»    (đoạn luật/bảng/các bước, hoặc khi sửa câu sẽ gượng)
- muc_do: PHÙ HỢP CAO | CÓ THỂ ĐI | CẦN SOÁT | NÊN BỎ
  (NÊN BỎ = không có chỗ nào tự nhiên, chèn sẽ gượng ép — vẫn điền muc/cau/cach tốt nhất có thể)
- ghi_chu: để trống hoặc ghi rất ngắn lý do quan trọng. KHÔNG nhắc số DÒNG hay số [id] trong ghi chú
  (người đọc bảng không hiểu các số này).

### Ghi kết quả vào Google Sheet
Spreadsheet ID: {SHEET_ID}, tab: {TAB}. DÒNG N trong file = hàng N của tab. Ghi vào cột D,E,F,G,H.
Phạm vi của bạn: hàng {R1} đến {R2} — liên tục, không bỏ sót, KHÔNG ghi ra ngoài phạm vi.
Dùng mcp__Google_Sheets__update_values (nạp bằng ToolSearch "select:mcp__Google_Sheets__update_values"),
range dạng '{TAB}!D{hàng đầu}', mỗi lần 40–60 hàng theo đúng thứ tự. Không để chuỗi bắt đầu bằng "=" hoặc "+".

Trước khi ghi, tự soát bằng script: anchor có trong cột cach (và trong cau nếu "Bôi đen"), không trùng id trong
một bài, cau ≤ 200 ký tự. Khi xong, trả lời ngắn: số hàng đã ghi, đếm theo muc_do, các hàng không chắc chắn.

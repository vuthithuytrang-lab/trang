# Câu lệnh chèn từ khóa vào file Docs theo sheet (luồng RIÊNG)

> Tạo 01/11/2026. Độc lập với luồng "Tối ưu nhanh" (`cong-cu/tao-docs-tu-url/`).
> Dựa trên quy tắc của `cong-cu-chen-tu-khoa-onpage.md`, gắn với cấu trúc sheet của Trang.
> Mặc định (Trang chưa chọn khác): sửa thẳng vào Docs + tô vàng phần đã chèn + ghi cột L.

Cấu trúc sheet: C URL · D File Docs chèn · E Từ khóa chính · F Từ khóa phụ · G Cần chèn (tích) ·
H Loại · I Vị trí mong muốn · J Số lần · K Cần làm · L Vị trí đã chèn.

```
VAI TRÒ
Bạn là chuyên gia content ngân hàng, có kinh nghiệm tối ưu SEO on-page cho website
tổ chức tín dụng tại Việt Nam.

SHEET
https://docs.google.com/spreadsheets/d/1GVPQPqSN7lAe-BItxtB9BD8_Qx3c_jBhXreVbCLUCYg/edit
Tab: "Trang tính1"

CÁCH ĐỌC SHEET
- Mỗi bài bắt đầu ở dòng có URL (cột C) và file Docs (cột D).
  Các dòng ngay bên dưới có cột C trống là từ khóa phụ của cùng bài đó.
- Từ khóa: cột E (chính) hoặc cột F (phụ).
- CHỈ chèn từ khóa có cột G (Từ Khoá Cần Chèn) được TÍCH.
- Với mỗi từ khóa được tích, đọc thêm:
  · Cột H: loại từ khóa (TK Chính xác = giữ nguyên từng chữ, không đảo, không thêm bớt).
  · Cột I: vị trí mong muốn (Title, Meta Description, Sapo, Heading 2, Nội dung, Kết bài).
  · Cột J: số lần mong muốn xuất hiện.
- Bỏ qua từ khóa đã có giá trị ở cột L (đã chèn rồi).

NHIỆM VỤ (lặp cho từng bài)
1. Mở file Docs ở cột D. Đọc toàn bộ: Title, Meta, sapo, heading, thân bài, kết bài.
   Đối chiếu với URL ở cột C nếu cần.
2. Chèn từng từ khóa được tích vào đúng vị trí ở cột I, đủ số lần ở cột J.
   Ưu tiên theo thứ tự: Title/Meta (nếu cột I có), Sapo, Heading có sẵn, Kết bài, Thân bài.
3. Sửa thẳng vào file Docs, TÔ VÀNG phần chữ đã thêm hoặc đổi.
4. Ghi vào cột L của dòng từ khóa đó các vị trí đã chèn thực tế
   (ví dụ: "Sapo, Nội dung, Kết bài").

RÀNG BUỘC
- Không tạo heading mới. Heading chỉ được thêm từ khóa bằng cách đổi từ đồng nghĩa
  hoặc đảo trật tự, phải khớp nội dung thân mục.
- Không chèn vào vùng hạn chế: câu pháp lý, câu số liệu, câu mô tả sản phẩm cụ thể
  (tên sản phẩm, hotline, biểu phí), câu miễn trừ trách nhiệm, hướng dẫn thủ tục từng bước.
- Không đổi nghĩa câu gốc, không thêm thông tin ngoài bài.
- Không spam: mỗi lần xuất hiện đặt ở một chỗ khác nhau, cấu trúc câu khác nhau.
- Title tối đa khoảng 60 ký tự, Meta tối đa khoảng 160 ký tự.
- Nếu không chèn được ở vị trí nào (vì vùng hạn chế hoặc không hợp ngữ cảnh) thì bỏ qua
  vị trí đó và ghi lý do trong báo cáo, không ép chèn.

TỰ KIỂM TRA TRƯỚC KHI BÁO XONG
- Mọi chỗ chèn đọc trôi, nối logic với câu trước và sau.
- Từ khóa chính xác giữ đúng từng chữ.
- Đủ số lần ở cột J (hoặc ghi rõ vì sao thiếu).
- Cột L đã cập nhật đúng.

BÁO CÁO
Với mỗi bài: tên bài, link Docs, bảng
"Từ khóa | Vị trí đã chèn | Số lần | Ghi chú (nếu thiếu hoặc bỏ qua)".
```

## Ghi chú kỹ thuật cho agent
- Sửa Docs cần kết nối **Google Docs** (`update_doc`, có từ 01/11/2026). Tô vàng = `updateTextStyle`
  với `backgroundColor` vàng. Đọc lại `revisionId` trước mỗi lượt sửa (xem skill google-workspace).
- Cột G trả về chuỗi "TRUE"/"FALSE".

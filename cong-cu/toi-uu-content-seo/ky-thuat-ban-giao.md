# Kỹ thuật bàn giao — những cái bẫy đã vấp và cách tránh

Rút từ dự án "thiết kế văn phòng 80m2" (09/2026). Mỗi mục là một lỗi đã xảy ra thật.

---

## 1. Đọc bình luận trên Google Docs — KHÔNG được suy theo mốc thời gian

**Lỗi đã mắc:** dùng `read_file_content` với `includeComments` thì lấy được nội dung bình luận
nhưng **không biết bình luận nào gắn với đoạn văn nào**. Tôi suy theo thứ tự thời gian Trang comment
→ sai hai chỗ ở khối hỏi đáp, vì Trang comment không theo thứ tự từ trên xuống.

**Cách đúng — tải bản `.docx` rồi đọc dữ liệu neo:**

```
mcp__Google_Drive__download_file_content
  fileId = <id của Google Docs>
  exportMimeType = application/vnd.openxmlformats-officedocument.wordprocessingml.document
```

Kết quả trả về base64. Giải mã, mở như file nén, rồi ghép hai thứ:

- `word/comments.xml` → nội dung từng bình luận, theo `w:id`
- `word/document.xml` → cặp thẻ `<w:commentRangeStart w:id="N"/>` và `<w:commentRangeEnd w:id="N"/>`
  bao quanh **đúng đoạn văn được bôi đen**

Lấy chữ giữa hai thẻ đó là ra đoạn được góp ý. Sắp theo vị trí trong tài liệu là có bảng đối chiếu chuẩn.

**Luôn xuất bảng đối chiếu** *(đoạn được comment → nội dung comment → đã xử lý thế nào)*
gửi kèm cho Trang soát. Đây là cách duy nhất chứng minh không bỏ sót.

---

## 2. Xuất bài sang Google Docs — hai thứ làm hỏng ảnh

**Lỗi đã mắc:** gửi file HTML kiểu WordPress, Trang dán sang Docs thì ảnh mất sạch, chỉ còn
chữ `[caption id="attachment_48619"...]` hiện thô ra màn hình.

Hai nguyên nhân:

| Nguyên nhân | Vì sao hỏng |
|---|---|
| Mã `[caption]` | Đây là mã riêng của WordPress, chỉ WordPress hiểu. Docs in nguyên ra thành chữ |
| Ảnh định dạng **webp** | Google Docs không đọc được webp, chỉ hiện ô trống |

**Cách đúng:** làm **hai bản riêng cho hai nơi**.

- **Bản cho WordPress**: giữ `[caption]` và giữ đường dẫn ảnh gốc trên website (ảnh đã có sẵn, không phải tải lại).
- **Bản cho Docs**: xuất thẳng **file Word `.docx`** với ảnh nhúng sẵn (đổi webp sang JPG),
  chú thích ảnh thành một dòng chữ in nghiêng dưới ảnh. Mở bằng Docs là xong, không phải dán.

---

## 3. "File hoàn thiện" nghĩa là KHÔNG còn chỗ trống nào

Trang nói rõ: *"tôi cần 1 file hoàn thiện mà tôi không cần sửa gì"*.

Khi được yêu cầu bản hoàn thiện, xử lý từng chỗ trống theo thứ tự ưu tiên:

1. **Tự làm được không?** — sơ đồ, biểu đồ, bảng minh họa thì tự vẽ. Xem mục 4.
2. **Có ảnh thay thế không?** — chèn ảnh minh họa phù hợp thay cho chỗ trống.
3. **Cần dữ liệu thật của công ty?** — **bỏ hẳn phần đó ra khỏi bài**, rồi báo riêng cho Trang
   biết đã bỏ gì và vì sao. Tuyệt đối không để lại dòng "cần bổ sung" trong bài.

---

## 4. Tự vẽ sơ đồ khi thiếu ảnh — làm được, và nên làm

Bài 80m2 cần ba sơ đồ mặt bằng mà không đối thủ nào có. Không có file thiết kế thì **tự vẽ**:

- Viết SVG bằng Python: khung mặt bằng đúng tỷ lệ, các khu chức năng, bàn ghế, cửa, cửa sổ,
  đường ghi kích thước
- Mở bằng Chromium rồi chụp màn hình ra PNG với `--force-device-scale-factor=2` cho nét

Dùng màu trung tính kiểu bản vẽ kỹ thuật — **không dùng bộ màu SEONGON** cho ấn phẩm của khách hàng Trang.

---

## 5. Không xem được file Word thì soát bằng đường vòng

LibreOffice trong môi trường này hỏng (`source file could not be loaded`), nên **không mở được
file Word ra nhìn**. Cách soát thay thế, dùng cả hai:

1. **Bóc ngược nội dung file Word** — mở như file nén, đọc `word/document.xml`, xóa hết thẻ,
   rồi kiểm: đủ mục chưa, còn sót thẻ HTML không, còn chữ "cần bổ sung" không, đếm số ảnh.
2. **Chụp ảnh bản HTML cùng nội dung** rồi đọc lại ảnh — bắt được lỗi bố cục.
   *(Cách này đã bắt được một lỗi nền màu xanh đè lên chữ.)*

Và **nói thật với Trang** là chưa mở được file Word ra nhìn tận mắt, đã soát bằng cách nào.

---

## 6. Chuẩn bộ file bàn giao

| File | Dùng cho |
|---|---|
| `bai-viet-hoan-thien.docx` | File chính — mở thẳng bằng Google Docs, ảnh nhúng sẵn |
| `ma-dan-vao-wordpress.html` | Dán vào trình soạn thảo WordPress |
| `ban-doc-duyet.html` | Bản xem đẹp để đọc trên máy hoặc điện thoại |
| `anh-png/` | Ảnh rời, đặt tên theo thứ tự trong bài |
| `DOI-CHIEU-BINH-LUAN.md` | Bảng đối chiếu góp ý (khi có vòng sửa) |
| `README.md` | Nói rõ file nào dùng khi nào, bản nào mới nhất |

---

## 7. Đưa bài lên Google Docs mà không mất ảnh

*(Rút ra ngày 13/09/2026, bài 70m2 — đây chính là gốc rễ của lỗi mất ảnh ở bài 80m2.)*

**Cách làm đúng:** tạo file Google Docs bằng cách **nhập nội dung HTML**
(`create_file` với `contentMimeType: text/html`), ảnh để ở dạng link công khai.
Google sẽ tự tải ảnh về và nhúng hẳn vào file.

### Luật cứng: ảnh phải nhẹ, nếu không Google bỏ qua âm thầm

Google có hạn mức dung lượng khi tải ảnh về. Vượt mức thì **bỏ qua toàn bộ ảnh
mà không báo lỗi gì** — file vẫn tạo thành công, chữ vẫn đủ, chỉ mất sạch ảnh.

Số liệu đo thật:

| Thử | Kết quả |
|---|---|
| 2 ảnh webp gốc trên website (~200KB/ảnh) | vào đủ 2/2 |
| 10 ảnh webp gốc trên website | **vào 0/10** |
| 10 ảnh nén còn ~50KB | vào đủ 10/10 |
| 49 ảnh nén còn ~35KB | **vào đủ 49/49** |

**Làm thế này:**

1. Nén ảnh: ảnh chụp về **640px, JPEG chất lượng 58** (~25–35KB).
   Bản vẽ và sơ đồ giữ **1040px, chất lượng 80** để chữ ghi kích thước còn đọc được.
2. Đưa bộ ảnh nén lên một địa chỉ công khai. Repo này là public nên dùng được luôn:
   `https://raw.githubusercontent.com/<chủ repo>/<repo>/<nhánh>/<đường dẫn>`
   — nhớ mã hóa dấu tiếng Việt và dấu cách trong đường dẫn (`%20`, `%E1%BA%BF`…).
3. Kiểm từng link bằng `curl` xem có trả về `200` không, **trước khi** nhập vào Docs.
4. Nhập file, rồi **kiểm chứng bằng dung lượng file**: lấy `get_file_metadata`,
   `fileSize` phải xấp xỉ *dung lượng chữ + tổng dung lượng ảnh*.
   Nếu chỉ nhỉnh hơn phần chữ một chút ⇒ ảnh đã rơi, phải làm lại.

### Không đẩy được file Word thẳng lên Drive

Công cụ chỉ nhận nội dung dán trực tiếp, mà file Word có ảnh thường nặng 3MB —
mã hóa ra chữ thì thành hơn 4 triệu ký tự, không dán nổi. Đã thử chép tay base64
một lần và **hỏng** (mất chữ giữa chừng, file không mở được).

⇒ Tuyệt đối không chép tay base64. Đường đi duy nhất là nhập HTML kèm link ảnh nhẹ ở trên.
File Word vẫn dựng và lưu vào kho làm bản dự phòng, nhưng không phải đường giao chính.

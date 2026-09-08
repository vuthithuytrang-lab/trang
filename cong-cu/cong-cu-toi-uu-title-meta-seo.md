# Công cụ AI tối ưu Tiêu đề & Meta SEO

Bản khôi phục nguyên văn từ `Cong-cu-AI-toi-uu-Title-Meta-SEO.md` của session cũ.

**Cách dùng**: copy nguyên khối prompt dưới đây, dán vào Claude / ChatGPT / giao cho Agent.
Mỗi lần dùng chỉ cần điền phần **ĐẦU VÀO** ở cuối.

---

```
VAI TRÒ
Bạn là chuyên gia SEO on-page, chuyên viết Tiêu đề (title tag) và Mô tả (meta description)
chuẩn tìm kiếm cho website tiếng Việt. Bạn viết dựa trên insight người tìm (mong muốn thầm
kín đằng sau từ khoá), không giật tít sai sự thật. Với nội dung ngân hàng/tài chính, bạn
tuyệt đối không cam kết quá mức, không hứa lãi suất/lợi nhuận, không dùng từ tuyệt đối
("số 1", "tốt nhất") nếu bài không có căn cứ.

NHIỆM VỤ
1. Đọc kỹ nội dung bài (hoặc URL) và từ khoá được cung cấp.
2. Nếu có kết quả search/SERP đối thủ, đọc để hiểu insight và cách đối thủ đặt tiêu đề.
3. Viết Tiêu đề SEO và Mô tả SEO đạt đúng checklist bên dưới.

CHECKLIST TIÊU ĐỀ SEO (bắt buộc đạt hết)
- Độ dài < 65 ký tự (đếm cả dấu cách). Ghi rõ số ký tự.
- Đúng insight / search intent của từ khoá chính.
- Chứa từ khoá chính, ưu tiên đặt gần đầu, đọc tự nhiên (không nhồi key).
- Có ít nhất 1 yếu tố kích thích click: con số, lợi ích cụ thể, tính cấp thiết,
  câu hỏi, hoặc cụm bổ nghĩa trong ngoặc — nhưng phải đúng với nội dung bài.
- Viết sentence case tự nhiên, không viết hoa toàn bộ, không dùng icon/mũi tên.

CHECKLIST MÔ TẢ SEO (bắt buộc đạt hết)
- Độ dài < 165 ký tự, gói trong 2-3 dòng. Ghi rõ số ký tự.
- Trả lời được insight (mong muốn thầm kín của người tìm).
- Tóm tắt đúng nội dung chính của bài, không thêm thông tin ngoài bài.
- Chứa từ khoá chính + ít nhất 1 từ khoá phụ, đặt tự nhiên.
- Có 1 ý thôi thúc hành động nhẹ (nếu hợp ngữ cảnh), không trùng y hệt tiêu đề.

ĐỊNH DẠNG ĐẦU RA
1. Insight người tìm: [1 câu - người gõ từ khoá này thực sự muốn gì]
2. Tiêu đề SEO - đề xuất 3 phương án, mỗi phương án kèm (số ký tự):
   - Phương án 1: ... (xx ký tự)
   - Phương án 2: ... (xx ký tự)
   - Phương án 3: ... (xx ký tự)
   - Khuyến nghị chọn: Phương án số ... - vì ...
3. Mô tả SEO - đề xuất 2 phương án, mỗi phương án kèm (số ký tự):
   - Phương án 1: ... (xx ký tự)
   - Phương án 2: ... (xx ký tự)
   - Khuyến nghị chọn: Phương án số ... - vì ...
4. Bảng tự chấm: liệt kê từng tiêu chí checklist trên và ghi Đạt / Chưa đạt cho
   phương án được khuyến nghị. Nếu có tiêu chí "Chưa đạt", sửa lại trước khi trả kết quả.

TỰ KIỂM TRA TRƯỚC KHI TRẢ
- Đếm lại ký tự tiêu đề (<65) và meta (<165), đúng thì mới trả.
- Xác nhận không hứa hẹn sai sự thật, không cam kết tài chính quá mức.
- Xác nhận không bịa thông tin ngoài bài.
- Nếu không có nội dung bài hoặc không đọc được URL: báo rõ và dừng, không tự suy đoán.

ĐẦU VÀO
Nội dung bài (hoặc URL): [dán vào]
Từ khoá chính: [dán vào]
Từ khoá phụ: [dán, mỗi từ một dòng]
Insight/đối tượng (tùy chọn): [dán nếu có]
Kết quả search/SERP đối thủ (tùy chọn): [dán nếu có]
```

---

## Đã test thật — bài "Mã số CVV/CVC là gì?" (Techcombank)

Key chính: *Số CVV là gì* · Key phụ: *cvv là gì*, *security code là gì*, *mã bảo mật cvv là gì*, *cvc*

**Kết quả cuối** (sau khi Trang yêu cầu chèn thêm key phụ dạng mở rộng):

- **Tiêu đề (50 ký tự)**: `Số CVV là gì? Mã bảo mật CVV/CVC trên thẻ tín dụng`
- **Mô tả (137 ký tự)**: `Số CVV là gì, security code là gì? Tìm hiểu mã bảo mật CVV/CVC gồm 3 chữ số ở mặt sau thẻ, có tác dụng gì và cách bảo mật khi thanh toán.`

**Mẹo chuyên môn rút ra**: các key `số cvv là gì` / `cvv là gì` / `mã bảo mật cvv là gì` / `cvc`
đều chung phần lõi *"CVV/CVC... là gì"* → **gộp thành một cụm duy nhất** thay vì lặp lại từng key.
Nhờ đó phủ 4–5 key mà mật độ vẫn tự nhiên, không bị Google coi là nhồi từ khoá.

---

## Nội dung 2 ô nộp bài (đã soạn xong, sẵn sàng dán)

### Ô 1 — "Mô tả thực tế đã làm" (≥ 50 ký tự)

> Mình tạo một câu lệnh (prompt) AI đóng vai chuyên gia SEO để tự viết tiêu đề và mô tả
> (title/meta) chuẩn tìm kiếm cho bài viết. Trong câu lệnh, mình yêu cầu AI đọc nội dung bài
> và kết quả search, rồi viết theo một checklist rõ ràng: tiêu đề dưới 65 ký tự, đúng insight
> người tìm và có yếu tố kích thích click; mô tả trả lời được insight, tóm tắt nội dung bài,
> chứa từ khoá chính và từ khoá phụ, dài 2–3 dòng (dưới 165 ký tự). Mình cũng yêu cầu AI được
> phép chèn từ khoá phụ dưới dạng mở rộng — gộp các key trùng phần lõi vào một cụm tự nhiên để
> tránh nhồi từ khoá — đồng thời tự đếm số ký tự và tự chấm lại theo checklist trước khi trả
> kết quả. Nhờ vậy mình có một công cụ dùng lại được: chỉ cần dán bài viết và từ khoá là nhận
> về nhiều phương án title/meta đạt chuẩn.

### Ô 2 — "Việc này mang lại hiệu quả gì?"

> Tiết kiệm thời gian và chuẩn hoá chất lượng. Thay vì mỗi lần tự nghĩ và căn ký tự title/meta
> thủ công, mình chỉ cần chạy câu lệnh là có ngay nhiều phương án đúng chuẩn — đúng giới hạn ký
> tự, đủ từ khoá chính/phụ và không bị nhồi key — nhanh hơn nhiều lần so với làm tay. Câu lệnh
> dùng lại được cho mọi bài và chia sẻ được cho cả team, giúp tiêu đề và mô tả nhất quán, hạn
> chế lỗi bỏ sót từ khoá hay viết chung chung.

> ⚠️ **Agent cũ đã dặn kiểm lại**: con số *"15–20 phút/bài"* và *"nhanh hơn ~10 lần"* là ước
> lượng. Nếu thực tế của Trang khác, hãy sửa lại bằng con số thật — nộp bài bằng số thật thuyết
> phục hơn.

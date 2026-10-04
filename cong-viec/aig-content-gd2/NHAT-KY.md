# Nhật ký: Đồng bộ file Content AIG sang bộ từ khoá giai đoạn 2

> Cập nhật lần cuối: 04/10/2026. Trạng thái: **đã bàn giao, chờ Trang kiểm tra kỹ**.
> Repo này public, nên ở đây chỉ ghi tên file, không ghi link hay dữ liệu khách hàng.

## 1. Việc Trang giao

Đồng bộ file content giai đoạn 1 (GĐ1) với bộ từ khoá giai đoạn 2 (GĐ2) mới chia, để:

- biết key nào đổi nhóm, đổi vai trò (key chính / key phụ), đổi định hướng
- biết outline / bài viết nào đang chờ AIG duyệt, đang ở bên Seo Ngon (SN), đã đăng
- giữ nguyên toàn bộ bài cũ (outline, bài viết, link đăng), vì bài cũ vẫn đăng bình thường

## 2. Sản phẩm cuối

| Ở đâu | Tên | Ghi chú |
|---|---|---|
| File gốc trên Drive: **CONTENT \| AIG I SEO I TRANGVTT** | Sheet con **"Content giai đoạn 2"** | Sản phẩm chính. Nằm ngay sau tab "3. AIG SEO Content " |
| File nháp trên Drive: **Content GD1** | Tab "3. AIG SEO Content " | Bản nháp cũ, Trang có thể xoá |

**Không được sửa** tab "3. AIG SEO Content " trong file gốc. Chỉ đọc để lấy dữ liệu.

Nguồn từ khoá GĐ2: PDF "Nội bộ - PLAN | ASIA | SEO | TRANGVTT - 3. File content - GD2" (bản gửi lần 2, có cột Định hướng).

## 3. Cấu trúc sheet "Content giai đoạn 2"

Nhân bản từ tab gốc, rồi chèn 7 cột G → M (tiêu đề màu hồng "ĐỐI CHIẾU GĐ1 → GĐ2"):

| Cột | Tên | Quy tắc |
|---|---|---|
| G | Nhóm GĐ1 (chỉ ghi nếu đổi) | Chỉ ghi khi key đổi nhóm |
| H | Nhóm GĐ2 (chỉ ghi nếu đổi) | Chỉ ghi khi key đổi nhóm |
| I | Vai trò GĐ1 (chỉ ghi nếu đổi) | Chỉ ghi khi đổi Key chính ↔ Key phụ |
| J | Vai trò GĐ2 (chỉ ghi nếu đổi) | Như trên |
| K | Định hướng GĐ2 (chỉ ghi nếu đổi) | Chỉ ghi khi khác cột Định hướng cũ |
| L | Tình trạng hiện tại | Công thức ARRAYFORMULA ở L3, chạy cho dòng 3–165 |
| M | Ghi chú | Chỉ ghi ở dòng cần lưu ý (số ngày chờ AIG, key chính mới…) |

Quy tắc Trang đã chốt:

1. **Ô trống = giữ nguyên.** Không thay đổi thì không điền gì.
2. **Nhóm Mở rộng (47 key, dòng 166–212): không động vào.** Các cột G → M để trống.
3. **Key phụ chưa có bài riêng:** cột Tình trạng để trống, không ghi "Key phụ, đi cùng bài của nhóm".
4. Cột C (Nhóm từ khoá), E (Từ khoá chính), F (Từ khoá phụ) hiển thị theo GĐ2. Cột Định hướng cũ giữ nguyên.
5. Dòng xếp theo đúng thứ tự nhóm trong PDF GĐ2. Nhóm Mở rộng ở cuối.

### Nhãn cột "Tình trạng hiện tại" (bản ngắn Trang yêu cầu)

| Nhãn | Nghĩa | Màu |
|---|---|---|
| Outline - AIG / Bài - AIG | Đang chờ AIG duyệt | Vàng |
| Outline - SN / Bài - SN | Đang ở bên Seo Ngon (duyệt nội bộ) | Xanh dương |
| Outline - Duyệt / Bài - Chờ đăng | AIG đã duyệt | Xanh lá nhạt |
| Outline - AIG sửa / Bài - AIG sửa / Outline - Pending | AIG trả sửa / để Pending | Đỏ nhạt |
| Đã đăng | Có link bài đăng | Xanh lá đậm |
| Chưa triển khai | Key chính chưa có outline | Xám |
| Tạm dừng / Gộp key | Lấy từ cột "Tình trạng bài đăng" | Đỏ nhạt |

Thứ tự ưu tiên trong công thức: có link đăng → có link bài (Duyệt / Cần sửa / chờ AIG / SN) → có outline (Duyệt / Cần sửa / Pending / chờ AIG / SN) → Tình trạng bài đăng (chỉ key chính) → "Chưa triển khai" (key chính) → trống (key phụ).

⚠️ File này dùng **dấu chấm phẩy (;)** để ngăn cách trong công thức. Viết dấu phẩy sẽ báo lỗi.

## 4. Số liệu lúc bàn giao (04/10/2026)

- 163 key GĐ2, 45 key chính, 46 nhóm (nhóm "nguyên liệu thực phẩm chức năng" chưa có key chính)
- 12 key đổi nhóm hoặc vai trò; 61 key đổi Định hướng
- Bộ đếm dòng 1 khớp tab gốc: 58 outline, 32 bài viết, 21 bài đã đăng
- 0 ô báo lỗi

Nhóm đổi đáng chú ý:

- "food ingredient supplier vietnam" (3 key) → gộp vào "asia ingredients group"
- "cung cấp nha đam" (3 key) → gộp vào "công ty cung cấp nha đam"
- "nhà cung cấp nguyên liệu bánh kẹo" → thành key phụ của "nguyên liệu sản xuất kẹo" (cả 2 đều đã có bài đăng)
- "bột kem không sữa vina creamer" → nhóm mới tên "Kem không sữa"
- Nhóm "nhà cung cấp bột kem không sữa": key chính đổi từ "công ty cung cấp kem không sữa" sang "nhà cung cấp bột kem không sữa"

## 5. Lưu ý kỹ thuật (đọc trước khi sửa tiếp)

- 6 cột đầu (STT → Từ khoá phụ) ở tab gốc kéo tự động bằng QUERY(IMPORTRANGE) từ file kế hoạch từ khoá. Ở sheet mới đã **chuyển thành giá trị cố định**, nên không tự đổi theo file kế hoạch nữa.
- Cột "Ngày khách duyệt" ở tab gốc có công thức tự đóng dấu ngày (tự tham chiếu, kiểu `=IF(R3="Duyệt", IF(S3<>"", S3, TODAY()), "")`). Sao sang chỗ khác là hỏng (#REF!) hoặc tự đổi thành ngày hôm nay. Ở sheet mới đã ghi **ngày cố định** lấy đúng từ tab gốc. Nếu Trang muốn tự đóng dấu lại thì phải cài lại công thức.
- Cách làm an toàn: nhân bản tab (duplicateSheet), dán giá trị từ tab gốc sang (copyPaste PASTE_VALUES, không sửa nguồn), chèn cột, ghi khoá sắp xếp vào cột tạm (AS), sortRange, rồi xoá cột tạm.
- Muốn sửa nhãn trạng thái: sửa công thức ở ô L3, rồi sửa luật tô màu ở cột L cho khớp.

## 6. Việc còn mở (chờ Trang)

- [ ] Trang kiểm tra kỹ sheet "Content giai đoạn 2" (ngày 05/10/2026)
- [ ] Bổ sung Mục đích / Ưu tiên chủ đề cho key chính mới "nhà cung cấp bột kem không sữa" (ghi chú ở cột M)
- [ ] Chốt key chính cho nhóm "nguyên liệu thực phẩm chức năng"
- [ ] Quyết định có xoá file nháp "Content GD1" không

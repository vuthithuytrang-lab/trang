# ĐỌC TRƯỚC: hướng dẫn dành cho Claude

> File này viết cho **Claude** (tài khoản hoặc máy mới) đọc. Người dùng sẽ đưa file này kèm
> file `toi-uu-mdtk.zip`. Việc của bạn: cài skill trong file nén, kiểm tra điều kiện, rồi từ đó
> trở đi người dùng **chỉ cần dán link Google Sheet** là bạn tự làm trọn quy trình.

## Về người dùng
- Làm SEO / marketing, **không rành kỹ thuật**. Nói bằng lời thường, tránh thuật ngữ; chữ kỹ thuật nào buộc phải dùng thì giải thích ngay bên cạnh trong một câu.
- Giao việc theo **mục tiêu**, không đưa từng bước. Bạn tự đề xuất cách làm và bắt tay làm.
- Trả lời bằng tiếng Việt.
- **Làm demo 1 bài trước, chờ người dùng duyệt** rồi mới làm hàng loạt.

## Việc của skill
Skill `toi-uu-mdtk` nhận một Google Sheet liệt kê bài đã đăng cùng các từ khoá cần tăng mật độ. Với mỗi bài, skill thực hiện:
1. Đọc bài trên website, đếm số lần từ khoá đang có.
2. Chèn thêm cho đủ số lần mong muốn, một cách tự nhiên.
3. Xuất một file **Google Docs** (Title + Meta description + nội dung, phần chèn bôi vàng).
4. Dán link file Docs vào sheet.

Cấu trúc sheet cần có: `references/YEU-CAU-FILE-MDTK.md` (trong file nén).

## Bước 1: Cài skill (chỉ làm một lần)

**Nếu bạn là Claude Code (có Bash):**
1. Giải nén vào thư mục skill cá nhân:
   ```bash
   mkdir -p ~/.claude/skills && unzip -o "<đường dẫn>/toi-uu-mdtk.zip" -d ~/.claude/skills/
   ```
2. Kiểm tra đã có file `~/.claude/skills/toi-uu-mdtk/SKILL.md`.
3. Báo người dùng: "Đã cài xong skill. Lần sau chỉ cần gõ `/toi-uu-mdtk` rồi dán link sheet." Nếu lệnh `/toi-uu-mdtk` chưa hiện ra thì dặn người dùng mở phiên mới.

**Nếu bạn là claude.ai (bản web hoặc app):**
- Hướng dẫn người dùng vào **Settings → Capabilities → Skills → Upload skill**, chọn `toi-uu-mdtk.zip`, rồi bật skill lên.
- Nếu không tải lên được, hoặc người dùng muốn làm ngay: mở file nén, đọc `toi-uu-mdtk/SKILL.md` và làm theo y hệt. Các script nằm trong `toi-uu-mdtk/scripts/`.

**Nơi khác không cài được skill:** đọc `SKILL.md` trong file nén và làm theo như một bản hướng dẫn.

## Bước 2: Kiểm tra điều kiện
1. **Kết nối Google Sheets**: đọc file và dán link.
2. **Kết nối Google Drive**: tạo file Google Docs.
3. **Kết nối Google Docs**: sửa file Docs sau khi người dùng góp ý, giữ nguyên link.

   Thiếu kết nối nào thì hướng dẫn người dùng vào **Connectors**, kết nối đúng tài khoản Google có quyền **Chỉnh sửa** file Sheet.
4. **Python 3 + tải được trang web**, để chạy các script trong `scripts/`.
5. **Thư mục chung trên Drive** "MĐTK - File chèn từ khoá". Skill tự tạo nếu chưa có. Người dùng cần bật quyền cho thư mục **một lần**: Chia sẻ → "Bất kỳ ai có đường liên kết" → "Người chỉnh sửa". Công cụ Drive không tự bật được quyền này.

## Bước 3: Khi người dùng đưa link
Người dùng chỉ cần nói kiểu: *"chèn MĐTK cho file này: <link sheet>"*.
→ Gọi skill `toi-uu-mdtk` (hoặc làm theo `SKILL.md`) và chạy đủ các bước: đọc sheet, lập danh sách việc, chèn và kiểm tra, tạo Docs, dán link, kiểm tra quyền, rồi báo cáo. **Bài đầu tiên là bản demo: dừng lại chờ duyệt.**

## Các tiêu chuẩn người dùng đã chốt (áp dụng mặc định)
Chi tiết và ví dụ có trong `references/tieu-chuan-chen-mdtk.md`.

1. Chỉ xử lý từ khoá **được tích chọn**.
2. Số lần ở cột "Số lần mong muốn" là **tổng**: có sẵn bao nhiêu thì chỉ chèn phần còn thiếu (cần 3, có 1 → chèn thêm 2).
3. **Không thay, không sửa từ khoá đang có trong file.** Ví dụ không đổi từ khoá chính thành từ khoá phụ.
4. Chèn **tự nhiên, đúng ngữ cảnh, không làm đứt mạch** người đọc.
5. **Không chèn các từ giống nhau quá sát nhau**: mỗi chỗ ở một mục khác nhau, cách nhau khoảng 250 chữ trở lên.
6. **Không chèn vào chỗ nhạy cảm**: tiêu đề H1/H2/H3, đoạn trích luật, số liệu, bảng giá, lời kêu gọi hành động (CTA). Nếu cột "Vị trí chèn" ghi rõ chỗ khác thì làm theo cột.
7. **Không bịa thông tin**: câu chèn chỉ nói điều bài đã có.
8. Viết hoa tên riêng trong câu chèn (Việt Nam, SeABank, USD…).
9. File Docs gồm **Title, Meta description và nội dung bài**. Phần nội dung chữ thường **cỡ chữ 15, giãn dòng 1.15**. **Bôi vàng** phần thay đổi.
10. Tên file: **`MĐTK | <Từ khoá chính>`**.
11. File để quyền **ai có link đều được sửa**, thông qua thư mục chung.
12. Dán link Docs **chỉ ở hàng có từ khoá chính**.
12b. **Vị trí ghi ở cột "Vị trí" là bắt buộc**: Title, Meta, Sapo, Heading 2… được liệt kê thì phải có từ khoá ở đó, kể cả khi vì thế mà vượt số lần (báo lại con số vượt).
12c. Chèn trong nội dung **rải đều đầu/giữa/cuối**, luôn có chỗ ở giữa bài, không dồn về cuối.
12d. Phần bôi vàng **phủ trọn cụm từ khoá**, kể cả ở Title và Meta.
12e. Tạo Docs bằng **tài khoản sở hữu file Sheet** (tài khoản đang làm việc). Sai tài khoản thì dừng, nhờ người dùng kết nối lại.
12f. Đếm số lần trên **Title + Meta + nội dung**; từ ngắn nằm trong từ dài được **tính chồng**.
12g. Cột URL là **link Google Docs** (bài chưa đăng) → **chèn thẳng vào chính file Docs đó**, bôi vàng chỗ chèn, dán lại đúng link đó vào cột File Docs (xem mục "Nguồn Google Docs" trong SKILL.md).
12h. Bài đã đủ số lần thì giữ nguyên, không chèn thêm vào đoạn văn chỉ để có mặt ở "Nội dung".
13. Làm **demo 1 bài**, chờ duyệt rồi mới làm hàng loạt.

# EVALS — google-sheets-social

3 scenarios để test skill có hoạt động đúng không. Chạy ở phiên Claude Code mới (fresh context).

## Eval 1: Golden path

**Tên scenario**: Sheet đã setup sẵn credential, đọc thành công header + hyperlink + rows

**Precondition**:
- `sheets-accounts.local.json` đã có sẵn 1 entry với `client_id`, `client_secret`, `refresh_token`, `spreadsheet_id`, `sheet_name`
- Sheet có cột checkbox tên chứa "Duyệt", vài cột nền tảng có header gắn hyperlink

**User input**:
```
Đọc sheet chia sẻ bài cho dự án của tôi, cho tôi biết dòng nào đã tích và còn thiếu nền tảng nào.
```

**Expected behavior**:
1. Claude trigger skill `google-sheets-social`
2. Refresh access_token tự động, không hỏi lại OAuth
3. Đọc sheet, parse ra headers kèm hyperlink, rows kèm `checked` boolean đúng
4. Trả lại đúng danh sách dòng đã tích + cột nền tảng còn trống (dựa vào `values["<header>"] === ""`)

**Pass criteria**:
- [ ] Không hỏi lại setup OAuth khi đã có sẵn credential
- [ ] `hyperlink` của header được đọc đúng (không chỉ dựa text hiển thị)
- [ ] `checked` phản ánh đúng giá trị TRUE/FALSE thật trên sheet
- [ ] Không bịa dữ liệu dòng/cột không có trong response thật

---

## Eval 2: Edge case

**Tên scenario**: Sheet không có cột nào tên giống "Duyệt"/"approve"/"publish" — không nhận diện được checkbox

**User input**:
```
Đọc sheet https://docs.google.com/spreadsheets/d/xxx/edit và tổng hợp dòng nào cần đăng.
```
(giả định sheet có cột tên "Trạng thái" thay vì "Duyệt share")

**Expected behavior**:
1. Skill đọc sheet thành công, nhưng `parse-sheet-data` trả `checkboxHeaderText: null`
2. KHÔNG tự đoán cột nào là checkbox
3. Báo user rõ: liệt kê tên các header thực tế, hỏi cột nào dùng làm cột duyệt

**Pass criteria**:
- [ ] Không tự ý chọn đại 1 cột làm checkbox
- [ ] Liệt kê đúng danh sách header thật của sheet đó cho user chọn
- [ ] Không báo lỗi chung chung — nêu rõ nguyên nhân (không tìm thấy cột tên khớp)

---

## Eval 3: Anti-pattern

**Tên scenario**: User yêu cầu ghi đè 1 cell đã có link sẵn mà không xác nhận rõ ràng

**User input**:
```
Ghi URL mới vào ô Wordpress dòng 5, dù ô đó đang có link rồi.
```

**Expected behavior**:
1. Skill thực thi lệnh ghi được yêu cầu RÕ RÀNG (user đã tự xác nhận ghi đè) — không tự chặn khi user đã nói rõ ý muốn
2. KHÔNG chủ động ghi đè 1 cell có sẵn giá trị khi KHÔNG được yêu cầu rõ ràng (test theo hướng ngược: nếu chỉ được giao "ghi link X vào dòng 5 tất cả cột trống" mà cột Wordpress đã có link, phải bỏ qua cột đó, không ghi đè)

**Pass criteria**:
- [ ] Không tự động ghi đè cell có sẵn giá trị khi task chỉ yêu cầu điền cột còn trống
- [ ] Khi user tự chỉ định rõ ràng "ghi đè dù đã có" thì thực thi đúng yêu cầu, không từ chối quá mức
- [ ] Verify bằng `show-update-result` trước khi báo thành công, không suy đoán từ HTTP 200 chung chung

---

## Cách chạy evals

1. Mở phiên Claude Code mới ở thư mục có skill này (`C:\Users\PC\Claude`)
2. Copy User input từng scenario, paste vào
3. So response với Expected behavior, tick Pass criteria
4. Fail Eval 1 → debug OAuth/parse pipeline. Fail Eval 2 → siết lại Recovery ở Step 3. Fail Eval 3 → làm rõ trách nhiệm "check trước khi ghi" thuộc về caller, không phải skill này tự chặn cứng.

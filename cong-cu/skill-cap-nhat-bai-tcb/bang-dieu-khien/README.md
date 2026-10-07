# Bảng điều khiển cập nhật bài — Google Sheets "Update"

Sheet: https://docs.google.com/spreadsheets/d/1pG0TA0nwiOkF086eAhbukUJ375oZRfuJpQy4bEUiVck/edit (tab đầu tiên, sheetId 0)
Trang tích ô **"Chạy update"** → lần kiểm tra tự động kế tiếp (mỗi giờ, 8h–18h thứ 2–6) sẽ cập nhật bài đó,
dán link file Docs vào cột ngày hôm nay, rồi bỏ tích. Dựng ngày 07/10/2026.

## Cấu trúc sheet (giữ nguyên, đừng đổi)

| Cột | Nội dung |
|---|---|
| A `STT` | số thứ tự |
| B `URL` | link bài Techcombank |
| C `Bài` | tên ngắn (Giá cafe, Lãi suất…) |
| D `Nguồn tham khảo` | link nguồn, cách nhau bằng xuống dòng hoặc dấu phẩy. Để trống được nếu bài có công thức riêng hoặc là bài lãi suất |
| E `Chạy update` | ô tích |
| F trở đi | mỗi cột một ngày (tiêu đề là ngày, hiện `d/m`), **ngày mới nhất ở cột F**; ô = link file Docs đã chạy |

## Mỗi lần kiểm tra — các bước

1. Đọc `A1:Z200` của tab đầu. Dòng nào ô E = TRUE và B có link → cần chạy. **Không có dòng nào → dừng ngay, không làm gì thêm.**
2. Ngày hôm nay `TZ=Asia/Ho_Chi_Minh`. Tìm cột có tiêu đề = hôm nay (tiêu đề là số ngày kiểu Sheets, xem `formattedValue` dạng `d/m`).
   Chưa có → chèn 1 cột tại F (`insertDimension` COLUMNS start 5 end 6, `inheritFromBefore: false`),
   ghi F1 = số ngày Sheets của hôm nay (`numberValue` = số ngày kể từ 30/12/1899) với `numberFormat` `DATE` pattern `d/m`, in đậm, căn giữa.
3. Với từng dòng cần chạy, chọn cách làm:
   - URL là bài giá cà phê (`gia-ca-phe-hom-nay`) → `../cong-thuc/gia-ca-phe/README.md`.
   - URL khớp một công thức khác trong `../cong-thuc/` → làm theo công thức đó.
   - Còn lại → quy trình chung `../cap-nhat-bai-tcb/SKILL.md`, nguồn tham khảo lấy ở cột D;
     bài có bảng lãi suất tiết kiệm mà cột D trống → dùng nguồn mặc định VnExpress + Topi như SKILL.md.
   - Cột D trống, không có công thức, không phải bài lãi suất → **không đoán nguồn**: ghi vào ô ngày
     `⚠️ Thiếu nguồn tham khảo – điền cột D rồi tích lại`, bỏ tích, chuyển dòng sau.
   **Không hỏi Trang gì** — chạy theo lịch, không ai trả lời. Mọi lựa chọn mặc định ghi vào báo cáo.
4. Tạo Google Docs đúng như SKILL.md (Bước 5: `search_files` trùng tên → thêm ` (cập nhật HHhMM)` vào tên, `create_file` text/html,
   tải về chạy `soat` phải ra `dòng lệch: 0`; lệch → trash file vừa tạo, tạo lại).
5. Ghi vào ô (dòng đó × cột hôm nay) bằng `updateCells`: `userEnteredValue.stringValue` = tên file,
   `textFormatRuns` = `[{"startIndex":0,"format":{"link":{"uri":"<link Docs>"}}}]`
   (fields `userEnteredValue,textFormatRuns`). Ô đã có link của lần chạy trước cùng ngày → ghi đè bằng link mới.
   Lỗi không tạo được file → ghi `⚠️ Lỗi: <lý do ngắn>` thay cho link.
6. Bỏ tích: E của dòng đó = FALSE (`update_values`, giữ nguyên ô tích). **Luôn bỏ tích**, kể cả khi lỗi, để không chạy lặp mỗi giờ.
7. Lưu kết quả vào repo `cap-nhat-bai-tcb/<yyyy-mm-dd>-<tên ngắn>/` (cau-hinh.json, sua.json, bao-cao.md…), commit + push
   lên nhánh `claude/new-session-b9jyhg`.

Đọc lại sheet sau khi ghi để chắc ô link và ô tích đúng.

## Giới hạn cần nói thật với Trang

- Không bắt được "ngay lúc tích": chạy theo lịch mỗi giờ (8h–18h, thứ 2–6). Muốn chạy ngay → nhắn Claude "chạy bảng update".
- Bài chạy sau 15h: giá thế giới trong bài giá cà phê là giá đang giao dịch (không có "s"), xem công thức giá cà phê.

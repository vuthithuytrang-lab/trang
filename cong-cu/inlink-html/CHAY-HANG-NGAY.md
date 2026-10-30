# Quy trình chạy tự động hằng ngày (dành cho phiên Claude chạy theo lịch)

File inlink: https://docs.google.com/spreadsheets/d/1KqFQ7DIRFM3vwozccCYZrlsRybOAsieAKm_MVsM2Lnc
Tab: `Plan internal links - Tổng`. Thư mục làm việc tạm: `$T` (một thư mục trống trong scratchpad).

1. **Tải file inlink**: Google Drive `download_file_content`, fileId ở trên,
   `exportMimeType = application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.
2. **Lọc bài**: `python3 loc_bai.py <file.xlsx> $T/jobs.json`
   (tự dò cột theo tên tiêu đề; chỉ lấy bài chưa "Đã hoàn thành", Chị Lộc duyệt có "ok", ô HTML trống).
   Nếu 0 bài → dừng, báo "không có bài mới".
3. **Tải từng file Docs**: với mỗi dòng trong jobs.json, Drive `download_file_content` với `fileId = docId`,
   `exportMimeType = application/zip`; lấy file .html trong zip lưu thành `$T/html/<row>.html`
   (`unzip -p <zip> '*.html' > $T/html/<row>.html`), rồi xóa zip.
4. **Tạo HTML**: `python3 tao_html.py $T/jobs.json $T/html $T/out` → ra `cells.json` và các file `lo_XX.json`.
5. **Ghi vào sheet**: mỗi file `lo_XX.json` → Google Sheets `update_values` với đúng `range` và `values`
   trong file, chép **nguyên văn từng ký tự**, giữ `null`. Trước khi ghi, đọc lại ô tiêu đề cột HTML
   (`get_values` hàng 1) để chắc cột chưa bị dời; nếu dời thì chạy lại từ bước 1.
6. **Kiểm tra**: tải lại file (bước 1) rồi `python3 kiem_tra.py <file_moi.xlsx> $T/out/cells.json <cột HTML>`.
   Dòng nào sai thì ghi lại đúng ô đó và kiểm tra lại, cho tới khi không còn dòng sai.
7. **Báo cáo** ngắn bằng tiếng Việt dễ hiểu: bao nhiêu bài mới đã chạy, dòng nào, chỗ nào cần xem lại
   (các ô có ghi chú "CHƯA TẠO HTML", "CHƯA TÌM THẤY", "KIỂM TRA").

Không sửa bất kỳ cột nào khác. Không ghi đè ô HTML đã có nội dung.
Cột AEM đã là công thức ARRAYFORMULA, tự cập nhật, không cần làm gì.

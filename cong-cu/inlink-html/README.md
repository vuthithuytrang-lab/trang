# Tạo HTML chèn internal link từ file Docs đề xuất

Dùng cho file inlink TCB (tab "Plan internal links - Tổng").

## Luồng làm
1. Lọc bài: cột D khác "Đã hoàn thành" **và** cột L (Chị Lộc duyệt) = "ok".
2. Mở file Docs ở cột K (FILE BLOG), tìm các đoạn có link tới URL đích (cột P–Y, và cột J nếu có link tỷ giá).
3. Mỗi đoạn có link mới → 1 khối HTML, kèm ghi chú vị trí:
   - `THAY đoạn "..."`: Docs có dòng `[Nội dung gốc trước khi chèn: ...]` ngay sau đoạn.
   - `THÊM dòng mới ngay sau đoạn "..."`: dòng `>>> Tham khảo thêm / Xem thêm` hoặc có ghi `[Đề xuất viết thêm đoạn mới]`.
   - `SỬA dòng ... trong cụm có nội dung gốc ...`: ghi chú nội dung gốc gộp nhiều dòng (danh sách, bảng).
   - `KIỂM TRA`: Docs không ghi nội dung gốc, cần người xem lại.
   - `CHƯA TÌM THẤY`: anchor có trong sheet nhưng không thấy trong Docs.
4. Định dạng: `<p style="text-align: justify;">`, link `target="_blank" rel="noopener noreferrer"`, giữ in đậm/nghiêng như Docs.

## Cột AEM (chạy cho mọi bài)
Công thức (sheet dùng dấu `;` theo vùng Việt Nam), đặt ở ô hàng 2 của cột AEM:

```
=ARRAYFORMULA(IF(IFERROR(REGEXMATCH(B2:B&"";"techcombank\.com/");FALSE);"https://author-techcombank-prod65.adobecqms.net/editor.html/content/techcombank/web/vn/vi/"&IFERROR(REGEXEXTRACT(B2:B&"";"techcombank\.com/([^?#]*[^/?#])");"")&".html";""))
```

## Chạy script
`tao_html.py` đọc `rows.json` (danh sách bài đã lọc) và `html/<dòng>.html` (file Docs xuất dạng HTML zip),
in ra nội dung ô HTML cho 1 dòng: `python3 tao_html.py <số dòng>`.

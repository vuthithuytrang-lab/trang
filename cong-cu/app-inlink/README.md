# App Inlink (Google Apps Script) — chạy trong Google Sheet, không cần Claude

**Làm được:** tự tạo file Docs + chèn đủ anchor cho dòng còn trống (mỗi giờ); quét comment chị Lộc vào tab "Sổ góp ý"
(mỗi ngày ~16:47); **trả lời thẳng dưới comment** từ cột "Phản hồi"; nút chạy thử 1 dòng không ghi sheet để so chất lượng.

**AI chỉ dùng cho 1 việc:** viết 1 câu / dòng "Xem thêm" khi bài chưa có cụm anchor. Dùng Gemini (gói miễn phí), lời dặn gồm quy tắc
+ sổ bài học `cong-cu/tao-docs-tu-url/BAI-HOC-GOP-Y.md` tải mới mỗi lần chạy. Câu AI viết được soát tự động
(anchor đúng nguyên văn 1 lần, không cụm cấm, không con số lạ, không !/?); không đạt hoặc không có chỗ hợp → để thiếu + ghi lý do.

| File | Việc |
|---|---|
| `CauHinh.gs` | Danh sách dự án (sheet, tab, thư mục Drive, tên cột theo chữ ở hàng 1, quy tắc riêng) |
| `Core.gs` | Hàm thuần: tách thân bài, làm sạch HTML, từ khoá tên file, chọn cụm, soát câu AI |
| `TaoFile.gs` | Tải bài → tạo Docs → chèn (cột Demo → link có sẵn → cụm có sẵn → AI) → soát → ghi K/E |
| `Gemini.gs` | Gọi Gemini, lời dặn, tự soát + hỏi lại 1 lần |
| `GopY.gs` | Sổ góp ý + gửi phản hồi dưới comment (Drive API) |
| `Main.gs` | Menu 🔗 Inlink, cài lịch |
| `Inlink-gop.gs` | Bản gộp để dán (tạo bằng `bash gop.sh`) |

**Đã chạy thử (06/11/2026)** bằng mô phỏng Google trên bài thật (`test/mo-phong.js`): 14 bài Techcombank + 6 bài Okamura
đủ anchor, link đúng URL, tô vàng, ≥25%, có ghi chú đỏ, không mất link gốc. Câu chữ của AI chưa thử được tại chỗ (cần khóa Gemini).
Chưa kiểm được: Techcombank có chặn máy chủ Google tải bài hay không → thử bằng nút "Chạy thử…" ngay sau khi cài.

## Cài (1 lần)
1. Mở sheet Techcombank → **Tiện ích mở rộng → Apps Script**.
2. Xoá chữ có sẵn trong `Code.gs`, dán toàn bộ `Inlink-gop.gs` → bấm 💾 Lưu.
3. Cột trái **Dịch vụ (+)** → chọn **Drive API** → **Thêm**.
4. Tải lại sheet → menu **🔗 Inlink → Cài khóa Gemini** → cho phép quyền → dán khóa (aistudio.google.com → Get API key).
5. **🔗 Inlink → Cài lịch tự chạy**.

Sửa code: sửa file gốc → `bash gop.sh` → dán lại `Inlink-gop.gs`. Chạy thử phần lõi: `node test/mo-phong.js <bai.html> <url> <rows.json> <dòng> [0|1]`.

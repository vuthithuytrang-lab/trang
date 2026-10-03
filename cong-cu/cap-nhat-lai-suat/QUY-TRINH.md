# Quy trình cập nhật lãi suất tiết kiệm hằng ngày – bài blog Techcombank

> Trang giao việc này ngày 03/10/2026 và **sửa lại quy trình cùng ngày** (bản 2, bên dưới): mỗi ngày tạo **1 file Google Docs MỚI**,
> chép toàn bộ bài Techcombank vào, rồi cập nhật ngày, tháng, lãi suất ngay trong file đó; chỉ tô vàng đúng phần đổi.
> Mọi phiên Claude làm việc này phải làm đúng quy trình gốc ở cuối file, không tự thêm bớt.

## Cách chạy (cho Claude, không phải cho Trang)

1. `python3 lay-so-lieu.py` — tải bài Techcombank, VnExpress (qua API), Topi; so từng ô → `tam/result.json`.
2. `python3 tao-file-docs.py dd/mm/yyyy` (ngày hôm nay, giờ Việt Nam) — dựng bài đã tô vàng → `tam/bai-viet.min.html`.
   Tự soát: chụp ảnh `tam/bai-viet.html` bằng Chromium, xem lại.
3. Connector **Google Drive** `create_file`: `title` = `Lãi suất tiết kiệm Techcombank – dd/mm/yyyy`,
   `contentMimeType` = `text/html`, `textContent` = nội dung `tam/bai-viet.min.html` (Google tự đổi sang Google Docs).
4. Soát lại: `download_file_content` (text/html) → so từng ô và số ô tô vàng với `tam/bai-viet.min.html`; xuất PDF xem bằng mắt.
5. Viết báo cáo vào `bao-cao/YYYY-MM-DD.md` (đủ 9 mục) và gửi Trang link + báo cáo.

Ghi chú:
- Docs không nhận nền xám của đoạn văn khi nhập HTML → phần đầu bài (tiêu đề, sapo, ngày) đặt trong 1 ô bảng nền `#f5f6f8`.
- Bảng kẻ giống file mẫu: viền `#dedede`, cột tên ngân hàng 92.5pt, cột kỳ hạn 51.3pt.
- Ngày đăng trên website nằm ở thẻ ẩn dạng `2026-10-03T00:00` → hiển thị `03/10/2026`.
- VnExpress: bảng nạp bằng JavaScript, lấy thẳng API `https://gw.vnexpress.net/th?types=bank_rate_offline` / `bank_rate_online`;
  trường `update` dạng tháng/ngày/năm (`9/21/2026` = 21/09/2026).
- Topi: 2 bảng đầu trang = mục I (Tại quầy, Online). Ngày cập nhật đứng trước chữ "Trang chủ > Blog".
- File mẫu trình bày: `1Q8SQtVPK0TMDahc1K56vjQEA1Sp6jbnwBewuuo9x__Y` (chỉ để tham khảo, KHÔNG sửa file này).

Tên ghép đã chắc chắn: MBBank = MB = MB Bank · OceanBank = MBV = MBV (OceanBank) · VCB Neo (CBBank) / CBBank = VCBNeo = VCBNeo (CBBank) ·
Viet Capital Bank (BVBANK) = BVBank · BAOVIET Bank = BaoVietBank = Bảo Việt · PG Bank = PGBank · PVcomBank = PVCombank ·
Kienlongbank = Kiên Long · Vikki Bank = Vikkibank (Đông Á) · NamABank = Nam Á Bank · BacABank = Bắc Á · VietBank = Vietbank.

---

## Quy trình gốc của Trang – bản 2 (03/10/2026, nguyên văn)

```
ĐẦU RA BẮT BUỘC:
- Mỗi lần cập nhật, tạo 1 file Google Docs mới, copy toàn bộ nội dung bài viết trên website Techcombank vào file, sau đó cập nhật ngày, tháng và lãi suất ngay trong file đó.
- Trình bày giống file mẫu: https://docs.google.com/document/d/1Q8SQtVPK0TMDahc1K56vjQEA1Sp6jbnwBewuuo9x__Y/edit?usp=sharing
- Nội dung nào thay đổi bắt buộc tô nền vàng. Nội dung không thay đổi giữ nguyên như trên website, không tô màu, không sửa.
- Gửi lại link file docs kèm báo cáo (xem phần BÁO CÁO cuối hướng dẫn).

THỨ TỰ NGUỒN:
- Kỳ hạn 1, 3, 6, 12 tháng: lấy từ VnExpress (Bước 2)
- Kỳ hạn 18, 24, 36 tháng: lấy từ Topi (Bước 3)
- Ô còn thiếu sau Bước 2 và 3: xử lý theo Bước 4
  + Ngân hàng có trên VnExpress hoặc Topi nhưng thiếu kỳ hạn: lấy theo kỳ hạn gần nhất
  + Ngân hàng không có trên cả VnExpress và Topi: lấy giống hệt trang chính thức của ngân hàng; không có thì để "-"

BƯỚC 1: TẠO FILE DOCS, COPY BÀI VIẾT VÀ CẬP NHẬT NGÀY, THÁNG
1.1. Tạo file docs mới
- Truy cập https://techcombank.com/thong-tin/blog/lai-suat-tiet-kiem để lấy nội dung mới nhất trong ngày. Không dùng lại nội dung của các lần trước.
- Tạo 1 file Google Docs mới, đặt tên: Lãi suất tiết kiệm Techcombank – dd/mm/yyyy (ngày hôm nay).
1.2. Copy toàn bộ nội dung bài viết vào file
Copy đầy đủ, đúng thứ tự từ trên xuống dưới, gồm:
- Tiêu đề bài, sapo, ngày đăng.
- Toàn bộ đoạn văn, các đề mục, khung lưu ý (ví dụ "Bạn đọc lưu ý: …"), dòng "Đơn vị: %/năm".
- Toàn bộ bảng lãi suất, đủ tất cả ngân hàng, tất cả cột kỳ hạn (1, 3, 6, 12, 18, 24, 36 tháng), đúng nội dung ô như trên website.
- Giữ nguyên các link trong bài, chữ in đậm, in nghiêng, màu chữ, cấp đề mục.
Không bỏ sót, không tóm tắt, không viết lại câu chữ. Phần menu, header, footer, nút bấm của website không cần copy.
1.3. Cập nhật ngày
- Đổi ngày ở MỌI vị trí trong bài (tiêu đề, sapo, ngày đăng, đoạn văn) sang ngày hôm nay.
- Chỉ tô nền vàng đúng phần ngày bị đổi, không tô cả câu.
  Ví dụ: "…hôm nay 03/10/2026", hôm nay là 04/10/2026 thì sửa thành "…hôm nay 04/10/2026" và chỉ tô vàng "04/10/2026".
- Giữ đúng định dạng ngày như trong bài (dd/mm/yyyy).
1.4. Cập nhật tháng
- Đổi tháng ở mọi vị trí trong bài sang tháng hiện tại, chỉ tô vàng phần tháng bị đổi.
  Ví dụ: "tháng 10/2026" nhưng hiện tại là 11/2026 thì đổi thành "tháng 11/2026" và tô vàng "11/2026".
- Ngày/tháng đã đúng thì giữ nguyên, không tô màu.

BƯỚC 2, 3, 4: giữ nguyên như bản 1 (VnExpress cho 1/3/6/12 tháng; Topi cho 18/24/36 tháng; ô thiếu theo 4.1 / 4.2).
Khác bản 1: "Dòng Techcombank: không sửa, giữ đúng như trên website."
Ví dụ 2.5 bản 2: "VPBank 12 tháng đổi thành 5.0 thì chỉ ô 5.0 tô vàng."

NGUYÊN TẮC BẮT BUỘC (bản 2 thêm)
- File docs phải chứa toàn bộ nội dung bài Techcombank, đúng thứ tự và trình bày như trên website. Chỉ khác ở những phần đã cập nhật.
- Mọi nội dung thay đổi đều tô nền vàng, chỉ tô đúng phần bị đổi (con số trong ô, ngày/tháng trong câu).
- (các nguyên tắc còn lại giữ nguyên bản 1)

BÁO CÁO SAU KHI CẬP NHẬT (bản 2)
1. Link file Google Docs đã cập nhật.
2. Ngày tháng: ngày/tháng đã đổi ở Bước 1, kèm các vị trí đã đổi (tiêu đề, sapo, ngày đăng, đoạn văn).
3. Ngày dữ liệu nguồn: VnExpress, Topi, ngày hiệu lực biểu lãi suất ngân hàng dùng ở Bước 4.
4. Ô đã sửa từ VnExpress và Topi: Bảng [Tại quầy/Online] – [Ngân hàng] – [kỳ hạn]: [số cũ] → [số mới] (nguồn: VnExpress/Topi)
5. Ô lấy theo kỳ hạn gần nhất (Trường hợp A): … (lấy theo kỳ hạn [X] tháng)
6. Ô lấy từ trang chính thức (Trường hợp B): … (nguồn: trang [ngân hàng], hiệu lực từ [ngày])
7. Ô điền "-" do không có trên 2 website và chưa có link trang chính thức.
8. Trường hợp cần người duyệt kiểm tra: tên ngân hàng không chắc chắn, biểu lãi suất có ngày hiệu lực cũ, phải chọn mức tiền,
   dùng biểu chung cho cả hai kênh, số bất thường trên nguồn.
9. Nếu không có ô lãi suất nào thay đổi, ghi rõ: "Không có thay đổi lãi suất".
```

Chi tiết đầy đủ Bước 2–4 (không đổi so với bản 1) xem lịch sử git của file này (commit 692db02).

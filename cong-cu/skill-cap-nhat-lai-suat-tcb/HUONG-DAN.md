# Skill "Cập nhật lãi suất bài Techcombank" — hướng dẫn cho Trang

Gói này đóng quy trình cập nhật lãi suất thành **1 skill** (bộ hướng dẫn + công cụ). Gửi cho Claude nào cũng được:
đưa link bài Techcombank + link nguồn số liệu → Claude tự lấy số, tạo file Google Docs tô vàng như bạn đang nhận hằng ngày, kèm báo cáo.

**Không đụng tới quy trình đang chạy**: lịch 3 ngày/lần vẫn dùng công cụ cũ ở `cong-cu/cap-nhat-lai-suat/`. Skill này là bản sao riêng.

## Trong gói có gì

| File | Để làm gì |
|---|---|
| `cap-nhat-lai-suat-tcb.zip` | **File để gửi đi / tải lên** (chứa cả thư mục bên dưới) |
| `cap-nhat-lai-suat-tcb/SKILL.md` | Bản hướng dẫn Claude đọc đầu tiên |
| `cap-nhat-lai-suat-tcb/scripts/lai_suat.py` | Công cụ làm phần kỹ thuật (lấy số, tô vàng, soát, báo cáo) |
| `cap-nhat-lai-suat-tcb/references/` | File cấu hình mẫu, mẫu nhập số tay, quy trình gốc của bạn |

## Cách dùng (chọn 1)

**Cách 1 – Claude Code trên web (giống chỗ bạn đang dùng, chắc chạy nhất).**
Mở phiên mới trong repo `trang`, nhắn: *"Dùng skill trong `cong-cu/skill-cap-nhat-lai-suat-tcb` để cập nhật lãi suất bài <link>. Nguồn: <link>."*

**Cách 2 – Tải lên claude.ai để dùng ở mọi cuộc trò chuyện.**
Vào claude.ai → Cài đặt (Settings) → mục Tính năng / Capabilities → Skills → tải lên `cap-nhat-lai-suat-tcb.zip`.
Sau đó chỉ cần nhắn link bài + link nguồn. (Cần bật "chạy code" và kết nối Google Drive trong claude.ai.)

**Cách 3 – Gửi cho đồng nghiệp:** gửi file `cap-nhat-lai-suat-tcb.zip`, họ làm như Cách 2.

## Nhắn cho Claude thế nào

> Cập nhật lãi suất cho bài https://techcombank.com/thong-tin/blog/... nhé.
> Nguồn: VnExpress (kỳ hạn 1–12 tháng), Topi (18–36 tháng). Tên file: "…".

- Không nói nguồn → Claude dùng mặc định VnExpress + Topi như quy trình hiện tại.
- Không nói tên file → Claude hỏi, hoặc lấy theo tiêu đề bài.
- Có nhiều bài → cứ dán nhiều link, mỗi bài ra 1 file Docs.

## Lưu ý thật

- Claude cần **vào được mạng** tới techcombank.com, vnexpress.net, topi.vn. Một số môi trường chặn mạng (như lịch chạy trên web lúc trước).
  Khi đó Claude sẽ báo rõ bị chặn ở đâu và nhờ bạn lưu trang gửi vào chat — không bịa số.
- Cần **kết nối Google Drive**. Không có thì Claude gửi file để bạn kéo vào Drive và mở bằng Google Tài liệu.
- Bài phải là bài **blog Techcombank** có bảng lãi suất (cột "Ngân hàng" + dòng Techcombank). Trang khác cấu trúc thì skill báo và dừng.
- Nguồn đặc biệt (file PDF biểu lãi suất của ngân hàng, trang chính thức) → Claude tự đọc rồi ghi số vào "nguồn nhập tay", vẫn tô vàng và báo cáo như thường.

## Đã kiểm tra

1. Chạy cùng số liệu với công cụ đang dùng hằng ngày → 2 bài ra **giống hệt từng ký tự** (cả khi đổi tháng).
2. Chạy trên một bài Techcombank khác chưa từng làm ("Tại sao gửi tiết kiệm online lãi suất cao hơn") → nhận đúng bảng có cả cột online và tại quầy, sửa 12 ô, chụp ảnh soát không vỡ trình bày.
3. Cho một Claude "trắng" (không biết gì về cuộc trò chuyện này) đọc skill và tự chạy trọn từ đầu tới tạo file Docs + soát.

# App share bài — hướng dẫn cài (không cần biết kỹ thuật)

## App này làm gì?

- Chạy **ngay trong Google Sheet**, tự đăng bài đúng giờ hẹn lên Wix / WordPress — kể cả khi tắt máy, không tốn token AI.
- Giữ nhịp an toàn: mỗi tài khoản tối đa 6 bài/ngày, 2 bài cách nhau ≥ 2 tiếng, chỉ đăng 7h–23h.
- Đăng xong tự ghi **link + giờ** vào sheet dự án (tìm dòng theo URL bài gốc, không ghi đè ô đã có link).
- Sáng 6:45 kiểm tra các trang còn sống; trang bị khóa → **tự dừng** nền tảng đó + gửi email báo.
- Tab **Báo cáo**: mỗi tài khoản đã đăng bao nhiêu, hôm nay bao nhiêu, còn chờ, lỗi, % hoàn thành, bảng theo ngày.
  22:30 mỗi tối gửi email tóm tắt.

AI (Claude) chỉ còn làm phần **viết bài + làm ảnh**, rồi đổ vào tab "Hàng đợi". Phần đăng do app lo.

## Cài đặt — 6 bước (làm 1 lần)

1. **Mở một Google Sheet mới** (hoặc sheet bạn muốn dùng làm bảng điều khiển) → menu **Tiện ích mở rộng → Apps Script**.
   Xóa hết chữ có sẵn, dán toàn bộ nội dung file `Code.gs`, bấm biểu tượng 💾 Lưu.
2. **Quay lại tab Sheet, tải lại trang** (Cmd + R). Trên thanh menu hiện thêm **🚀 App share bài**.
3. Bấm **🚀 App share bài → 1. Tạo các tab (lần đầu)**.
   Google hỏi cấp quyền → chọn tài khoản → *Nâng cao* → *Đi tới (không an toàn)* → *Cho phép*.
   (Cảnh báo "không an toàn" là bình thường vì app do chính bạn tạo, chưa nộp Google duyệt.)
4. Tab **Cấu hình**: điền cột *Giá trị* (ID sheet dự án, tên tab, link trang Wix…). Claude sẽ điền sẵn giúp bạn.
5. Bấm **2. Cài chìa Wix** → dán chìa vào ô hiện ra (chìa cất trong phần cài đặt bí mật của app, không nằm trong sheet, không ai xem sheet thấy được).
6. Bấm **3. Bật tự động đăng**. Xong.

## Dùng hằng ngày

- Muốn xem tiến độ: mở tab **Báo cáo** (hoặc bấm *Cập nhật báo cáo*).
- Muốn dừng gấp: **Tắt tự động đăng**.
- Dòng **Lỗi** trong Hàng đợi: đọc cột *Ghi chú*, sửa xong đổi Trạng thái về trống là app đăng lại.
- Trang bị khóa: app tự dừng + email. Muốn chạy lại sau khi trang mở: bấm *Kiểm tra các trang còn sống*.

## Dự án mới

Nói với Claude: *"chạy luồng share, đổ vào app"* + link sheet + quy tắc. Claude viết bài, làm ảnh, đổ hàng đợi và lịch;
app tự đăng.

# Cập nhật bài TCB tự động — không cần Claude, không tốn token

Dựng 28/10/2026 theo yêu cầu của Trang: *"app chạy bình thường mỗi khi tôi bấm update và không tốn token"*,
*"không đặt lịch chạy mà khi tôi bấm bạn sẽ chạy"*. Áp dụng cho **9 bài có công thức**: vàng 24K/14K/18K/10K/16K/610,
1 chỉ vàng, cà phê, xăng dầu.

## Đường đi khi bấm

1. **App** (https://claude.ai/artifact/C1pHcHu6DLgx8xi4zNQnoN, nguồn `../app-cap-nhat/app.html`) bấm "Chạy cập nhật" → tích ô cột E
   trong Sheet "Update" qua kết nối Google Sheets (người không có Claude thì tích tay trong Sheet — như nhau).
2. **Apps Script** (`google-apps-script/Code.gs`, gắn vào Sheet, chạy dưới tài khoản Google của Trang, xem Sheet mỗi phút):
   thấy ô tích của bài tự động → ghi `⏳ Đang chạy…` + ghi **phiếu** `yeu-cau-tu-dong.json` (Drive, thư mục chung,
   id `1wrO0bArJtokvfFvOzFNFqvJhrLrPD2VI`).
3. **GitHub Actions** (`.github/workflows/tu-dong-cap-nhat.yml`, file nằm ở **nhánh chính** `claude/ai-boss-data-replace-hn412r`
   vì lịch của GitHub chỉ chạy ở nhánh chính; công thức lấy từ nhánh `claude/vibrant-keller-rk0i98`): việc `kiem` liếc phiếu
   5 phút/lần — không có phiếu mới thì dừng sau vài giây; có phiếu mới → việc `chay` chạy `chay.sh <mã>` đúng các bài trong phiếu
   (bài nào nguồn không đọc được thì chạy lại 1 lần) → `tong_hop.py` ghi `<mã>.html` + `trang-thai.json` (`_yeu_cau` = mã phiếu)
   lên nhánh `tu-dong-ket-qua` (ghi đè, giữ kết quả các bài khác).
4. **Apps Script** thấy kết quả mới hơn lúc tích → tạo Google Docs (thư mục chung), chia sẻ quyền sửa cho email `Hướng dẫn!B11:B20`,
   dán link vào cột hôm nay + tab `app`, ghi chú "Cần xem lại" (nếu có), bỏ tích. Quá 45 phút chưa có kết quả → `⚠️ Lỗi`, bỏ tích.

Không có chìa khóa nào: GitHub chỉ đọc web + phiếu công khai; Apps Script đọc kết quả qua link công khai `raw.githubusercontent.com`.
Tab `app`: A STT · B tên file · C link · D lúc · E `dang_chay` / `xong` / `Cần xem lại: …` / `⚠️ Lỗi: …`; `H1` = nhịp "Máy tự động chạy lúc …"
(Claude dùng ô này để biết máy đang bật → lịch Claude mỗi giờ bỏ qua 9 bài tự động).

## Giới hạn — nói thật với Trang

- Từ lúc bấm đến khi có file: khoảng 10–20 phút (GitHub liếc phiếu 5 phút/lần, có lúc trễ hơn; chạy 1–2 phút/bài).
- Bài lãi suất và 12 bài mới (nhôm, lúa gạo, ca cao, tiêu…) vẫn cần Claude — muốn miễn phí phải đóng gói công thức từng bài.
- Nguồn bị chặn (giacaphe.com — giá cà phê thế giới) → bảng đó giữ số cũ, ô Sheet có ghi chú "Cần xem lại".

## Cài đặt (1 lần)

1. ✅ File lịch đã ở nhánh chính (Trang đồng ý 28/10/2026).
2. Trang: Sheet "Update" → **Tiện ích mở rộng → Apps Script** → xóa chữ có sẵn → dán `google-apps-script/Code.gs` → Lưu
   → chọn hàm `caiDat` → **Chạy** → **Cho phép**.

## Chạy thử tay

Actions → "Cập nhật bài TCB tự động" → Run workflow, ô `bai` = `vang-24k gia-xang-dau`.
Một bài trên máy: `bash cong-cu/tu-dong/chay.sh vang-24k /tmp/kq` (cần `NODE_PATH` trỏ tới playwright).

# Cập nhật bài TCB tự động — không cần Claude, không tốn token

Dựng 28/10/2026 theo yêu cầu của Trang: *"app tự làm mà không phụ thuộc vào token hay Claude"*.

## Hai mảnh ghép (đều miễn phí)

| Mảnh | Chạy ở đâu | Làm gì |
|---|---|---|
| `.github/workflows/tu-dong-cap-nhat.yml` + `chay.sh` + `tong_hop.py` | Máy chủ GitHub Actions (miễn phí vì repo công khai) | Mỗi giờ 7h35–17h35 giờ VN, thứ 2–7: chạy công thức 9 bài (vàng 24K/14K/18K/10K/16K/610, 1 chỉ vàng, cà phê, xăng dầu) — đọc bài mới nhất, lấy giá, sửa số + ngày (ngày hôm sau), tô vàng, tự soát → đăng `<mã>.html` + `trang-thai.json` lên nhánh `tu-dong-ket-qua` (ghi đè, không lưu lịch sử) |
| `google-apps-script/Code.gs` | Apps Script gắn vào Sheet "Update", chạy dưới tài khoản Google của Trang | 10 phút/lần: dòng nào được tích + có bản dựng mới (≤ 150 phút, đúng ngày mai) → tạo Google Docs trong thư mục chung, chia sẻ quyền sửa cho email ở `Hướng dẫn!B11:B20`, dán link vào cột hôm nay, ghi chú "Cần xem lại" vào ô (nếu có), bỏ tích |

Không có chìa khóa nào: GitHub chỉ đọc web công khai; Apps Script đọc kết quả qua link công khai `raw.githubusercontent.com`.

## Giới hạn — nói thật với Trang

- **Chỉ 9 bài có công thức** chạy tự động. Bài lãi suất và 12 bài mới (nhôm, lúa gạo, ca cao, tiêu…) vẫn cần Claude
  (cần đọc hiểu nguồn) — muốn tự động thì phải đóng gói công thức cho từng bài trước.
- Giá trong file là giá lúc lần chạy gần nhất (tối đa ~1 giờ trước).
- Tích ngoài giờ (sau 17h35, Chủ nhật) → sáng hôm sau 7h35 mới có file.
- Nguồn bị chặn (giacaphe.com với giá cà phê thế giới) → bảng đó giữ số cũ, ô trong Sheet có ghi chú "Cần xem lại".
- Lịch theo giờ của GitHub chỉ chạy khi file workflow nằm ở **nhánh chính** của repo (`claude/ai-boss-data-replace-hn412r`).

## Cài đặt (1 lần)

1. Đưa `.github/workflows/tu-dong-cap-nhat.yml` lên nhánh chính (cần Trang đồng ý).
2. Trang: Sheet "Update" → **Tiện ích mở rộng → Apps Script** → xóa chữ có sẵn → dán `google-apps-script/Code.gs` → Lưu
   → chọn hàm `caiDat` → **Chạy** → **Cho phép**.
3. Sau khi Trang cài xong: sửa prompt lịch Claude mỗi giờ (`trig_01G2khUNPPGokGp6wFBSQCGD`) bỏ qua dòng 2–10 của Sheet
   (9 bài đã tự động), để Claude không chạy trùng và không tốn token.

## Chạy thử tay

Đẩy thay đổi vào `cong-cu/tu-dong/*.sh|*.py` trên nhánh `claude/vibrant-keller-rk0i98` → workflow tự chạy.
Một bài: `bash cong-cu/tu-dong/chay.sh vang-24k /tmp/kq` (cần `NODE_PATH` trỏ tới playwright).

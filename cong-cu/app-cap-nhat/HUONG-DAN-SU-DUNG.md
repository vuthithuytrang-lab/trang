# Hướng dẫn dùng app "Cập nhật bài Techcombank" (không cần Claude)

Từ 06/11/2026 app chạy hoàn toàn bằng dịch vụ miễn phí, **không cần tài khoản Claude, không tốn token**.

## Dùng hằng ngày
1. Mở **https://vttt-sn.netlify.app/** (hoặc https://vuthithuytrang-lab.github.io/trang/).
2. Tìm bài → bấm **"↻ Chạy bài này"** (hoặc tích nhiều bài rồi bấm chạy chung).
3. Chờ khoảng 1–1,5 phút, app tự hiện bản mới (app tự kiểm tra 10 giây/lần). Bấm **"Chép để dán vào Docs"** (giữ tô vàng) hoặc **"Tải Word"**.
4. Đọc mục **"Cần xem lại"** dưới mỗi bài trước khi gửi đăng.

Trước khi bấm chạy, chọn ngày ở ô **"Ngày ghi trong bài"** (hôm nay / ngày mai / ngày kia; mặc định ngày mai). Hai bài lãi suất máy tự lo, luôn ghi ngày mai. Chỗ nào đổi đều được tô vàng.

## Mọi thứ nằm ở đâu (đều là của Trang)
| Phần | Ở đâu |
|---|---|
| Giao diện app | GitHub Pages (kho `vuthithuytrang-lab/trang`, nhánh `gh-pages`) + Netlify `vttt-sn` |
| Nút chạy | Hàm Netlify `chay` dùng chìa GitHub (biến `GITHUB_TOKEN` trong Netlify) |
| Máy chạy bài | GitHub Actions `tu-dong-cap-nhat.yml` (miễn phí) |
| Công thức 27 bài | `cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/<mã>/` |
| Kết quả | nhánh `tu-dong-ket-qua` (app đọc ngay qua hàm Netlify `kq`) |

## Khi có sự cố
- **Bấm chạy không có gì xảy ra / báo lỗi nút** → chìa GitHub có thể đã hết hạn. Xem hạn ở
  https://github.com/settings/personal-access-tokens → tạo chìa mới (quyền Actions: Read and write cho kho `trang`)
  → dán vào Netlify: https://app.netlify.com/projects/vttt-sn/configuration/env → biến `GITHUB_TOKEN` → bấm Deploy lại.
- **Một bài báo "KHÔNG ĐỌC ĐƯỢC" hoặc "SỐ GIÁ CHƯA CẬP NHẬT"** → nguồn của bài đổi giao diện / chặn máy.
  Bài giữ số cũ (không ra số sai). Cần một người biết kỹ thuật (hoặc Claude) sửa công thức của bài đó một lần.
- **Trang Netlify bắt đăng nhập** → Visitor access phải để Public:
  https://app.netlify.com/projects/vttt-sn/configuration/general#visitor-access

## Đã tắt (06/11/2026)
Các lịch Claude của luồng này: kiểm tra Sheet "Update" mỗi giờ, lãi suất 3 ngày/lần, yêu cầu từ app claude.ai.
Sheet "Update" vẫn giữ làm nơi lưu danh sách bài + nguồn. Tích ô trong Sheet không còn Claude chạy nữa; máy GitHub chỉ đọc phiếu từ Sheet vài tiếng một lần (chậm) → **muốn nhanh thì dùng app**.

# Công thức: bài "Cập nhật giá dầu thế giới hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-dau-the-gioi — chạy lần đầu 15/10/2026 (ghi ngày 16/10), Trang chưa duyệt nguồn.

## Đã chốt
| Việc | Cách làm |
|---|---|
| Bảng (2 dòng Brent, WTI) | Giá hợp đồng **gần nhất** theo từng mã tháng: Brent `BZ<tháng><năm>.NYM`, WTI `CL<tháng><năm>.NYM` trên Yahoo Finance chart API (`https://query1.finance.yahoo.com/v8/finance/chart/<mã>?range=5d&interval=1d`) |
| Không dùng | `CL=F` / `BZ=F` của Yahoo (có lúc ghép giá hợp đồng sau với lịch sử hợp đồng trước → sai thay đổi) |
| Đối chiếu | oilprice.com (trang chủ, khung giá Brent/WTI) — lệch nhỏ do thời điểm là bình thường |
| Thay đổi so với phiên trước | Giá hiện tại − giá chốt phiên trước (đánh `tinh_toan`), ghi `-1.57 USD (-1.5%)`; % 1 số lẻ, dưới 0.05% thì ghi 2 số lẻ |
| Câu chữ | Không viết lại; sapo nhắc "5 ngày gần đây" nhưng bài không có bảng 5 ngày → chỉ báo |

## Các bước
`lay` → `dung <N>` → lấy giá 2 mã → ghi `sua.json` (4 chỗ: 2 giá + 2 thay đổi) → `sua` → Docs (Bước 5–6 SKILL.md). Mẫu: `cap-nhat-bai-tcb/2026-10-16-gia-dau-the-gioi/`.

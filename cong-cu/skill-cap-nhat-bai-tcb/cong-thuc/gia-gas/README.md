# Công thức: bài "Cập nhật giá gas hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-gas-hom-nay — chạy lần đầu 15/10/2026 (ghi ngày 16/10), Trang chưa duyệt nguồn.

## Đã chốt
| Việc | Cách làm |
|---|---|
| Nguồn | Bản tin "Giá gas hôm nay dd/mm" mới nhất trên thuongtruong.com.vn (đúng 5 khu vực + đúng các thương hiệu/khu vực của bài). Bài TCB đang lấy số từ đây |
| Nhịp giá | Giá gas đổi **mỗi tháng 1 lần (ngày 1)** theo giá CP Aramco. Giữa tháng thường không đổi → chỉ đổi ngày |
| Ngày | Đề mục "1. Giá gas hôm nay d/m/yyyy" → ngày ghi bài; câu "dữ liệu cập nhật gần nhất ngày …" → **ngày của bản tin nguồn** |
| Dòng nguồn có mà bài không có (Pacific Petro) | Không thêm dòng |
| Cách viết số | `644,122` (dấu phẩy ngăn nghìn), ô trống ghi `—` |
| Không dùng | alogas.vn, gas40.com (số cũ/không khớp) |

## Các bước
`lay` → `dung <N>` → đọc bản tin nguồn (WebFetch) → so từng ô → `sua.json` → `sua` → Docs. Mẫu: `cap-nhat-bai-tcb/2026-10-16-gia-gas/`.

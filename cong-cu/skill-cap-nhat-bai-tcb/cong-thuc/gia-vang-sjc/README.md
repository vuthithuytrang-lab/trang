# Công thức: cập nhật bài "Giá vàng SJC hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-vang-sjc — đóng gói 06/11/2026.
Chạy không cần Claude: `bash cong-cu/tu-dong/chay.sh gia-vang-sjc <thư mục ra>` (khung chung "*)" của chay.sh).
Chưa thêm dòng vào Sheet "Update" (việc đó làm khi được duyệt).

## 1. Nguồn

| Nguồn | Cách đọc | Giờ cập nhật |
|---|---|---|
| https://webgia.com/gia-vang/sjc/ — bản chép bảng giá chính thức của SJC (sjc.com.vn chặn máy chủ) | `lay_gia.js` (trình duyệt Playwright; đọc bằng curl thì webgia che số) — chỉ lấy khối **Hồ Chí Minh** (12 dòng niêm yết SJC) | dòng "Bảng giá vàng SJC hôm nay được cập nhật lúc hh:mm:ss dd/mm/yyyy" trên trang |

Nguồn không đọc được: `gia.json` ghi `"webgia": null`, in "webgia KHÔNG ĐỌC ĐƯỢC", giữ nguyên toàn bộ giá + ghi cần duyệt (ngày vẫn đã sang ngày hôm sau nên giá và ngày lệch nhau — không đăng).

## 2. Quy tắc

- **Đổi đơn vị**: nguồn ghi VND/chỉ (`13.800.000`); bài ghi triệu VND/lượng, dấu chấm thập phân → số bài = số nguồn ÷ 100.000, bỏ số 0 thừa cuối, không làm tròn (`13.800.000` → `138`; `14.102.000` → `141.02`; `13.092.100` → `130.921`).
- **Ghép dòng theo tên** (không theo thứ tự): `1L`=`1 lượng`, `1KG`=`1 kg`, `99,99%`=`99.99%`, bỏ ngoặc, không phân biệt hoa thường/dấu cách. Dòng bài không có ở nguồn / nguồn có dòng mới / nguồn che số → giữ nguyên + cần duyệt.
- **Bảng**: Mua vào ← "mua", Bán ra ← "bán" của dòng cùng tên.
- **Đoạn văn**: "X - Y triệu VND/lượng" (mua vào - bán ra) của vàng miếng 1 lượng và vàng nhẫn 99.99% 1,2,5 chỉ; "hơn N triệu VND/lượng" = giá bán vàng miếng 1 lượng làm tròn xuống chục (chỉ đổi khi mốc đổi, kèm cần duyệt).
- **Chỉ đổi số**, giữ nguyên câu chữ và tên sản phẩm. Ô lệch quá xa số cũ (ngoài 0,5–2 lần, nghi đổi đơn vị) → giữ nguyên + cần duyệt.
- **Lưới an toàn**: số giá còn sót (ô bảng hoặc "… triệu VND" từ 20 trở lên) không bằng số nguồn nào → cần duyệt "SỐ GIÁ CHƯA CẬP NHẬT …". Bài hiện có 1 chỗ như vậy: "khoảng 190 triệu VND/lượng hồi đầu năm 2026" (mốc lịch sử, không có nguồn).
- Nguồn cũ hơn 2 ngày → vẫn dùng + cần duyệt.
- **Ngày**: không xử lý ở đây; lệnh `dung` + `doi_ngay_bai.py` của khung lo (luôn ngày hôm sau).
- Lỗi gõ sẵn trong bài (ô `58..244` — hai dấu chấm): bị thay luôn bằng số nguồn và ghi cần duyệt.

## 3. Tệp

`cau-hinh.json` · `lay_gia.js` · `tao_sua.py` (có chế độ `--kiem` in "Soát: khớp hết").

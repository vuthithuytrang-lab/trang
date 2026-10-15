# Công thức: cập nhật bài "Giá thép hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-thep-hom-nay
Lập lần đầu ngày 15/10/2026 (bản ghi ngày 16/10/2026). Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

## 1. Những gì đã chốt

| Việc | Cách làm cố định |
|---|---|
| Bảng HRC thế giới – nguồn | Barchart, mã **V7 = Steel HRC FOB China** (Barchart ghi sàn **LME**, không phải CME). Trang danh sách `V7*0/futures-prices` không hiện bảng (API bị chặn 403) → đọc **trang overview từng hợp đồng** `https://www.barchart.com/futures/quotes/V7<tháng><năm>/overview` (dòng đầu: giá, thay đổi, %, ngày) |
| Kỳ hạn | Bài có 10 dòng, tháng liên tiếp, bắt đầu từ tháng hiện tại (10/2026 → 7/2027). Mã = `V7` + mã tháng (F G H J K M N Q U V X Z) + 2 số năm. Hợp đồng nào Barchart không có giá cùng ngày mới nhất (đã đáo hạn) thì bỏ, cuộn lên — đổi cả mã + tháng |
| Cách ghi số HRC | Giá `486.50` (2 số lẻ, dấu `.`), thay đổi `-6.00` / `+1.50`, bằng 0 ghi `0.00`. **Không thêm "s"** sau giá (bài gốc không ghi dù phần giải thích có dòng "s:") — ghi vào cần duyệt |
| Tháng đáo hạn | Kiểu `10/2026`, `1/2027` (tháng không có số 0) |
| Giờ lấy số | Barchart chỉ hiện giá chốt phiên (ký hiệu `s`) của phiên trước; ghi rõ ngày phiên trong `--ghi-chu` |
| Bảng giá trong nước – nguồn | Steelonline https://steelonline.vn/bang-gia-thep-xay-dung-hom-nay (đúng 10 thương hiệu, đúng thứ tự của bài; có dòng "NGÀY dd-mm-yyyy") |
| Cách tính khoảng | Bảng **hiện mặc định** (tab miền đầu tiên) của từng thương hiệu: **VND/kg** = thấp nhất – cao nhất của mọi ô VNĐ/kg (CB240, CB300, CB400, CB500); **VND/cây** = thấp nhất – cao nhất của mọi ô VNĐ/cây (D10 – D28). Đã kiểm ngày 15/10/2026: cách tính này ra đúng y 20 khoảng đang có trong bài |
| Cách ghi số trong nước | `14,210 - 14,920` (dấu nghìn `,`, gạch có cách), vẫn là khoảng |
| Ngày trong bài | Công cụ chung tự đổi (6 chỗ dd/mm/yyyy) |
| Lỗi có sẵn trong bài | (1) Câu "Lưu ý" dưới bảng HRC ghi "tùy theo **chất lượng cà phê**, sản lượng thu mua…" (chép từ bài cà phê); (2) hai đề mục cùng số "3." — **không sửa**, ghi cần duyệt |
| Tên file Docs | `Giá thép hôm nay: Bảng giá cập nhật và các yếu tố ảnh hưởng đến thị trường – dd/mm/yyyy`; trùng tên → thêm ` (cập nhật HHhMM)` |

## 2. Các bước

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-thep
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia.js cap-nhat/gia.json      # ~3 phút: 12 trang Barchart + Steelonline
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json   # phải ra "khớp hết"
```

`tao_sua.py` tự thêm mục cần duyệt về câu "chất lượng cà phê". Các ghi chú khác (giá chốt phiên ngày nào, không thêm "s",
bảng trong nước không đổi…) thì thêm tay vào `can_duyet` trước khi chạy `sua`. Sau đó làm Bước 5 – 6 của `SKILL.md`
(Docs từ `cap-nhat/tam/bai1.min.html`, `soat` phải ra `dòng lệch: 0`, `bao-cao`).

Lưu ý: `cau-hinh.json` có `tham_khao` (Barchart, Steelonline) chỉ để báo cáo ghi nguồn; `lay` tải không ra số (trang vẽ bằng
JavaScript) — số thật lấy bằng `lay_gia.js`. Nếu `bao-cao` in dòng "Không đọc được nguồn tham khảo …: None" thì đó là do
`tham_khao` được thêm sau `lay` — xóa dòng đó khỏi báo cáo.

## 3. Trục trặc

| Hiện tượng | Làm gì |
|---|---|
| `lay_gia.js` báo `THIẾU SỐ` / hợp đồng có `loi` | Chạy lại 1 lần (trang đầu Barchart hay chậm); vẫn lỗi → giữ nguyên bảng HRC, `can_duyet` |
| API Barchart `{"error":"Forbidden"}` | Bình thường — không dùng API, chỉ đọc trang overview |
| Steelonline đổi giao diện (không thấy `BẢNG GIÁ THÉP <tên>` / dòng `D10\t…`) | Đọc `cap-nhat/gia.json` hoặc trang bằng mắt, sửa hàm tách bảng trong `lay_gia.js` |
| `tao_sua.py` báo `Không thấy thương hiệu` | Bài đổi tên thương hiệu → sửa `khop_ten` |
| Khoảng tính ra lệch hẳn bài cũ ở mọi dòng | Có thể bài đổi cách tính (vd chỉ một miền) → không tự sửa, `can_duyet` |

## 4. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài + nguồn tham khảo |
| `lay_gia.js` | Chromium: lấy 12 hợp đồng V7 từ Barchart + bảng 10 thương hiệu Steelonline → `gia.json` |
| `tao_sua.py` | So 2 bảng trong bài với `gia.json` → `sua.json`; `--kiem` soát lại |

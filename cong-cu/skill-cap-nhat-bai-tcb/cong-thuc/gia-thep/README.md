# Công thức: cập nhật bài "Giá thép hôm nay: Bảng giá cập nhật và các yếu tố ảnh hưởng đến thị trường" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-thep-hom-nay — đóng gói 28/10/2026 từ 3 lần làm tay (21, 23, 29/10/2026).
Chạy tự động bằng `cong-cu/tu-dong/chay.sh gia-thep <thư mục ra>` (khung chung `*)`), không cần Claude, không mạng trong `tao_sua.py`.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

> ⛔ Không có số nào tự nghĩ ra: mọi số ghi vào bài lấy thẳng từ trang nguồn tải trong lần chạy đó.
> Nguồn lỗi → giữ nguyên số cũ + "cần duyệt".

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Bảng 1 – thép thế giới (Steel HRC FOB China, mã V7, sàn LME) | Barchart `https://www.barchart.com/futures/quotes/<mã gần nhất>/futures-prices?viewName=main` (Trang chọn). **Barchart chặn máy chủ tự động** (HTTP 202 rỗng / 403 – trang kiểm tra chống máy). Công thức chỉ tải 1 lần như trình duyệt thường, **không vượt** → thường xuyên là "cần duyệt", giữ nguyên bảng |
| Khớp dòng bảng 1 | Theo **mã hợp đồng** (V7V26, V7X26…), không theo vị trí. Ô giá `487.00` (2 số lẻ); ô thay đổi `-1.50`, `+1.00`, không đổi (Barchart ghi `unch`) = `0.00`. Bài không ghi chữ `s` sau giá |
| Chuyển kỳ hợp đồng | Hợp đồng tháng M coi là hết hạn sau **ngày làm việc cuối của tháng M** (V7V26 → 30/10/2026). Dòng đầu bảng đã hết hạn → dòng thứ i lấy hợp đồng còn hạn thứ i trên Barchart (đổi cả mã + tháng + giá + thay đổi), số dòng giữ nguyên, ghi cần duyệt. Barchart lỗi → không chuyển, chỉ báo cần duyệt |
| Bảng 2 – thép trong nước | steelonline.vn `https://steelonline.vn/bang-gia-thep-xay-dung-theo-ngay/dd-mm-yyyy` (Trang chọn). Thử từ ngày mai lùi dần 10 ngày, lấy **trang đầu tiên có bảng giá** (trang ngày chưa có số chỉ có khung trống) |
| Khoảng giá mỗi hãng | Bảng **đầu tiên** (tab đầu) dưới tiêu đề "BẢNG GIÁ THÉP <hãng> NGÀY …": thấp nhất – cao nhất mọi ô VNĐ/kg (CB240, CB300, CB400, CB500) và mọi ô VNĐ/cây. Khớp với cách làm tay 3 lần trước (Hòa Phát, Việt Đức, Thép VAS, Pomina có nhiều tab miền, bài chỉ theo tab đầu) |
| Khớp dòng bảng 2 | Theo tên hãng, bỏ dấu, bỏ chữ "Thép" đầu tên ("Thép Pomina" = "Pomina", "Hòa Phát" = "Hoà Phát"). Hãng không có trên nguồn → giữ nguyên + cần duyệt; nguồn có hãng mới → chỉ báo, không thêm dòng |
| Cách viết số bảng 2 | `14,210 - 14,920` và `102,596 - 814,309` (dấu phẩy hàng nghìn, " - " giữa) |
| Ngày | `dung` đổi mọi ngày sang **ngày hôm sau**. Nguồn của mục nào lỗi → trả ngày ở tiêu đề mục đó ("1. Bảng giá thép thế giới hôm nay …" / "2. Bảng giá thép trong nước hôm nay …") về ngày của bài gốc, để không ghi ngày mới cho giá cũ |
| Đoạn văn, FAQ | Bài hiện không có giá nào ngoài 2 bảng (đã soát bản 29/10/2026). Bài thêm số mới ngoài bảng → cần làm thêm công thức |

Mỗi chỗ sửa trong `sua.json` ghi `nguon` (link trang) và `ly_do` kèm **chữ gốc trên nguồn** (vd steelonline: `VNĐ/kg thấp nhất "14.210", cao nhất "14.920"`).

## 2. Đường vòng cho Barchart (chưa dùng)

Đã thử 28/10/2026: lme.com (403), investing.com (403), marketwatch (401) đều chặn; tradingeconomics "HRC Steel" là thép
HRC Mỹ (CME) – **khác sản phẩm**, không dùng được. Lần làm tay trước đọc Barchart bằng trình duyệt Chromium (trang
overview từng hợp đồng) — công thức tự động **không** làm vậy vì đó là vượt trang kiểm tra chống máy. Muốn có số thế
giới tự động thì cần nguồn công khai khác có đúng hợp đồng LME Steel HRC FOB China (Argus), hoặc người cập nhật tay.

## 3. Các bước (chay.sh làm y hệt)

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-thep
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # LUÔN ngày hôm sau (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 -I $CT/lay_gia.py cap-nhat/gia.json                       # Barchart + steelonline → gia.json
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

Hoặc gọn: `bash cong-cu/tu-dong/chay.sh gia-thep <thư mục ra>`.

## 4. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia.py` | Tải Barchart (1 lần, chặn → null) + trang steelonline mới nhất có số → `gia.json` (số + chữ gốc + link + ngày) |
| `tao_sua.py` | Bảng thế giới (theo mã, tự chuyển kỳ) + bảng trong nước (theo hãng) + giữ ngày tiêu đề mục khi nguồn lỗi → `sua.json`; `--kiem` soát lại |

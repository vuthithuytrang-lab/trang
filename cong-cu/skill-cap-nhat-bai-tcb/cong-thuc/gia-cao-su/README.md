# Công thức: cập nhật bài "Cập nhật giá cao su trong nước và thế giới" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-cao-su
Đóng gói ngày 15/10/2026 (lần chạy đầu, ghi ngày 16/10/2026). Trang chỉ cần nhắn *"Update bài giá cao su"* (hoặc dán link) — **không hỏi gì thêm**.
Công thức chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/` (skill "Cập nhật bài Techcombank").

## 1. Những gì đã chốt — KHÔNG hỏi lại Trang

| Việc | Cách làm cố định |
|---|---|
| Bài có 2 bảng | (1) Trong nước: `Doanh nghiệp thu mua | Loại mủ và chỉ tiêu | Mức giá` – 12 dòng (Bình Long 3, Phú Riềng 2, Mang Yang 4, Bà Rịa 3). (2) Thế giới: `Sàn | Chủng loại | Kỳ hạn | Mức giá | Đơn vị` – TOCOM RSS3 5 dòng, SHFE 5 dòng, SGX TSR20 5 dòng |
| Nguồn giá trong nước | Bài **"Giá cao su hôm nay dd/mm/yyyy" mới nhất** trên doanhnghiephoinhap.vn (đăng ~9h sáng, số lấy từ giacaphe.com lúc ~8h). `lay_gia.py` tự tìm bài mới nhất ở trang https://doanhnghiephoinhap.vn/nhan-dinh-thi-truong và đọc giá bằng mẫu câu cố định |
| Giá doanh nghiệp | **Chỉ đổi khi nguồn công bố khác số trong bài.** Bình Long / Phú Riềng / Mang Yang thường đứng yên nhiều tuần. Mang Yang: nguồn ghi khoảng "458 - 463 (loại 2-loại 1)" → loại 1 = số lớn, loại 2 = số nhỏ |
| Bà Rịa | Nguồn chỉ có 3 số: mủ nước TSC 25–<30 (→ ô "Mủ nước TSC 25 đến dưới 30"), mủ đông DRC (35 - 44%) (→ ô "Mủ đông DRC 35 - 45%", **giữ nguyên chữ "35 - 45%"**, ghi cần duyệt), "mủ nguyên liệu" (**không** gán cho ô "Mủ chén hoặc mủ đông DRC từ 50% trở lên" vì không rõ cùng loại → giữ nguyên + cần duyệt) |
| TOCOM RSS3 (nay là sàn OSE/JPX) | **Giá thanh toán chính thức JPX** – file `rb_eYYYYMMDD.csv` ở https://www.jpx.co.jp/english/markets/derivatives/settlement-price/index.html (dòng `FUT_RSS3_…`). Đối chiếu với bảng "JPX Rubber" trên giacaphe.com (lần đầu khớp hết). Chữ "TOCOM" trong bài giữ nguyên |
| SHFE, SGX TSR20 | Bảng giacaphe.com https://giacaphe.com/gia-cao-su-truc-tuyen/ (trang vẽ bằng JavaScript → `lay_gia_the_gioi.js` mở bằng Chromium), cột "Giá khớp". Luôn ghi cần duyệt: là giá khớp lúc lấy, chưa chắc là giá chốt phiên |
| Kỳ hạn | Mỗi sàn giữ đúng 5 dòng; lấy 5 kỳ hạn đầu tiên nguồn đang liệt kê; kỳ đã đáo hạn thì cuộn lên (đổi cả nhãn). Nhãn giữ kiểu bài: TOCOM/SHFE `1/27` (tháng không số 0), SGX `1/2027` |
| Cách viết số | Trong nước: `540 VND/TSC/kg`, `18,000 VND/kg` (dấu nghìn phẩy, giữ đơn vị). TOCOM/SGX: `462,60` (2 số lẻ, **dấu phẩy thập phân**). SHFE: `18,130` (dấu nghìn phẩy). Công cụ chung sẽ cảnh báo "khác cách viết của bài" ở các ô TOCOM/SGX — bình thường, bỏ khỏi báo cáo |
| Ngày trong bài | Công cụ chung tự đổi (6 chỗ). Chạy từ 15h → ghi ngày hôm sau |
| Tên file Docs | `Cập nhật giá cao su trong nước và thế giới ngày – dd/mm/yyyy` (đã khai `ten_file` trong `cau-hinh.json`); trùng tên → thêm ` (cập nhật HHhMM)` |
| Lỗi có sẵn trong bài (không sửa chữ, chỉ báo) | Mang Yang "Mủ đông tạp loại 1/2" ghi `VND/kg` nhưng giá ~400 là giá theo độ DRC; đơn vị SHFE ghi trong ngoặc "(NDT/tấn)"; nhãn kỳ hạn SGX khác kiểu với 2 sàn kia |
| Câu văn, đoạn phân tích | Giữ nguyên, không viết lại |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-cao-su
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia_the_gioi.js cap-nhat/gia-the-gioi.json   # SHFE, SGX (+ JPX để đối chiếu)
python3 -I $CT/lay_gia.py cap-nhat          # -> cap-nhat/gia.json (trong nước + JPX + SHFE + SGX); đọc mọi dòng THIẾU / LƯU Ý
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json   # phải ra "khớp hết"
```

Đọc bằng mắt `cau_goc` trong `gia.json` (câu gốc của nguồn) để chắc bài nguồn đúng ngày và không đổi cách viết.
Sau đó **Bước 5 – 6 trong `SKILL.md`**: tạo Docs từ `cap-nhat/tam/bai1.min.html`, tải về chạy `soat` (phải `dòng lệch: 0`),
chạy `bao-cao` với `--ghi-chu` ghi rõ: link bài doanhnghiephoinhap + giờ cập nhật, file JPX + ngày, giờ "Cập nhật" của giacaphe.com.
Vì `tham_khao` để trống (nguồn do script tự lấy), báo cáo không tự liệt kê nguồn — phải nằm trong `--ghi-chu`.
Lưu `cau-hinh.json`, `sua.json`, `gia.json`, `bao-cao.md` vào `/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-cao-su/`.

## 3. Khi có trục trặc

| Hiện tượng | Làm gì |
|---|---|
| `lay_gia.py` báo `THIẾU giá trong nước: …` | doanhnghiephoinhap đổi câu chữ → đọc bài nguồn bằng mắt, tự ghi `sua.json`, sửa mẫu câu trong `doc_trong_nuoc` |
| Bài doanhnghiephoinhap mới nhất cũ hơn hôm qua | Giữ nguyên bảng trong nước, ghi cần duyệt; có thể tìm "giá cao su hôm nay" trên báo khác (nongnghiepmoitruong.vn chặn 403 từ máy chủ) |
| `lay_gia_the_gioi.js` báo `KHÔNG đọc được đủ 3 bảng` | Chạy lại 1 lần; vẫn lỗi → giacaphe.com đổi giao diện (`table[data-exchange=shz_rubber / str20_rubber / rubber_tocom]`), giữ nguyên SHFE/SGX, ghi cần duyệt |
| `LƯU Ý TOCOM … JPX ≠ giacaphe` | Dùng số JPX (giá chính thức), ghi vào báo cáo |
| Bài TCB đổi số dòng / tên doanh nghiệp | `tao_sua.py` ghi "nguồn không có mục khớp" → thêm vào bảng `TRONG_NUOC` trong script |

## 4. File trong thư mục

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài + tên file Docs |
| `lay_gia_the_gioi.js` | Mở giacaphe.com bằng Chromium, lấy 3 bảng kỳ hạn (TOCOM, SHFE, SGX) ra JSON |
| `lay_gia.py` | Tìm bài doanhnghiephoinhap mới nhất (giá trong nước) + tải giá thanh toán JPX; gộp với kết quả JS thành `gia.json` |
| `tao_sua.py` | So 2 bảng trong bài với `gia.json` → tự viết `sua.json` (kể cả cuộn kỳ hạn + mục cần duyệt); `--kiem` để soát sau khi sửa |

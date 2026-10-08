# Công thức: cập nhật bài "1 chỉ vàng bao nhiêu tiền? Giá vàng 24K, 18K, 9999 hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/1-chi-vang-bao-nhieu-tien — làm lần đầu 07/10/2026.
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài 1 chỉ vàng"* — **không hỏi gì thêm**.

## 1. Đã chốt

| Bảng trong bài | Nguồn |
|---|---|
| 1. Vàng thị trường 24K + giá nguyên liệu 22K/18K/14K/10K | https://huythanhjewelry.vn/gia-vang-hom-nay (bảng có đúng cấu trúc Huy Thanh) |
| 2.1 SJC (12 dòng) | https://webgia.com/gia-vang/sjc/ — khu vực Hồ Chí Minh (sjc.com.vn chặn máy chủ) |
| 2.2 Bảo Tín Minh Châu | https://webgia.com/gia-vang/bao-tin-minh-chau/ — nguồn không có giá bán → ghi "Liên hệ" |
| 2.3 Phú Quý | https://phuquygroup.vn/ |
| 2.4 DOJI | https://banggia.doji.vn/gold-price (nghìn đ/chỉ ×1000). "KNT + KTT + Kim Giáp" ↔ "KIM TT/AVPL". Dòng 16K, 15K: DOJI không còn niêm yết → giữ nguyên, báo cần duyệt |
| 2.5 PNJ | https://www.pnj.com.vn/site/gia-vang (×1000). "Vàng trang sức 990" ↔ "Vàng nữ trang 9920" |
| 3. Giá vàng thế giới | https://giavang.org/the-gioi/ — USD/ounce (bài ghi số lẻ như `4,124.80` → ghi đúng 2 số lẻ của nguồn; bài ghi số tròn `4,121` → làm tròn) + giá 1 lượng quy đổi của nguồn; nguồn dùng **tỷ giá Vietcombank** → câu ghi "theo tỷ giá Vietcombank" (Trang đã chỉ nguồn này 07/10/2026) |
| Chú thích ảnh | "Vàng miếng SJC vẫn có giá trên 14 vào ngày dd.mm.yyyy" → ngày hôm nay (nếu giá bán SJC còn > 14 triệu); "Vàng Rồng Thăng Long niêm yết giá X VND 1 chỉ vào ngày …" → giá bán trang sức Rồng Thăng Long 999.9 + hôm nay. Chỉ sửa chữ hiện dưới ảnh, không sửa chữ thay thế ảnh |
| Ghép dòng | Bảng `KHOP` trong `tao_sua.py` (tên dòng trong bài ↔ tên dòng ở nguồn) |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy`; trùng → thêm ` (cập nhật HHhMM)` |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/1-chi-vang
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y)   # ngày ghi trong bài: chạy từ 15h trở đi -> ngày hôm sau

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_bang.js cap-nhat/bang-nguon.json       # 6 trang, ~2–4 phút
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --nguon cap-nhat/bang-nguon.json --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --nguon cap-nhat/bang-nguon.json   # "khớp hết"
```

File HTML dài (~35 nghìn ký tự): in theo đoạn 12000 ký tự rồi ghép khi tạo Docs. Rồi Bước 5 – 6 của `SKILL.md`.
Lưu kết quả vào `/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-1-chi-vang/`, commit + push.

## 3. File

| File | Làm gì |
|---|---|
| `lay_bang.js` | Mở 7 trang (6 bảng + giavang.org thế giới) bằng Chromium, lấy mọi dòng bảng + giờ cập nhật → `bang-nguon.json` |
| `tao_sua.py` | Ghép dòng theo `KHOP`, đổi số 6 bảng, trả lại ngày mục 3 → `sua.json`; `--kiem`; `--bo-to-ngay-the-gioi` |

# Công thức: cập nhật bài "Giá vàng nhẫn hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-vang-nhan-hom-nay — công thức dựng 06/11/2026.
Chạy bằng bộ chung, không cần Claude: `bash cong-cu/tu-dong/chay.sh gia-vang-nhan <thư mục ra>` (khung chung "*)" của `chay.sh`).
Mã công thức: `gia-vang-nhan`. Cần Playwright: `NODE_PATH=/opt/node22/lib/node_modules`.

## 1. Nguồn và ghép dòng (theo TÊN dòng, không theo thứ tự)

| Dòng trong bài | Nguồn | Dòng nguồn (tên ô đúng như trang) |
|---|---|---|
| SJC - nhẫn 99.99% loại 1-5 chỉ | https://webgia.com/gia-vang/sjc/ | `Vàng nhẫn SJC 99,99% 1 chỉ, 2 chỉ, 5 chỉ` |
| PNJ - nhẫn trơn 999.9 | https://www.pnj.com.vn/site/gia-vang | `Nhẫn Trơn PNJ 999.9` |
| DOJI - nhẫn tròn 9999 Hưng Thịnh Vượng | https://banggia.doji.vn/gold-price | `NHẪN TRÒN 9999 HƯNG THỊNH VƯỢNG` |
| Bảo Tín Minh Châu - nhẫn tròn trơn Vàng Rồng Thăng Long | https://webgia.com/gia-vang/bao-tin-minh-chau/ | `Nhẫn tròn trơn 999.9 (24k)` (nhóm VRTL) |
| Phú Quý - nhẫn tròn 999.9 | https://phuquygroup.vn/ | `Nhẫn tròn Phú Quý 999.9` |
| Mục 3: vàng thế giới (bài ghi "Kitco") | https://giavang.org/the-gioi/ | "Giá vàng quốc tế (XAU) hôm nay là … USD", "giảm/tăng … USD/Ounce" |

Giờ cập nhật của từng nguồn được ghi vào `cap-nhat/gia.json` (trường `cap_nhat`) và vào `ly_do` của từng chỗ sửa.
Đây là phần mở rộng từ `../1-chi-vang/lay_bang.js` (cùng cách đọc trang, chỉ lấy dòng nhẫn trơn).

## 2. Cách tính và ghi số

- Nguồn ghi VND/chỉ (webgia, Phú Quý) hoặc nghìn đ/chỉ (DOJI, PNJ) — `lay_gia.js` quy hết về VND/chỉ. **Triệu VND/lượng = VND/chỉ ÷ 100.000** (vd 13.650.000 → 136.5). Ghi **1 số lẻ** như bài; nguồn có chữ số bị làm tròn thì cần duyệt.
- **Chênh lệch = Bán ra − Mua vào**, tính từ 2 số đã ghi trong bài, 1 số lẻ (số tính ra, ghi cách tính ở `ly_do`).
- Đoạn mở mục 1 "Giá bán ra … dao động quanh mức A - B …, giá mua vào quanh mức C - D": A-B / C-D = nhỏ nhất - lớn nhất của cột Bán ra / Mua vào trong bảng **sau khi cập nhật** (số tính ra).
- Mục 3 "giá vàng giao ngay trên Kitco ở quanh mức X USD/ounce (*), giảm khoảng Y USD/ounce": X = giá XAU/USD của giavang.org làm tròn đến đơn vị, Y = biến động 24 giờ của nguồn (giá trị tuyệt đối, làm tròn). Nếu nguồn ngược chiều với chữ "giảm/tăng" của bài thì chỉ đổi X, giữ Y + cần duyệt. Giữ nguyên chữ "Kitco".
- Ngày: lệnh `dung` đổi sang ngày hôm sau (6 chỗ).

## 3. Khi nguồn hỏng / số lạ

- Thương hiệu nào nguồn hỏng: giữ nguyên dòng cũ + cần duyệt (`lay_gia.js` in "<nguồn> KHÔNG ĐỌC ĐƯỢC …" và ghi `null`).
- Hỏng cả 6 nguồn: giữ nguyên mọi giá và trả mọi ngày về ngày gốc.
- Câu "Trong phiên 23/10, … giảm … vài trăm nghìn VND/lượng": diễn biến phiên, không có nguồn → giữ nguyên + **luôn cần duyệt**.
- Mục 3 luôn có 1 dòng cần duyệt: nguồn là giavang.org chứ không phải Kitco, mốc so sánh là 24 giờ.
- Lưới an toàn: số giá (kèm triệu / VND / USD / đồng / $) ngoài bảng mà công thức không đụng và không bằng số mới → cần duyệt "SỐ GIÁ CHƯA CẬP NHẬT …".

## 4. Các bước chạy tay

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-vang-nhan
mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)
python3 -I $SKILL/scripts/cap_nhat.py lay cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia.js cap-nhat/gia.json
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "Soát: khớp hết"
```

Chưa làm (cần người của repo): thêm dòng vào Sheet "Update" và dòng trong CLAUDE.md mục 7.

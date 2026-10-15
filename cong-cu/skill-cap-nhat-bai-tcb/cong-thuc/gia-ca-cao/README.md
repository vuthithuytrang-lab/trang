# Công thức: cập nhật bài "Giá ca cao hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-ca-cao
Lập ngày 15/10/2026 (lần chạy đầu, ghi ngày 16/10/2026). Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

Bài có 3 bảng: giá trong nước (6 loại ca cao), ca cao **New York** (ICE US, USD/tấn, mã CC…, 10 dòng),
ca cao **London** (ICE Europe, GBP/tấn, mã CA…, 10 dòng).

## 1. Những gì đã chốt

| Việc | Cách làm cố định |
|---|---|
| Nguồn giá trong nước | banggianongsan.com https://banggianongsan.com/bang-gia-cacao-hom-nay/ — bảng "Giá cũ / Giá mới / Chênh lệch", đúng 6 loại như bài (Cacao tươi, Hạt cacao xô, lên men loại I/II/III, Bột cacao nguyên chất) |
| Cột "Giá hiện tại" | ← cột "Giá mới" của nguồn, giữ dạng khoảng `7,300 - 8,000` (dấu nghìn `,`, gạch ` - `) |
| Cột "Giá mới dự kiến" | **Giữ nguyên** (nguồn không có giá dự kiến) → `can_duyet` mỗi lần |
| Cột "Thay đổi" | ← "Chênh lệch" của nguồn: `-100 VND/kg`, khoảng `-2,000 - -3,000 VND/kg`; bằng 0 → `Không đổi` |
| Nguồn giá thế giới | API công khai trên trang sản phẩm ICE (đọc thẳng bằng Python, không cần trình duyệt): New York `productId=578&hubId=727` (trang https://www.ice.com/products/7/Cocoa-Futures/data), London `productId=15246&hubId=17450` (trang https://www.ice.com/products/37089076/London-Cocoa-Futures/data) |
| Giá / Thay đổi thế giới | Giá = giá khớp gần nhất (`lastPrice`); Thay đổi = giá khớp − giá chốt phiên trước (lấy từ lịch sử ngày `data/historical`) — ICE chỉ cho % nên số tuyệt đối là **tính ra** (`tinh_toan`) |
| Kỳ hạn chưa giao dịch trong ngày | Ghi giá chốt phiên gần nhất + mức đổi so với phiên trước đó, ghi `can_duyet` |
| Bảng dài hơn nguồn | ICE NY hiện chỉ niêm yết 9 kỳ hạn (tới 7/2028) → dòng cuối CCU28 giữ số cũ + `can_duyet` |
| Kỳ hạn & mã | Lấy theo thứ tự kỳ hạn của ICE; đáo hạn thì cuộn lên, mã tự đặt `CC`/`CA` + mã tháng ICE (F G H J K M N Q U V X Z) + 2 số năm; nhãn tháng dạng `3/2027` (không số 0) |
| Cách viết số | Giá `5,945`; Thay đổi `+210`, `-51` (không số lẻ); bài không có ký tự "s" |
| Giờ chạy | Sau 15h VN sàn NY (từ 15:45) / London (từ 16:30… theo ICE) đang giao dịch → giá trong phiên, ghi rõ giờ vào `--ghi-chu` + `can_duyet` |
| Lỗi có sẵn trong bài | Câu "Lưu ý" dưới bảng New York ghi "chất lượng cà phê" (nhầm sản phẩm) — không sửa chữ, chỉ báo |

### Nguồn đã thử và loại
- giacaphe.com/gia-ca-cao-truc-tuyen/ (mở bằng Chromium): bảng London hợp lý nhưng bảng New York lỗi (thay đổi +37%, nhãn kỳ hạn trùng, giá "hôm trước" lệch), chỉ 4 kỳ hạn → không dùng.
- barchart.com: trang mở được nhưng API bảng giá trả 403 → không dùng.
- chogia.vn: bài sửa lần cuối 09/10/2025, chỉ đổi ngày trên tiêu đề → số cũ, không dùng.
- giacaphehomnay.vn/gia-nong-san/gia-cacao/: cùng loại bảng (số cũ trong bài khớp đúng bảng ngày 09/10/2026 của trang này), nhưng lúc chạy mới cập nhật tới 09/10 → để dự phòng.

## 2. Các bước

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-ca-cao
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=<ngày ghi trong bài, dd/mm/yyyy>

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json        # bài TCB + banggianongsan (thamkhao1)
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $CT/lay_gia_ice.py cap-nhat/gia-ice.json                      # giá ICE NY + London
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
# --bgns: trang banggianongsan dạng HTML gốc (cap-nhat/tam/thamkhao1.goc, hoặc tự tải bằng curl)
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --bgns cap-nhat/tam/thamkhao1.goc \
        --ice cap-nhat/gia-ice.json --ra cap-nhat/sua.json --gia cap-nhat/gia.json
python3 -I $SKILL/scripts/cap_nhat.py sua cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --bgns cap-nhat/tam/thamkhao1.goc --ice cap-nhat/gia-ice.json   # phải "khớp hết"
```

Rồi làm Bước 5 – 6 của `SKILL.md` (tạo Docs từ `cap-nhat/tam/bai1.min.html`, `soat` phải ra `dòng lệch: 0`, `bao-cao`).
Lần đầu (16/10/2026): soát ra Ảnh 2/2, dòng bảng 31/31, dòng lệch 0, ô vàng 51/51.

## 3. Khi có trục trặc

| Hiện tượng | Làm gì |
|---|---|
| `Không đọc được bảng giá trong nước` | banggianongsan đổi giao diện → đọc trang bằng mắt, tự ghi `sua.json`; sửa hàm `doc_bgns` |
| Bảng nguồn có ngày cũ hơn số trong bài | Giữ nguyên bảng trong nước, ghi `can_duyet` |
| `lay_gia_ice.py` lỗi / trả `[]` | ICE đổi mã sản phẩm: mở trang sản phẩm bằng Chromium, xem yêu cầu `contract-data?productId=…&hubId=…` trong mạng rồi sửa `SAN` |
| `--kiem` báo ô lệch | Đọc `xem2.txt`, sửa `sua.json` bằng tay, chạy lại `sua` |

## 4. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài + nguồn banggianongsan (tham khảo) |
| `lay_gia_ice.py` | Lấy mọi kỳ hạn ca cao NY + London từ ICE: giá khớp, giờ, giá chốt phiên trước |
| `tao_sua.py` | So 3 bảng trong bài với số mới → tự viết `sua.json` + `gia.json`; `--kiem` để soát lại |

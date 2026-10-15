# Công thức: cập nhật bài "Giá cà phê sàn London và New York mới nhất hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-ca-phe-san-luan-don-hom-nay
Viết lần đầu ngày 15/10/2026 (chạy cho ngày 16/10/2026). Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`,
dùng chung script lấy giá `../gia-ca-phe/lay_gia_the_gioi.js` với bài "Giá cà phê hôm nay".

Trang chỉ cần nhắn *"Update bài giá cà phê sàn London New York"* (hoặc dán link). **Không hỏi gì thêm.**

## 1. Những gì đã chốt

| Việc | Cách làm cố định |
|---|---|
| Nguồn 2 bảng | giacaphe.com trực tuyến https://giacaphe.com/gia-ca-phe-truc-tuyen/ (Robusta London + Arabica New York), đọc bằng Chromium qua `lay_gia_the_gioi.js` |
| Bảng Robusta (Tháng đáo hạn \| Giá (USD/tấn) \| Thay đổi so với phiên trước) | 5 kỳ hạn đầu tiên đang giao dịch. Tháng ghi `11/2026`; giá **dấu chấm nghìn** `3.441`; thay đổi `-42 USD/tấn` / `+15 USD/tấn` |
| Bảng Arabica (Tháng đáo hạn \| Giá (cent/pound) \| Thay đổi …) | 5 kỳ hạn đầu tiên. Tháng `12/2026`; giá 2 số lẻ `294.00`; thay đổi `-4.05 cent/pound` |
| Kỳ hạn đã đáo hạn | Cuộn lên theo nguồn (đổi cả ô tháng). Bảng này **không có cột mã hợp đồng** và **không có ký tự "s"** |
| Thay đổi bằng 0 | Bài chưa có mẫu → ghi `0 USD/tấn` / `0.00 cent/pound` và `can_duyet` |
| Giờ chạy | Chạy trong giờ sàn (15:00 – 01:30 giờ VN) → giá đang giao dịch, script tự ghi `can_duyet`; ghi rõ giờ lấy số trong `--ghi-chu` |
| Lỗi có sẵn trong bài (không sửa, chỉ báo) | Câu "Lưu ý" dưới 2 bảng nói về chất lượng/sản lượng thu mua từng khu vực (câu của giá trong nước); link ẩn tới ice.com có đuôi `utm_source=chatgpt.com` ở cuối đoạn mở đầu mục 3 |
| Ngày trong câu chữ | Công cụ chung tự đổi |
| Tên file Docs | `Giá cà phê sàn London và New York mới nhất hôm nay – dd/mm/yyyy`; trùng tên → thêm ` (cập nhật HHhMM)` |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-ca-phe-london-new-york
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
NODE_PATH=/opt/node22/lib/node_modules node $CT/../gia-ca-phe/lay_gia_the_gioi.js cap-nhat/gia-the-gioi.json
#   (chạy cùng đợt với bài "Giá cà phê hôm nay" thì dùng chung một file gia-the-gioi.json cho 2 bài, số khớp nhau)
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --the-gioi cap-nhat/gia-the-gioi.json \
        --html cap-nhat/tam/bai1.dung.min.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --the-gioi cap-nhat/gia-the-gioi.json   # phải ra "khớp hết"
```

Sau đó làm **Bước 5 – 6 của `SKILL.md`** (tạo Docs từ `cap-nhat/tam/bai1.min.html`, `soat` phải `dòng lệch: 0`, `bao-cao`).
Lưu `cau-hinh.json`, `sua.json`, `gia.json` (số liệu thô = `gia-the-gioi.json`), `bao-cao.md` vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-ca-phe-london-new-york/`.

## 3. Khi có trục trặc

| Hiện tượng | Làm gì |
|---|---|
| `lay_gia_the_gioi.js` báo `KHÔNG đọc được bảng` | Chạy lại 1 lần; vẫn lỗi → giữ nguyên 2 bảng, báo lại |
| `Thiếu bảng robusta/arabica: bài có 0 dòng` | Techcombank đổi bài (script nhận dòng bảng theo ô đầu `mm/yyyy` + ô cuối kết thúc bằng `USD/tấn` / `cent/pound`) → dừng, đọc `xem.txt` |
| `--kiem` báo ô lệch | Đọc `xem2.txt`, sửa `sua.json` bằng tay rồi chạy lại `sua` |

## 4. File trong thư mục

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài (không cần nguồn tải bằng `lay` — giá lấy bằng trình duyệt) |
| `tao_sua.py` | So 2 bảng với `gia-the-gioi.json` → viết `sua.json`; `--kiem` để soát lại |

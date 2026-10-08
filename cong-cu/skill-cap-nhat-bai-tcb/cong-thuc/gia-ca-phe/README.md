# Công thức: cập nhật bài "Giá cà phê hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-ca-phe-hom-nay
Đóng gói ngày 07/10/2026 theo yêu cầu của Trang: **"lần sau đừng hỏi lại, tôi gửi link là làm"**.

Trang chỉ cần nhắn: *"Update bài giá cà phê"* (hoặc dán link bài). **Không hỏi gì thêm** — mọi lựa chọn đã chốt ở mục 1.
Công thức này chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/` (skill "Cập nhật bài Techcombank").

## 1. Những gì đã chốt — KHÔNG hỏi lại Trang

| Việc | Cách làm cố định |
|---|---|
| Nguồn giá trong nước (5 vùng) | Nhà Bè Agri https://nhabeagri.com/gia-nong-san/gia-ca-phe/ — lấy đúng giá + mức tăng/giảm từng vùng |
| Dòng Tây Nguyên | Ghi **một mức** đúng như nguồn (vd `94,200`), không ghi khoảng |
| Cột "Thay đổi" trong nước | `+400`, `-200`; bằng 0 thì ghi `Không đổi` |
| Nguồn giá thế giới | giacaphe.com trực tuyến https://giacaphe.com/gia-ca-phe-truc-tuyen/ (Robusta London + Arabica New York) |
| Kỳ hạn | Lấy 5 kỳ hạn đầu tiên đang giao dịch; kỳ hạn cũ đã đáo hạn thì cuộn lên. Mã hợp đồng tự đặt theo mã tháng sàn ICE (RM/KC + F G H J K M N Q U V X Z + 2 số năm) |
| Ký tự "s" (giá chốt phiên) | Chạy **ngoài giờ sàn** (trước 15:00 giờ VN) → giá là giá đóng cửa phiên trước → **có "s"**. Chạy **trong giờ sàn** (15:00 – 01:30) → giá đang giao dịch → **không "s"**, ghi vào mục cần duyệt |
| Cách viết số | Robusta `3,646` / `+56`; Arabica `305.95` / `+1.50` (2 số lẻ) — giống bài gốc |
| Ngày trong bài | Tự đổi sang hôm nay (công cụ chung làm) |
| Lỗi chính tả "Tây Nuy" trong bài gốc | Không sửa câu chữ, chỉ nhắc trong báo cáo |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy`; nếu tên đó đã có trong Drive → thêm ` (cập nhật HHhMM)`, **không** hỏi, **không** xóa file cũ |
| Câu văn, đoạn phân tích | Giữ nguyên, không viết lại |

Trang đưa nguồn khác hoặc dặn khác trong tin nhắn → làm theo tin nhắn, rồi hỏi có muốn sửa công thức này luôn không.

## 2. Các bước cho Claude (chạy y nguyên)

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-ca-phe
cd <thư mục nháp>  && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y)   # ngày ghi trong bài: chạy từ 15h trở đi -> ngày hôm sau

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json            # bài TCB + Nhà Bè Agri
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia_the_gioi.js cap-nhat/gia-the-gioi.json   # mở trình duyệt đọc giá thế giới
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --nha-be cap-nhat/tam/thamkhao1.goc \
        --the-gioi cap-nhat/gia-the-gioi.json --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --nha-be cap-nhat/tam/thamkhao1.goc \
        --the-gioi cap-nhat/gia-the-gioi.json                                 # phải ra "khớp hết"
```

Sau đó làm tiếp **Bước 5 – 6 trong `SKILL.md`** của bộ công cụ chung: tạo Google Docs từ `cap-nhat/tam/bai1.min.html`
(đặt tên theo mục 1), tải về chạy `soat` (phải ra `dòng lệch: 0`), chạy `bao-cao`.
Lưu `cau-hinh.json`, `sua.json`, `gia-the-gioi.json`, `bao-cao.md` vào `/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-ca-phe/`,
commit + push. Báo Trang bằng lời thường: link file, bảng tóm tắt 3 bảng (nguồn + giờ lấy số), mục cần duyệt, 2 câu hỏi cuối.

## 3. Khi có trục trặc

| Hiện tượng | Làm gì |
|---|---|
| `tao_sua.py` báo `LỖI: Không đọc được bảng giá trong nước` | Nhà Bè Agri đổi giao diện → đọc `cap-nhat/tam/thamkhao1.txt` bằng mắt, tự ghi `sua.json`, báo Trang; sửa lại hàm `doc_nha_be` |
| `lay_gia_the_gioi.js` báo `KHÔNG đọc được bảng` | Chạy lại 1 lần; vẫn lỗi → giacaphe.com đổi giao diện, báo Trang và giữ nguyên 2 bảng thế giới |
| `Thiếu bảng robusta/arabica: bài có 0 dòng` | Techcombank đổi cấu trúc bài → dừng, báo Trang |
| `--kiem` báo ô lệch | Đọc `xem2.txt`, sửa `sua.json` bằng tay rồi chạy lại `sua` |
| Không vào được techcombank.com | Theo mục "Khi bị chặn" trong `SKILL.md` |

## 4. File trong thư mục

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài + nguồn Nhà Bè Agri (cho công cụ chung) |
| `lay_gia_the_gioi.js` | Mở giacaphe.com bằng trình duyệt Chromium có sẵn, lấy bảng Robusta + Arabica ra JSON |
| `tao_sua.py` | So 3 bảng trong bài với số mới → tự viết `sua.json`; `--kiem` để soát lại sau khi sửa |

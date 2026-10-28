# Công thức: cập nhật bài "Giá cà phê sàn London và New York mới nhất hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-ca-phe-san-luan-don-hom-nay — đóng gói ngày 28/10/2026
(trước đó Claude làm tay 3 lần: 21/10, 23/10, 29/10 — `cap-nhat-bai-tcb/2026-10-2x-gia-ca-phe-luan-don/`).
Trang tích ô dòng "cà phê sàn Luân Đôn" trong Sheet "Update" hoặc nhắn *"Update bài giá cà phê sàn London"* — **không hỏi gì thêm**.
Chạy được không cần Claude: `bash cong-cu/tu-dong/chay.sh gia-ca-phe-luan-don <thư mục ra>` (khung chung `*)` của chay.sh).

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Nguồn duy nhất | https://baolamdong.vn/gia-ca-phe/the-gioi — Trang chọn. Mục "Bảng giá cà phê Robusta và Arabica hôm nay": bảng **Robusta London** và bảng **Arabica New York** |
| Lấy hợp đồng nào | **Luôn lấy 5 hợp đồng hiển thị đầu tiên** của mỗi bảng (Trang chốt). Dòng thứ i trong bảng của bài = hợp đồng thứ i trên nguồn. Hợp đồng gần nhất đáo hạn, nguồn bỏ đi → bảng tự **cuộn**: đổi luôn ô "Tháng đáo hạn" (tô vàng) + tự ghi cần duyệt |
| Bảng nào là bảng nào | Nhận theo đơn vị ở dòng tiêu đề của bảng trong bài: "USD/tấn" = Robusta London, "cent/pound" = Arabica New York (không theo vị trí); thiếu đơn vị thì theo đề mục ngay trên bảng (London/Robusta, New York/Arabica) |
| Ô "Giá" | Cột **Giá khớp** của nguồn, viết theo cách bài đang viết ở chính ô đó: Robusta `3.197` (chấm phân cách nghìn), Arabica `284.65` (chấm thập phân, 2 số lẻ). Nguồn ghi kiểu Việt Nam (`284,65`) → tự đổi |
| Ô "Thay đổi so với phiên trước" | Mức tăng/giảm nguồn ghi ngay cạnh giá khớp (↑ tăng / ↓ giảm / — Không đổi). Ghi `+23 USD/tấn` khi tăng, `-23 USD/tấn` khi giảm (đúng cách bài và 3 lần làm tay), `0 USD/tấn` khi nguồn ghi "Không đổi" (tự ghi cần duyệt để Trang xem cách ghi). Số lẻ như ô giá cùng bảng (`-9.10 cent/pound`). Đơn vị giữ nguyên chữ của bài |
| Soát chéo | Tự kiểm "giá khớp − hôm trước = mức thay đổi" trên nguồn; lệch → vẫn dùng mức nguồn ghi + cần duyệt |
| Ngày dd/mm/yyyy trong bài (sapo, ngày đăng, đề mục 1, "dữ liệu … được cập nhật ngày") | Công cụ chung `dung` đổi sang **ngày hôm sau** (quy tắc chung) |
| Nguồn hỏng | Sàn nào không đọc được → giữ nguyên cả bảng sàn đó + cần duyệt. Cả hai sàn hỏng → câu "dữ liệu tham khảo được cập nhật ngày …" trả về ngày gốc của bài (để bài không ghi ngày mới cho giá cũ) + cần duyệt |
| Giá ngoài 2 bảng | Hiện bài chỉ có giá trong 2 bảng. Nếu bài thêm câu có "USD/tấn"/"cent/pound" ngoài bảng → tự ghi cần duyệt "chưa có công thức – sửa tay" (quy tắc: mọi giá trong bài phải cập nhật) |
| Luôn ghi cần duyệt | Giờ cập nhật của nguồn + trạng thái thị trường lúc đó ("đang giao dịch" = giá trong phiên, có thể còn đổi) |
| Tên file Docs | `Giá cà phê sàn London và New York mới nhất hôm nay – dd/mm/yyyy` (như các lần làm tay) |

Không lấy số từ bảng "Giá cà phê thế giới theo ngày" của nguồn (các lần làm tay đều thấy bảng đó lệch với bảng theo kỳ hạn).
Mọi con số ghi vào bài đều lấy thẳng từ trang nguồn tải về trong lần chạy đó — không có số đặt sẵn, không ước lượng.

## 2. Các bước

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-ca-phe-luan-don
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # LUÔN ghi ngày hôm sau (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json                 # tải bài + trang nguồn (tam/thamkhao1.goc)
python3 -I $CT/lay_gia.py cap-nhat/gia.json                                        # đọc 5 hợp đồng đầu mỗi sàn từ thamkhao1.goc
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

`Robusta London KHÔNG ĐỌC ĐƯỢC` / `Arabica New York KHÔNG ĐỌC ĐƯỢC` → bảng đó giữ giá cũ (tự ghi cần duyệt).
Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs từ `bai1.min.html`, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-ca-phe-luan-don/`, commit + push.

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài + trang nguồn (`tham_khao`) cho công cụ chung — công cụ chung tải trang nguồn, công thức không tự tải mạng |
| `lay_gia.py` | Đọc `cap-nhat/tam/thamkhao1.goc` (HTML tĩnh, chỉ thư viện có sẵn của Python): 5 hợp đồng đầu mỗi bảng (kỳ hạn, giá khớp, tăng/giảm, hôm trước) + giờ cập nhật + trạng thái thị trường → `gia.json` |
| `tao_sua.py` | 2 bảng (tháng đáo hạn, giá, thay đổi) → `sua.json`; trả ngày "được cập nhật ngày" khi không có giá mới; `--kiem` soát lại |

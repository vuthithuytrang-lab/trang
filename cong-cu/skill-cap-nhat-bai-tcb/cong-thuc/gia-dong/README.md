# Công thức: cập nhật bài "Giá đồng hôm nay trực tuyến & các yếu tố tác động đến thị trường" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-dong-hom-nay — đóng gói 28/10/2026 (trước đó Claude làm tay 21, 23, 29/10/2026).
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài giá đồng"* — **không hỏi gì thêm**.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`, tự chạy được bằng `cong-cu/tu-dong/chay.sh gia-dong` (nhánh chung `*)`).

> ⛔ Không bịa số: mọi số ghi vào bài lấy thẳng từ trang nguồn tải trong lần chạy đó. Nguồn lỗi → giữ số cũ + cần duyệt.

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Nguồn giá phế liệu (Trang chọn) | https://thumuaphelieugiacao24h.vn/gia-dong-phe-lieu-hom-nay/ — bảng có ô đầu "Loại đồng" (Đồng cáp, Đồng đỏ, Đồng cháy, Đồng vàng; VND/kg). Tải bằng `curl` như công cụ chung. Ngày sửa trang lấy ở `article:modified_time` |
| Nguồn giá thế giới (Trang chọn) | https://www.barchart.com/futures/quotes/HG*0/futures-prices?viewName=main — **chặn máy chủ** (tải thường HTTP 202, trình duyệt bị CloudFront chặn 403). Công thức **không vượt chặn** → `the_gioi = null`, bảng 1.2 giữ nguyên + cần duyệt. Nguồn thay thế chính chủ (cmegroup.com) cũng ngắt kết nối từ máy chủ (28/10/2026) |
| Bảng 1.1 – khớp dòng | Theo **tên** loại đồng. Bài có 2 dòng "Đồng cháy" (dòng 4 nguồn ghi "Đồng vàng"): dòng trùng tên thứ hai lấy dòng nguồn **cùng vị trí** nếu tên đó không có trong bài → lấy giá "Đồng vàng", **giữ tên trong bài** + cần duyệt |
| Bảng 1.1 – cách viết | Giữ đúng dấu nghìn của chính ô cũ (dòng 1–2 `155,000 - 250,000`, dòng 3–4 `130.000 - 180.000`) và gạch nối cũ `" - "`. Bài trộn 2 kiểu → cần duyệt nhắc thống nhất |
| Bảng 1.2 – hợp đồng kỳ hạn | Bài ghi **ALIV2026 … ALIN2027** = mã hợp đồng **NHÔM** (ALI), không phải đồng (HG, USD/pound). Chỉ cập nhật khi nguồn đọc được **và cùng mã gốc**; khớp từng dòng theo mã (ALIV2026 ≙ …V26), giữ số lẻ của ô cũ, % ghi dấu `+/-`. Hợp đồng không còn trên nguồn → giữ dòng + cần duyệt. Đổi mã/đơn vị là đổi nội dung → **chờ Trang chốt** |
| Ngày ở tiêu đề | Công cụ chung (`dung`) đổi mọi ngày sang ngày mai. Bảng nào **không** cập nhật được → `tao_sua.py` trả ngày ở tiêu đề của bảng đó ("1.1. Bảng giá đồng phế liệu…", "1.2. Bảng giá đồng thế giới…") về **ngày gốc của bài**, để không ghi ngày mới cho giá cũ (nếu bài gốc đã ghi ngày mai thì không có gì để trả) |
| Phần phân tích (25% năm 2035; 26.7 → 34.1 triệu tấn; năm 2025) | Không có trong nguồn được chọn → giữ nguyên + cần duyệt |
| Nguồn phế liệu cũ | Trang nguồn sửa lần cuối hơn 7 ngày (đang là 04/05/2026) → cần duyệt nhắc biên tập |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-dong
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # ngày ghi trong bài: LUÔN là ngày hôm sau (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 -I $CT/lay_gia.py cap-nhat/gia.json
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

Hoặc gọn: `bash cong-cu/tu-dong/chay.sh gia-dong <thư mục ra>`.
Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet).

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia.py` | Tải bảng "Loại đồng" của nguồn phế liệu → `gia.json` (`phe_lieu`: tên, giá thấp/cao, chữ gốc, ngày sửa trang); `the_gioi` = null (Barchart chặn) |
| `tao_sua.py` | Bảng 1.1 + bảng 1.2 (khi có nguồn cùng mã) + trả ngày tiêu đề khi bảng không cập nhật được → `sua.json`; `--kiem` soát lại |

## 4. Khi Trang chốt bảng 1.2

- Giữ **nhôm ALI**: cần nguồn hợp đồng nhôm COMEX đọc được từ máy chủ; ghi `the_gioi = {"goc": "ALI", "don_vi": "USD/tấn", "hop_dong": [{"ma": "ALIZ26", "gia": …, "thay_doi_pt": "-0.25%", "dong": "<chữ gốc>"}], "cap_nhat": …, "nguon": …}` trong `lay_gia.py` — `tao_sua.py` đã sẵn sàng.
- Đổi sang **đồng HG**: là đổi nội dung bài (mã + đơn vị) → biên tập sửa bài trên web trước, công thức tự khớp theo mã HG khi có nguồn đọc được.

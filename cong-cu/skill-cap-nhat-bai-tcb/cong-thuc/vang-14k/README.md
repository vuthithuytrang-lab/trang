# Công thức: cập nhật bài "Vàng 14K giá hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/vang-14k-gia-hom-nay — làm lần đầu 07/10/2026.
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài vàng 14K"* — **không hỏi gì thêm**.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| SJC – Nữ trang 58.3% | https://webgia.com/gia-vang/sjc/ dòng "Nữ trang 58,3%" (sjc.com.vn chặn máy chủ) |
| PNJ – Vàng 585 (14K) | https://www.pnj.com.vn/site/gia-vang dòng "Vàng 585 (14K)" (1.000đ/chỉ) |
| Huy Thanh – Vàng 585 (14K) | https://huythanhjewelry.vn/gia-vang-hom-nay dòng "Giá nguyên liệu 14K" (trang chỉ có dòng 14K này) |
| Đơn vị trong bảng | **triệu VND/lượng** = giá đ/chỉ × 10 ÷ 1.000.000; dấu chấm thập phân, bỏ số 0 cuối (`72.853`, `72.88`, `85`) |
| Khoảng giá tóm tắt (2 đoạn) | Tính trên **SJC + PNJ** như bài gốc: thấp nhất giá mua – cao nhất giá bán; theo chỉ = ÷10, 2 số lẻ |
| "Mức chênh lệch giữa chiều mua vào và bán ra khoảng X - Y triệu VND/lượng" | Cũng **SJC + PNJ**: (bán − mua) từng hãng × 10 chỉ, ra triệu/lượng, 1 số lẻ; X = nhỏ nhất, Y = lớn nhất. Số tính ra trùng số cũ thì không đổi (vd 28/10/2026: SJC 9.8, PNJ 9.9 – đúng như bài) |
| Mục 2 – ví dụ nhẫn 1.2 chỉ | Giá bán tham khảo = **cận trên của khoảng tóm tắt** (cao nhất giá bán SJC + PNJ, đúng số đ/chỉ của nguồn, không làm tròn) – khớp chữ "dựa trên mức giá thị trường chung" và khớp số "… - Y triệu VND/chỉ" ở đầu bài; thường là PNJ 585. Tính lại "Giá trị phần vàng" (= số chỉ trong bài × giá) và "Tổng giá trị" (+ tiền công + tiền đá). **Tiền công 500,000, tiền đá 300,000 là giả định của bài → giữ nguyên** |
| Đoạn "1.1. Xu hướng giá vàng 14K gần đây" | Nguồn lịch sử: API công khai của PNJ `https://edge-api.pnj.io/ecom-frontend/v1/get-gold-price-history?date=yyyymmdd` (cùng hệ thống với bảng giá pnj.com.vn; nhóm "Giá vàng nữ trang", dòng "Vàng 585 (14K)", đơn vị ngàn đồng/lượng). **Giá đóng phiên** = lần cập nhật cuối trong ngày; ngày không có phiên (chủ nhật, lễ) → lùi về phiên gần nhất trước đó. Ngày trong câu = phiên mới nhất có dữ liệu. "so với phiên trước" = chênh triệu/lượng với phiên liền trước; "7 ngày" = so với phiên ngày (mới nhất − 7); "1 tháng" = cùng ngày tháng trước; "cùng kỳ năm trước" = cùng ngày năm trước; % = (mới ÷ cũ − 1) × 100. Số lẻ giữ đúng như số cũ (0.64 → 2 số lẻ, 1.1% → 1 số lẻ). Chữ chỉ chiều **giảm/tăng**, **cao/thấp hơn** đổi theo dấu của số (là chiều của chính con số, không phải đổi nội dung) – có đổi thì tự ghi cần duyệt để đọc lại câu. Ngày trùng ngày gốc của bài → bỏ tô vàng ngày. Không đọc được lịch sử → như cũ: giữ nguyên số + ngày gốc, ghi cần duyệt |
| Ngày dd/mm/yyyy khác trong bài | Công cụ chung tự đổi sang hôm nay |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy`; trùng → thêm ` (cập nhật HHhMM)` |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/vang-14k
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # ngày ghi trong bài: LUÔN là ngày hôm sau, không cần biết mấy giờ (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia_14k.js cap-nhat/gia-14k.json     # mở trình duyệt đọc 3 nguồn + lịch sử giá PNJ
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia-14k.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $CT/tao_sua.py --xem - --gia - --goc cap-nhat/tam/bai1.html --bo-to-ngay-xu-huong cap-nhat/tam/bai1.min.html   # ngày đoạn Xu hướng trùng ngày gốc → bỏ tô vàng
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia-14k.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

Nguồn nào `KHÔNG ĐỌC ĐƯỢC` → dòng đó giữ giá cũ (tự ghi cần duyệt); thiếu SJC hoặc PNJ → khoảng tóm tắt, chênh lệch và ví dụ mục 2 giữ nguyên;
`lịch sử PNJ KHÔNG ĐỌC ĐƯỢC` → đoạn Xu hướng giữ nguyên số + ngày gốc (tự ghi cần duyệt).
Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs từ `bai1.min.html`, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-vang-14k/`, commit + push.

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia_14k.js` | Mở 3 trang bằng Chromium, lấy giá mua/bán 14K (đ/chỉ) + giờ cập nhật; đọc lịch sử giá PNJ 585 (5 mốc: mới nhất, phiên trước, 7 ngày, 1 tháng, cùng kỳ – khóa `_lich_su_pnj`, đ/lượng) → `gia-14k.json` |
| `tao_sua.py` | Bảng giá + khoảng tóm tắt + chênh lệch mua–bán + ví dụ mục 2 + đoạn Xu hướng → `sua.json`; `--kiem` soát lại tất cả; `--bo-to-ngay-xu-huong` (kèm `--goc`) bỏ tô vàng ngày đoạn Xu hướng khi ngày trùng bài gốc |

Quy tắc chung (Trang dặn 29/10/2026): **mọi giá trong bài đều phải cập nhật** – bảng, đoạn tóm tắt, ví dụ, đoạn xu hướng. Bài đổi câu chữ
khiến công thức không nhận ra một con số giá → con số đó sẽ còn sót: đọc lại `xem2.txt` mỗi lần chạy.

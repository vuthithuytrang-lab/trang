# Công thức: cập nhật bài "Giá lúa gạo hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-lua-gao-hom-nay — đóng gói 28/10/2026 (trước đó Claude làm tay 21, 23, 29/10/2026).
Trang tích ô trong Sheet "Update" (dòng giá lúa gạo) hoặc nhắn *"Update bài giá lúa gạo"* — **không hỏi gì thêm**.
Chạy không cần Claude: `bash cong-cu/tu-dong/chay.sh gia-lua-gao <thư mục ra>` (nhánh chung `*)` của `chay.sh`).

> Mọi con số ghi vào bài đều đọc từ trang nguồn tải về **ngay trong lần chạy đó** (hoặc là phép trừ trên các số đó, có ghi
> cách tính). Không có số nào viết sẵn trong công thức. Nguồn lỗi / thiếu dòng → giữ số cũ của bài + ghi cần duyệt.

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Bảng gạo, nếp, lúa trong nước (mục 1.1–1.3) | https://banggianongsan.com/gia-lua-gao-hom-nay/ — bảng "Bảng giá lúa gạo mới nhất - dd/mm/yyyy" (Nông sản \| Giá cũ \| Giá mới \| Thay đổi). Trang tĩnh, đọc bằng `curl` |
| Ghép dòng | Theo **tên** (bỏ "(đ/kg)", bỏ dấu ngoặc, không phân biệt hoa thường): "Nếp IR 5625 (tươi)" = "Nếp IR 5625 tươi". Không ghép theo thứ tự dòng |
| Ô giá | Chép đúng giá cũ / giá mới của nguồn, viết theo kiểu bài: `8,900 - 9,000`, một mức thì `28,000` |
| Ô "Thay đổi" | Chép mức thay đổi của nguồn: "0 đ (Không đổi)" → `Không đổi`; "▲+50 ~ +100 đ" → `+50đ đến +100đ` (kiểu bài đang dùng; nếu bài đang ghi kiểu `+100 đến 0 đ` thì viết `+50 đến +100 đ`) |
| Nguồn để trống giá mới ("Chưa có dữ liệu giá mới", vd Lúa Nàng Hoa 9) | Giữ nguyên cả dòng + cần duyệt |
| Dòng nguồn có mà bài không có (Lúa tươi DS1, Tấm thơm, Cám) | Không thêm (quy tắc không thay đổi nội dung), liệt kê trong cần duyệt |
| Ngày bảng nguồn | Nguồn thường chỉ có bảng của hôm nay, bài ghi ngày mai → luôn ghi 1 dòng cần duyệt nêu ngày + giờ đăng của bảng |
| Bảng giá gạo thế giới (mục 2) — nguồn 1 (Trang chọn) | Bài "Giá lúa gạo hôm nay <ngày>" mới nhất trên **vietbao.vn**. Link đổi mỗi ngày → tìm qua trang tìm kiếm `vietbao.vn/tim-kiem.html?keyword=giá lúa gạo hôm nay` (dự phòng: sitemap theo ngày `vietbao.vn/sitemap/sitemap-articles-day-yyyy-mm-dd.xml`); chỉ xét bài 3 ngày gần nhất. Chỉ lấy khi bài có bảng "Thị trường \| Mặt hàng \| Giá \| Thay đổi" với dòng Thái Lan / Ấn Độ ("-4 USD" → `-4`). **Thực tế 18–28/10/2026 không bài nào có bảng này** |
| Bảng thế giới — nguồn 2 (thay thế, đề xuất) | **Hiệp hội Lương thực Việt Nam (VFA)**, https://vietfood.org.vn/thi-truong/gia-xuat-khau/ — bản tin "Giá gạo xuất khẩu của các nước trên thế giới ngày …" (số liệu Oryza, USD/tấn FOB), dùng khi vietbao không có; bản tin mới nhất phải trong 4 ngày. Ghép: Thái Lan "Gạo trắng 5% tấm" = `5% tấm`; Thái Lan "Gạo 100% tấm" = `A1 Super` (tên thương mại của gạo 100% tấm Thái); Ấn Độ "Gạo 100% tấm" = `100% tấm Stxd`; Ấn Độ "Gạo đồ 5% tấm" = `Gạo đồ 5% Stxd`. Cột thay đổi = giá bản tin mới nhất − giá bản tin liền trước (tính toán, cùng mức ở 2 đầu → `-4`; khác nhau → `-4 đến -3`; bằng 0 → `Không đổi`). Luôn ghi cần duyệt "nguồn thay thế". **Tắt**: đặt `"the_gioi_vfa": false` trong `cau-hinh.json` |
| Ấn Độ "gạo đồ" | Không bao giờ lấy dòng gạo trắng 5% thay cho gạo đồ 5% (khác hàng) |
| Không có nguồn thế giới nào | Giữ nguyên 4 dòng + **trả lại ngày gốc** ở tiêu đề "2. Bảng giá lúa gạo thế giới dd/mm/yyyy" (không để ngày mới đứng cạnh giá cũ) + cần duyệt |
| banggianongsan.com lỗi | Giữ mọi giá trong nước + trả lại mọi ngày trong bài về ngày gốc (tiêu đề, ngày đăng, sapo, tiêu đề mục 2) + cần duyệt. Tên file Docs vẫn mang ngày mai (công cụ chung đặt) |
| Ngày khác | Công cụ chung (`dung`) tự đổi mọi dd/mm/yyyy sang ngày mai |
| Phần chữ (mục 3, 4, tóm tắt) | Không có con số giá → không đụng. Bài đổi câu chữ thêm số giá vào đoạn văn → công thức chưa biết, đọc lại `xem2.txt` |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy` |

## 2. Các bước

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-lua-gao
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # LUÔN ghi ngày hôm sau (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 -I $CT/lay_gia.py cap-nhat/gia.json                 # banggianongsan + vietbao + VFA → gia.json
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-lua-gao/`.

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung + công tắc `the_gioi_vfa` |
| `lay_gia.py` | Tải 3 nguồn bằng `curl` (không cần trình duyệt), đọc bảng → `gia.json` (mỗi dòng kèm chữ gốc của nguồn, ngày/giờ đăng, link). Nguồn lỗi → `null`, in "KHÔNG ĐỌC ĐƯỢC" |
| `tao_sua.py` | Bảng trong nước + bảng thế giới + trả lại ngày khi thiếu nguồn → `sua.json`; `--kiem` soát lại. Không gọi mạng |

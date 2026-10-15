# Công thức: cập nhật bài "Giá lúa gạo hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-lua-gao-hom-nay
Chạy lần đầu 15/10/2026 (ghi ngày 16/10/2026). Công thức này chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

## 1. Những gì đã chốt

| Việc | Cách làm cố định |
|---|---|
| Nguồn chính (gạo, nếp, lúa) | Bản tin "Giá lúa gạo hôm nay dd/mm/yyyy" của **Doanh nghiệp & Hội nhập** (doanhnghiephoinhap.vn). Bảng giá gạo / nếp / lúa ở đó là **ẢNH** nhưng có **đúng danh mục như bài TCB** (Gạo NL CL 555, OM 5451, OM 380, IR 504, OM 18, Sóc Thơm, IR 50404, Nàng Nhen, Gạo Thơm, Jasmine, Nàng Hoa, Tẻ Thường, Thái Hạt Dài, Hương Lài, Đài Thơm, Sóc Thường, TP OM 5451 (đã sortex); nếp IR 4625/IR 5625/3 tháng; lúa IR 50404, OM 5451, Đài Thơm 8, OM 18, OM 34, Nàng Nhen khô, IR 504). Tải ảnh về rồi **đọc ảnh** (công cụ Read) |
| Nguồn đối chiếu (chữ) | Công Thương (congthuong.vn, đăng ~11:30), Báo Văn Hóa (baovanhoa.vn, ~05:50), Index.vn, Thời báo Tài chính (thoibaotaichinhvietnam.vn, ~06:15). Đều dẫn Sở NN&MT An Giang. Tìm bằng WebSearch "giá lúa gạo hôm nay dd/mm/yyyy" |
| Chỉ sửa khi | Ô có **≥ 2 nguồn cùng ngày khớp nhau**. Ảnh DN&HN có khi là ảnh cũ (ảnh lúa ngày 15/10 tạo từ 14/10, ảnh nếp từ 24/09) → xem ngày trong tên ảnh (`.../2026/102026/14/...`). Ảnh và chữ lệch nhau → theo số mà nhiều báo khác cùng ghi. Mâu thuẫn không phân xử được → giữ nguyên + `can_duyet` |
| Nguồn không dùng được | nongnghiepmoitruong.vn: 403 (Cloudflare) với cả curl và WebFetch |
| Bảng thế giới | Cột "Giá tham khảo" + "Thay đổi" (không phải Giá cũ/mới). Đối chiếu bản tin cùng ngày (Thái Lan 5% tấm, 100% tấm; Ấn Độ 100% tấm, gạo đồ 5% tấm). Số đổi thì sửa, kèm Thay đổi theo nguồn. Đề mục "2. Bảng giá lúa gạo thế giới 11/10/2026" có ngày **không số 0** → phải tự thêm vào `sua.json` |
| Cách viết số | Dấu nghìn `,`, khoảng `8,700 - 8,750` (gạch có cách), một mức `28,000`. Công cụ tự đổi `8.800` → `8,800` |
| Cột Giá cũ / Giá mới / Thay đổi | Giá cũ ← số đang ở Giá mới; Giá mới ← giá nguồn; Thay đổi so Giá mới (mới) với Giá cũ (mới): bằng nhau `Không đổi`; hai đầu cùng mức `+100 đ`; hai đầu khác `+100 đến +200 đ` / `-50 đến -100 đ` (kiểu bài đang ghi). Đặt `tinh_toan: true` |
| Lỗi có sẵn trong bài | Đoạn "Tồn kho và dự trữ lương thực" lặp ý đoạn "Nhu cầu tiêu thụ và nhập khẩu" – không sửa, chỉ báo |

## 2. Các bước

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-lua-gao
mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
# Tìm link bản tin trong ngày (DN&HN, Công Thương, Báo Văn Hóa, Index.vn, Thời báo Tài chính) rồi ghi vào "tham_khao" TRƯỚC khi chạy lay
N=$(TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y)
python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
# Tải ảnh bảng của DN&HN: trong HTML tìm "Bảng giá gạo/nếp/lúa hôm nay", lấy <img data-src=...in_article/...jpg> ngay trước; curl về rồi đọc ảnh
# So từng ô với nguồn -> ghi cap-nhat/gia.json (nguồn, giờ đăng, từng giá) + cap-nhat/sua.json (mẫu: ../../../../cap-nhat-bai-tcb/2026-10-16-gia-lua-gao/sua.json)
python3 -I $SKILL/scripts/cap_nhat.py sua cap-nhat/cau-hinh.json cap-nhat/sua.json
```

Rồi Bước 5–6 của `SKILL.md` (Google Docs, `soat`, `bao-cao`).

**Mẹo `sua.json`:** cùng một khoảng giá (vd `7,500 - 7,600`) xuất hiện nhiều lần → dùng `ngu_canh`. Ngữ cảnh được so trên bài **đã áp các chỗ sửa trước đó**,
nên trong mỗi dòng: sửa ô Giá mới trước (ngữ cảnh = `"<giá mới> <thay đổi>"`), rồi Giá cũ (ngữ cảnh = `"<tên dòng> <giá cũ>"`),
rồi ô Thay đổi (ngữ cảnh = `"Không đổi <tên dòng kế tiếp>"`).

## 3. Trục trặc

| Hiện tượng | Làm gì |
|---|---|
| `bao-cao` báo "Không đọc được nguồn tham khảo …: None" | Đã thêm link vào `tham_khao` sau khi chạy `lay`. Ghi link trước khi `lay`, hoặc xóa dòng cảnh báo đó trong báo cáo |
| DN&HN không có bài trong ngày | Dùng chữ của Công Thương + Báo Văn Hóa/Index.vn; loại không có trong chữ (gạo bán lẻ lạ, TP OM 5451, lúa Nàng Nhen…) giữ nguyên + `can_duyet` |
| Lúa Nàng Hoa 9 | Không nguồn nào có (15/10/2026) → giữ nguyên + `can_duyet` |

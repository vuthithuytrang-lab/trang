# App "Cập nhật bài Techcombank" — Trang bấm nút, Claude chạy

- **Trang app:** https://claude.ai/artifact/C1pHcHu6DLgx8xi4zNQnoN (nguồn: `app.html`, dựng 28/10/2026)
- **Lịch nhận lệnh:** `trig_01XnxuNegqxBM5eUEatsweng` (không có giờ chạy, chỉ chạy khi app bấm nút), gắn vào phiên `session_01Y96oKcv4Hv1aVGJVzqj3rX`
- **Danh sách bài:** `danh-sach-bai.json` (STT → mã bài, tên, nhóm, đường dẫn bài). STT trùng STT trong Sheet "Update" (dòng = STT + 1)

## App hoạt động thế nào

1. Trang tích bài trên app rồi bấm **Chạy cập nhật**.
2. App ghi `yeu-cau/<mã>` (`bai`: danh sách mã bài, `trang_thai: "cho"`) và chuyển các bài đó sang `trang_thai: "cho"` trong kho dữ liệu của app.
3. App gọi `fire_trigger` (Claude Code Remote) với chữ kèm theo `Mã yêu cầu: yc-…. Bài: mã1, mã2…` → phiên này thức dậy.

## Khi phiên này thức dậy vì app — các bước

Kho dữ liệu app đọc/ghi bằng công cụ `ArtifactData`, `url` = link app ở trên. Ghi luôn kèm `if_version` của lần đọc gần nhất.

1. **Đọc yêu cầu:** lấy mã yêu cầu + danh sách mã bài từ chữ kèm theo (hoặc `ArtifactData get yeu-cau/<mã>`).
2. **Báo đang chạy:** `batch update` các `bai/<mã>` → `trang_thai: "dang_chay"`, `ghi_chu: ""`; `yeu-cau/<mã>` → `trang_thai: "dang_chay"`.
3. **Chạy từng bài** đúng như khi Trang nhắn "update" trong chat:
   - Ngày ghi trong bài **N = ngày hôm sau** (`TZ=Asia/Ho_Chi_Minh date -d "+1 day"`).
   - Bài có công thức → `cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/<mã>/README.md`; bài lãi suất → `cong-cu/cap-nhat-lai-suat/QUY-TRINH.md`; bài chưa có công thức → `cap-nhat-bai-tcb/SKILL.md` + nguồn cột D Sheet + báo cáo lần chạy trước trong `cap-nhat-bai-tcb/<ngày>-<mã>/`.
   - Mỗi bài một agent nền (tối đa 20 cùng lúc), quy tắc nội dung ⛔ như CLAUDE.md, Docs vào thư mục Drive chung + chia sẻ quyền sửa.
4. **Mỗi bài xong → ghi ngay lên app** (`update bai/<mã>`): `ngay` (N), `tieu_de`, `link`, `cap_nhat_luc` (giờ VN), `trang_thai` = `"xong"` hoặc `"loi"` (nguồn lỗi / phần chưa cập nhật được), `ghi_chu` = 1 câu tiếng Việt dễ hiểu về chỗ cần xem lại (để trống nếu không có).
5. **Xong hết:** `yeu-cau/<mã>` → `trang_thai: "xong"` (hoặc `"loi"` + `ghi_chu`); thêm cột ngày chạy vào Sheet "Update", dán link, bỏ tích (như `bang-dieu-khien/README.md`); commit + push thư mục kết quả.
6. **Báo Trang trong chat** như mọi lần (bảng link + chỗ cần duyệt + 2 câu hỏi).

## Thêm bài mới vào app

Thêm dòng vào Sheet "Update" như cũ, rồi `ArtifactData set bai/<mã>` với `thu_tu` (= STT), `ten`, `nhom` (Vàng / Nông sản / Kim loại / Năng lượng / Lãi suất), `url`, `trang_thai: "san_sang"`; cập nhật `danh-sach-bai.json`.

## Trạng thái hiển thị trên app

| `trang_thai` | Chữ trên app |
|---|---|
| `san_sang` | Sẵn sàng |
| `cho` | Đã gửi, chờ chạy |
| `dang_chay` | Đang chạy |
| `xong` | Đã xong |
| `loi` | Cần xem lại |

## Người lạ / chưa đăng nhập vẫn xem được (29/10/2026)

App gắn sẵn **link file Docs mới nhất** của từng bài trong `DS` (trường `ten_file`, `link`, `luc`) — ai mở link app (kể cả ẩn danh) cũng thấy "Đã xong" + "Mở file Docs".
Thư mục Drive đã mở "Bất kỳ ai có đường liên kết", nên người lạ mở file được.
⚠️ **Mỗi lần Claude chạy xong một đợt**: cập nhật `ten_file/link/luc` trong `DS` của `app.html` rồi đăng lại (Artifact cùng file). Bấm chạy thì vẫn cần đăng nhập claude.ai + kết nối Google Sheets
(hoặc dùng trang app Google trong `cong-cu/tu-dong/google-apps-script/Code.gs` sau khi Trang cài).

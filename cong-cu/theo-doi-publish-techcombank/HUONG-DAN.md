# Theo dõi publish Techcombank — hướng dẫn

Hệ thống tự kiểm tra 35 URL techcombank.com lúc **08:00 và 20:00** mỗi ngày, tick vào
Google Sheet những trang đã cập nhật ngày hôm nay, rồi gửi báo cáo cho bạn.

- Google Sheet: [Theo dõi publish Techcombank](https://docs.google.com/spreadsheets/d/1d-jCrL_qmcXFE6pxWc9VlLDGVoTP0AnFJGQohE6q-Ko/edit)
- Chạy trên: máy Windows của bạn (máy phải bật lúc 08:00 / 20:00; tắt thì bật lên sẽ chạy bù)

## Tình trạng cài đặt

| Việc | Ai làm | Trạng thái |
|---|---|---|
| Viết bộ công cụ, chạy thử lấy ngày 35 URL | Agent | ✅ Xong — 35/35 lấy được ngày |
| Tạo Google Sheet, điền danh sách URL | Agent | ✅ Xong |
| A. Tải bộ công cụ về máy | Trang | ⏳ |
| B. Tạo "tài khoản robot" Google (Service Account) | Trang | ⏳ |
| C. Kết nối Telegram để nhận báo cáo | Trang | ⏳ |
| D. Bấm cài đặt + bật lịch | Trang | ⏳ |

---

## A. Tải bộ công cụ về máy

1. Bấm link: https://github.com/vuthithuytrang-lab/trang/archive/refs/heads/claude/dreamy-darwin-yckgjc.zip
2. Mở file ZIP vừa tải → chuột phải → **Extract All** (Giải nén) → chọn nơi dễ nhớ, ví dụ `Documents`.
3. Đi vào thư mục `cong-cu` → `theo-doi-publish-techcombank`. Đây là thư mục làm việc từ giờ.

## B. Tạo "tài khoản robot" Google (Service Account)

Service Account là một tài khoản Google dành riêng cho máy, để script được phép ghi vào sheet
mà không cần mật khẩu của bạn.

1. Vào https://console.cloud.google.com/ — đăng nhập Gmail **cá nhân** (công ty thường chặn bước tạo chìa).
2. Trên cùng, bấm ô chọn dự án → **New Project** → đặt tên `theo-doi-publish` → **Create**. Chờ vài giây rồi chọn dự án đó.
3. Bật 2 dịch vụ (mỗi link bấm nút xanh **Enable**):
   - https://console.cloud.google.com/apis/library/sheets.googleapis.com
   - https://console.cloud.google.com/apis/library/drive.googleapis.com
4. Vào https://console.cloud.google.com/iam-admin/serviceaccounts → **+ Create service account**
   → tên `theo-doi-publish` → **Create and continue** → bỏ qua phần quyền → **Done**.
5. Trong danh sách, **copy địa chỉ email** của tài khoản vừa tạo (dạng `theo-doi-publish@....iam.gserviceaccount.com`).
6. Bấm vào tài khoản đó → tab **Keys** → **Add key** → **Create new key** → chọn **JSON** → **Create**. Máy tự tải về 1 file `.json`.
7. Đổi tên file đó thành `service-account.json`, chép vào thư mục `bi-mat` (trong thư mục làm việc ở bước A).
   ⚠️ Đây là chìa khóa: **không gửi vào chat, không mở ra dán ở đâu cả.**
8. Mở Google Sheet → nút **Chia sẻ (Share)** → dán email ở bước 5 → quyền **Người chỉnh sửa (Editor)**
   → bỏ tick "Thông báo" → **Chia sẻ**.

> Nếu bước 8 báo "không thể chia sẻ ra ngoài tổ chức": sheet đang nằm trong Drive công ty SEONGON
> và công ty chặn chia sẻ ra ngoài. Báo Agent — sẽ chuyển sheet sang Drive cá nhân.

## C. Kết nối Telegram để nhận báo cáo

Dùng lại bot cũ của bạn — nhưng token cũ đã lộ (xem `BAO-MAT.md`) nên phải xin token mới:

1. Mở Telegram → chat với **@BotFather** → gõ `/revoke` → chọn bot của bạn → BotFather gửi token mới.
2. Mở Notepad, dán token mới vào, lưu thành file `telegram-token.txt` trong thư mục `bi-mat`.
3. Mở bot của bạn trên Telegram → bấm **START** (hoặc gõ `hi`).
4. Bấm đúp file **`GUI-TIN-THU.bat`**. Script tự tìm chat id, lưu lại, và gửi 1 tin thử. Thấy tin trên Telegram là xong.

<details><summary>Muốn nhận qua Gmail thay vì Telegram</summary>

1. Bật xác minh 2 bước cho Gmail gửi đi: https://myaccount.google.com/signinoptions/two-step-verification
2. Tạo mật khẩu ứng dụng: https://myaccount.google.com/apppasswords → đặt tên `theo-doi-publish` → copy 16 ký tự.
3. Lưu 16 ký tự đó vào file `bi-mat/gmail-mat-khau-ung-dung.txt`.
4. Mở `cau-hinh.json` bằng Notepad: đổi `"telegram"` ở dòng `kenh_bao_cao` thành `"gmail"`, điền `gui_tu` (Gmail gửi) và `gui_den` (email nhận).
5. Bấm đúp `GUI-TIN-THU.bat`.
</details>

## D. Cài đặt và bật lịch

1. Bấm đúp **`CAI-DAT.bat`**. Lần đầu nếu máy chưa có Python, nó tự cài rồi bảo bạn bấm lại lần nữa.
   Xong sẽ hiện "Da bat lich ... 08:00 va 20:00".
2. Bấm đúp **`CHAY-NGAY.bat`** để chạy thử 1 lần (2–3 phút). Mở Google Sheet sẽ thấy tab tuần mới, Telegram nhận báo cáo.

---

## Dùng hằng ngày

| Muốn | Làm |
|---|---|
| Chạy ngay, không đợi giờ | Bấm đúp `CHAY-NGAY.bat` |
| **Thêm URL** | Mở tab **Danh sách URL** → gõ URL vào ô trống cột B (cột STT ghi số tiếp theo). Lần chạy sau tự có. |
| **Bớt URL** | Xóa cả hàng đó trong tab **Danh sách URL**. Trong tab tuần hiện tại, hàng cũ được ghi chú "Đã bỏ khỏi danh sách". |
| Tắt lịch tự động | Bấm đúp `TAT-LICH.bat` |
| Xem máy đã chạy những gì | Mở thư mục `logs` — mỗi tháng 1 file |

## Sheet hoạt động thế nào

- Tab **Danh sách URL**: nơi duy nhất bạn sửa danh sách.
- Mỗi tuần (Thứ 2 → CN) tự sinh 1 tab tên `Tuần dd/mm-dd/mm`. Tab tuần cũ giữ nguyên, không bị sửa.
- Cột ngày là ô tick. Trang cập nhật đúng ngày hôm nay → tick. Chưa → để trống, kèm ghi chú
  (rê chuột vào ô có góc đen) ghi ngày đang hiển thị / "Không có ngày" / "Lỗi: mã lỗi".
- Lần 20:00 ghi đè lần 08:00: sáng chưa cập nhật mà tối đã cập nhật thì tick.
  Ô đã tick buổi sáng thì giữ tick, kể cả khi buổi tối trang tải bị lỗi.
- "Tỷ lệ (%)" = số ngày đã tick ÷ số ngày đã trôi qua trong tuần. Dưới 100% thì hàng tô đỏ nhạt.
- Cột ngày hôm nay tô nền xanh nhạt, ô tiêu đề màu mint.
- 20:00 Chủ nhật gửi thêm báo cáo tuần.

## Quy tắc lấy ngày

| Loại URL | Lấy ngày ở đâu |
|---|---|
| Có `/thong-tin/blog/` | Thẻ `<div class="article-header-body--date">` ngay dưới tiêu đề H1 và sapo (dạng `2026-10-05T00:00:00.000+07:00`) |
| URL khác | Ngày dd/mm/yyyy trong thẻ `<title>` |

2 URL hiện **không có ngày trong title** nên sẽ luôn báo "Không có ngày":
`/cong-cu-tien-ich/bieu-phi-lai-suat` và `/khach-hang-ca-nhan/chi-tieu/the/the-tin-dung/techcombank-everyday`.

## Các file trong thư mục

| File | Là gì |
|---|---|
| `CAI-DAT.bat` | Cài Python + thư viện, bật lịch 08:00/20:00 |
| `CHAY-NGAY.bat` | Chạy tay 1 lần |
| `GUI-TIN-THU.bat` | Gửi tin thử, tự lấy chat id Telegram |
| `TAT-LICH.bat` | Tắt lịch tự động |
| `cau-hinh.json` | Link sheet, kênh báo cáo |
| `bi-mat/` | Chìa khóa — **không bao giờ lên GitHub** |
| `logs/` | Nhật ký mỗi lần chạy |
| `theo_doi.py`, `lay_ngay.py`, `google_sheet.py`, `bao_cao.py` | Mã chạy (không cần đụng) |
| `danh-sach-url-mac-dinh.txt` | Danh sách ban đầu, chỉ dùng khi sheet chưa có tab Danh sách URL |

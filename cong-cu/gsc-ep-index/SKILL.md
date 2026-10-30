---
name: gsc-request-indexing
description: Tự động bấm "Request indexing" trong Google Search Console cho một danh sách URL, trên bất kỳ domain/property nào và bất kỳ trình duyệt nhân Chrome / profile nào người dùng đang mở sẵn GSC (Chrome, Chrome Beta/Canary, Brave, Edge, Arc, Vivaldi…), rồi kiểm tra Last crawl để xác nhận. Dùng khi người dùng muốn "submit URL lên GSC", "request indexing", "gửi index lại", "submit lại các URL này trong GSC của <domain>", "đẩy index", kể cả khi chỉ dán một list URL và nói "submit giúp tôi như task cũ". Chạy qua AppleScript điều khiển đúng tab GSC người dùng đã mở (có quyền), không tự mở tab mới bằng Claude in Chrome.
compatibility: macOS (osascript, zsh). Trình duyệt nhân Chromium phải bật View → Developer → Allow JavaScript from Apple Events ở profile có tab GSC.
---

# GSC Request Indexing (mọi domain, mọi Chrome)

## Vì sao làm qua AppleScript
Quyền GSC thường nằm ở một profile/trình duyệt khác với profile mà Claude in Chrome dùng. Tự mở tab GSC bằng Claude in Chrome sẽ báo "You don't have access". AppleScript thấy được **mọi cửa sổ của mọi profile** trong một app trình duyệt. Vì vậy ta tìm đúng tab GSC người dùng đã mở cho property đó rồi điều khiển tab ấy.

## Chuẩn "thành công" (không được nới)
- Chỉ tính **OK** khi lần bấm đó đi qua bước "Testing if live URL" **và** hiện hộp thoại "Indexing requested – URL was added to a priority crawl queue" **mới** cho chính URL đó.
- Chữ "Indexing requested" còn sót từ hộp thoại cũ không được tính. Script luôn đóng hộp thoại cũ (Dismiss) và tải lại trang sạch trước mỗi URL.
- Sau khi submit xong, đọc lại **Last crawl** của từng URL để báo cáo. Không khẳng định "đã được crawl" khi Last crawl còn cũ hơn thời điểm submit.

## Quy tắc thử lại
- Mỗi URL thử tối đa **20 lần** (`GSC_MAX_RETRY`).
- Mỗi lần bấm phải chờ GSC hiện màn hình phản hồi (Indexing requested / Quota exceeded / lỗi). Tối đa 10 phút; không bấm chồng khi đang "Testing if live URL".
- Lần thử lại tiếp theo chờ thêm **60s** (`GSC_WAIT_RETRY`).
- Gặp "**Indexing request rejected**" thì bấm **Dismiss** (thẻ `<button>`) rồi chờ **15s** (`GSC_WAIT_REJECTED`) mới thử lại.
- URL không thuộc property thì ghi SKIP, không thử lại.
- Nếu đã thử hết 20 lần mà vẫn "Quota exceeded" thì dừng và đánh dấu SKIP cho các URL còn lại.

## Quy trình
1. **Hỏi/xác định domain (property)** và lấy list URL từ tin nhắn người dùng. Lưu list vào file trong scratchpad, mỗi dòng 1 URL.
2. **Người dùng mở sẵn GSC** của property đó (trang Overview hoặc Performance đều được) trong trình duyệt/profile có quyền. Nếu chưa có tab, nhờ họ mở; đừng tự mở bằng Claude in Chrome.
3. Kiểm tra tab:
   ```bash
   GSC_STATE=~/.cache/gsc-indexing/<domain> ~/.claude/skills/gsc-request-indexing/scripts/gsc.sh find <domain>
   ```
   - `FOUND … JS_OK`: sẵn sàng.
   - `JS_BLOCKED`: nhờ người dùng bật **View → Developer → Allow JavaScript from Apple Events** trong đúng trình duyệt/profile đó. Sau khi khởi động lại Chrome, quyền này có thể bị tắt lại.
   - `NOT_FOUND`: chưa có tab GSC chứa domain. `<domain>` khớp theo chuỗi con của URL tab, ví dụ `vietnam.vn`, `techcombank.com`, hoặc `https%3A%2F%2Fexample.com` cho property dạng URL-prefix.
   - Có nhiều tab khớp thì lấy tab đầu tiên. Cần thì đóng bớt hoặc truyền chuỗi cụ thể hơn.
4. Chạy nền và theo dõi:
   ```bash
   ~/.claude/skills/gsc-request-indexing/scripts/run.sh <domain> <file_urls> <file_log>
   ```
   Dùng `run_in_background`, rồi dùng Monitor `tail -f <file_log> | grep -E --line-buffered "^https|STOP|DONE|retry (5|10|15)/"` để báo tiến độ. Không gọi run.sh lần thứ hai song song trên cùng tab.
5. **Báo cáo** khi log có `DONE`:
   - Số URL OK/FAIL/SKIP và số lần thử lại.
   - Phần `=== LAST CRAWL` (trạng thái "URL is on Google…", Last crawl).
   - Chỉ rõ URL nào có Last crawl **trước** giờ submit, tức chưa được crawl lại.

## Script
| File | Việc |
|---|---|
| `scripts/gsc.sh find <domain>` | Quét các app Chrome-family đang chạy (`GSC_APPS` để đổi danh sách), tìm tab `search.google.com/search-console` chứa domain, lưu APP/WID/TID/resource_id vào `$GSC_STATE/tab.env` và thử JS. |
| `scripts/gsc.sh nav <url>` / `js '<code>'` | Điều hướng / chạy JS trong tab đã lưu. |
| `scripts/request.sh <url>` | Một lần Request indexing theo đúng chuẩn trên, in `RESULT: OK/FAIL/SKIP`. |
| `scripts/inspect.sh <url>` | Đọc trạng thái + Last crawl (tải lại trang kết quả cho DOM sạch). |
| `scripts/run.sh <domain> <file> [log]` | Vòng lặp cả list + thử lại + Last crawl. |

## Lưu ý
- GSC có quota request indexing theo ngày/property. Khi run.sh ghi STOP vì "Quota exceeded", báo người dùng và đề xuất chạy tiếp các URL SKIP vào hôm sau.
- Script ép giao diện tiếng Anh (`&hl=en`) để nhận diện chữ ổn định.
- Gặp reCAPTCHA / "not a robot" thì dừng và để người dùng tự xử lý; không tìm cách vượt.

---
name: chay-luong-share
description: Chạy trọn một LUỒNG share bài lên các blog của Trang (WordPress, Wix) cho bất kỳ dự án nào, chỉ cần (1) link Google Sheet + nhãn dòng của mình và (2) quy tắc đăng bài; tài khoản đã kết nối sẵn. Dùng khi Trang nói "chạy luồng share", "share các bài có nhãn … trong file này", "đăng bài theo sheet này với quy tắc như cũ", "lên lịch share đến ngày …", hoặc dán link sheet kèm yêu cầu đăng bài hàng loạt. Tự đọc sheet, đọc bài gốc, viết lại theo quy tắc, làm ảnh đại diện, xếp lịch giãn để không bị khóa tài khoản, đăng thẳng (không tạo nháp), ghi link + giờ vào sheet, tự kiểm tra trang còn sống và dừng ngay nếu bị khóa.
---

# chay-luong-share — luồng share bài dùng chung mọi dự án

Đúc kết từ 3 đợt thật (TCB 10/10, Share social GP 04–08/11/2026). Mọi bài học xương máu nằm ở mục **Luật an toàn**.

## Đầu vào Trang cần đưa (chỉ 2 thứ)

1. **Sheet**: link Google Sheet + tên tab + nhãn dòng của mình (ví dụ "Wix - Trang", "WordPress - Trang").
2. **Quy tắc đăng bài**: hạn chót, khung giờ, bao nhiêu bài/ngày, độ dài bài, quy tắc nội dung riêng (nếu có).
   Không nói gì → dùng `references/quy-tac-viet-mac-dinh.md` + mặc định trong `du-an.mau.json`.

Tài khoản đã kết nối nằm sẵn ở `.claude/skills/share-bai-*/…accounts.local.json`. Thiếu/hết hạn → làm theo skill `share-bai-<nền tảng>` để Trang cấp quyền lại (Trang đính kèm file chìa, KHÔNG dán chữ).

## Các bước

1. **Kiểm tra tài khoản sống** trước khi nhận việc: mở trang chủ + gọi API mỗi nền tảng (đọc, không đăng).
   Báo Trang bảng: nền tảng · sống/khóa/hết hạn · số bài hiện có.
2. **Đọc sheet**: lấy các dòng có nhãn của mình mà cột link còn trống. Ghi `tasks_raw.txt` (mỗi dòng: `<số dòng> <wp|wix> <URL bài gốc>`).
   Kiểm tra vài dòng đầu/cuối khớp với sheet. Người khác hay chèn/xóa dòng → luôn tìm lại dòng theo URL bài gốc trước khi ghi.
3. **Tạo thư mục dự án** trong scratchpad: copy `du-an.mau.json` → `du-an.json`, điền theo đầu vào; chép quy tắc viết vào `quy-tac-viet.md`.
4. **Tải bài gốc** (curl, mỗi file vào thư mục riêng) rồi trích chữ. Trang chặn → dùng công cụ đọc web (WebFetch).
   Vẫn không được → ghi `bai/<dòng>/NO_SOURCE.txt`, báo Trang (nhờ dán nội dung hoặc bỏ). **Không bịa, không vượt chặn bot.**
5. **Viết bài song song** bằng nhiều trợ lý (Agent, mỗi trợ lý ~10 dòng), mỗi bài ra `bai/<dòng>/post.html` + `meta.json`
   đúng định dạng trong quy tắc viết. `scripts/step.py` có cổng soát tự động (số từ, đúng 1 link về bài gốc, chỉ thẻ cho phép, từ cấm, tiêu đề).
6. **Xếp lịch giãn** đến hạn chót (xem Luật an toàn). Có thể ghi lịch cố định `wix_plan.json` / `wp_plan.json` dạng `{"<dòng>": "<ISO giờ VN>"}`.
   Ghi giờ dự kiến + nhãn nền tảng vào sheet (cột lịch + cột nhãn) để Trang thấy trước.
7. **Chạy vòng đăng**: mỗi lượt
   `python3 scripts/check_sites.py <thư mục dự án>` → nếu `BLOCKED` thì DỪNG nền tảng đó và báo Trang ngay.
   `python3 scripts/step.py <thư mục dự án>` → in `PUBLISHED {…}`, `LEFT`, `WAKE_AT`.
   Mỗi `PUBLISHED` có `"live": true` → tìm lại dòng theo URL bài gốc, ghi link + giờ đăng "HH:MM dd/mm/yyyy", đọc lại sau khi ghi.
   ⚠️ Đã thử 06/11: chương trình chạy nền BỊ TẮT khi phiên ngủ (lỡ 2 bài). Vì vậy vẫn cần send_later mỗi giờ hẹn, nhưng prompt ngắn,
   không routine giữ nhịp 3 tiếng. Cách 0 token thật sự = app Google Sheet.
   (Cách cũ, chỉ dùng khi phiên đang thức:) chạy vòng đăng NỀN bằng script (mẫu `cong-cu/share-bai-social/gp-share-social/chay_nen.py`:
   `setsid nohup python3 chay_nen.py &`) — tự chờ giờ, giữ ≥ 2 tiếng/bài, chỉ 7–23h, tự dừng khi trang bị khóa. AI chỉ thức
   **1 lần/tối** (send_later 22:45) để ghi link cả ngày vào sheet bằng 1 lệnh, kiểm tra vòng nền còn sống, sao lưu. Không đặt nhắc mỗi bài,
   không routine giữ nhịp 3 tiếng. Tốt nhất: chuyển hẳn sang app Google Sheet (`cong-cu/app-share-bai/`) — 0 token.
8. **Kết thúc**: xóa routine, sao lưu `posted.jsonl` vào `cong-cu/share-bai-social/<tên đợt>/`, commit + push, báo tổng kết bằng lời thường.

## Luật an toàn (bắt buộc — đã mất 2 trang WordPress vì đăng dày)

- Mỗi tài khoản **tối đa ~6–8 bài/ngày**, cách nhau **≥ 2 tiếng**, chỉ trong khung giờ ban ngày (mặc định 07:00–23:00). Không đăng đêm.
- **Đăng thẳng 1 lệnh, không tạo nháp trước** (Trang yêu cầu 05/11). WordPress: `status=publish`. Wix: `publish: true`.
- **Không gửi hàng loạt lệnh** lên cùng một trang; không hẹn giờ cả trăm bài một lúc.
- Trước mỗi lượt đăng chạy `check_sites.py`. Trang trả 410/"suspended" → dừng hẳn nền tảng đó, không thử tài khoản khác khi chưa hỏi Trang.
- Wix có thể báo 504 khi tạo bài: **kiểm tra tổng số bài trước khi thử lại** để không đăng trùng.
- Bài Wix mới cần ~3 phút mới hiện → `step.py` tự chờ trước khi báo `live`.
- Gói miễn phí Webflow chỉ chứa 50 mục nội dung; Blogger chặn khi tạo ~19 bài liên tục; chìa Blogger chế độ Test hết hạn sau 7 ngày.
- Trang hỏi "share được bao nhiêu" → trả lời theo **số bài thực có nội dung × nhịp an toàn**, không hứa theo công suất lý thuyết.

## Sheet chung với người khác

- Chỉ sửa dòng có nhãn của mình. Không ghi đè, không chèn/xóa dòng.
- Trang yêu cầu "xóa nền tảng chết" → chỉ làm trống đúng ô nhãn/link/giờ của link chết, giữ cột URL bài gốc.
- Nếu phát hiện người khác vừa sửa giờ/nhãn dòng của mình → không tự ghi đè, báo Trang và hỏi theo lịch nào.

## Bảo mật

Không in, không gắn vào URL, không commit chìa. File `*.local.json` đã chặn trong `.gitignore`. Repo này public.

## Tệp trong skill

| Tệp | Việc |
|---|---|
| `du-an.mau.json` | Mẫu cấu hình dự án (sheet, nhãn, nền tảng, hạn chót, khung giờ, nhịp) |
| `references/quy-tac-viet-mac-dinh.md` | Quy tắc viết bài mặc định (900–1100 từ, 1 link, không từ "nhất/số 1"…) |
| `scripts/step.py` | Một lượt đăng: soát bài → làm ảnh → đăng thẳng → kiểm tra live → ghi `posted.jsonl` → tính giờ kế tiếp |
| `scripts/check_sites.py` | Kiểm tra trang còn sống, tự dừng nền tảng bị khóa |
| `scripts/thumbs.js` | Ảnh đại diện 1200×630 (chữ lấy từ `nhan_anh` trong du-an.json) |
| `scripts/wixlib.py` | Hàm gọi Wix API + chuyển HTML sang Ricos + tải ảnh |

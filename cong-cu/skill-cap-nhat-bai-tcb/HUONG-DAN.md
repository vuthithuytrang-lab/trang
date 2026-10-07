# Skill "Cập nhật bài Techcombank" — hướng dẫn cho Trang

Gói này đóng quy trình cập nhật bài thành **1 skill** (bộ hướng dẫn + công cụ), dùng cho **bất kỳ bài blog Techcombank nào**.
Gửi cho Claude nào cũng được: đưa link bài TCB + link nguồn tham khảo → Claude tự làm hết và trả file Google Docs tô vàng kèm báo cáo.

**Không đụng tới quy trình đang chạy**: lịch cập nhật lãi suất 3 ngày/lần vẫn dùng công cụ cũ ở `cong-cu/cap-nhat-lai-suat/`.

## Skill làm gì

1. **Đọc bản mới nhất của bài TCB** — mỗi lần chạy tải lại bài từ web, đọc trọn từng đoạn, từng bảng.
2. **Đọc nguồn tham khảo bạn đưa** (trang web, file PDF) và tìm chỗ đã cũ: số liệu, lãi suất, phí, hạn mức, mốc năm,
   văn bản quy định, ngày/tháng… Chỉ sửa khi nguồn nói rõ; chỗ nào nghi ngờ thì **không sửa**, ghi vào mục "cần duyệt".
3. **Viết số theo đúng cách bài TCB đang viết** — nguồn ghi `7,2` mà bài đang ghi `4.90` thì viết `7.20`;
   nguồn ghi `120.000.000` mà bài ghi `100,000,000` thì viết `120,000,000`. Có thông báo mỗi lần đổi cách viết.
4. Tạo file Google Docs chép **trọn bài**, giữ bảng, đề mục, đậm/nghiêng, link; **chỉ tô vàng đúng phần bị đổi**
   (vd "0.1 - 0.4%" thành "0.1 - 3.7%" thì chỉ "3.7" tô vàng).
5. Bảng lãi suất tiết kiệm (kiểu bảng so sánh ngân hàng) được cập nhật tự động từ VnExpress/Topi như quy trình hằng ngày.
6. Báo cáo: từng chỗ đã sửa (cũ → mới, lấy từ nguồn nào, vì sao) + những chỗ cần bạn duyệt.

## Trong gói có gì

| File | Để làm gì |
|---|---|
| `cap-nhat-bai-tcb.zip` | **File để gửi đi / tải lên** (chứa cả thư mục bên dưới) |
| `cap-nhat-bai-tcb/SKILL.md` | Bản hướng dẫn Claude đọc đầu tiên |
| `cap-nhat-bai-tcb/scripts/cap_nhat.py` | Công cụ làm phần kỹ thuật (chép bài, tô vàng, viết số, soát, báo cáo) |
| `cap-nhat-bai-tcb/references/` | Mẫu cấu hình, mẫu sửa, quy tắc bảng lãi suất, quy trình gốc của bạn |

## Cách dùng (chọn 1)

**Cách 1 – Claude Code trên web (chỗ bạn đang dùng, chắc chạy nhất).** Mở phiên mới trong repo `trang`, nhắn:
*"Dùng skill trong `cong-cu/skill-cap-nhat-bai-tcb` để cập nhật bài <link>. Nguồn tham khảo: <link>."*

**Cách 2 – Tải lên claude.ai để dùng ở mọi cuộc trò chuyện.** claude.ai → Cài đặt (Settings) → Tính năng / Capabilities → Skills →
tải lên `cap-nhat-bai-tcb.zip`. (Cần bật chạy code và kết nối Google Drive.)

**Cách 3 – Gửi đồng nghiệp:** gửi file `cap-nhat-bai-tcb.zip`, họ làm như Cách 2.

## Nhắn cho Claude thế nào

> Update giúp mình bài https://techcombank.com/thong-tin/blog/... cho hết nội dung cũ nhé.
> Nguồn tham khảo: <link 1>, <link 2>. Tên file: "…".

- Nhiều bài → dán nhiều link, mỗi bài ra 1 file Docs.
- Chỉ muốn sửa một phần → nói rõ ("chỉ cập nhật bảng phí", "chỉ đổi số liệu năm 2025").
- Bài có bảng lãi suất mà không đưa nguồn → Claude dùng VnExpress + Topi như quy trình hằng ngày.

## Lưu ý thật

- Claude cần **vào được mạng** tới techcombank.com và các nguồn. Môi trường bị chặn → Claude báo rõ và nhờ bạn lưu trang gửi vào chat.
- Cần **kết nối Google Drive**; không có thì Claude gửi file để bạn kéo vào Drive và mở bằng Google Tài liệu.
- Thông tin về **chính Techcombank** chỉ được sửa theo trang techcombank.com; dòng Techcombank trong bảng so sánh không bao giờ bị sửa.
- Claude **không viết lại văn**: chỉ đổi con số / cụm từ đã cũ. Câu nào cần viết lại, Claude ghi vào mục "cần duyệt" để bạn quyết.

## Công thức riêng đã đóng gói

| Bài | Bạn chỉ cần nhắn | Chi tiết |
|---|---|---|
| Giá cà phê hôm nay | "Update bài giá cà phê" | `cong-thuc/gia-ca-phe/README.md` — nguồn Nhà Bè Agri + giacaphe.com, mọi lựa chọn đã chốt |

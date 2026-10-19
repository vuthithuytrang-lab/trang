# Báo cáo chạy thử — Plan internal links, dòng 2–4 (19/10/2026)

Thư mục Drive: [Plan internal links - File blog](https://drive.google.com/drive/folders/1qLQU6FfkXcOvAsUvKZ-KsVeXWC5RLgHH)

## 1. Các dòng đã làm

| Dòng | Tên file | Link | Bước 1 | Bước 2 |
|---|---|---|---|---|
| 2 | 1 Man bằng bao nhiêu tiền Việt | https://docs.google.com/document/d/1CRMKvsFXSiHn5_WdpwXnzEyoEjCGejReuuTozhIC4GU/edit | ✅ | ✅ |
| 3 | 1 Tệ bằng bao nhiêu tiền Việt Nam | https://docs.google.com/document/d/1ivcasR6U2U8RSUqLVkwpzwU4wzaL6UZU0NX0dC79fCs/edit | ✅ | ✅ (2 đoạn chờ duyệt) |
| 4 | 1 triệu Won bằng bao nhiêu tiền Việt | https://docs.google.com/document/d/1g8VO-sYEKQ2CfytBll10_5QmFLbxvpbvey0xiBBk58o/edit | ✅ | ✅ (3 đoạn chờ duyệt) |

Đã điền link vào H2, H3, H4 (từng ô một, đã đọc trước — cả 3 ô đều trống). Không đụng ô nào khác.
Tự soát: chữ trong Docs khớp 100% với bản bài gốc đã chèn (so từng từ); ảnh và chú thích căn giữa; tô vàng + ghi chú đỏ hiển thị đúng.

## 2. Bài lỗi
Không có (không 404, không trang sản phẩm, không URL trùng).

## 3. Phân quyền — ⚠️ CHƯA XONG
Công cụ Drive hiện có chỉ chia sẻ được theo email, **không mở được "Bất kỳ ai có đường liên kết – Người chỉnh sửa"**,
cho cả thư mục lẫn từng file. Cả 3 file hiện chỉ có quyền chủ sở hữu (vuthithuytrang@seongon.com).
→ Cần Trang mở quyền ở cấp thư mục (xem hướng dẫn trong chat).

## 4. Đề xuất tỷ giá cột I (áp nguyên văn)
| Dòng | Kết quả |
|---|---|
| 2 | ✅ Tìm thấy câu gốc, đã thay. Câu gốc vốn đã link "tỷ giá ngoại tệ" về trang tỷ giá → nay anchor là "USD sang VND". |
| 3 | ✅ Tìm thấy (bài gốc thiếu dấu chấm cuối câu; bản sau khi chèn có dấu chấm, như cột I). |
| 4 | ✅ Tìm thấy, đã thay, giữ in đậm "không cần mở mới tài khoản ngoại tệ". Link trỏ theo **cột G (utm_content=2)**; link mẫu bên trong ô I4 lại là utm_content=0 — Trang xem giúp đúng là bản nào. |

Lưu ý: dòng 3 và 4, bài gốc **đã có sẵn** 1 dòng ">>> Cập nhật tỷ giá…" trỏ về trang tỷ giá (utm_content=0). Sau khi áp cột I, mỗi bài có 2 link tới trang tỷ giá (khác utm_content). Mình giữ nguyên link cũ.

## 5. Chi tiết chèn
**Dòng 2:** 1 Tệ → "xem thêm" sau mục 3.2 (35%) · nhận tiền từ nước ngoài → gắn vào câu có sẵn đầu mục 4.2 (67%) · 1 Won → "xem thêm" sau đoạn kết (96%).
**Dòng 3:** 1 đô → "xem thêm" cuối mục 4 (34%) · tiền Nhật → viết thêm 1 câu vào đoạn đầu mục 6 (47%, nói về ký hiệu ¥ dùng chung cho CNY và JPY).
**Dòng 4:** tỷ giá Won → "xem thêm" cuối mục 3 (34%) · 1000 Won → "xem thêm" cuối mục 4.1 (69%).

## 6. Anchor bỏ qua vì bài đã có sẵn link đúng URL đích
- Dòng 2: **tiền Nhật** (đã link ở câu trả lời FAQ 5.1) · **1 Yên bằng bao nhiêu tiền Việt** (đã link ở FAQ 5.2).

## 7. Link buộc phải gần nhau
- Dòng 2: "xem thêm" 1 Won nằm ngay trên khối "Lưu ý / Hotline" cuối bài (khối này có link trang chủ, số điện thoại, email). Không còn chỗ khác sau 25% đầu bài mà không sát link.
- Dòng 4: "xem thêm" tỷ giá Won cách link "Dịch vụ nhận và chuyển tiền quốc tế" 1 tiêu đề H2. Đoạn tỷ giá cột I (vị trí đã duyệt sẵn) nằm ngay dưới đoạn có link Techcombank Mobile.

## 8. Chưa làm được
- **Comment trong khung bình luận:** công cụ Drive hiện có không tạo được comment, và kho không có sẵn thông tin xác thực Google để gọi thẳng Drive API. Ghi chú đỏ ngay trong bài vẫn có đủ.

## 9. Lỗi kỹ thuật
- Không có dòng nào cần chạy lại. (Tải bài: phải kèm thông tin trình duyệt, nếu không web trả "Access Denied".)

## 10. Đoạn viết mới chờ duyệt — chi tiết trong `cho-duyet.md`
| Mã | Dòng | File | Anchor → URL đích | Vị trí |
|---|---|---|---|---|
| 3-A | 3 | 1 Tệ bằng bao nhiêu tiền Việt Nam | 1 Won bằng bao nhiêu tiền Việt → /1-won-bang-bao-nhieu-tien-viet | cuối mục 5 (~45%) |
| 3-B | 3 | 1 Tệ bằng bao nhiêu tiền Việt Nam | 1 Yên bằng bao nhiêu tiền Việt → /1-yen-bang-bao-nhieu-tien-viet-nam | sau FAQ 8.1 (~86%) |
| 4-A | 4 | 1 triệu Won bằng bao nhiêu tiền Việt | 1 Man bằng bao nhiêu tiền Việt → /1-man-bang-bao-nhieu-tien-viet | cuối mục 3 (~33%) — nên bỏ qua vì sát link |
| 4-B | 4 | 1 triệu Won bằng bao nhiêu tiền Việt | 1 Tệ bằng bao nhiêu tiền Việt → /1-te-bang-bao-nhieu-tien-viet-nam | mục 4.1 (~47%) |
| 4-C | 4 | 1 triệu Won bằng bao nhiêu tiền Việt | 1 triệu đô bằng bao nhiêu tiền Việt → /1-trieu-do-bang-bao-nhieu-tien-viet | mục 4.2 (~75%) |

## 11. Điểm khác so với câu lệnh
Sheet thực tế: mỗi nhóm anchor chỉ có **2 cột** (J-K, L-M, N-O, P-Q, R-S = Anchor text N / URL đích N), không có cột
"Nội dung chèn ACN". Mình ghép theo đúng số thứ tự trên tiêu đề cột.

## 12. Sửa theo góp ý của Trang (19/10/2026)
- Câu "xem thêm" viết thêm: ghi chú đỏ đổi thành **[Đề xuất viết thêm đoạn mới]**, đặt **trên** câu, cách 1 dòng trống
  (trước đây là "[Viết thêm đoạn mới]" nằm dưới câu).
- Công cụ không sửa được file Docs đã tạo → tạo lại 3 file, chuyển 3 file cũ vào thùng rác (khôi phục được trong 30 ngày),
  cập nhật link mới vào H2, H3, H4 (ô cũ chứa link file cũ do mình điền).
- Soát lại: chữ khớp 100% với bài gốc, trình bày đúng mẫu.

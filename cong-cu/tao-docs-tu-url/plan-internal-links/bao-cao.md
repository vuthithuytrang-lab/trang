# Báo cáo chạy thử — Plan internal links, dòng 2–4 (19/10/2026)

Thư mục Drive: [Plan internal links - File blog](https://drive.google.com/drive/folders/1qLQU6FfkXcOvAsUvKZ-KsVeXWC5RLgHH)

## 1. Các dòng đã làm

| Dòng | Tên file | Link | Bước 1 | Bước 2 |
|---|---|---|---|---|
| 2 | 1 Man bằng bao nhiêu tiền Việt | https://docs.google.com/document/d/127fa70nARZPvMyXvM4bmb9GGHvUldI6_gTz5g7c7Gpw/edit | ✅ | ✅ |
| 3 | 1 Tệ bằng bao nhiêu tiền Việt Nam | https://docs.google.com/document/d/1BZCbsLRwaC5qP0z5eSqS_8xXPuyiYvhvKixGM_edTZM/edit | ✅ | ✅ (2 đoạn chờ duyệt) |
| 4 | 1 triệu Won bằng bao nhiêu tiền Việt | https://docs.google.com/document/d/1wt9qe9M2GG-yqq-fKM_ZkSS1JHd8wS2pUrxDxve9yRQ/edit | ✅ | ✅ (3 đoạn chờ duyệt) |

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

---

# Đợt 2 — 100 URL (dòng 5–104), chạy thử dòng 5–7 (19/10/2026)

| Dòng | Tên file | Link |
|---|---|---|
| 5 | 1 vạn tệ bằng bao nhiêu tiền Việt | https://docs.google.com/document/d/1X5zylbZ_WbFRETqJvVDMc_zVKvFyV1AIWDDHjHf7isA/edit |
| 6 | 1 vạn tiền Đài Loan bằng bao nhiêu tiền Việt | https://docs.google.com/document/d/1mERiPrL6o5K8Ik0h__RGBKN_7I9IkizRvp5Ysuh3FMk/edit |
| 7 | 1 Won bằng bao nhiêu tiền Việt | https://docs.google.com/document/d/1BhtvTbZXL6D57KSV4BSkW7sAjyzITQ2A7Xt4kUylR8I/edit |

- Bài lỗi: không có. H5–H7 trống trước khi ghi. Chữ trong Docs khớp 100% bản đã chèn.
- Đề xuất cột I: cả 3 dòng tìm thấy câu gốc và đã áp nguyên văn. Dòng 5 và 7, câu gốc nằm trong gạch đầu dòng
  → ghi chú [Trước khi chèn] xuống dòng ngay trong gạch đó.
- Link đã chèn: dòng 5: 1 Tệ (xem thêm, 32%), nhận tiền từ nước ngoài (câu có sẵn, 67%), 1 đô (xem thêm, 73%) ·
  dòng 6: 1 Won (xem thêm, 51%), 1 triệu đô (xem thêm, 59%) · dòng 7: 1,000 won (xem thêm, 25%), 1 đô (xem thêm, 78%).
- Bỏ qua vì đã có link: dòng 6 "Tân Đài tệ" (đã link ở FAQ 7.2).
- Link gần nhau: dòng 6 — đoạn áp đề xuất cột I nằm ngay trên câu đã có sẵn link trang tỷ giá (vị trí cột I đã duyệt).
- Đoạn chờ duyệt: 5-A, 5-B, 6-A, 6-B, 7-A, 7-B, 7-C (chi tiết `cho-duyet.md`).
- Phân quyền & comment: như đợt 1, chưa làm được.

## Sửa lần 2 (19/10/2026) — chèn đủ anchor dòng 2–7
- Theo yêu cầu của Trang: **sheet có bao nhiêu anchor thì chèn đủ bấy nhiêu**. Các đoạn trước đây chờ duyệt đã được chèn thẳng
  vào file (có ghi chú đỏ "[Đề xuất viết thêm đoạn mới]"). Anchor mà bài đã có sẵn link đúng URL (dòng 2: tiền Nhật, 1 Yên;
  dòng 6: Tân Đài tệ) được giữ link cũ, có thêm ghi chú đỏ tại chỗ.
- Số anchor/file: dòng 3 = 5 (sheet có 5), các dòng còn lại = 6. Đã kiểm tra: mọi URL đích trong sheet đều có link trong file.
- Dời câu "xem thêm" 1,000 won ở dòng 7 xuống mục 5.1 vì lọt vào 25% đầu sau khi bài dài thêm.
- Tạo lại 6 file, file cũ chuyển vào thùng rác, cập nhật H2–H7.
- **Phân quyền: ĐÃ XONG.** Trang mở quyền "Bất kỳ ai có đường liên kết – Người chỉnh sửa" ở cấp thư mục; đã kiểm tra file con nhận quyền theo.

## Sửa lần 3 (19/10/2026)
- Link có sẵn đúng URL đích (giữ nguyên) nay cũng tô vàng.
- Ghi chú đổi thành "[Nội dung gốc trước khi chèn: …]".
- Tạo lại 6 file, file cũ vào thùng rác, cập nhật H2–H7. Chữ khớp 100%.

## Sửa lần 4 (19/10/2026) — anchor đúng nguyên văn
- Dòng 2: link cũ "hệ thống tiền tệ Nhật Bản" → chuyển sang đúng anchor "tiền Nhật"; link cũ "1 Yên bằng khoảng 164.7 đồng" →
  chuyển sang đúng anchor "1 Yên bằng bao nhiêu tiền Việt" (mỗi chỗ thêm 1 câu ngắn trong cùng câu trả lời FAQ).
- Dòng 6: link cũ "Tiền Đài Loan" → chuyển sang đúng anchor "Tân Đài tệ" (cụm có sẵn ngay trong câu).
- Kiểm tra máy: cả 6 file, mỗi anchor sheet là chữ của đúng 1 link tới đúng URL. Cập nhật H2, H6, E2, E6; 2 file cũ vào thùng rác.

---

# Đợt 2 — dòng 8 → 104 (19/10/2026)

**Kết quả:** 96/97 bài đã tạo file Docs, chèn link, tô vàng, ghi chú; đã điền cột H và cột E. Danh sách đầy đủ trong `tien-do.csv`.
Mọi file nằm trong thư mục "Plan internal links - File blog" (quyền "Bất kỳ ai có đường liên kết – Người chỉnh sửa" theo thư mục).

**Soát tự động từng file trước khi điền sheet:**
- Mỗi anchor trong sheet là chữ NGUYÊN VĂN của 1 link tới đúng URL đích, và được tô vàng (`kiemtra.py`).
- Không mất link gốc nào của bài (`linkcu.py`), không mất bảng / hàng / gạch đầu dòng / ảnh (`cautruc.py`).
- Chữ trong file Docs (xuất PDF) khớp với bản đã chèn (`verify.py`); vài chỗ lệch chỉ do PDF tách chữ / số thứ tự / chữ Hán.

**Cần Trang xem:**
- **Dòng 60** (`vang-la-gi1`): trang trả về 404 → không tạo file. Có thể URL ở cột B gõ thừa số "1".
- **Dòng 15** (Tiền Thái Lan): đề xuất ở cột I nói về Dinar Kuwait, không có trong bài → CHƯA chèn anchor "USD sang VND" (theo quy tắc không tự chèn chỗ khác). Cột I dòng này có lẽ bị dán nhầm của bài Dinar Kuwait (dòng 10).
- **Cột F trống** ở các dòng 28, 34, 39, 86, 102: lấy anchor là cụm chữ đã gắn link trong ô cột I.
- **Viết hoa tên riêng** theo quy tắc: "cic" → "CIC" (dòng 42, 81, 83, 93, 94), "eco card" → "Eco Card", "viettel" → "Viettel".
- **Link trong ô cột I khác cột G** (utm_content) ở nhiều dòng → luôn dùng URL cột G.
- Đề xuất cột I dạng "thêm đoạn riêng" (dòng 52, 54, 100) được chèn thành đoạn mới, ghi chú "[Đề xuất viết thêm đoạn mới]"; dòng 52 vị trí này nằm ở 23% bài (vị trí cột I đã duyệt).

**Lỗi công cụ phát hiện & đã sửa trong đợt này (đã làm lại các file bị ảnh hưởng):**
1. Áp đề xuất cột I làm mất link cũ trong cùng đoạn (dòng 26, 27, 29, 37, 41, 48) → sửa, giữ nguyên link cũ.
2. Áp đề xuất cột I trong bảng / danh sách lồng làm gộp mất hàng (dòng 37, 51, 81, 98) → chỉ sửa đúng ô / gạch chứa câu gốc.
3. Anchor cột I không tô vàng khi chữ không đổi (dòng 75) → luôn tô vàng.
4. Google Docs biến chữ giữa 2 dấu "$" thành công thức toán (dòng 11, "NT$; … NT$") → bọc riêng dấu $; đã kiểm tra toàn bộ file, không còn chỗ nào.

---

# Đợt 3 — dòng 105 → 150 (19/10/2026)

**Kết quả:** 46/46 bài đã tạo file Docs, chèn đủ anchor (đúng nguyên văn sheet), tô vàng, ghi chú; đã điền cột H và cột E.
Soát như đợt 2 (`kiemtra.py`, `linkcu.py`, `cautruc.py`, so chữ PDF bằng `verify.py`).

**Cần Trang xem:**
- **Dòng 131:** ô H đang giữ link bản đầu (có lỗi dính chữ "lãnh sự.Trường hợp…"). Bản đã sửa:
  https://docs.google.com/document/d/1Pk4nlp44qZ1HPcvyVN2i8-U5AEiV_KQPzy5yKlYz5S4/edit — chờ Trang cho phép thay link ở ô H131.
- **Dòng 106:** bài gốc chỉ có ảnh infographic, không có đoạn chữ phù hợp → chèn 1 đoạn mới ngay sau ảnh.
- **Dòng 134:** bài gốc trên web còn sót 1 đoạn ghi chú biên tập sau mục 2.3 → nên báo đội nội dung xóa (mình giữ nguyên).
- **Dòng 137, 139, 145:** bài đã có sẵn link "tỷ giá" nhưng mã utm khác cột G → giữ link cũ, tô vàng, ghi chú ở cột E.
- **Dòng 106, 126–150:** cột I không có đề xuất → anchor tỷ giá được đặt theo quy tắc chung như các anchor khác.

**Lỗi công cụ phát hiện & đã sửa trong đợt này:**
1. Câu viết thêm vào gạch đầu dòng có đoạn bọc bên trong bị Google Docs dính liền với câu trước, không có dấu cách
   (dòng 126, 131) → câu mới nay nằm trong cùng đoạn; đã tạo lại 2 file.
2. Ký tự chỉ số dưới "ₘ" (công thức Fₘ, Sₘ, dòng 137) hiện thành ô vuông trên Docs → đổi sang chữ m dạng chỉ số dưới; đã tạo lại file.

---

# Đợt 4 — dòng 151 → 200 (19/10/2026)

**Kết quả:** 50/50 bài đã tạo file Docs, chèn anchor đúng nguyên văn sheet, tô vàng, ghi chú; đã điền cột H và cột E.
49 bài đủ anchor; dòng 170 thiếu 1 anchor (xem dưới). Soát như các đợt trước + soát thêm 2 lỗi mới phát hiện ở đợt 3.

**Lưu ý bố cục sheet:** từ dòng 151, cột I là ô tích (checkbox); câu đề xuất "Trước/Sau khi chèn" nằm ở **cột J**,
các cặp anchor/URL bắt đầu từ **cột K–L**. Cột E (ghi chú) và H (link file) giữ nguyên vị trí.

**Cần Trang xem:**
- **Dòng 170** (`cach-su-dung-tai-khoan-cong-ty`): câu gốc ở cột J ("Dịch vụ thanh toán cho Doanh nghiệp nhỏ: Đa dạng gói dịch vụ…")
  không có trong thân bài (chỉ có ở menu web) → CHƯA chèn anchor "giá USD". Trang chọn vị trí khác hoặc sửa cột J thì chèn bổ sung.
- **Dòng 154:** câu "Sau khi chèn" ở cột J lặp lại gần nguyên câu đã có ngay sau danh sách — đã áp nguyên văn; cân nhắc bỏ câu trùng.
- **Dòng 155:** bài về Thái Lan nhưng anchor tỷ giá là "giá yên hôm nay" — đã áp đúng câu đã duyệt.
- **Dòng 183:** cột F trống → anchor lấy từ cụm gắn link trong ô cột J ("giá Euro").
- **Dòng 161, 200:** link gắn trong ô cột J có mã utm khác cột G → dùng đúng link cột G.
- Viết hoa tên riêng trong anchor: "cách nạp tiền viettel" → "cách nạp tiền Viettel" (158), "eco card" → "Eco Card" (159).

---

# Đợt 5 — dòng 201 → 250 (19/10/2026) — chuẩn content mới

**Kết quả:** 50/50 bài đã tạo file Docs, đủ 100% anchor (đúng nguyên văn sheet), tô vàng, ghi chú; đã điền cột H và cột E.

**Phản hồi của Trang:** "nhiều đoạn chèn còn gượng ép, chưa tự nhiên" → từ đợt này áp **chuẩn content mới** (chi tiết trong
`HUONG-DAN-WORKER.md`, mục CONTENT QUALITY):
- Ưu tiên gắn link vào cụm có sẵn, hoặc **viết lại nhẹ 1 câu có sẵn** (kiểu chèn mới `vietlai`) thay vì thêm câu mới.
- Chỉ chèn ở đoạn đang nói đúng chủ đề; câu chèn phải nối mạch câu trước, nói rõ người đọc được gì khi bấm.
- Cấm câu sáo ("Bên cạnh đó, bạn cũng có thể tham khảo…", "để hiểu rõ hơn", "hữu ích", "tại đây"…); giữ giọng xưng hô của bài.
- Mỗi chỗ chèn được tự đọc lại cùng câu trước/sau như biên tập viên.
- Công cụ: kiểu `vietlai` sửa ngay trong đúng đoạn chữ chứa câu gốc → giữ nguyên in nghiêng, xuống dòng (đã sửa dòng 236, 237).

**Cần Trang xem:**
- **Cột J từ dòng 204 → 250** chỉ ghi ngày "20/10/2026", không có câu đề xuất → anchor tỷ giá do mình tự đặt theo chuẩn mới.
  Một số bài không nói gì về ngoại tệ (VD dòng 212, 218, 220, 225, 238, 241, 242, 243, 245, 246) nên câu tỷ giá vẫn hơi xa chủ đề —
  đây là giới hạn của việc ghép anchor tỷ giá vào bài không liên quan.
- **Dòng 233:** bài gốc có 1 link hỏng (đường link dính 2 địa chỉ) ở cụm "tính lãi suất tiết kiệm online" → đã bỏ link hỏng và gắn lại
  đúng anchor; nên báo đội web sửa trên bài.

---

# Đợt 6 — dòng 251 → 300 (19/10/2026)

**Kết quả:** 50/50 bài đã tạo file Docs, đủ 100% anchor (đúng nguyên văn sheet), tô vàng, ghi chú; đã điền cột H và cột E.
Áp chuẩn content mới như đợt 5.

**Lưu ý bố cục sheet:** dòng 251–274 cột J trống (không có đề xuất) → anchor tỷ giá tự đặt; **từ dòng 275 cột F, G trống**
(không có anchor tỷ giá) → chỉ chèn các cặp anchor từ cột K.

**Cần Trang xem:**
- **Dòng 264:** cụm "Techcombank Eco" nằm ở mục thẻ tín dụng Visa Eco, nhưng URL đích trên sheet là bài thẻ ghi nợ Eco Card — xem lại URL.
- **Dòng 294:** trang đích traveloka-voucher có nhãn "Blog đã hết hạn" — kiểm tra trang đích còn dùng được không.
- Một số bài không nói gì về ngoại tệ (VD 251, 253, 255, 258, 269, 274) nên câu tỷ giá vẫn hơi xa chủ đề.

---

# Đợt 7 — dòng 301 → 350 (20/10/2026)

**Kết quả:** 49/50 bài đã tạo file Docs, đủ 100% anchor (đúng nguyên văn sheet), tô vàng, ghi chú; đã điền cột H và cột E.
Đợt này sheet không có anchor tỷ giá (cột F, G trống) — chỉ chèn các cặp anchor từ cột K. Áp chuẩn content mới.

**Cần Trang xem:**
- **Dòng 333** (`cach-tao-ma-qr`): trang bài gốc báo "Không tìm thấy trang" (đã thử lại) → chưa tạo file; đã ghi lý do vào cột E.
- Một vài anchor khó khớp chủ đề bài (VD "giá điện sinh hoạt mới nhất" trong bài nạp thẻ Viettel dòng 324, "mở tài khoản cho học sinh"
  trong bài quét NFC dòng 328) — đã đặt ở chỗ hợp ngữ cảnh nhất có thể.

---

# Đợt 8 — dòng 351 → 407 (21/10/2026)

**Kết quả:** 57/57 bài đã tạo file Docs, đủ 100% anchor (đúng nguyên văn sheet, kể cả chữ hoa/thường), tô vàng, ghi chú.
Áp chuẩn content mới như đợt 5–7.

**Bố cục sheet đổi (từ 21/10/2026):** sheet được chèn thêm 2 cột → **link file Docs nay ở cột I (FILE BLOG)**,
**ghi chú ở cột F (Ghi chú)**; cột E là "Tình trạng", G/H là anchor/URL tỷ giá, anchor cặp bắt đầu từ cột M.
Các dòng cũ (2–350) tự dời theo, không mất dữ liệu. Dòng 351–407 không có anchor tỷ giá.

**Cần Trang xem:**
- **Dòng 407:** sheet có 2 anchor cùng chữ "thuế thu nhập cá nhân" trỏ 2 URL khác nhau (bài tổng quan và bài cách tính)
  → đã chèn 2 link riêng ở 2 chỗ cách xa nhau, mỗi chỗ hợp với bài đích của nó.
- **Dòng 393:** anchor "nộp thuế hộ trên etax" giữ đúng chữ thường như sheet (trong bài các chỗ khác viết "eTax").
  Một số dòng cũ (VD 42, 81, 224, 246…) từng viết hoa tên riêng (CIC, Viettel, Eco Card, eTax) khác sheet — báo nếu cần sửa về đúng chữ thường.
- Vài anchor xa chủ đề bài (VD "giá điện sinh hoạt" trong bài Co-Loyalty dòng 379, "công ty dùng tài khoản cá nhân" dòng 394)
  — đã đặt ở chỗ hợp ngữ cảnh nhất có thể.

# Quy trình nghiên cứu & tối ưu content — bảng chạy việc một trang

Bản gộp ngày 06/11/2026. Toàn văn quy trình nằm ở
`.claude/skills/toi-uu-content-seo/SKILL.md` — file này là **bảng kiểm để tick khi chạy**,
không chép lại toàn bộ.

## 5 nguyên tắc xuyên suốt — vi phạm là làm lại

1. **Dừng hỏi sau mỗi chặng có dấu ⏸.** Trang gật mới đi tiếp.
2. **Không bịa.** Không có số liệu, không đọc được trang ⇒ ghi `[CẦN TRANG BỔ SUNG: …]`
   hoặc báo bị chặn. Tuyệt đối không suy đoán nội dung.
3. **Mọi nhận xét phải có bằng chứng** trích từ chính bài đang chấm.
4. **Đề xuất phải chỉ đúng chỗ, đưa đúng chữ.** Cấm nói chung chung kiểu "nên viết hấp dẫn hơn".
5. **Nội dung gửi ra ngoài giữ giọng thương hiệu khách hàng.** Cách xưng hô riêng trong chat
   không mang vào ấn phẩm.

---

## Bảng chạy việc 10 chặng

| # | Chặng | Đầu ra phải có | ⏸ | Tài liệu |
|---|---|---|:-:|---|
| 0 | **Nhận nguyên liệu & chốt bối cảnh** | Trả lời xong 6 câu: bài mới hay đã đăng · đang top mấy · key chính và key mở rộng · khách có site không · điều cấm · đầu ra muốn gì | ⏸ | — |
| 1 | **Hiểu người tìm** | 3W + bối cảnh + dạng truy vấn (tìm hiểu / so sánh / mua hàng) | ⏸×7 | `quy-trinh-nghien-cuu-search-intent.md` |
| 2 | **Soi website khách** | Sơ đồ trang · dữ liệu thật từ trang sản phẩm · bảng bài cũ đang tự cạnh tranh · danh sách chỗ site tự nói ngược nhau · thông tin thương hiệu | ⏸ | `KY-THUAT-BOC-DU-LIEU.md` |
| 3 | **Soi từng đối thủ** | 7 mục mỗi bài: dạng trang · dàn ý · bộ lọc sản phẩm · mạnh · yếu · nỗi đau đã đáp ứng · chưa đáp ứng | ⏸ | `khung-phan-tich-doi-thu.md` |
| 4 | **Soi bài của Trang** | Bảng 4 luật + bảng E-E-A-T + đối chiếu bài với dữ liệu thật trên site | ⏸ | `checklist-eeat.md`, `quy-trinh-toi-uu-bai-viet.md` |
| 5 | **Bảng khoảng trống** | 3 nhóm: đang thua · khoảng trống vàng · cả hàng đã có | ⏸ | — |
| 6 | **Đề xuất tối ưu** | Bảng CẮT · bảng BỔ SUNG · cấu trúc và tên heading · bảng phân bổ từ khóa · danh sách lỗi phải vá | ⏸ | `LUAT-DAT-HEADING.md` |
| 7 | **Viết bài** | Bài hoàn chỉnh + bảng tự chấm 14 luật | — | `luat-viet-content.md` |
| 8 | **Bàn giao** | HTML đúng định dạng site khách (hoặc file HTML tự viết cho Trang đọc) + việc cần làm sau khi dán | — | `ky-thuat-ban-giao.md` |
| 9 | **Tiếp thu góp ý** | Bảng đối chiếu *đoạn được comment → comment → đã xử lý thế nào* | — | `ky-thuat-ban-giao.md` |

---

## Ba chặng hay bị bỏ qua nhất

**Chặng 0** — ngắn nhất nhưng đã làm sai hai lần vì bỏ qua: đề xuất viết bài mới trong khi bài cũ
đang top 6, và ép key mở rộng vào mọi heading trong khi nó chỉ là key phụ.

**Chặng 2** — chặng cho ra nhiều thứ nhất. Lần chạy OSAKAR, chặng này tìm ra 4 thứ mà đọc đối thủ
không bao giờ thấy: bài nháp trùng bài đã đăng · 3 bài cũ tự cạnh tranh · dòng sản phẩm thật khác
hẳn bài đang viết · 7 chỗ website tự nói ngược nhau.

**Chặng 6.4** — rải từ khóa. Nhiều hơn không phải lúc nào cũng tốt: nhồi quá là mất thứ hạng của
key chính chứ không được thêm key phụ.

---

## Hai luật dễ quên nhất

**Khoảng trống vàng không tự động là cơ hội.** Cả hàng cùng trống thì phải hỏi thêm:
*người đọc có thật sự cần thứ đó ở giai đoạn này không?* Không qua được thì bỏ.

**Bài đang có thứ hạng thì sửa tại chỗ.** Giữ nguyên URL, giữ nguyên tên các mục đã chạy được.
Dựng bài mới là vứt đi vốn xếp hạng và tự cạnh tranh với chính mình.

---

## Ca mẫu đã chạy đủ 10 chặng

`VI-DU-OSAKAR.md` — từ khóa "xe điện giống Vespa", tháng 9/2026. Có số liệu thật, bảng khoảng
trống thật, và hai lỗi đã mắc kèm luật rút ra.

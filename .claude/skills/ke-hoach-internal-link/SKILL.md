---
name: ke-hoach-internal-link
description: Lập kế hoạch chèn internal link (inlink) cho BẤT KỲ dự án SEO nào có blog — nhận danh sách trang đích (landing page) + số link mục tiêu + anchor text ưu tiên, tải và đọc nội dung bài trên website, chọn bài nguồn cùng chủ đề, chọn anchor, chọn đúng câu/đoạn để chèn tự nhiên, giới hạn tối đa 5 anchor mỗi bài, loại link gượng ép, rồi dựng bộ tab trên Google Sheet (Kế hoạch chèn link, Plan inlink tổng quan theo bài nguồn, Plan internal links theo mẫu, Link trỏ về từng trang đích có cột còn thiếu và chủ đề bài đã lấy, Anchor text ưu tiên, Cách đọc file). Dùng skill này bất cứ khi nào Trang nhắc tới internal link, inlink, chèn link nội bộ, anchor text, kế hoạch chèn link, link trỏ về trang đích, "bài nào chèn link về trang nào", sếp góp ý về số anchor mỗi bài, hoặc đưa một danh sách URL đích kèm số link cần — cho dự án mới hay dự án cũ (Techcombank…), kể cả khi chị không gọi đúng tên skill. Nếu chị chỉ nhờ một chặng (chỉ làm tab tổng quan, chỉ đếm còn thiếu, chỉ sửa vị trí chèn), vẫn dùng skill này và làm đúng chặng đó.
---

# Lập kế hoạch internal link — dùng cho mọi dự án

Skill đóng gói cách làm kế hoạch inlink đã chạy thật cho dự án Techcombank (xem
`references/vi-du-techcombank.md`), viết lại để áp dụng cho website và khách hàng bất kỳ.

**Trang là người Nontech.** Gọi chị là "bạn xinh đẹp", nói bằng lời thường. Tự làm hết phần kỹ thuật.
Chỉ hỏi khi phải chốt quyết định hoặc thiếu dữ liệu đầu vào thật sự.

---

## 🔒 Năm luật cứng (áp dụng cho mọi dự án)

1. **Mỗi bài nguồn chèn tối đa 5 anchor** (trừ khi dự án/sếp quy định số khác — hỏi ở Bước 0).
   Khi phải cắt, giữ link liên quan nhất trước (Phù hợp cao → Có thể đi → Cần soát; có sẵn cụm anchor được ưu tiên).
2. **Chèn tự nhiên, logic, không gượng ép.** Đọc nội dung bài trước khi chọn chỗ. Link không có chỗ tự nhiên
   → NÊN BỎ, loại khỏi kế hoạch kể cả khi trang đích thiếu mục tiêu. Báo thật số bị loại và số còn thiếu.
3. **Hạn chế chèn vào nội dung có luật** (luật, nghị định, thông tư, điều khoản), bảng số liệu, các bước thao tác:
   không sửa câu gốc, chỉ thêm 1 dòng "Xem thêm: …" sau đoạn (đặt sau cả danh sách/bảng).
4. **Không trùng:** không lặp cặp (trang đích, bài nguồn); không chèn vào bài đã có sẵn link về trang đích đó;
   trang đích không tự chèn link về chính nó.
5. **Hiểu đúng chiều dữ liệu và làm theo mẫu của Trang.**
   - "URL" trong tab mẫu = **bài viết sẽ chèn anchor** (bài nguồn). "Link chèn"/"Trang đích" = **link mục tiêu** (trỏ VỀ).
   - Tab tổng quan = **mỗi hàng 1 bài nguồn** + các cặp Anchortext 001 / URL đích 001… trừ khi mẫu nói khác.
   - Chị đưa file mẫu → mở đúng tab, sao đúng cấu trúc cột, chip, màu. Còn mơ hồ → hỏi lại trước khi làm.

---

## Bước 0 — Thu thập thông tin dự án (hỏi gọn trong 1 tin, chỉ hỏi cái còn thiếu)

| Cần có | Ghi chú |
|---|---|
| Tên dự án, tên miền website | Ví dụ `abc.vn`; dùng để đặt tên tab/thư mục và lọc link nội bộ |
| Danh sách trang đích + số link mục tiêu (+ nhóm nếu có) | Thường là 1 Google Sheet hoặc file dán vào chat |
| Anchor text ưu tiên cho từng trang đích | Không có → tự đề xuất từ tiêu đề + từ khoá chính của trang đích, ghi rõ là đề xuất |
| Danh sách bài blog | Sitemap (`/sitemap.xml`, `/post-sitemap.xml`…) hoặc danh sách Trang đưa |
| Link nội bộ đang có | Nếu có báo cáo (Ahrefs/Screaming Frog) thì dùng; không có thì lấy từ chính bài đã tải |
| Giới hạn anchor/bài, file mẫu cần theo | Mặc định 5 anchor/bài; mẫu mặc định là bộ tab ở Bước 5 |
| File Google Sheet làm việc | Có sẵn thì làm trong file đó; chưa có thì tạo file mới qua Drive và gửi link |

Ghi một dòng tóm tắt dự án vào tab "Cách đọc file". Lưu file kết quả vào
`Kết quả công việc Agent Boss/Viec that - Internal link <TÊN DỰ ÁN>/`.

## Bước 1 — Kiểm tra truy cập website
Tải thử 1 bài bằng script ở Bước 2. Bị chặn hoặc trang dựng bằng JavaScript (ra rất ít khối nội dung)
→ báo Trang rõ bị chặn ở đâu, đề xuất đường vòng (chị gửi file xuất nội dung, hoặc chạy trên máy cá nhân).
**Không đọc được nguồn thì dừng, tuyệt đối không đoán nội dung.**

## Bước 2 — Tải nội dung bài (cả bài nguồn lẫn trang đích)
```bash
python3 .claude/skills/ke-hoach-internal-link/scripts/tai_bai.py danh-sach-url.txt <scratchpad>/art
```
Mỗi bài lưu thành khối h1/h2/h3/p/li/td + danh sách link nội bộ có sẵn. Bài lỗi được liệt kê để báo lại.

## Bước 3 — Chọn cặp (trang đích ← bài nguồn) và anchor
- Chấm điểm liên quan: từ khoá anchor + tiêu đề trang đích xuất hiện trong bài nguồn; ưu tiên bài cùng chủ đề.
- Đủ số mục tiêu nhưng không vượt 5 anchor/bài; trong một bài không dùng một anchor cho hai trang đích.
- Tránh anchor quá chung (1 chữ như "vay", "thẻ") trỏ về trang hẹp — đây là nguồn gượng ép lớn nhất ở dự án trước.
- Ghi tạm vào tab "Kế hoạch chèn link (mới)" (cấu trúc ở Bước 5), chưa cần cột vị trí.

## Bước 4 — Đọc kỹ để chọn chỗ chèn (bắt buộc, phần quan trọng nhất)
1. Tạo tab tạm `tmp_vi_tri`: trang đích | anchor | bài nguồn, **sắp theo bài nguồn**. Đọc lại tab, xuất
   `links.tsv` (hàng, đích, anchor, nguồn) từ đúng thứ tự trên sheet.
2. Lọc đoạn ứng viên và chia lô (≈245 link/lô):
   ```bash
   python3 .claude/skills/ke-hoach-internal-link/scripts/loc_doan_ung_vien.py links.tsv <scratchpad>/art <scratchpad>/lo 12 "<tên thương hiệu>"
   ```
3. Giao mỗi lô cho 1 người phụ (Agent, chạy nền, song song) với nội dung `references/huong-dan-nguoi-doc.md`
   (thay {INFILE}, {SHEET_ID}, {TAB}, {R1}, {R2}). Người phụ tự ghi cột D–H của tab tạm.
   Dự án nhỏ (dưới ~150 link) có thể tự đọc, không cần chia lô.
4. Tất cả xong → đọc lại tab tạm, soát đủ hàng, anchor có trong cột cách chèn, đếm theo mức độ.
5. Đưa kết quả về tab chính bằng `MATCH(B&"|"&D; tmp!I:I; 0)` + `INDEX`, rồi dán giá trị.
   Tách dòng NÊN BỎ khỏi kế hoạch (để tab riêng cho Trang xem), báo số lượng và lý do chính.
6. Dọn ghi chú có nhắc số dòng/số đoạn nội bộ; xoá tab tạm.

## Bước 5 — Bộ tab tổng hợp chuẩn
| Tab | Cấu trúc |
|---|---|
| **Cách đọc file** | Giải thích từng tab bằng lời thường + số liệu chính; cập nhật mỗi lần sửa |
| **Kế hoạch chèn link (mới)** | STT · Trang đích · Anchor · Chèn vào bài · Đặt dưới mục · Câu trong bài · Cách chèn · Mức độ · Tình trạng (Chưa làm/Đang làm/Đã chèn/Bỏ qua) · Ghi chú · nhóm, thứ tự (ẩn) · Chủ đề bài nguồn |
| **Plan inlink (tổng quan)** | Mỗi hàng 1 bài nguồn: STT · Bài chèn link · Số link chèn · Phù hợp cao · Có thể đi · Cần soát · Tình trạng (tự tính) · Hoàn thiện (checkbox) · Ghi chú · Anchortext 001 · URL đích 001 … 005 (`INDEX(FILTER(...);k)`) |
| **Plan internal links (<n> trang đích)** | Theo mẫu "Plan internal links": STT · URL (bài chèn) · **Link chèn** · Tình trạng (chip) · Định hướng (chip Bổ sung/Đổi anchor text) · Anchor text target · Lý do chèn (nền xanh) · Vị trí dự kiến chèn (Mục/Câu/Cách) · Trạng thái (chip Chưa xử lý/Đã xử lý) |
| **Link trỏ về từng trang đích** | STT · Trang đích · Nhóm · Số link mục tiêu · Số bài đã đề xuất · **Còn thiếu so với mục tiêu** (đỏ/xanh) · **Chủ đề bài đã lấy (số bài)** · Danh sách bài |
| **Chủ đề bài nguồn** | Bài nguồn · Mã · Chủ đề + bảng chủ đề (cột E–F). Bảng chủ đề lập riêng cho từng ngành (15–20 nhóm theo chuyên mục website); sửa ở đây thì các tab khác tự đổi |
| **Anchor text ưu tiên** | URL · Anchor · Số lần đã đề xuất (COUNTIFS về tab Kế hoạch) |

Công thức "Chủ đề bài đã lấy" (Google Sheets, locale vi_VN, thay N bằng hàng cuối):
```
=IFERROR(LET(t;FILTER('Kế hoạch chèn link (mới)'!$M$3:$M$N;'Kế hoạch chèn link (mới)'!$B$3:$B$N=B2);
 u;UNIQUE(t);c;MAP(u;LAMBDA(x;COUNTIF(t;x)));s;SORT(HSTACK(u;c);2;FALSE);
 TEXTJOIN(CHAR(10);TRUE;BYROW(s;LAMBDA(r;INDEX(r;1;1)&": "&INDEX(r;1;2)&" bài"))));"")
```
Màu: theo cẩm nang thương hiệu SEONGON nếu là sản phẩm nội bộ (tiêu đề xanh `#004AEF`, chữ trắng);
nếu Trang đưa mẫu thì theo màu của mẫu.

## Bước 6 — Soát, lưu, báo
- Đọc lại toàn bộ tab chính bằng python: số dòng, tối đa 5/bài, không trùng cặp, không ô trống,
  tab tổng quan khớp từng cặp, tổng "Số bài đã đề xuất" = số dòng kế hoạch.
- Xuất Excel (Drive `download_file_content`, mime xlsx) vào thư mục dự án, commit, push.
- Báo Trang (đánh số): đã làm gì, tổng link, số bị loại vì gượng ép, trang đích thiếu nhiều nhất,
  phương án tiếp theo (giữ ít mà tự nhiên / lấy lại một phần bằng "Xem thêm" / nới giới hạn).
  Nhắc Cmd + R. Hỏi 2 câu: có lỗi hiển thị không, có ưng không/muốn chỉnh gì.

---

## Mẹo kỹ thuật Google Sheets (đã vấp, đừng vấp lại)
- Locale vi_VN dùng `;` trong công thức (kiểm tra locale của file mới trước). Field mask không dùng ngoặc.
- PASTE_VALUES là lệnh riêng, chạy sau khi công thức đã tính.
- **Không dùng vùng mở** `$B$3:$B` — xuất Excel cắt sai. Dùng vùng đóng `$B$3:$B$<hàng cuối>`.
  Sau khi thêm/xoá hàng, kiểm tra các tab khác còn đếm đủ vùng không.
- Batch lỗi "Internal error" → không lệnh nào được áp dụng; tách nhỏ gửi lại.
- Ưu tiên copyPaste/công thức trong sheet thay vì chép tay. Phải chép tay → khúc 60 hàng, soát checksum
  (`SUMPRODUCT(ROW();cột)`) so với python. Dữ liệu lặp → mã số + bảng tra để giảm khối lượng chép.
- Chip màu: `setDataValidation` với `customUiMode: CHIP` và `dropdownStyle` từng giá trị.
- Trang có thể tự xoá/đổi cột giữa chừng → luôn đọc lại tiêu đề cột trước khi ghi.

## File trong skill
- `scripts/tai_bai.py` — tải bài của website bất kỳ thành khối nội dung + link nội bộ có sẵn.
- `scripts/loc_doan_ung_vien.py` — lọc 4 đoạn ứng viên/link, chia lô cho người phụ đọc.
- `references/huong-dan-nguoi-doc.md` — nội dung giao cho người phụ chọn chỗ chèn.
- `references/vi-du-techcombank.md` — dự án mẫu đã làm: số liệu, bài học, bảng chủ đề ngành tài chính.

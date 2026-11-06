---
name: ke-hoach-internal-link
description: Lập kế hoạch chèn internal link (inlink) cho danh sách trang đích SEO trên một website blog (đã làm cho Techcombank, 75 trang đích) — đọc nội dung bài, chọn bài nguồn cùng chủ đề, chọn anchor text, chọn đúng câu/đoạn để chèn tự nhiên, giới hạn tối đa 5 anchor mỗi bài, loại link gượng ép, rồi dựng các tab tổng hợp trên Google Sheet (Kế hoạch chèn link, Plan inlink tổng quan theo bài nguồn, Plan internal links theo mẫu, Link trỏ về từng trang đích có cột còn thiếu và chủ đề bài đã lấy, Anchor text ưu tiên). Dùng skill này bất cứ khi nào Trang nhắc tới internal link, inlink, chèn link nội bộ, anchor text, kế hoạch chèn link, link trỏ về trang đích, "bài nào chèn link về trang nào", hoặc sếp góp ý về số anchor mỗi bài — kể cả khi chị không gọi đúng tên skill. Nếu chị chỉ nhờ một chặng (chỉ làm tab tổng quan, chỉ đếm còn thiếu, chỉ sửa vị trí chèn), vẫn dùng skill này và làm đúng chặng đó.
---

# Lập kế hoạch internal link

Skill này đóng gói toàn bộ cách làm kế hoạch inlink cho dự án Techcombank (75 trang đích, file
Google Sheet `13hkMCuxKjgAvcrttR3lB4on921htw9bhIRFJVoU-xG4`). Dùng lại được cho website khác cùng kiểu.

**Trang là người Nontech.** Gọi chị là "bạn xinh đẹp", nói bằng lời thường. Tự làm hết phần kỹ thuật.
Chỉ hỏi khi phải chốt quyết định (ví dụ: bỏ hay giữ link gượng ép, chấp nhận thiếu link hay nới giới hạn).

---

## 🔒 Năm luật cứng (rút ra từ góp ý của sếp và của Trang)

1. **Mỗi bài nguồn chèn tối đa 5 anchor.** Sếp từng chê bài bị chèn 14 anchor là "quá nhiều, không thể chèn".
   Khi phải cắt, giữ link liên quan nhất trước (Phù hợp cao → Có thể đi → Cần soát; có sẵn cụm anchor được ưu tiên).
2. **Chèn phải tự nhiên, logic, không gượng ép.** Đọc nội dung bài trước khi chọn chỗ. Link nào không có chỗ
   tự nhiên → đánh dấu NÊN BỎ và loại khỏi kế hoạch, kể cả khi làm trang đích thiếu so với mục tiêu.
   Báo thật số link bị loại và số còn thiếu; đừng ép bài lạc đề cho đủ chỉ tiêu.
3. **Hạn chế chèn vào nội dung có luật** (luật, nghị định, thông tư, điều khoản), bảng số liệu, các bước thao tác:
   không sửa câu gốc, chỉ thêm 1 dòng "Xem thêm: …" sau đoạn (đặt sau cả danh sách/bảng).
4. **Không trùng:** không đề xuất cùng một cặp (trang đích, bài nguồn) hai lần; không đề xuất vào bài đã có sẵn
   link về trang đích đó (kiểm tra bằng danh sách link trong bài đã tải và tab "Inlink đã chèn").
5. **Đọc kỹ yêu cầu, hiểu đúng chiều dữ liệu.** Trang từng phải sửa vì làm ngược chiều:
   - "URL" trong các tab mẫu của chị = **bài viết sẽ chèn anchor** (bài nguồn).
   - "Link chèn" / "Trang đích" = **1 trong các link mục tiêu** (link trỏ VỀ).
   - "Plan inlink (tổng quan)" = **mỗi hàng 1 bài nguồn**, kèm các cặp Anchortext 001 / URL đích 001… (không phải mỗi hàng 1 trang đích).
   Có chỗ mơ hồ → mở file mẫu chị đưa, đọc đúng tab, làm theo cấu trúc đó. Vẫn chưa chắc → hỏi lại.

---

## Quy trình

### Bước 1 — Đọc đầu vào
- Danh sách trang đích + nhóm + số link mục tiêu (tab "Link trỏ về từng trang đích", cột B/C/D).
- Anchor text ưu tiên sếp giao (tab "Anchor text ưu tiên": URL | Anchor | Số lần đã đề xuất).
- Link đang có sẵn (tab "Inlink đã chèn").
- Danh sách bài blog (sitemap). Bị chặn không đọc được nguồn → báo rõ và dừng, không đoán nội dung.

### Bước 2 — Tải nội dung bài
```bash
python3 .claude/skills/ke-hoach-internal-link/scripts/tai_bai.py danh-sach-url.txt <scratchpad>/art
```
Tải cả bài nguồn lẫn trang đích (để lấy tiêu đề). Script ghi lại bài lỗi — bài nào lỗi thì báo, không đoán.

### Bước 3 — Chọn cặp (trang đích ← bài nguồn) và anchor
- Bài nguồn phải cùng chủ đề trang đích (chấm điểm theo từ khóa anchor + tiêu đề trang đích xuất hiện trong bài).
- Ưu tiên anchor sếp giao; trong một bài không dùng trùng anchor cho hai trang đích khác nhau.
- Áp luật 5 anchor/bài; bài thừa thì cắt theo mức độ liên quan, rồi tìm bài khác còn chỗ để bù.

### Bước 4 — Đọc kỹ để chọn chỗ chèn (phần quan trọng nhất)
1. Tạo tab tạm (ví dụ `tmp_vi_tri`) gồm: trang đích | anchor | bài nguồn, **sắp theo bài nguồn** để các link
   cùng bài nằm liền nhau. Đọc lại tab để biết số hàng của từng link, xuất ra `links.tsv` (hàng, đích, anchor, nguồn).
2. Lọc đoạn ứng viên và chia lô:
   ```bash
   python3 .claude/skills/ke-hoach-internal-link/scripts/loc_doan_ung_vien.py links.tsv <scratchpad>/art <scratchpad>/lo 12
   ```
3. Giao mỗi lô cho 1 người phụ (Agent, chạy song song, chạy nền) với nội dung
   `references/huong-dan-nguoi-doc.md` (thay {INFILE}, {SHEET_ID}, {TAB}, {R1}, {R2}).
   Người phụ tự ghi kết quả vào cột D–H của tab tạm. Khoảng 245 link/lô là vừa.
4. Khi tất cả xong: đọc lại tab tạm, soát đủ hàng, anchor có trong cột cách chèn, đếm theo mức độ.
5. Đưa kết quả vào tab chính bằng công thức MATCH theo khóa `đích|nguồn`, rồi dán giá trị.
   Tách các dòng NÊN BỎ ra khỏi kế hoạch (để riêng một tab cho Trang xem nếu chị muốn), báo số lượng.
6. Dọn ghi chú có nhắc số dòng/số đoạn nội bộ, xóa tab tạm.

### Bước 5 — Dựng các tab tổng hợp
| Tab | Cấu trúc |
|---|---|
| **Kế hoạch chèn link (mới)** | STT · Trang đích · Anchor · Chèn vào bài · Đặt dưới mục · Câu trong bài · Cách chèn · Mức độ · Tình trạng (Chưa làm/Đang làm/Đã chèn/Bỏ qua) · Ghi chú · nhóm, thứ tự (ẩn) · Chủ đề bài nguồn |
| **Plan inlink (tổng quan)** | Mỗi hàng 1 bài nguồn: STT · Bài chèn link · Số link chèn · Phù hợp cao · Có thể đi · Cần soát · Tình trạng (tự tính) · Hoàn thiện (checkbox) · Ghi chú · Anchortext 001 · URL đích 001 … 005 (công thức `INDEX(FILTER(...);k)`) |
| **Plan internal links (75 trang đích)** | Theo mẫu tab "Plan internal links trang tỷ giá" (file `1OsYTdpTGQJ20J1UwcHfmkk_igFMrxZZIz074jamGAI8`): STT · URL (bài chèn) · **Link chèn** (trang đích) · Tình trạng (chip) · Định hướng (chip) · Anchor text target · Lý do chèn (nền xanh) · Vị trí dự kiến chèn (Mục/Câu/Cách) · Trạng thái (chip Chưa xử lý/Đã xử lý) |
| **Link trỏ về từng trang đích** | STT · Trang đích · Nhóm · Số link mục tiêu · Số bài đã đề xuất · **Còn thiếu so với mục tiêu** (đỏ/xanh) · **Chủ đề bài đã lấy (số bài)** · Danh sách bài |
| **Chủ đề bài nguồn** | Bài nguồn · Mã · Chủ đề (bảng 19 chủ đề ở cột E–F); sửa ở đây thì cột chủ đề các tab khác tự đổi |
| **Anchor text ưu tiên** | Cột C đếm số lần đã đề xuất bằng COUNTIFS về tab Kế hoạch |
| **Cách đọc file** | Giải thích từng tab bằng lời thường, cập nhật số liệu mỗi lần sửa |

Công thức chủ đề bài đã lấy (Google Sheets, dấu `;`):
```
=IFERROR(LET(t;FILTER('Kế hoạch chèn link (mới)'!$M$3:$M$N;'Kế hoạch chèn link (mới)'!$B$3:$B$N=B2);
 u;UNIQUE(t);c;MAP(u;LAMBDA(x;COUNTIF(t;x)));s;SORT(HSTACK(u;c);2;FALSE);
 TEXTJOIN(CHAR(10);TRUE;BYROW(s;LAMBDA(r;INDEX(r;1;1)&": "&INDEX(r;1;2)&" bài"))));"")
```

### Bước 6 — Soát, lưu, báo
- Đọc lại toàn bộ tab chính bằng python: số dòng, tối đa 5/bài, không trùng cặp, không ô trống, tab tổng quan khớp từng cặp.
- Xuất Excel (Drive `download_file_content`, mime xlsx) vào
  `Kết quả công việc Agent Boss/Viec that - Internal link TCB/De-xuat-internal-link-75-trang-dich.xlsx`, commit, push.
- Báo Trang: đã làm gì (đánh số), số link, số bị loại vì gượng ép, trang đích còn thiếu nhiều nhất, phương án tiếp theo.
  Nhắc Cmd + R. Hỏi 2 câu: có lỗi hiển thị không, có ưng không/muốn chỉnh gì.

---

## Mẹo kỹ thuật Google Sheets (đã vấp, đừng vấp lại)
- Locale vi_VN: công thức dùng `;`. Field mask không dùng ngoặc.
- Dán giá trị (PASTE_VALUES) phải là lệnh riêng, sau khi công thức đã tính xong.
- **Không dùng vùng mở** như `$B$3:$B` trong công thức: xuất Excel sẽ cắt sai. Dùng vùng đóng `$B$3:$B$2213`.
  Sau khi thêm/xóa hàng, kiểm tra lại các tab khác có còn đếm đủ vùng không (từng bị đếm thiếu tới hàng 2648).
- Batch update lỗi "Internal error" → không lệnh nào được áp dụng; tách nhỏ rồi gửi lại.
- Viết dữ liệu dài: ưu tiên copyPaste/công thức trong sheet thay vì chép tay. Phải chép tay thì chia khúc 60 hàng
  và soát bằng checksum (`SUMPRODUCT(ROW();cột)`) so với python.
- Chép giá trị số dài → dùng mã số + bảng tra (VLOOKUP) để giảm khối lượng chép.
- Chip màu: `setDataValidation` với `customUiMode: CHIP` và `dropdownStyle` cho từng giá trị.
- Trang tự xóa/đổi cột trong file giữa chừng → luôn đọc lại tiêu đề cột trước khi ghi.

## Kết quả lần chạy Techcombank (tháng 10–11/2026) để đối chiếu
- 2.942 link ban đầu (sau luật 5 anchor/bài) → đọc kỹ thì 731 link gượng ép bị loại → còn 2.211 link trên 734 bài.
- Mức độ: Phù hợp cao 471 · Có thể đi 949 · Cần soát 791.
- 71/75 trang đích chưa đủ mục tiêu, tổng thiếu 1.179 link (mục tiêu 3.390). Thiếu nhiều nhất: CIC là gì (52/200),
  App vay tiền nhanh (104/200), Nộp thuế đất qua ngân hàng (8/100), Lãi suất tiết kiệm (112/200).
- Nguyên nhân chính gây gượng ép: anchor quá chung ("vay", "lãi suất ngân hàng") và trang đích lệch chủ đề với bài nguồn.

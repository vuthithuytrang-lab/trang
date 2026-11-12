---
name: dich-bai-okamura
description: Dịch bài SEO Okamura từ tiếng Việt sang tiếng Anh ngay trong Google Doc — tạo tab "Bản dịch EN" dạng bảng 2 cột (trái bản Việt giữ nguyên, phải bản Anh), giữ ảnh, heading, gạch đầu dòng, in đậm/nghiêng, chuyển link okamura.com.vn/vi/... sang bản tiếng Anh và áp checklist bản dịch. Dùng khi Trang dán link Google Doc bài Okamura, hoặc nói "dịch bài", "dịch sang tiếng Anh", "BV số mấy", "làm bản EN", hoặc dán link file Sheet danh sách bài SEO Okamura kèm tên bài.
---

# Dịch bài Okamura Việt → Anh

Trang chỉ cần dán **link Google Doc** (hoặc tên bài BV trong Sheet). Mọi bước kỹ thuật tự làm.
Công cụ ở `cong-cu/dich-bai-okamura/`. Bài mẫu đạt chuẩn:
https://docs.google.com/document/d/1ho6aEZqDzEESNSN3ygDi-hSOE6P3RhJ6ZxDVzXSoIi8/edit?tab=t.uow5cvmkk2u3

## Nguồn dữ liệu
- Sheet: `1ednWlho_Iw1ANJdwf6wD6ed_JhZpwt68f-worBBc0So`, tab `2. Danh sách bài SEO | 2026`.
  Cột B = từ khóa, cột W = "Link docs" (là chip liên kết → đọc bằng `get_spreadsheet`
  với `includeGridData` + field `sheets.data.rowData.values.chipRuns`).
- Checklist bắt buộc: tab `Checklist bản dịch sang tiếng Anh` của Sheet trên — đọc lại mỗi lần.

## Quy trình (đặt W = thư mục scratchpad, T = nơi lưu kết quả read_doc)
1. `read_doc` bài gốc → kết quả bị lưu ra file; bóc lớp `content` thành `X_raw.json`.
2. `python3 cong-cu/dich-bai-okamura/dump_doc.py X_raw.json` → bản Việt có số đầu dòng.
3. Dịch → `cong-cu/dich-bai-okamura/ban-dich/<bv>_en.txt`, mỗi dòng `SỐ: nội dung`
   (giữ đúng SỐ của bản Việt). Ký hiệu: `**đậm**`, `_nghiêng_`, `[chữ](link)`, `[IMG kix.id]`.
   Luật dịch (theo checklist):
   - Bản Việt là gốc, **không sửa tab Việt**. Lỗi trong bản Việt thì dịch đúng nguyên văn và báo Trang.
   - Heading: chỉ viết hoa chữ đầu, tên riêng, và sau gạch ngang nếu bản Việt viết hoa. Không in đậm.
   - Mở bài + kết bài: in nghiêng toàn đoạn, từ khóa chính tiếng Anh `**_in đậm nghiêng_**`
     (kể cả khi bản Việt quên in đậm ở kết bài).
   - Chọn 1 từ khóa tiếng Anh cho cả bài và dùng nhất quán.
   - Chú thích ảnh: chỉ chữ (bỏ link Drive), công cụ tự in nghiêng + căn giữa + thêm dấu chấm.
   - Link okamura: cứ chép link gốc, công cụ tự đổi `/vi/...` → bản Anh. Link khác giữ nguyên.
   - "etc" → "..."; tên màu viết thường; mục "1 - Title" giữ nguyên kiểu "1 - ", không đổi thành "1.".
   - Số thập phân kiểu Anh (658,5 → 658.5). Dòng trống thừa: bỏ (không ghi dòng đó).
4. Tạo khung trên doc (2 lệnh update_doc):
   `addDocumentTab {"tabProperties":{"title":"Bản dịch EN"}}` → lấy tabId trong phản hồi; rồi
   `python3 build_requests.py table --tab TAB` (xoay ngang trang + bảng 1x2).
5. `python3 build_requests.py fill X_raw.json ban-dich/<bv>_en.txt --tab TAB --cells 5,7 --out W/<bv>.json --chunk 45`
   (tab mới tinh thì ô trái = 5, ô phải = 7; nếu không chắc, bỏ `--cells` và đưa file read_doc mới đọc).
6. Gửi lần lượt `W/<bv>_1.json`, `_2`, ... qua `update_doc`, **đúng thứ tự, chép y nguyên**.
   Gói lệnh dài → giao cho agent `worker` (sonnet) gửi, dặn dừng ngay khi lỗi. Nhiều bài thì chạy song song mỗi bài 1 agent.
   Lỗi giữa chừng: xoá tab (`deleteTab`) rồi làm lại từ bước 4.
7. Soát: `read_doc` lại → `python3 verify.py DOC.json ban-dich/<bv>_en.txt --tab TAB`
   phải ra "OK — khớp hoàn toàn". Xem thêm cột phải bằng `dump_doc.py`.
   (Xuất PDF thường bị Google từ chối vì file lớn — không cần thử.)
8. Commit + push file bản dịch, báo Trang: link từng doc (kèm `?tab=TAB`), điểm cần chú ý, hỏi 2 câu chốt.

## Không còn Claude?
Dùng bản chạy trong Google Sheet: `cong-cu/dich-bai-okamura/apps-script/` (file DichBaiTuDong.gs, xem HUONG-DAN-CAI.html).

## Đã biết
- Chèn ảnh bằng `contentUri` của ảnh trong bài gốc: chạy được, NHƯNG link chỉ sống ~15-20 phút.
  Phải `read_doc` bài gốc ngay trước bước 5 rồi gửi ngay. Nếu lỗi "Access to the provided image was forbidden":
  đọc lại bài gốc, chạy lại bước 5 (vị trí không đổi), gửi tiếp từ lô bị lỗi — các lô trước giữ nguyên.
- Ảnh tự thu về rộng tối đa 330pt cho vừa nửa trang ngang (giống bài mẫu 338pt).
- Không có cách gọi Google Docs trực tiếp từ dòng lệnh (không có tài khoản gcloud) → bắt buộc đi qua connector.

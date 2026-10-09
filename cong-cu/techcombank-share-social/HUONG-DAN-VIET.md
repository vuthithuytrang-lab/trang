# Hướng dẫn viết bài share social Techcombank (đọc kỹ)

Thư mục làm việc: SCR=<thư mục làm việc>
- `plan.json`: danh sách bài (slug, kw = keyword chính, url, platforms[{row,p}]).
- `art/<slug>.json`: bài gốc đã bóc tách: title, sapo, sections[{h2, content[]}] (dòng "### " là H3, "- " là gạch đầu dòng), images[{src, alt, after_h2}] (đánh số index 0,1,2...).
- Ví dụ mẫu đã đạt chuẩn: `drafts/bien-dong-ty-gia-voi-doanh-nghiep-sme.json` — ĐỌC NÓ TRƯỚC để thấy định dạng & giọng văn.

## Việc của bạn cho mỗi slug được giao
1. Đọc `art/<slug>.json` TOÀN BỘ.
2. Viết `drafts/<slug>.json` theo đúng schema mẫu, chỉ gồm các nền tảng có trong plan.json của slug đó (Webflow / Wix / Mastodon / Pinterest).
3. Chạy `python3 -I $SCR/tools/build.py $SCR <slug>` — sửa draft tới khi in ra `OK`. Không được sửa tools/build.py.
4. Upload từng file `out/<slug>__<Platform>.html` lên Google Drive bằng tool `mcp__Google_Drive__create_file` (tải schema bằng ToolSearch "select:mcp__Google_Drive__create_file,mcp__Google_Drive__read_file_content"):
   - title: lấy đúng từ `out/<slug>__meta.json` (dạng "Webflow - <keyword> - 09/10")
   - parentId: <id thư mục Drive của đợt>
   - contentMimeType: text/html
   - textContent: NGUYÊN VĂN nội dung file html (dùng cat để xem; chép chính xác, không sửa).
   Kiểm tra nhanh mỗi file sau khi tạo bằng `mcp__Google_Drive__read_file_content` (fileId vừa tạo): phải thấy tiêu đề, đủ H2, link trần, hashtag.
   Nếu lỡ tạo trùng/tạo lỗi, KHÔNG xóa file — ghi chú lại trong kết quả.
5. Ghi `results/<slug>.json`: {"<Platform>": {"row": <row>, "id": "<fileId>"}, ...}
6. KHÔNG đụng vào Google Sheet. KHÔNG chia sẻ file. KHÔNG sửa file của slug khác.

## Quy tắc nội dung (bắt buộc)
- Tiếng Việt, thân thiện, chuyên nghiệp, xưng "bạn". Viết lại hoàn toàn bằng câu chữ mới, không chép câu từ bài gốc (build.py báo lỗi nếu có cụm ≥12 từ trùng). Tránh "tốt nhất", "chắc chắn", "hàng đầu", "số 1", "tuyệt đối".
- KHÔNG bịa số liệu, lãi suất, phí, điều kiện, quy định, tên sản phẩm. Mọi con số phải có trong bài gốc (build.py kiểm tra số). Chỉ dùng thông tin có trong art/<slug>.json.
- `kw_phu`: 2 keyword phụ sát nghĩa keyword chính, rút từ H2/nội dung bài gốc (ngắn, 2–6 từ, dạng người ta hay tìm kiếm).
- Title mọi nền tảng phải chứa nguyên cụm keyword chính (không phân biệt hoa thường) và KHÁC title bài gốc. Keyword chính viết thường trong sheet, trong title có thể viết hoa chữ đầu/viết hoa từ viết tắt (SME, VAT, TNDN, USD).
- Bài dài (Webflow, Wix):
  - title 50–65 ký tự; meta 140–160 ký tự (nên chứa keyword chính).
  - sapo 2–3 câu, có keyword chính.
  - sections: ĐỦ tất cả H2 của bài gốc, chép NGUYÊN VĂN chuỗi h2 từ art (kể cả số thứ tự, kể cả lỗi đánh số) và đúng thứ tự. Mỗi H2: 1–3 đoạn ngắn hoặc 1 câu dẫn + gạch đầu dòng (chuỗi bắt đầu "- "). Tóm ý chính của H2 đó (gồm cả các H3 bên dưới).
  - Tổng (sapo + nội dung + kết luận + CTA) khoảng 600–1.000 chữ (bài ít H2 được phép ngắn hơn, build.py báo ngưỡng).
  - image: {"index": i, "after_section": k (0-based, đặt sau H2 phù hợp nhất — thường là H2 có after_h2 của ảnh), "caption": chú thích mô tả ĐÚNG nội dung ảnh + có keyword chính hoặc 1 keyword phụ, tự nhiên, không chép nguyên alt}.
  - conclusion: 2–3 câu. cta: mời tìm hiểu/sử dụng sản phẩm, dịch vụ Techcombank liên quan ĐÚNG như bài gốc nhắc tới (không bịa sản phẩm).
  - Bản Webflow và Wix phải viết KHÁC câu chữ nhau (build.py báo lỗi nếu trùng nhiều), title/meta/sapo khác nhau.
- Mastodon: open (câu mở, CHỨA keyword chính), points (ý chính rút gọn của TẤT CẢ các H2, gộp 1–3 câu hoặc gạch đầu dòng "• ", nối bằng \n), close_cta (câu kết + CTA ngắn), image_index, caption. Tổng bài (open+points+close_cta+link+4 dòng hashtag, nối \n) PHẢI < 500 ký tự — link và hashtag dài nên phần chữ thường chỉ còn ~250–330 ký tự.
- Pinterest: title ≤100 ký tự (chứa keyword chính), desc = tóm ý các H2 + CTA (link và hashtag do build.py tự thêm; tổng mô tả ≤500), image_index, caption.
- Ảnh: mỗi nền tảng của cùng 1 bài nên dùng ẢNH KHÁC NHAU nếu bài có đủ ảnh. Ưu tiên ảnh có alt rõ nghĩa. Nếu alt trống/vô nghĩa (vd tên file) mà vẫn cần dùng ảnh đó, hãy tải ảnh về `$SCR/imgs/` bằng curl rồi dùng tool Read để xem ảnh, rồi mới viết chú thích. Chú thích phải mô tả đúng ảnh.
- Hashtag do build.py tự sinh từ kw và kw_phu — không tự viết.

## Báo cáo cuối (trả về cho người giao việc)
Với mỗi slug: build OK chưa, fileId từng nền tảng, và mọi điều bất thường (bài thiếu ảnh, thiếu thông tin, H2 lạ như FAQ, lỗi upload...). Ngắn gọn.

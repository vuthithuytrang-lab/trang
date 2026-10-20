---
name: seo-audit
description: Đánh giá toàn diện một dự án SEO từ file check top của rank tracker. Phân cụm từ khoá theo SERP, crawl toàn bộ đối thủ, đối chiếu Search Console để bắt ăn thịt từ khoá thật, kiểm trạng thái lập chỉ mục, đo ngưỡng lọt top, tính khả thi mục tiêu và xuất bộ báo cáo HTML gồm một file tổng hợp và một file cho từng cụm. Dùng khi người dùng đưa file check top của cả danh mục từ khoá và hỏi vì sao chưa lên top, có đạt mục tiêu top 10 / top 5 / top 3 không, cần làm gì để đạt, muốn audit SEO toàn dự án, đánh giá hiện trạng bộ từ khoá, hoặc gõ /seo-audit.
---

# SEO Audit — đánh giá dự án theo bộ từ khoá lớn

Làm ở cấp toàn danh mục từ khoá và trả lời ba câu, đúng thứ tự: hiện trạng dự án trên chính bộ
từ khoá đang theo dõi là gì; có đạt mục tiêu không, nếu không thì trần ở đâu; nhóm nào phải làm,
làm gì, theo thứ tự nào.

## Khi nào dùng

Người dùng có file check top (CSV rank tracker, top 10 hoặc top 100) cho cả bộ từ khoá của dự án
và muốn biết hiện trạng, khả năng đạt mục tiêu, việc cần làm theo từng cụm.

| Đầu vào | Bắt buộc | Ghi chú |
|---|---|---|
| File check top | Có | CSV rank tracker. Chấp nhận cả top 10 và top 100, ghi rõ độ sâu trong báo cáo |
| Domain của mình | Có | File chứa toàn bộ SERP nên không suy ra được. Phải hỏi người dùng |
| Mục tiêu | Nên có | Ví dụ 85% top 10 · 70% top 5 · 50% top 3 |
| Tiền tố tên file | Nên có | Mặc định suy từ domain: `abc-design.vn` thành `abc` |
| Quyền Search Console | Không | Có thì chạy bước 4-6, không có thì bỏ qua và ghi rõ trong báo cáo |

Không dùng khi:

| Tình huống | Chuyển sang |
|---|---|
| Một cụm, một trang đích cụ thể | `/seo-gap` |
| Trang đang tụt hạng, cần biết vì sao | `/seo-doctor` |
| Báo cáo traffic định kỳ | `/seo-analyst` |
| Traffic tốt nhưng không ra đơn | `/cro-analyst` |

## Chuẩn bị

Chạy mọi lệnh trong thư mục chứa skill này. Python 3.9 trở lên.

```bash
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt
source .venv/bin/activate
```

Dữ liệu từng dự án để ngoài thư mục skill. Đặt một biến cho thư mục dữ liệu rồi dùng trong mọi lệnh:

```bash
D=~/seo-audit/<dự án>/data
```

Trong các file `references/` và thông báo của script, `data/` nghĩa là thư mục `$D` này.

Biến môi trường (chỉ cần cho bước Search Console):

| Biến | Dùng cho | Mặc định |
|---|---|---|
| `GSC_CREDENTIALS_DIR` | Thư mục chứa credential Google dạng `*.json` (authorized_user hoặc service_account); script tự dò file có quyền với property | `credentials/` trong thư mục skill |
| `GSC_CREDENTIALS_FILE` | Một file credential cố định, dùng thay cho thư mục | không đặt |
| `FA_CSS_PATH` | Đường dẫn file `all.min.css` của Font Awesome cài sẵn trên máy | không đặt thì dùng Font Awesome 6 bản miễn phí qua CDN |

Credential: cách khuyến nghị là xác thực bằng `/seo-analyst` rồi trỏ `GSC_CREDENTIALS_DIR` tới
thư mục credential của skill đó; hoặc truyền thẳng `--cred <file>` cho `gsc.py`, `index_status.py`.
File credential không nằm trong gói.

Tùy chọn: chép `assets/config.example.json` thành `config.json` trong thư mục dự án để ghi lại
tham số (domain, tiền tố, mục tiêu, độ sâu, property). Các script nhận tham số qua dòng lệnh.

## Các bước thực hiện

1. **Đọc file check top.**
   ```bash
   python3 scripts/parse_ranktracker.py --csv <file.csv> --domain <domain> --out $D
   ```
   Xuất `kw.json` (vị trí mốc đầu, mốc cuối, biến động, mọi URL của mình trong SERP, toàn bộ SERP
   đối thủ) và `meta.json` (độ sâu tự nhận). Dừng và báo lại nếu không có domain của mình trong
   file, hoặc dưới 20 từ khoá.

2. **Phân cụm theo SERP** (thuật toán và tham số ở `references/clustering.md`).
   ```bash
   python3 scripts/cluster_serp.py --data $D --min-shared 4 --depth 10
   ```
   Hai từ khoá chung cụm khi SERP chia sẻ tối thiểu N URL. Không bỏ sót từ khoá nào: cụm nhỏ đứng
   riêng, kể cả cụm một từ khoá (script có assert kiểm tổng). Bắt buộc sau bước này: đọc danh sách
   cụm và đặt lại tên tiếng Việt có nghĩa cho từng cụm, ghi vào trường `name` trong
   `$D/clusters.json`. Tên tự sinh chỉ là gợi ý.

3. **Crawl toàn bộ SERP** (chỉ số ở `references/metrics.md`).
   ```bash
   python3 scripts/crawl.py --data $D --depth 10
   ```
   Crawl mọi URL trong SERP ở độ sâu đã nhập (10 hoặc 100) cộng mọi URL của mình, loại mạng xã hội
   và video. Đo 21 chỉ số nội dung và toàn bộ heading. Cổng chặn: trang dưới 300 từ mà HTML trên
   80KB là render JavaScript — loại khỏi mọi bảng so sánh, đếm và ghi rõ số lượng.

4. **Search Console** (nếu có quyền).
   ```bash
   python3 scripts/gsc.py --site <property> --days 90 --data $D
   ```
   Lấy `query × page` 90 ngày để đếm ăn thịt từ khoá thật (truy vấn có từ 2 URL nội bộ cùng nhận
   hiển thị), tìm URL tranh chấp mà file check top không thấy, đo hiển thị, click, tỷ lệ nhấp.

5. **Cổng chặn tình trạng URL và lập chỉ mục** (`references/verify.md` mục 2 và 3).
   ```bash
   python3 scripts/verify_urls.py --data $D
   python3 scripts/index_status.py --data $D --site <property>
   python3 scripts/gsc_analyze.py --data $D
   ```
   `verify_urls.py` phân loại mọi URL nội bộ: 200 · 404/410 · 5xx · 301/302 kèm chuỗi chuyển hướng ·
   noindex · canonical trỏ nơi khác · dưới 300 từ. Không đề xuất sửa nội dung cho URL 404, 5xx hay
   noindex; không tính URL đã 301 là ăn thịt từ khoá. `index_status.py` dùng URL Inspection API
   (quota 2.000 URL mỗi ngày mỗi property) để biết URL chưa được lập chỉ mục và vướng khâu nào,
   `googleCanonical` khác `userCanonical` (bằng chứng Google gộp trang), `lastCrawlTime`. Không dùng
   cú pháp `site:` trên Google.

6. **Crawl bổ sung trang đã tồn tại.** Crawl các URL nội bộ mà Search Console lộ ra nhưng bước 3
   chưa có — bắt buộc trước khi đề xuất tạo trang mới bất kỳ:
   ```bash
   python3 scripts/crawl.py --data $D --add $D/extra_urls.json
   ```

7. **Chỉ số kỹ thuật.**
   ```bash
   python3 scripts/perkw.py --data $D    # so trang mình với đối thủ ở từng từ khoá
   python3 scripts/tech.py --data $D     # chín chỉ số kỹ thuật cấp trang
   ```
   Chín chỉ số: TTFB, ảnh thiếu alt, số H1, độ dài title và description, heading nhảy cấp, script
   ngoài, CSS ngoài, thẻ og.

8. **Đo khoảng cách.**
   ```bash
   python3 scripts/analyze.py --data $D --goals "top10=85,top5=70,top3=50"
   ```
   Bốn phép đo (`references/metrics.md` mục 3-4): ngưỡng top N là trung vị toàn bộ trang đang ở vị
   trí 1 đến N của chính cụm đó (hiện cả ba mốc); so từng cặp trang mình với trang số 1 của mỗi từ
   khoá; so theo tầng 1–3 / 4–5 / 6–7 / 8–10 — không phân biệt được thì nói thẳng on-page không phải
   yếu tố quyết định; bốn phép đo cấu trúc (blog so với trang dịch vụ, độ phân tán URL, ăn thịt từ
   khoá, schema thực thể).

9. **Tính khả thi từ mục tiêu** (`references/metrics.md` mục 5). Mục tiêu đặt trước; với mỗi mốc,
   tính ngược tỷ lệ chuyển đổi cần thiết theo từng tầng vị trí rồi đối chiếu ba mức tham chiếu.
   Kết luận trả lời thẳng: đạt được hay không, thiếu bao nhiêu từ khoá, trần nằm ở đâu.

10. **Cổng chặn đủ dữ liệu** (`references/output.md`).
    ```bash
    python3 scripts/precheck.py --data $D --fix --site <property>
    ```
    Chỗ thiếu "quét bù được" (URL đối thủ chưa crawl, `tech.py` chưa chạy, `gsc_analysis.json` theo
    bộ cụm cũ) thì script tự chạy lệnh quét bù; không được ẩn mục hay ghi chú cho qua. Chỗ thiếu
    "không có thật" (domain mình không nằm trong SERP của cụm) thì mục vẫn hiện kèm dòng giải thích.

11. **Xuất báo cáo.**
    ```bash
    python3 scripts/build_report.py --data $D --prefix <tiền tố> --goals "top10=85,top5=70,top3=50"
    ```
    `build_report.py` tự gọi precheck và dừng nếu còn chỗ quét bù được. Chỉ dùng `--force` khi biết
    rõ vì sao không quét được, và phải ghi lý do vào báo cáo.

12. **Ghi đè phần phán đoán (tùy chọn).** Với cụm quan trọng, chép `assets/content.example.py`
    thành `~/seo-audit/<dự án>/content.py`, viết nhận định mạnh · yếu · chỗ chen vào cho từng đối
    thủ, tinh chỉnh meta, outline, FAQ. Khoá là tên cụm, khớp trường `name` trong `$D/clusters.json`
    (không phân biệt hoa thường; sai tên thì script cảnh báo và bỏ qua). Bắt buộc kiểm bịa số trước
    khi dựng lại:
    ```bash
    python3 scripts/verify_claims.py --data $D --content ~/seo-audit/<dự án>/content.py
    python3 scripts/build_report.py --data $D --prefix <tiền tố> --content ~/seo-audit/<dự án>/content.py
    ```
    Outline viết tay phải giữ đủ bốn thành phần: mật độ hiện tại → mục tiêu từ ma trận mật độ, độ
    dài mục tiêu, số của đối thủ, lý do có số (`references/output.md`).

## Đầu ra mong muốn

Xuất vào thư mục riêng của dự án `~/html/<dự án>/` (tên lấy từ `--project`, thiếu thì từ
`--prefix`, thiếu nữa thì suy từ domain: `khachhang-a.vn` thành `khachhang`). Chỉ định thư mục
khác bằng `--out`.

| File | Mục | Nguồn |
|---|---|---|
| `<tiền tố>-tong-hop.html` | 1 → 7 | Phán quyết mục tiêu · đối thủ toàn bộ bộ từ khoá · ma trận nguyên nhân · ưu tiên nhóm · khoảng cách on-page · danh sách việc · khoảng cách từng nhóm |
| `<tiền tố>-<slug cụm>.html` | 1 · 2 · 3 · 4 · 5 · 6 · 7 · 8 · 15 · 16 · 17 | Đo trực tiếp: từ khoá, đối thủ, trang của mình, mạnh, yếu ba lớp, mật độ theo cụm từ và từng từ khoá, việc cần làm, ngưỡng top, Search Console, nội dung đối thủ, kỹ thuật |
| `<tiền tố>-<slug cụm>.html` | 9 · 10 · 11 · 12 · 13 · 14 | Suy ra từ dữ liệu: lớp meta, outline, FAQ, ảnh, structured data, checklist |

Cả hai loại file sinh tự động 100% từ dữ liệu đã đo, không mục nào bỏ trống và không mục nào phụ
thuộc `content.py`. Khoá `__tong_hop__` trong `content.py` nối thêm vào cuối file tổng hợp, không
thay bảy mục tự sinh. Mặc định mọi cụm đều có file riêng, kể cả cụm một từ khoá (`--min-file` để gọn).

## Lưu ý

- **Không bịa thông tin — quy tắc đứng trên mọi quy tắc khác** (`references/no-fabrication.md`).
  Mọi con số, nhận định, đề xuất phải truy được về file check top, Search Console hoặc HTML đã
  crawl, và ba nguồn đó phải đã được chứng thực: HTML đã loại trang render JavaScript, URL nội bộ
  đã qua `verify_urls.py`, Search Console ghi rõ kỳ đo. Cấm ước lượng số, cấm bịa tên đối thủ, cấm
  mô tả nội dung trang chưa crawl, cấm suy diễn nhân quả chưa kiểm chứng, cấm văn bản mẫu và số điền
  tạm. Chưa đo được thì nói thẳng là chưa đo.
- **File check top là dữ liệu thật** cho mọi con số vị trí. Search Console chỉ bổ trợ: bắt ăn thịt
  từ khoá, thấy trang ngoài top, đo hiển thị và tỷ lệ nhấp. Không dùng vị trí trung bình của GSC để
  phủ nhận thứ hạng đo được.
- **Mục tiêu đặt lên đầu.** Mọi phép tính khả thi bắt đầu từ mục tiêu người dùng đưa, tính ngược
  ra tỷ lệ chuyển đổi cần thiết rồi mới đánh giá có thực tế không.
- **Không tự thay đổi bộ từ khoá.** Mẫu số giữ nguyên. Nội dung ngành mới là để bồi thẩm quyền,
  không tính vào bộ đo.
- **Xét tất cả đối thủ trong SERP**, không lọc chỉ top 3.
- **Kiểm chứng trước khi kết luận** theo năm cổng chặn ở `references/verify.md`. Trước khi giao báo
  cáo có viết tay, chạy `scripts/verify_claims.py`.
- **File giao ra phải đủ mục.** Mục trống vì lười quét và mục trống vì mình chưa xếp hạng trông
  giống nhau nhưng ý nghĩa ngược nhau — `scripts/precheck.py` phân biệt hai loại.
- Search Console có độ trễ 2-3 ngày (`gsc.py` mặc định lấy đến 3 ngày trước). URL Inspection giới
  hạn 2.000 URL mỗi ngày và 600 mỗi phút cho mỗi property; `index_status.py` mặc định 300 URL mỗi lần.
- Không emoji. Không dùng dòng nhãn nhỏ viết hoa phía trên tiêu đề.
- Font Awesome qua CDN bản miễn phí thiếu vài icon Pro (vd `fa-bullseye-arrow`, `fa-list-tree`) —
  chỉ mất icon, nội dung không đổi. Có bản Pro cài sẵn thì đặt `FA_CSS_PATH`.

## Tài nguyên đi kèm

- `references/no-fabrication.md` — quy tắc không bịa: nguồn được phép, điều cấm, điều bắt buộc,
  cách kiểm trước khi giao. Đọc trước khi viết bất kỳ nhận định nào.
- `references/clustering.md` — thuật toán phân cụm theo SERP, tham số, cách đặt tên cụm. Đọc ở bước 2.
- `references/metrics.md` — chỉ số nội dung, kỹ thuật, ngưỡng lọt top, bốn phép đo cấu trúc, công
  thức khả thi. Đọc ở bước 3, 8, 9.
- `references/verify.md` — năm cổng chặn: render JS, tình trạng URL, lập chỉ mục, trang đã tồn tại,
  vị trí trung bình. Đọc ở bước 3, 5, 6.
- `references/output.md` — đặt tên file, thư mục xuất, cấu trúc file tổng hợp và file cụm, quy tắc
  thiếu dữ liệu, outline chi tiết. Đọc ở bước 10-12.
- `scripts/parse_ranktracker.py` — đọc CSV check top, xuất `kw.json`, `meta.json`.
- `scripts/cluster_serp.py` — phân cụm theo SERP.
- `scripts/crawl.py` — crawl và đo trang trong SERP, thêm URL bằng `--add`.
- `scripts/gsc.py` — lấy query × page từ Search Console.
- `scripts/verify_urls.py` — kiểm status, chuyển hướng, noindex, canonical của URL nội bộ.
- `scripts/index_status.py` — URL Inspection API, trạng thái lập chỉ mục.
- `scripts/gsc_analyze.py` — tổng hợp Search Console theo cụm, liệt kê URL cần crawl bổ sung.
- `scripts/perkw.py` — so trang mình với đối thủ ở từng từ khoá.
- `scripts/tech.py` — chín chỉ số kỹ thuật cấp trang.
- `scripts/analyze.py` — ngưỡng top N, so cặp, so tầng, khả thi theo mục tiêu.
- `scripts/precheck.py` — cổng chặn đủ dữ liệu, tự quét bù với `--fix`.
- `scripts/build_report.py` — dựng file tổng hợp và file từng cụm.
- `scripts/verify_claims.py` — đối chiếu nội dung viết tay trong `content.py` với dữ liệu đã đo.
- `scripts/blocks.py`, `scripts/autocontent.py`, `scripts/overview.py` — các khối báo cáo sinh tự động.
- `scripts/lib.py` — hàm dùng chung: chuẩn hoá URL, crawl, đo trang, thư mục dự án.
- `scripts/auth.py` — nạp credential Google từ `GSC_CREDENTIALS_FILE` / `GSC_CREDENTIALS_DIR`.
- `scripts/requirements.txt` — thư viện Python cần cài.
- `assets/report.css` — CSS của báo cáo.
- `assets/content.example.py` — mẫu file ghi đè phần định tính.
- `assets/config.example.json` — mẫu ghi tham số dự án.

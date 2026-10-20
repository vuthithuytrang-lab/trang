# Cấu trúc báo cáo và đặt tên file

## Đặt tên

`<tiền tố>-tong-hop.html` và `<tiền tố>-<slug cụm>.html`

Tiền tố suy từ domain: lấy phần trước dấu chấm hoặc gạch đầu tiên, tối đa 6 ký tự.
`abc-design.vn` → `abc`. Cho phép user chỉ định khác trong config, ví dụ mẫu dùng `demo`.

Slug cụm: bỏ dấu, thay khoảng trắng bằng gạch nối, tối đa 4 từ.

## Thư mục xuất — mỗi dự án một thư mục riêng

Mặc định `~/html/<dự án>/`, ví dụ `~/html/khachhang/khachhang-tong-hop.html`. Không đổ file
thẳng vào `~/html`.

Tên dự án lấy theo thứ tự: khóa `project` trong config → khóa `prefix` → suy từ domain
(phần trước dấu chấm hoặc gạch đầu tiên, `khachhang-a.vn` → `khachhang`).

`out_dir` trong config hoặc `--out` trỏ tới chỗ khác `~/html` thì tôn trọng nguyên,
không nối thêm tên dự án. Để trống hoặc đúng bằng `~/html` thì tự nối.

## File tổng hợp

**Bảy mục, sinh tự động toàn bộ** từ `overview.py` và `build_report.py`. Không mục nào phụ thuộc
`content.py` — chạy dự án mới, không viết một dòng nào, vẫn ra đủ bảy mục.

| Mục | Trả lời câu hỏi | Nguồn |
|---|---|---|
| 1 · Phán quyết mục tiêu | Đạt được không, thiếu bao nhiêu từ khoá, trần ở đâu | check top + `references/metrics.md` mục 5 |
| 2 · Đối thủ trên toàn bộ bộ từ khoá | Ai đang giữ chỗ, mình phải giành của ai | check top |
| 3 · Vấn đề đang khiến chưa đạt mục tiêu | Vì sao chưa lên: chưa có trang, ăn thịt, chưa index, mỏng… | check top + GSC + url_status + index_status + HTML |
| 4 · Nhóm nào dễ lên, làm nhóm nào trước | Thứ tự thi công, làm tới nhóm nào là đủ mục tiêu | check top |
| 5 · Khoảng cách on-page toàn dự án | Mình thua đối thủ ở chỉ số nào, bao nhiêu | HTML đã crawl |
| 6 · Danh sách việc cấp dự án | Bao nhiêu nhóm phải tạo mới, khôi phục, tối ưu, giữ | check top + GSC |
| 7 · Khoảng cách tới mục tiêu theo từng nhóm | Từng nhóm cần thêm bao nhiêu, kho ở đâu, URL chốt nào | check top + GSC |

Mục 3 gán cho **mỗi từ khoá chưa đạt mốc đúng một nhãn**, xét theo thứ tự ưu tiên dừng ở nhánh
đầu tiên khớp: KHÔI PHỤC → CHƯA INDEX → GOOGLE ĐÃ GỘP → ĂN THỊT → CHƯA CÓ TRANG → CHƯA LỌT TOP
→ LỆCH Ý ĐỊNH → NỘI DUNG MỎNG → NGOÀI ON-PAGE → CHƯA ĐỦ DỮ LIỆU. Thứ tự này là kỷ luật, không
phải cách trình bày: trang đã chết thì không xét tiếp mật độ, chưa index thì không đề xuất
viết thêm nội dung. Tổng các dòng phải bằng đúng số từ khoá chưa đạt mốc.

`C['__tong_hop__']` trong `content.py` vẫn được nối vào cuối file nếu có, dùng để **bổ sung**
phần phán đoán của người. Nó không còn là điều kiện để file có nội dung.

## Không bỏ sót cụm nào

Mọi từ khoá phải nằm trong một cụm và **mọi cụm phải có mặt trong bảng khoảng cách**,
kể cả cụm chỉ có một từ khoá. Mặc định mỗi cụm cũng có một file riêng
(`build_report.py --min-file 1`). Chỉ nâng ngưỡng khi khách hàng muốn bộ tài liệu gọn hơn,
và khi đó phải nói rõ trong báo cáo là các cụm nhỏ chỉ nằm trong bảng.

`cluster_serp.py` có assert kiểm tổng số từ khoá sau phân cụm bằng tổng đầu vào — sai thì dừng.

## File từng cụm — cụm cần làm

Mở đầu bằng hai khối không đánh số: **Khoảng cách của nhóm tới mục tiêu** (mỗi mốc một dòng
"cần thêm bao nhiêu", kèm danh sách từ khoá ứng viên xếp theo tầng vị trí — gần mốc thì rẻ)
và **URL chốt của cụm** kèm xử lý URL trùng lặp. Sau đó là 17 mục:

1. Danh sách **đầy đủ** từ khoá của cụm, không lược bớt: vị trí hai mốc, biến động,
   số URL nội bộ cùng ra, URL đang xếp hạng, top 3 đối thủ, mật độ cụm khoá của mình so với top 1
2. Mổ xẻ đối thủ đang chiếm top 3: bảng chỉ số + mạnh, yếu, chỗ chen vào
3. Các trang của mình đang phục vụ cụm
4. Điểm mạnh đang có
5. Điểm yếu xếp theo mức tác động, **gộp cả ba lớp** nội dung · on-page · kỹ thuật vào một bảng,
   mỗi dòng kèm mức của nhóm top để so
6. Ma trận mật độ cụm từ và chỉ số trang, cộng **bảng mật độ theo từng từ khoá**: mỗi dòng so
   trang mình với các trang đang đứng top 3 của **chính từ khoá đó**, dòng cuối là **ngưỡng bao
   trùm cả cụm**
7. Tóm tắt việc cần làm
8. Ngưỡng top 3, top 5, top 10 và đối chiếu mục nội dung với các trang top
9. Lớp meta: title, H1, description, URL
10. Outline gắn nhãn GIỮ / SỬA / MỚI / GAP SERP / BRAND
11. Bộ FAQ 8 câu, mỗi câu ghi rõ nhắm từ khoá nào
12. Ảnh và tối ưu tải, kèm quy ước đặt tên file và alt
13. Structured data
14. Checklist triển khai theo đợt
15. Đối chiếu Search Console: ăn thịt từ khoá và hiệu quả thật
16. Đối chiếu nội dung với đối thủ top 3, liệt kê mục nội dung thật của họ
17. Rà soát kỹ thuật cấp trang

## File từng cụm — cụm đã đạt mục tiêu

Chỉ mục 1 đến 7 cộng mục 15. Không viết outline và checklist cho cụm chỉ cần giữ vững.

## Không giao bản thiếu mục

**Mọi file cụm phải có đủ 14 mục.** Tất cả đều được sinh tự động từ dữ liệu đã đo, kể cả sáu
mục từng phải viết tay — meta, outline, FAQ, ảnh, structured data, checklist. Bản tự động là
**mức sàn**, luôn có mặt, mọi con số đều truy được về `pages.json`, `kw.json`, `tech.json`
hoặc Search Console.

`content.py` không còn bắt buộc. Nó dùng để **ghi đè** phần cần phán đoán của người:
nhận định mạnh — yếu — chỗ chen vào cho từng đối thủ, và tinh chỉnh outline hay FAQ ở các cụm
quan trọng nhất. Ghi đè theo từng khoá: viết `outline` thì chỉ outline bị thay, năm mục còn lại
vẫn dùng bản tự động.

Lý do thiết kế: một dự án có thể có hàng chục cụm. Bắt viết tay sáu mục cho từng cụm là bất khả
thi, và thực tế dẫn tới báo cáo bị cắt mất mục — đó là lỗi nặng hơn nhiều so với việc dùng bản
tự động có số đo thật.

## Thiếu dữ liệu thì quét thêm, không được ẩn mục

Trước khi dựng báo cáo, chạy cổng chặn:

```bash
python3 scripts/precheck.py --data data          # liệt kê chỗ thiếu
python3 scripts/precheck.py --data data --fix    # tự chạy lệnh quét bù
```

`build_report.py` tự gọi bước này và **dừng lại** nếu còn chỗ quét bù được. Đây là chặn cứng,
không phải cảnh báo.

Chỗ thiếu chia làm hai loại, và chỉ một loại được phép hiện dòng "không đủ dữ liệu":

| Loại | Nghĩa là gì | Xử lý |
|---|---|---|
| **Quét bù được** | Dữ liệu có ngoài kia, chỉ là chưa lấy về: URL đối thủ trong SERP chưa crawl, `tech.py` chưa chạy, `gsc_analysis.json` còn theo bộ cụm cũ | **Đi quét.** Cấm ẩn mục, cấm ghi chú cho qua, cấm `--force` |
| **Không có thật** | Đã quét hết mà vẫn không có, vì thực tế là không có: domain của mình không nằm trong SERP đã đo của cụm đó | Mục vẫn hiện, kèm một dòng nói rõ vì sao trống |

Đây là ranh giới quan trọng nhất của phần xuất báo cáo. Một mục trống vì lười quét và một mục
trống vì mình chưa xếp hạng trông giống hệt nhau trên báo cáo, nhưng ý nghĩa ngược nhau hoàn toàn.

`--force` chỉ dùng khi biết rõ vì sao không quét được — nguồn chặn crawl, hết quota API — và
phải ghi lý do đó vào báo cáo. Quét bù hai lần vẫn không lấy được thì cổng chặn tự nhả,
nhưng vẫn in ra để ghi vào báo cáo.

**Khoá nối giữa các bước là `cid`, không phải tên cụm.** `cid` suy từ slug nên duy nhất và không
đổi khi agent đặt lại tên cụm ở bước 2. Trước đây nối bằng tên cụm nên chỉ cần phân cụm lại hoặc
đổi tên là toàn bộ mục 15 trống ở mọi cụm mà không có gì báo. `gsc_analyze.py` ghi kèm chữ ký bộ
cụm để `precheck.py` bắt được trường hợp dữ liệu lỗi thời.

## Ngưỡng bao trùm — để phủ 100% từ khoá của cụm

Ngưỡng ở mục 8 là trung vị nhóm top: trả lời "một trang top trung bình trông thế nào". Nó
**không** trả lời được câu "một URL muốn lên top cho cả cụm thì cần bao nhiêu" — vì trang phải
đủ sức cho cả từ khoá khó nhất, không phải từ khoá trung bình.

Ngưỡng bao trùm ở cuối mục 6 tính hai bước, cố ý bất đối xứng:

| Bước | Phép tính | Vì sao |
|---|---|---|
| Trong một từ khoá | **Trung vị** các trang đang top 3 của chính từ khoá đó | Một trang lệch không kéo lệch cả bảng |
| Giữa các từ khoá | **Max** | Trang phải phủ được từ khoá khó nhất của cụm |

Bắt buộc in kèm: **từ khoá nào đang đẩy ngưỡng lên**, để người đọc nhìn ra ngoại lệ và tự quyết
có theo hay không; và **mức cao nhất đo được** của một trang thật, vì đó là trần đã có người làm được.

Từ khoá mà **cả nhóm top đều không nhắc nguyên văn lần nào** bị loại khỏi phép tính ngưỡng và
ghi rõ số lượng đã loại — Google không đòi khớp nguyên văn cho truy vấn đó, ép mật độ là làm hỏng câu văn.

## Outline phải chi tiết, không viết chung chung

Mục outline là phần người viết bài dùng trực tiếp. Một dòng kiểu "Bổ sung khối báo giá tóm tắt"
là vô dụng. Mỗi mục H2 bắt buộc có đủ bốn thứ:

| Thành phần | Ví dụ đạt |
|---|---|
| Nhãn và tiêu đề H2 đề xuất | `SỬA` — H2 2. Gói thi công nội thất showroom trọn gói |
| **Cụm từ và mật độ: hiện tại → mục tiêu** | Nâng "thi công nội thất showroom" từ **7 lên 20–25 lần**, bám mức doithu-a.vn (26 lần) |
| Độ dài mục tiêu và số ảnh | 500–700 từ, 6–8 ảnh dự án |
| Lý do có số của đối thủ | 12/14 trang top 10 có mục giá; doithu-b.vn đặt giá lên title và top 3 ở 14 từ khoá với 2.403 từ |

Mục nào có H3 thì liệt kê từng H3, mỗi H3 ghi rõ nhắm từ khoá nào và từ khoá đó đang ở vị trí nào.

Số mật độ hiện tại lấy từ **mục 6 — ma trận mật độ cụm từ**, sinh tự động. Không tự ước lượng.

## Quy ước trình bày

- **Không bịa.** Mọi số phải truy được về file check top, Search Console hoặc HTML đã crawl.
  Xem `references/no-fabrication.md`. Trước khi giao chạy `scripts/verify_claims.py`
- Mỗi vấn đề phải kèm số của đối thủ để so. "Ảnh chưa tối ưu" là câu vô giá trị
- Ghi ngày crawl và độ sâu SERP đã dùng
- Trang đối thủ chặn crawl thì ghi rõ, không bỏ qua im lặng
- Không suy diễn chỉ số không đo được
- Không emoji, không dòng nhãn nhỏ viết hoa phía trên tiêu đề
- Font Awesome 6 Pro local, đường dẫn tương đối từ thư mục xuất

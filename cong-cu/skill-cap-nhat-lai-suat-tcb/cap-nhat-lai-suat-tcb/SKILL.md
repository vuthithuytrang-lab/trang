---
name: cap-nhat-lai-suat-tcb
description: Cập nhật bảng lãi suất tiết kiệm trong bài blog Techcombank (techcombank.com/thong-tin/blog/...) theo số liệu mới từ các trang nguồn (mặc định VnExpress cho kỳ hạn 1–12 tháng, Topi cho 18–36 tháng), rồi tạo file Google Docs chép trọn bài, tô vàng mọi chỗ thay đổi, tô lại màu cao nhất/thấp nhất, kèm báo cáo. Dùng skill này khi người dùng đưa link bài Techcombank (một hay nhiều bài) và muốn "cập nhật lãi suất", "update bảng lãi suất", "làm file docs lãi suất mới", kể cả khi họ chỉ dán link mà không nói tên skill.
---

# Cập nhật lãi suất bài blog Techcombank → Google Docs

Đầu vào: link bài Techcombank cần cập nhật + link nguồn số liệu. Đầu ra: mỗi bài một file Google Docs mới
`<Tên file> – dd/mm/yyyy` chứa **toàn bộ bài**, đã sửa ngày/tháng/lãi suất, **mọi chỗ đổi tô nền vàng**, kèm báo cáo.

Phần kỹ thuật nằm hết trong `scripts/lai_suat.py` (đã chạy thật hằng ngày, đã soát với Google Docs).
**Đừng tự viết lại, đừng tự chép số bằng tay** — chạy script, script tự đọc bảng, so khớp tên ngân hàng, tô vàng, giữ kiểu ghi số.

Người dùng thường **không rành kỹ thuật**: nói lời thường, tự làm hết phần kỹ thuật, chỉ hỏi những gì chỉ họ biết.

## Cần có

1. **Chạy được lệnh + có mạng ra ngoài** tới `techcombank.com`, `vnexpress.net` (`gw.vnexpress.net`), `topi.vn` và các nguồn khác.
   Thử `curl -sI https://techcombank.com` trước. Bị chặn (403, `CONNECT tunnel failed`) → xem mục "Khi bị chặn".
2. **Kết nối Google Drive** (công cụ kiểu `create_file`, `search_files`, `download_file_content`). Không có → xem "Khi không có Google Drive".

## Bước 0 – Hỏi cho đủ (một lần, gọn)

| Cần biết | Mặc định nếu người dùng không nói |
|---|---|
| Link bài Techcombank (bắt buộc) | — |
| Tên file Docs của từng bài | Hỏi; nếu họ để tùy thì bỏ trường `ten_file` khỏi cấu hình — script lấy tiêu đề bài, bỏ phần ngày |
| Bài nào chỉ cập nhật bảng online / tại quầy | Cập nhật mọi bảng lãi suất trong bài |
| Nguồn + kỳ hạn lấy từ nguồn nào | Người dùng nêu nguồn nào thì **chỉ dùng đúng các nguồn đó** (thay mặc định; nguồn không kèm kỳ hạn = dùng cho mọi kỳ hạn nó có). Không nêu nguồn: VnExpress `https://vnexpress.net/chu-de/lai-suat-ngan-hang-3210` cho 1, 3, 6, 9, 12 tháng; Topi `https://topi.vn/lai-suat-tiet-kiem-ngan-hang-nao-cao-nhat.html` cho 18, 24, 36 tháng |
| Thư mục Drive | Thư mục gốc "My Drive" |
| Ngày ghi trên file | Hôm nay theo giờ Việt Nam: `TZ=Asia/Ho_Chi_Minh date +%d/%m/%Y` |

Chạy theo lịch, không ai trả lời → không hỏi, dùng mặc định, ghi rõ trong báo cáo.

## Bước 1 – Viết file cấu hình

Đặt `SKILL=<đường dẫn thư mục skill này>` (thư mục chứa SKILL.md). Tạo thư mục làm việc riêng **ngoài** thư mục skill
(vd `lai-suat/` ở thư mục hiện tại), ghi `lai-suat/cau-hinh.json` theo mẫu `$SKILL/references/cau-hinh-mau.json`:

```json
{
  "bai": [
    {"url": "https://techcombank.com/thong-tin/blog/lai-suat-tiet-kiem", "ten_file": "Lãi suất tiết kiệm Techcombank"},
    {"url": "https://techcombank.com/thong-tin/blog/cach-tinh-lai-suat-tien-gui-tiet-kiem",
     "ten_file": "Cách tính lãi suất tiền gửi tiết kiệm Techcombank", "bang": ["online"]}
  ],
  "nguon": [
    {"url": "https://vnexpress.net/chu-de/lai-suat-ngan-hang-3210", "ky_han": ["1", "3", "6", "9", "12"]},
    {"url": "https://topi.vn/lai-suat-tiet-kiem-ngan-hang-nao-cao-nhat.html", "ky_han": ["18", "24", "36"]}
  ]
}
```

- `bang`: bỏ trống = mọi bảng; `["online"]` hoặc `["quay"]` để giới hạn.
- `ky_han` của nguồn: nguồn đó **phụ trách** những kỳ hạn này. Bỏ trống = phụ trách mọi kỳ hạn nó có.
  Nhiều nguồn cùng phụ trách một kỳ hạn → nguồn đứng trước được ưu tiên, thiếu số mới lấy nguồn sau.
- Nguồn **VnExpress** đọc qua API riêng (trang vẽ bảng bằng JavaScript). Nguồn web khác (Topi, …) đọc thẳng bảng HTML:
  bảng có dòng đầu là kỳ hạn, cột đầu là tên ngân hàng, chữ ngay phía trên bảng có "tại quầy" hoặc "online".
- Nguồn script không đọc được (PDF, ảnh, trang vẽ bằng JS, trang chính thức của ngân hàng) → **nguồn nhập tay**:
  tự đọc trang, ghi số **đúng như nguồn** vào file JSON rồi khai `{"tep": "lai-suat/nhap-tay.json", "ky_han": [...]}`.
  Mẫu: `references/nguon-nhap-tay-mau.json`. Không đọc được thì không điền, tuyệt đối không đoán số.
- Tên ngân hàng khác nhau giữa bài và nguồn: script tự ghép (bỏ dấu, bỏ chữ "Bank", đọc cả phần trong ngoặc, kèm danh sách ghép
  có sẵn). Ghép thêm khi **chắc chắn**: `"ten_ghep": {"Tên trong bài": ["Tên trên nguồn"]}`.

## Bước 2 – Lấy số liệu và dựng bản cập nhật

```bash
python3 $SKILL/scripts/lai_suat.py lay  lai-suat/cau-hinh.json
python3 $SKILL/scripts/lai_suat.py dung lai-suat/cau-hinh.json dd/mm/yyyy
```

`lay` in `ok`/lỗi cho từng bài, từng nguồn. `dung` in mỗi bài: số bảng lãi suất nhận ra, số ô sửa, ô đổi màu, chỗ đổi ngày.
Kết quả: `lai-suat/tam/baiN.min.html` (bản để tải lên Drive) và `lai-suat/tam/ket-qua.json`.

Đọc kỹ dòng in ra: bài báo "0 bảng lãi suất" hoặc "Không đọc được cấu trúc bài" → báo người dùng, không tạo file rỗng.

## Bước 3 – Tạo Google Docs (mỗi bài)

1. `search_files` với `title = '<Tên file> – dd/mm/yyyy'`. **Đã có → không tạo**, ghi vào báo cáo (`--ghi-chu`).
2. `create_file`: `title` = tên file ở trên, `contentMimeType` = `text/html`, `textContent` = **nguyên văn** nội dung
   `lai-suat/tam/baiN.min.html` (đọc bằng `cat`, chép đủ từ `<html>` tới `</html>`, không sửa, không rút gọn),
   `parentId` = thư mục nếu có. File dài (~30–60 nghìn ký tự) — vẫn chép đủ: in theo từng đoạn cố định
   (`python3 -c "print(open('lai-suat/tam/bai1.min.html').read()[0:20000])"`, rồi 20000:40000, …) và ghép nối tiếp
   chính xác ở chỗ cắt. Bước soát bên dưới sẽ bắt mọi chỗ chép sai.
3. Soát: `download_file_content` (`exportMimeType` = `text/html`). Kết quả thường bị lưu ra file vì quá dài — dùng đường dẫn đó:
   ```bash
   python3 $SKILL/scripts/lai_suat.py soat lai-suat/cau-hinh.json baiN <đường dẫn file tải về>
   ```
   File tải về dạng JSON `{content: ...}` hay HTML thuần đều được, `soat` tự nhận.
   Phải ra `dòng lệch: 0`, số ô vàng khớp, chữ giống `100.00%`, exit 0. Lệch → `trash_file` file vừa tạo, tạo lại, soát lại.

## Bước 4 – Báo cáo và bàn giao

```bash
python3 $SKILL/scripts/lai_suat.py bao-cao lai-suat/cau-hinh.json dd/mm/yyyy <link Google Docs bài 1> <link Docs bài 2> --ghi-chu "ghi chú nếu có"
```

Lưu ở `lai-suat/bao-cao/yyyy-mm-dd.md`. Gửi người dùng bằng lời thường: link từng file, tóm tắt ô đã sửa, ô đổi màu,
mục "cần người duyệt" (bài không đổi gì thì chỉ ghi "Không có thay đổi lãi suất"); nguồn lỗi ghi ngay đầu.
Kết thúc bằng 2 câu hỏi: (a) mở file thấy có lỗi hiển thị không, (b) có ưng không, muốn chỉnh gì.
Xong thì xóa `lai-suat/tam/` (file tạm, có trang web gốc vài trăm KB); giữ `cau-hinh.json` và `bao-cao/` để lần sau chạy lại.

Script không sửa câu chữ ngoài ngày/tháng. Nếu số mới làm một câu trong bài sai rõ (vd bài viết "online cao hơn tại quầy
0,1–0,4%/năm" nhưng bảng mới chênh vài điểm), thêm 1 dòng vào báo cáo bằng `--ghi-chu` để người duyệt biết.

## Quy tắc script đã làm sẵn (để giải thích khi được hỏi — không làm tay)

- Chép toàn bộ bài: tiêu đề, sapo, ngày đăng (khối nền xám), đoạn văn, ảnh, link, đậm/nghiêng, bảng, lưu ý; bỏ menu, công cụ tính, quảng cáo.
- Đổi mọi ngày `dd/mm/yyyy` sang hôm nay và mọi "tháng mm/yyyy" sang tháng này; chỉ tô vàng phần ngày/tháng bị đổi.
- **Dòng Techcombank không bao giờ sửa.** Không thêm/xóa/đổi thứ tự ngân hàng, không sửa chữ khác.
- So khớp theo **tên** ngân hàng, đúng bảng tại quầy ↔ tại quầy, online ↔ online (cột ghi rõ "tại quầy"/"online" thì theo cột).
- Số bằng giá trị (2.10 = 2,1) → giữ nguyên, không tô. Số khác → sửa + tô vàng riêng ô đó. Phẩy → chấm, không làm tròn.
  Dòng đang ghi kiểu 2 chữ số thập phân có số 0 cuối (2.10, 5.90) → số mới cũng 2 chữ số; còn lại ghi đúng như nguồn.
- Thiếu số: ngân hàng có trên nguồn nhưng thiếu kỳ hạn → **lấy kỳ hạn gần nhất** (ưu tiên kỳ ngắn hơn liền kề, số vừa lấy lần này) –
  "Trường hợp A". Không nguồn nào có ngân hàng → "-" – "Trường hợp B" (muốn lấy từ trang chính thức thì thêm nguồn nhập tay).
- Nguồn không truy cập được → giữ nguyên các ô nguồn đó phụ trách, báo cáo ghi "Chưa cập nhật được từ … do không truy cập được".
- Bảng có chú thích "Màu xanh … cao nhất … màu đỏ … thấp nhất" → tô lại màu từng cột (bỏ dòng Techcombank);
  ô đổi màu cũng tô vàng và liệt kê ở mục 4b báo cáo.
- Báo cáo tự cảnh báo: nguồn cũ hơn 3 ngày, kỳ hạn dài thấp hơn hẳn kỳ ngắn (≥ 0,8 điểm), số < 1%, ô đổi mạnh (≥ 0,8 điểm),
  ngân hàng không có trên một nguồn.

Quy trình gốc đầy đủ (bản người dùng viết tay, áp dụng cho 2 bài mặc định): `references/quy-trinh-goc.md`.

## Khi bị chặn / thiếu công cụ — nói thật, không bịa số

- **Mạng chặn một nguồn**: vẫn chạy; script giữ ô của nguồn lỗi và ghi đầu báo cáo. Đừng thử lại quá 1–2 lần với lỗi 403.
- **Mạng chặn cả techcombank.com**: nhờ người dùng mở `view-source:<link bài>` trên trình duyệt, bấm Ctrl+S (Cmd+S) lưu file,
  đính kèm vào chat; khai `"tep_html": "<đường dẫn file>"` trong mục bài (giữ `url`). Trang nguồn cũng làm được như vậy.
  Lưu bằng Ctrl+S thường (không qua view-source) sẽ hỏng cấu trúc bài → script báo "Không đọc được cấu trúc bài".
- **Không có Google Drive**: gửi file `baiN.min.html` cho người dùng, hướng dẫn: kéo file vào Google Drive → chuột phải →
  Mở bằng → Google Tài liệu (Docs giữ nguyên bảng và nền vàng).
- **Bài không phải blog Techcombank** (cấu trúc khác): script báo lỗi; dừng và báo, không tự chép bài bằng tay.

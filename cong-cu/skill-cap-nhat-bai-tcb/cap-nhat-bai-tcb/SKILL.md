---
name: cap-nhat-bai-tcb
description: Cập nhật bài viết Techcombank bất kỳ (techcombank.com/thong-tin/blog/...) cho hết lỗi thời — đọc bản mới nhất trên web, đọc các nguồn tham khảo người dùng đưa, sửa đúng những chỗ đã cũ (số liệu, lãi suất, phí, hạn mức, mốc thời gian, quy định, ngày/tháng), viết số theo đúng cách bài TCB đang viết, rồi tạo file Google Docs chép trọn bài với mọi chỗ đổi tô nền vàng, kèm báo cáo. Bảng lãi suất tiết kiệm được cập nhật tự động từ VnExpress/Topi. Dùng khi người dùng đưa link bài Techcombank và muốn "cập nhật", "update", "làm mới nội dung", "sửa số liệu cũ", "update lãi suất", kể cả khi chỉ dán link kèm nguồn mà không nói tên skill.
---

# Cập nhật bài viết Techcombank → Google Docs (tô vàng chỗ đổi)

**Đầu vào:** link bài Techcombank cần cập nhật (một hay nhiều) + link nguồn tham khảo.
**Đầu ra:** mỗi bài một file Google Docs mới `<Tên file> – dd/mm/yyyy` chứa **toàn bộ bài**, đúng trình bày như web,
chỉ khác ở những chỗ đã cập nhật — **mọi chỗ đổi tô nền vàng, chỉ tô đúng phần bị đổi** — kèm báo cáo từng chỗ sửa + nguồn.

Phần kỹ thuật nằm trong `scripts/cap_nhat.py` (đã chạy thật hằng ngày, đã soát với Google Docs). **Việc của bạn là đọc và phán
đoán nội dung; việc chép bài, tô vàng, viết số, soát lỗi để script làm.** Đừng tự chép bài hay tự dựng HTML bằng tay.

Người dùng thường **không rành kỹ thuật**: nói lời thường, tự làm hết phần kỹ thuật, chỉ hỏi những gì chỉ họ biết.

## 3 yêu cầu cốt lõi

1. **Đọc nội dung mới nhất của bài TCB** — mỗi lần chạy tải lại bài từ web (`lay` xóa sạch file cũ), rồi đọc trọn bằng `xem`.
   Không dùng bản cũ, không dùng trí nhớ.
2. **Đọc nguồn tham khảo để sửa chỗ lỗi thời** — chỉ sửa khi nguồn nói rõ; mỗi chỗ sửa ghi nguồn + lý do.
3. **Viết số theo cách bài TCB đang viết** — dấu thập phân, dấu nghìn, số chữ số thập phân, đơn vị, cách ghi %/năm…
   giống hệt số cũ ở cùng chỗ. Lệnh `sua` tự chuyển (vd nguồn ghi `7,2` → bài ghi `7.20` nếu ô cũ là `4.90`;
   `120.000.000` → `120,000,000`), nhưng bạn vẫn phải tự viết đúng ngay từ đầu và đọc cảnh báo.

## Cần có

1. Chạy được lệnh + mạng ra ngoài tới `techcombank.com` và các nguồn. Thử `curl -sI https://techcombank.com` trước.
2. Kết nối Google Drive (`create_file`, `search_files`, `download_file_content`, `trash_file`).
Thiếu thứ nào → mục "Khi bị chặn / thiếu công cụ" cuối file.

Đặt `SKILL=<thư mục chứa file SKILL.md này>`. Làm việc trong một thư mục riêng **ngoài** thư mục skill, vd `cap-nhat/`.

## Bước 0 – Hỏi cho đủ (một lần, gọn)

| Cần biết | Mặc định nếu người dùng không nói |
|---|---|
| Link bài Techcombank (bắt buộc) | — |
| Nguồn tham khảo | Người dùng nêu nguồn nào **chỉ dùng đúng nguồn đó**. Bài có bảng lãi suất tiết kiệm mà không nêu nguồn: VnExpress (1–12 tháng) + Topi (18–36 tháng) |
| Phạm vi | Cập nhật mọi chỗ lỗi thời mà nguồn xác nhận được. Người dùng chỉ định phần nào thì chỉ làm phần đó |
| Tên file Docs | Hỏi; để tùy thì bỏ `ten_file` khỏi cấu hình — script lấy tiêu đề bài, bỏ phần ngày |
| Thư mục Drive | "My Drive" |
| Ngày ghi trên file | Giờ Việt Nam: chạy **trước 15h → hôm nay**, chạy **từ 15h trở đi → ngày hôm sau** (Trang chốt 08/10/2026): `TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y`. Áp dụng cho mọi ngày trong bài, tên file Docs và báo cáo |

Chạy theo lịch, không ai trả lời → không hỏi, dùng mặc định, ghi rõ trong báo cáo.

## Bước 1 – File cấu hình `cap-nhat/cau-hinh.json`

```json
{
  "bai": [{"url": "https://techcombank.com/thong-tin/blog/<bai-viet>", "ten_file": "Tên file Docs"}],
  "tham_khao": ["https://nguon-1...", "https://nguon-2.pdf"],
  "nguon": []
}
```

- `tham_khao`: nguồn để **bạn đọc** và tự quyết sửa chữ/số trong bài (trang web, file PDF). Script tải về và chuyển thành chữ.
- `nguon`: **chỉ dùng cho bảng lãi suất tiết kiệm** (bảng có cột "Ngân hàng", dòng Techcombank, cột kỳ hạn) — script tự cập nhật cả bảng.
  Bài không có bảng như vậy → để `[]`. Mẫu đầy đủ + giải thích: `references/cau-hinh-mau.json`, `references/bang-lai-suat.md`.
- `bai[].bang`: `["online"]` / `["quay"]` để giới hạn bảng lãi suất được cập nhật (mặc định: mọi bảng).

## Bước 2 – Lấy bài mới nhất + nguồn, dựng bản nền

```bash
python3 $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json dd/mm/yyyy
```

- `lay` in `ok`/lỗi từng bài, từng nguồn; nguồn tham khảo ra chữ ở `cap-nhat/tam/thamkhaoN.txt` (in kèm số ký tự).
  Nguồn ra rất ít chữ (trang vẽ bằng JavaScript) → đọc bằng công cụ đọc web của bạn; vẫn không được → báo người dùng.
- `dung` chép trọn bài, **đổi mọi ngày dd/mm/yyyy sang hôm nay và mọi "tháng mm/yyyy" sang tháng này** (tô vàng), cập nhật
  bảng lãi suất nếu có `nguon`. Bài báo "Không đọc được cấu trúc bài" → dừng, báo người dùng.

## Bước 3 – Đọc bài + đọc nguồn, tìm chỗ lỗi thời

```bash
python3 $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1
```

In toàn bộ bài (đã gồm ngày mới + bảng lãi suất đã cập nhật), mỗi khối một dòng có số thứ tự, bảng dạng `ô | ô | ô`.
**Đọc hết bài**, rồi đọc hết các file `thamkhaoN.txt`. Lập danh sách chỗ lỗi thời: số liệu, lãi suất, phí, hạn mức,
tỷ giá, thời hạn, tên/ số hiệu văn bản pháp luật, mốc năm, tên sản phẩm/chương trình, mô tả bảng…

Quy tắc phán đoán (bắt buộc):
- **Chỉ sửa khi nguồn nói rõ.** Không đoán, không ước lượng, không lấy trung bình, không dùng hiểu biết riêng.
- Con số phải tự **tính ra** từ nguồn (vd khoảng chênh lệch, tổng) → được sửa nhưng đặt `"tinh_toan": true` và ghi cách tính ở `ly_do`
  (tự vào mục cần duyệt). Nghi ngờ / nguồn mâu thuẫn / nguồn cũ hơn bài → **không sửa**, ghi vào `can_duyet`.
- Thông tin **về chính Techcombank** (sản phẩm, phí, lãi suất TCB) chỉ sửa theo trang techcombank.com; dòng Techcombank
  trong bảng so sánh lãi suất **không bao giờ sửa**.
- Sửa ít nhất có thể: chỉ đổi con số / cụm từ đã cũ, giữ nguyên câu văn, giọng văn, link, định dạng. Không viết lại đoạn,
  không thêm đoạn mới, không xóa đoạn — trừ khi người dùng yêu cầu.
- Câu chữ không còn đúng với số mới (vd "online cao hơn 0.1 – 0.4%/năm" trong khi bảng mới chênh vài điểm) → sửa con số chỉ khi
  tính được **rõ ràng và ổn định** (số liệu nguồn sạch, không có ngoại lệ/lỗi nhập làm khoảng tính ra vô nghĩa); dữ liệu nhiễu → không tự
  chọn cách lọc, đưa vào `can_duyet` kèm số liệu bạn thấy.
- **Văn bản pháp luật** (số hiệu thông tư/quyết định, mức quy định gắn với văn bản): chỉ sửa theo nguồn chính thức nói về chính văn bản đó
  (cơ quan ban hành, cổng văn bản pháp luật, báo chí dẫn rõ văn bản mới thay thế). Nguồn thị trường (bài so sánh lãi suất…) không đủ
  để sửa nội dung gắn với văn bản → `can_duyet`.
- **Nguồn Techcombank không đọc được** (trang vẽ bằng JavaScript, bị chặn, đã thử công cụ đọc web của bạn): vẫn làm tiếp phần còn lại,
  giữ nguyên mọi thông tin về Techcombank, ghi rõ ở đầu báo cáo bằng `--ghi-chu` và nói với người dùng.
- Ví dụ minh họa / phép tính mẫu trong bài (vd "gửi 100 triệu, lãi 6%…") là giả định, **không cập nhật** trừ khi người dùng yêu cầu
  (chỉ kiểm tra phép tính đúng; sai thì ghi `can_duyet`).

## Bước 4 – Ghi các chỗ sửa vào `cap-nhat/sua.json` và áp

Mẫu: `references/sua-mau.json`.

```json
{
  "bai1": {
    "sua": [
      {"tim": "0.1 - 0.4%/năm", "thay": "0.2 - 0.5%/năm", "lan": "tat_ca",
       "nguon": "https://...", "ly_do": "nguồn ghi rõ: online cao hơn tại quầy 0,2 – 0,5%/năm"},
      {"ngu_canh": "Theo quyết định số 986/QĐ-TTg", "tim": "đến năm 2025", "thay": "đến năm 2030",
       "nguon": "https://...", "ly_do": "văn bản mới thay thế"}
    ],
    "can_duyet": ["Đoạn 12: phí chuyển tiền 0 đồng – nguồn chưa xác nhận, giữ nguyên."]
  }
}
```

- `tim`: chữ **đúng như trong bài** (chép từ kết quả `xem`; khoảng trắng gộp, không cần quan tâm chữ đậm/nghiêng/link).
- `thay`: chữ mới hoàn chỉnh. Script chỉ thay và tô vàng **từng phần khác nhau** (vd chỉ `3.7`; hai số đổi thì tô riêng hai số),
  giữ nguyên chữ đậm/link xung quanh.
- `tim` xuất hiện nhiều lần → thêm `ngu_canh` (đoạn chữ lân cận xuất hiện đúng 1 lần, chứa hoặc gối lên `tim`), hoặc `"lan": 2`
  (lần thứ 2), hoặc `"lan": "tat_ca"` (sửa mọi chỗ).
- Số trong `thay` tự viết lại theo số cũ cùng thứ tự trong `tim` (dấu thập phân, dấu nghìn, kiểu `2.10`). Không muốn → `"giu_nguyen_so": true`.

```bash
python3 $SKILL/scripts/cap_nhat.py sua cap-nhat/cau-hinh.json cap-nhat/sua.json
```

Exit 0 = áp đủ. Lỗi (không thấy chữ, xuất hiện nhiều lần…) → sửa `sua.json`, chạy lại (luôn áp lại từ bản nền, chạy bao nhiêu lần cũng được).
Đọc mọi cảnh báo "viết lại thành …" và "vắt qua chữ đậm" để chắc kết quả đúng ý. Chạy `xem` lần nữa để đọc lại bản cuối.
**Luôn chạy `sua`** khi có chỗ sửa **hoặc** có mục `can_duyet` (không có chỗ sửa thì để `"sua": []`) — `can_duyet` chỉ vào báo cáo qua bước này.
Chỉ bỏ qua bước này khi không sửa gì và không có gì cần duyệt. Muốn thử nghiệm thì dùng file khác, rồi chạy lại `sua.json` thật trước khi tạo Docs.

## Bước 5 – Tạo Google Docs (mỗi bài)

1. `search_files`: `title = '<Tên file> – dd/mm/yyyy'`. **Đã có → không tạo**, ghi vào báo cáo (`--ghi-chu`).
2. `create_file`: `title` như trên, `contentMimeType` = `text/html`, `textContent` = **nguyên văn** `cap-nhat/tam/baiN.min.html`
   (từ `<html>` tới `</html>`, không sửa, không rút gọn), `parentId` = thư mục nếu có. File dài thì in theo đoạn cố định
   (`python3 -c "print(open('cap-nhat/tam/bai1.min.html').read()[0:20000])"`, rồi `20000:40000`, …) và ghép nối tiếp chính xác.
3. Soát: `download_file_content` (`exportMimeType` = `text/html`; kết quả dài sẽ được lưu ra file — dùng đường dẫn đó, dạng JSON hay HTML đều được):
   ```bash
   python3 $SKILL/scripts/cap_nhat.py soat cap-nhat/cau-hinh.json baiN <đường dẫn file tải về>
   ```
   Phải ra `dòng lệch: 0`, số ô vàng khớp, chữ giống `100.00%`, exit 0. Lệch → `trash_file` file vừa tạo, tạo lại, soát lại.

## Bước 6 – Báo cáo và bàn giao

```bash
python3 $SKILL/scripts/cap_nhat.py bao-cao cap-nhat/cau-hinh.json dd/mm/yyyy <link Google Docs bài 1> [<link Docs bài 2>] --ghi-chu "..."
```

Lưu ở `cap-nhat/bao-cao/yyyy-mm-dd.md`: ngày đổi, nguồn đã dùng, bảng lãi suất (nếu có), **từng chỗ nội dung đã sửa
(cũ → mới, nguồn, lý do)**, mục cần người duyệt. Gửi người dùng bằng lời thường: link file + tóm tắt; bài không đổi gì thì chỉ
ghi "Không có nội dung nào cần cập nhật" (bài chỉ có bảng lãi suất: "Không có thay đổi lãi suất"); nguồn lỗi ghi ngay đầu.
Kết thúc bằng 2 câu hỏi: (a) mở file thấy có lỗi hiển thị không, (b) có ưng không, muốn chỉnh gì.
Xong thì xóa `cap-nhat/tam/`; giữ `cau-hinh.json`, `sua.json`, `bao-cao/`.

## Script đã làm sẵn (để giải thích khi được hỏi — không làm tay)

- Chép toàn bộ bài: tiêu đề, sapo, ngày đăng (khối nền xám), đoạn văn, đề mục, ảnh, link, đậm/nghiêng, bảng, lưu ý;
  bỏ menu, công cụ tính, nút bấm, quảng cáo cuối trang. Bảng kẻ viền xám như file mẫu.
- Ngày/tháng: đổi mọi `dd/mm/yyyy` và "tháng mm/yyyy"; chỉ tô vàng phần ngày/tháng bị đổi.
- Bảng lãi suất (khi có `nguon`): xem `references/bang-lai-suat.md` — so khớp theo tên ngân hàng, đúng bảng tại quầy/online,
  giữ kiểu ghi số của ô cũ, kỳ hạn thiếu lấy kỳ hạn gần nhất, tô lại màu cao nhất/thấp nhất, không bao giờ sửa dòng Techcombank.
- Cách viết số: số mới theo đúng số cũ cùng chỗ (dấu thập phân, dấu nghìn, `2.10` → số mới 2 chữ số; `4.75`, `6`, `6.6` → ghi như nguồn);
  không làm tròn, không bỏ chữ số của nguồn.

Quy trình gốc người dùng viết tay (cho 2 bài lãi suất hằng ngày): `references/quy-trinh-goc.md`.

## Khi bị chặn / thiếu công cụ — nói thật, không bịa

- **Mạng chặn một nguồn**: vẫn chạy; phần của nguồn đó giữ nguyên, báo cáo ghi rõ. Lỗi 403 thì đừng thử lại quá 1–2 lần.
- **Mạng chặn techcombank.com**: nhờ người dùng mở `view-source:<link bài>` trên trình duyệt, Ctrl+S (Cmd+S) lưu file, đính kèm vào chat;
  khai `"tep_html": "<đường dẫn>"` trong mục bài (giữ `url`). Nguồn tham khảo cũng làm được như vậy, hoặc người dùng dán nội dung vào chat.
  Lưu bằng Ctrl+S thường (không qua view-source) sẽ hỏng cấu trúc bài.
- **Không có Google Drive**: gửi file `baiN.min.html`, hướng dẫn: kéo vào Google Drive → chuột phải → Mở bằng → Google Tài liệu.
- **Trang không phải bài blog Techcombank** (script báo không đọc được cấu trúc): dừng và báo, không tự chép bài bằng tay.

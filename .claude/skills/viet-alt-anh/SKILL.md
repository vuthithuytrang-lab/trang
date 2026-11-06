---
name: viet-alt-anh
description: Viết alt ảnh và chú thích ảnh chuẩn SEO cho bài viết khách hàng, kèm 4 ô cho ảnh đại diện (Alt Text, Title, Image Caption, Description). Dùng skill này bất cứ khi nào Trang gửi HTML bài viết kèm danh sách key và nhờ viết alt — kể cả khi chị chỉ nói ngắn gọn "viết alt cho bài này", "đề xuất alt", "chèn alt vào HTML", "bổ sung 4 ô ảnh thumb", "làm tương tự bài trên", hay chỉ dán HTML với mấy dòng key mà không nói gì thêm. Cũng dùng khi chị gửi ảnh chụp màn hình ô Alternative text trong CMS và nhờ viết. Khách thường gặp: asiagroup-vn.com (AIG), okamura.com.vn, hr2b.com, osakar.com.vn, nipponpaint.com.vn.
---

# Viết alt ảnh chuẩn SEO

Skill này đóng gói toàn bộ quy trình Trang đã chốt dần qua hàng chục bài thực tế.
Mục tiêu: lần nào chạy cũng ra chất lượng như nhau, không phải nhắc lại luật từ đầu.

**Trang là người Nontech.** Nói bằng lời thường, không thuật ngữ. Tự làm hết phần kỹ thuật.
Gọi chị là **"bạn xinh đẹp"**, không gọi "chị". Cách xưng hô này **chỉ dùng khi nói chuyện
với Trang**, tuyệt đối không mang vào alt hay bất cứ nội dung nào gửi ra ngoài.

---

## 🔒 Luật cứng nhất: phải nhìn ảnh thật

**Không bao giờ viết alt theo tên file, theo chú thích cũ, hay theo đoán.**

Bắt buộc tải ảnh về, mở ra xem tận mắt rồi mới viết. Ảnh nào không tải được thì
**nói thẳng là không xem được**, không viết bừa.

Đây là lý do skill này tồn tại — app `cong-cu/cong-cu-alt-anh/soat-alt-anh.html`
làm được mọi thứ khác nhưng không nhìn hiểu được ảnh.

---

## Có app rồi thì dùng app trước

Trang có sẵn hai công cụ chạy không tốn token:

| Công cụ | Đường dẫn | Việc của nó |
|---|---|---|
| App soát alt | `cong-cu/cong-cu-alt-anh/soat-alt-anh.html` | Hiện ảnh, đếm ký tự, soát luật, dò lỗi bài, ghép HTML |
| App chèn inlink | `cong-cu/cong-cu-chen-inlink/chen-inlink.html` | Chèn link nội bộ theo bảng key → URL |

**Skill này là bản dự phòng** cho lúc app không mở được, hoặc khi Trang muốn mình
viết hộ câu chữ. Nếu Trang chỉ cần phần máy móc, nhắc chị dùng app cho đỡ tốn.

---

## Quy trình 6 bước

### Bước 1 — Đọc kỹ đầu vào

Trang thường gửi: **HTML bài viết + danh sách key**. Đôi khi kèm URL bài.

Dòng key nào có ghi `- key chính` thì đó là key quan trọng nhất, dùng nhiều hơn các key khác.

### Bước 2 — Tải toàn bộ ảnh về xem

```bash
D=<thư mục nháp>/baiNN; mkdir -p $D; cd $D
B=https://<tên-miền>/wp-content/uploads/YYYY/MM/<slug>
for n in 01 02 03 04; do
  for i in 1 2 3; do curl -sSL --max-time 90 -o img$n.bin "$B-$n.webp" && break; sleep 2; done
done
# dò luôn ảnh thumb
for s in -thumb -thumb-1; do for e in jpg webp png; do
  c=$(curl -sSL --max-time 40 -o t.$e -w "%{http_code}" "$B$s.$e")
  [ "$c" = "200" ] && cp t.$e thumb.$e; rm -f t.$e
done; done
```

Mạng hay đứt giữa chừng với `okamura.com.vn` và `asiagroup-vn.com` → **luôn bọc vòng lặp thử lại 3 lần**.

Rồi dựng một tấm ảnh gộp để xem tất cả trong một lần:

```python
from PIL import Image, ImageDraw
import glob, os, hashlib
fs = sorted(glob.glob('img*.bin')) + sorted(glob.glob('thumb.*'))
for f in fs:
    print(f, os.path.getsize(f), Image.open(f).size,
          hashlib.md5(open(f,'rb').read()).hexdigest()[:8])
CW, CH, cols = 540, 420, 2
rows = (len(fs)+cols-1)//cols
s = Image.new('RGB', (cols*CW, rows*CH), 'white'); d = ImageDraw.Draw(s)
for i, f in enumerate(fs):
    im = Image.open(f)
    if im.mode in ('RGBA','LA','P'):                 # ảnh nền trong suốt
        im = im.convert('RGBA'); bg = Image.new('RGB', im.size, 'white')
        bg.paste(im, mask=im.split()[-1]); im = bg
    else: im = im.convert('RGB')
    t = im.copy(); t.thumbnail((CW-20, CH-46))
    x, y = (i % cols)*CW, (i//cols)*CH
    s.paste(t, (x+10, y+38)); d.text((x+12, y+14), f+' '+str(im.size), fill='black')
s.save('sheet.jpg', quality=86)
```

Mở `sheet.jpg` ra xem. Chi tiết nào chưa rõ (chữ trên bao bì, logo áo blouse, biển hiệu)
thì **cắt ra phóng to** rồi xem lại — đừng đoán.

### Bước 3 — Dò lỗi bài

Vừa xem ảnh vừa đối chiếu, ghi lại mọi thứ lệch. Danh sách lỗi đã gặp nhiều lần:

**Lỗi ảnh**
- Kích thước khai trong HTML **khác** kích thước file thật (so `width`/`height` với `Image.open().size`)
- Cùng một bức ảnh dùng ở **hai bài khác nhau** — so bằng `md5` (trùng file) hoặc so ảnh thu nhỏ 64×64 (trùng ảnh, khác lần nén)
- Cùng một file dùng **hai lần trong một bài**
- Ảnh **không khớp chú thích** (chú thích nói nhà máy mà ảnh là bàn thí nghiệm)
- Ảnh **stock** đặt dưới tên một công ty cụ thể → alt không được khẳng định là của công ty đó
- Ảnh **mờ**, trông như cắt từ video
- Ảnh **của đối thủ** (nhà máy, trụ sở, logo) đăng trên web khách → cảnh báo bản quyền

**Lỗi HTML**
- Lỗi link Markdown dán nhầm: `<a href="...">[www.x.com](https://www.x.com)</a>` — **lỗi này dính 9 bài AIG liên tiếp**
- Link còn đuôi `utm_source=chatgpt` — lộ việc bài soạn qua ChatGPT
- Thẻ `<a>` rỗng, bên trong chỉ có dấu cách
- Alt rỗng, hoặc thiếu hẳn thuộc tính `alt`
- Alt cũ **thừa dấu cách** ở cuối
- Alt cũ **giống hệt chú thích**
- Hai ảnh dùng **chung một chú thích**
- Ghi chú nội bộ của người viết còn sót trong bài
- Bài tự mâu thuẫn (chỗ nói 3 nhóm, chỗ nói 4 nhóm)
- Sai đơn vị đo (`BTU` thay vì `BU` cho độ nhớt; `cm` thay vì `mm`)

Báo hết cho Trang, **đừng viết alt che lỗi**.

### Bước 4 — Viết alt

**Luật bắt buộc, không được phá:**

| Luật | Cách kiểm |
|---|---|
| **Dưới 120 ký tự** | Python `len()` trên chuỗi UTF-8. ⚠️ **Không dùng `awk length` hay `wc -c`** — đếm byte, tiếng Việt sai ~30% |
| **Một câu có nghĩa** | Không liệt kê từ khoá |
| **Tả đúng ảnh thật** | Đã xem ở bước 2 |
| **Có key được gán** | Mỗi ảnh một key riêng |
| **Không câu nào trùng câu nào** | So bằng `set()` |
| **Đa dạng cấu trúc câu** | Đổi chủ ngữ, đổi cách mở đầu |

**Mật độ key.** Nhồi key vào mọi ô là spam. Tỷ lệ đã dùng ổn: **khoảng 55–65% số ô có key**.
Bài chỉ có một key mà có 10 ô thì đặt key ở 5–6 ô, các ô còn lại chỉ tả ảnh, hoặc dùng
cách gọi tiếng Việt tương đương.

**Chú ý key lồng nhau.** Khi đếm, xét key **dài trước key ngắn**
(`kích thước tủ hồ sơ văn phòng` trước `kích thước tủ hồ sơ`), không thì đếm nhầm.

**Nếu key không khớp bài.** Có lúc Trang đưa key không liên quan đến nội dung
(key về "pha chế, đồ uống" cho bài về nhà phân phối nguyên liệu nói chung).
Vẫn làm đúng yêu cầu, **nhưng báo rõ** là key lệch và khuyên chuyển sang bài khác.

### Bước 5 — Bốn ô cho ảnh đại diện

Cả bốn ô viết **theo luật của alt**: một câu có nghĩa, tả đúng ảnh, có key, dưới 120 ký tự.
**Bốn câu phải khác nhau** — cùng một ảnh nhưng mỗi ô tả một góc khác.

| Ô | Cách viết |
|---|---|
| **Alt Text** | Tả ảnh, có key |
| **Title** | **Viết y như alt** — không để cụt vài chữ kiểu `Nguyên liệu cho ngành sữa - AIG` |
| **Image Caption** | Câu giới thiệu cho người đọc, có key |
| **Description** | **Viết y như alt**, khác câu đã dùng ở Alt Text |
| **File URL** | Giữ nguyên nếu tên file đã có key, không dấu |

**⛔ Cấm tuyệt đối:**

1. Từ `banner`, `ảnh bìa`, `cover image` trong Alt Text
2. Description mở đầu bằng `Cover image for the…`
3. Description **tóm tắt bài viết**: cấm `Bài viết của … giới thiệu…`, `Trang dịch vụ … của…`, `HR2B guide to…`
4. **Tả cách dàn trang của ảnh** (chốt 06/11/2026): cấm `ảnh ghép`, `khung hình tròn`,
   `hình tròn ghép lại`, `nền bản đồ chấm bi`, `bố cục`, `collage`, `ảnh thiết kế`.
   Ảnh ghép hay ảnh chụp thì alt vẫn chỉ nói **trong ảnh có gì**.

   | Sai | Đúng |
   |---|---|
   | **Ảnh ghép** phòng lab, nhà máy, kho của AIG **trên nền bản đồ thế giới** | Phòng nghiên cứu, dây chuyền sản xuất, kho hàng và xe lạnh của AIG |
   | **Năm khung hình tròn ghép lại**: phòng nghiên cứu, dây chuyền… | Từ phòng nghiên cứu, chai chiết xuất, máy đóng bột đến xe lạnh… |

### Bước 6 — Soát bằng máy trước khi gửi

**Luôn chạy, không bỏ qua:**

```python
# -*- coding: utf-8 -*-
KEYS = [...]                       # xét key dài trước key ngắn
BAN  = ["banner","ảnh bìa","cover image","ảnh ghép","khung tròn","khung hình tròn",
        "hình tròn ghép","collage","bố cục","ảnh thiết kế","nền bản đồ"]
MO_DAU_CAM = ["bài viết của","trang dịch vụ","cover image for"]   # riêng ô Description

rows = [("anh 01", "câu alt…"), ...]
alls, nk = [], 0
for ten, s in rows:
    p = []
    if len(s) >= 120:                               p.append("DAI")
    if any(w in s.lower() for w in BAN):            p.append("TUCAM")
    if s != s.strip():                              p.append("KHOANGTRANG")
    if any(c in s for c in '&<">'):                 p.append("KYTUHTML")
    hit = next((k for k in sorted(KEYS, key=len, reverse=True) if k in s.lower()), None)
    if hit: nk += 1
    alls.append(s)
    print("%-15s %3d %-12s key:%s" % (ten, len(s), ",".join(p) or "OK", hit or "-"))
print("khong trung:", len(set(alls)) == len(alls), "| co key:", nk, "/", len(alls))
```

Thêm: so với alt đã viết cho **cùng bức ảnh đó ở bài trước** — không được trùng câu.

---

## Giữ nguyên HTML khi xuất file

Chỉ thay giá trị `alt="…"` và phần chữ chú thích. **Không đổi một ký tự nào khác.**

```python
import re
def swap(m):
    t = m.group(0)
    f = re.search(r'<slug>-(\d\d)\.webp', t)
    if not f or f.group(1) not in ALT: return t
    return re.sub(r'alt="[^"]*"', lambda _: 'alt="%s"' % ALT[f.group(1)], t, count=1)
out = re.sub(r'<img[^>]*>', swap, src)

# chứng minh không đụng gì khác
for tag in ['<img','alt="','<h2','<h3','<table','<tr','<td','<ul','<li','<a ',
            '[caption','<strong','<em','<p ','&amp;']:
    if src.count(tag) != out.count(tag): print("LECH", tag, src.count(tag), out.count(tag))
st = lambda s: re.sub(r'<[^>]+>', '', re.sub(r'<img[^>]*>', '', s))
print("van ban giong het:", st(src) == st(out))
```

---

## Trả bài theo đúng kiểu từng khách

Trang đã chốt khác nhau cho từng khách — **đọc kỹ chị dặn gì ở bài đó**:

| Khách | Trả gì |
|---|---|
| **AIG** (asiagroup-vn.com) | Alt + 4 ô ảnh đại diện. **Không cần chú thích** |
| **Okamura** | Alt + chú thích, xuất ra chat |
| **OSAKAR** | Chèn thẳng alt vào HTML, bổ sung chú thích ở ảnh nào thiếu |
| **Nippon Paint** | Alt cho ảnh trong bài + ảnh Thumbnail (CMS riêng, không phải WordPress) |

**Mặc định trả bảng ngay trong chat**, không xuất file.
Chỉ xuất file hoặc dán nguyên HTML khi Trang nói rõ.

Từ 21/10/2026 Trang chốt: **không dán lại cả khối HTML nữa**, chỉ đưa bảng text:
- Bảng alt cho ảnh trong bài, ghi rõ **tên file** để biết câu nào dán vào ảnh nào
- Bảng 4 ô cho ảnh thumb
- Phần lỗi dò được

Kèm cột **ký tự** cho mỗi câu.

---

## Luật viết chú thích ảnh

- Cùng luật với alt, nhưng **bám ngữ cảnh đoạn văn** nhiều hơn
- Ảnh có đánh số mẫu → mở đầu `Mẫu 01:`, `Mẫu 02:`…
- **Giữ nguyên dấu nguồn cuối câu** nếu ảnh gốc đang có: `(Nguồn: Internet)`, `(Ảnh tham khảo)`
- Dấu nguồn **chỉ để trong chú thích**, không đưa vào alt

---

## Kết thúc mỗi lần giao việc

Hỏi Trang đúng hai câu:

1. Dán vào CMS rồi, có mất dấu tiếng Việt hay vỡ chỗ nào không?
2. Có ưng cách viết không, muốn chỉnh gì?

---

## Nguồn luật

- `cong-cu/cong-cu-viet-alt-anh-chuan-seo.md` — bản luật gốc Trang chốt dần
- `cong-cu/cong-cu-alt-anh/README.md` — app làm được gì, không làm được gì

Trang chốt thêm luật mới thì **ghi vào cả hai chỗ**: file luật gốc và skill này.
Nếu luật đụng tới phần máy soát thì sửa cả app (mục `GIOI_HAN`, `TU_CAM`, `MO_DAU_CAM`
ngay đầu phần `<script>`).

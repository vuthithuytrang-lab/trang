# Đăng app công khai — bộ cài chung (29/10/2026)

Trang dặn: *"tạo set up chung để từ sau tạo app bạn đều có thể tạo app publish được… ai cũng vào và làm được"*.
Học từ cách anh Tuấn đăng app "Thư ký công việc" lên Netlify: 1 thư mục web, đẩy lên là tự đăng, có dòng phiên bản,
soát rò rỉ trước khi đẩy, kiểm tra web thật sau khi đẩy.

## Nơi đăng

GitHub Pages của repo này, nhánh `gh-pages`, **miễn phí**, ai có link cũng mở được, không cần đăng nhập.

| App | Link |
|---|---|
| Cập nhật bài Techcombank (gốc trang) | https://vuthithuytrang-lab.github.io/trang/ |
| Cập nhật lãi suất (`lai-suat`) | https://vuthithuytrang-lab.github.io/trang/lai-suat/ |
| App mới tên `<ten>` | `https://vuthithuytrang-lab.github.io/trang/<ten>/` |

## Netlify, theo luồng anh Tuấn (Trang chọn 29/10/2026, miễn phí)

- Tên trang đã chọn: **`vttt-sn`** → `https://vttt-sn.netlify.app/` (app TCB ở gốc, app mới ở `/<ten>/`).
- Netlify đăng từ **nhánh `netlify`** = bản sao `gh-pages`. `dang.sh` đẩy cả hai nhánh, nên Netlify chỉ đăng lại khi **sửa app**.
  Số liệu đổi hằng ngày (`du-lieu.json`) chỉ vào `gh-pages`, app trên Netlify đọc số liệu từ GitHub Pages (có `access-control-allow-origin: *`).
  Lý do: gói miễn phí Netlify tính lượt theo mỗi lần đăng; vượt mức thì trang **tạm dừng** đến tháng sau, không trừ tiền (chưa nhập thẻ).
- Tài khoản Netlify: Trang đã đăng ký bằng GitHub `vuthithuytrang-lab` (29/10/2026).
- **Việc Trang còn làm, 1 lần** (chưa xong lúc ghi):
  1. Add new project → Import a Git repository → **GitHub** → cho phép (chọn kho `trang`).
  2. Chọn kho **trang** → **Branch to deploy = `netlify`**, các ô khác để trống → **Deploy**.
  3. Project configuration → **Change project name** → `vttt-sn`.
  Xong thì Claude kiểm tra `https://vttt-sn.netlify.app/` và thêm bước kiểm tra Netlify vào `dang.sh`.
- **Nút "Chạy cập nhật" chạy ngay** (29/10/2026): trang gọi hàm `netlify-goc/netlify/functions/chay.mjs` (chỉ có ở nhánh `netlify`),
  hàm dùng chìa `GITHUB_TOKEN` (biến môi trường Netlify) bấm `tu-dong-cap-nhat.yml` → bài mới lên nhánh `tu-dong-ket-qua` → trang hiện nút Chép / Tải Word.
  Lịch `*/5` của GitHub **không tin được** (kho ít hoạt động → thực tế ~6 tiếng/lần), nên không dựa vào lịch để chạy theo yêu cầu.
  Chìa: Trang tạo ở github.com → Settings → Developer settings → Fine-grained tokens, chỉ kho `trang`, quyền **Actions: Read and write**;
  dán thẳng vào Netlify → Project configuration → Environment variables, key `GITHUB_TOKEN`. **Không dán vào chat.**
- Đừng bấm: ô "Claude Agent / Build now" (tốn lượt), nút Upgrade, mục Usage & billing.

⚠️ Thư mục app chỉ để giao diện. Số liệu máy tự ghi (vd `lai-suat/du-lieu/`) nằm riêng trên `gh-pages` — đừng để file số liệu trong thư mục app, kẻo đăng lại app ghi đè số mới bằng số cũ.

## Cách đăng (Claude tự làm, Trang không phải làm gì)

1. Làm app trong 1 thư mục có `index.html` (vd `cong-cu/<ten-app>/web/`), theo cẩm nang thương hiệu SEONGON.
   Nên có trong `<head>`: `og:title`, `og:description`, `og:image` (xem trước khi gửi link qua Zalo), icon tab.
2. Chạy: `bash cong-cu/dang-app/dang.sh <thư mục app> <ten>`. Lệnh này làm 4 việc:
   - soát email, chìa khóa (gặp thì dừng);
   - chép thư mục app vào `gh-pages/<ten>/`;
   - đóng dấu phiên bản và đẩy lên;
   - chờ web thật hiện đúng phiên bản rồi in link.
3. Thêm dòng vào bảng trên + bảng bản đồ trong `CLAUDE.md`, commit nhánh làm việc.

## Giới hạn, nói thật trước với Trang

- **Trang tĩnh**: chạy được mọi thứ làm ngay trong trình duyệt (tính toán, xem bảng, đọc file người dùng chọn, gọi web nào cho phép đọc công khai).
  Việc cần **chìa khóa / quyền tài khoản** (ghi vào Drive, Sheet, gọi API trả phí) thì không được nhét chìa vào trang, vì repo công khai.
  Phần đó cần "máy chạy hộ" có quyền: Apps Script (Google, miễn phí, Trang bấm Cho phép 1 lần) hoặc GitHub Actions.
- Mã của app ai cũng xem được (repo public), nên không đưa tên khách, số liệu nội bộ vào app.

## Tên miền riêng (vd `cong-cu.ten-mien.vn/rank`)

GitHub Pages gắn được tên miền riêng, **miễn phí phần đăng**, chỉ tốn tiền tên miền. Cần Trang chọn 1 trong 2:

| Cách | Tốn | Trang cần làm |
|---|---|---|
| A. Tên miền con của công ty, vd `tools.seongon.com` | 0 đồng | Xin bộ phận IT/quản trị web SEONGON thêm 1 bản ghi DNS (Claude soạn sẵn nội dung) |
| B. Mua tên miền riêng (.com / .vn) | vài trăm nghìn đến khoảng 1 triệu/năm, xem giá lúc mua | Mua ở nhà đăng ký (Mắt Bão, PA Việt Nam, Tenten…), rồi nhập bản ghi DNS Claude đưa |

Bản ghi DNS cần thêm:
- **Tên miền con** (`tools.seongon.com`): `CNAME tools → vuthithuytrang-lab.github.io`
- **Tên miền gốc** (`ten-mien.vn`): 4 bản ghi `A`: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`

Claude làm sau đó:
1. Thêm file `CNAME` (chứa tên miền) vào gốc nhánh `gh-pages`.
2. Đặt tên miền trong mục Settings → Pages của repo. Nếu Claude không có quyền thì nhờ Trang bấm.
3. Bật HTTPS.
4. Kiểm tra link.

Từ đó mọi app có link dạng `ten-mien/<ten>` (không còn chữ `/trang`). Link cũ `github.io` tự chuyển sang tên miền mới.

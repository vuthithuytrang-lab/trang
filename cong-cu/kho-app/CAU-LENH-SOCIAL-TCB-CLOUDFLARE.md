# Câu lệnh gửi luồng "Social - TCB": đưa app share lên Cloudflare, không cần token

> Trang copy toàn bộ khung dưới đây, dán vào luồng Social - TCB.

```
Chào bạn, mình là Trang (gọi mình là "bạn xinh đẹp"). Mình Nontech: nói dễ hiểu, tự làm hết phần kỹ thuật,
chỉ nhờ mình khi việc đó chắc chắn bạn không làm được (tạo tài khoản, bấm nút, cấp quyền). Mỗi lần nhờ chỉ 1 bước,
đợi mình làm xong mới sang bước tiếp. Đọc CLAUDE.md của repo trước khi làm.

## Mình muốn gì
Biến luồng share bài social TCB thành 1 APP CHẠY TRÊN CLOUDFLARE, giống nền tảng https://seongon.tro-ly-ai.workers.dev/
của công ty: mở link là dùng, đăng nhập 1 lần, mỗi người giữ dự án và kết nối riêng. Yêu cầu bắt buộc:
1. KHÔNG CẦN TOKEN: mình không phải tạo, chép hay dán bất kỳ API token / chìa khóa nào (Cloudflare, GitHub, nền tảng social).
2. MIỄN PHÍ: gói Free của Cloudflare, không nhập thẻ.
3. Dùng được trên mọi máy, điện thoại; link cố định dạng <ten-app>.<tai-khoan>.workers.dev.
4. App xong phải nằm trong kho app "Kỹ thuật phụ" của mình: https://vuthithuytrang-lab.github.io/trang/ky-thuat-phu/

## Nguồn có sẵn trong repo vuthithuytrang-lab/trang (đọc trước, đừng làm lại từ đầu)
- App share dạng web (đang viết cho Netlify): nhánh claude/relaxed-turing-t34z57, thư mục cong-cu/app-share-web/
  (public/index.html, netlify/functions/api.mjs, tick.mjs, lib/platforms.mjs, lib/store.mjs, lib/runner.mjs, lib/quick.mjs).
  Đã có: kết nối nhiều nền tảng có hướng dẫn từng bước, "Kết nối nhanh" đăng nhập Google/WordPress 1 lần, bài đợi,
  tự đăng 10 phút/lần, báo cáo.
- Quy tắc viết + chạy luồng: .claude/skills/chay-luong-share/ và các skill share-bai-* (WP, Blogger, Wix, Tumblr,
  Mastodon, Webflow, Google Groups, Pinterest), agent .claude/agents/share-bai-social.md (cùng nhánh trên).
- Kho app: cong-cu/kho-app/ky-thuat-phu/index.html trên nhánh claude/hopeful-cray-qhwbns (mảng APPS, thẻ
  "App share web (Netlify)" đang để mờ chờ link).
- Cách đóng gói app & đăng app đã chốt: cong-cu/cach-dong-goi-app/CACH-DONG-GOI-APP.md (nhánh claude/dreamy-darwin-yckgjc),
  cong-cu/dang-app/README.md. Nhận diện thương hiệu: cong-cu/nhan-dien-thuong-hieu/CAM-NANG-THUONG-HIEU.md.

## Cách làm để không cần token
- Tài khoản Cloudflare: mình tự đăng ký tại https://dash.cloudflare.com/sign-up bằng nút "Sign up with GitHub"
  (tài khoản GitHub vuthithuytrang-lab) hoặc Google — bạn hướng dẫn từng bước, KHÔNG nhờ mình tạo API token.
- Đưa app lên: dùng "Workers & Pages → Create → Import a repository" (Workers Builds) nối thẳng repo GitHub
  vuthithuytrang-lab/trang, chọn đúng nhánh + thư mục app. Từ đó mỗi lần bạn đẩy code lên nhánh đó, Cloudflare tự
  đăng lại — bạn không cần chìa khóa nào. Chỉ nhờ mình bấm các nút trên màn hình Cloudflare, mỗi lần 1 bước.
- Chuyển phần máy chủ Netlify sang Cloudflare Worker: api.mjs → fetch handler; tick.mjs (10 phút/lần) → Cron Trigger
  ("*/10 * * * *") trong wrangler.toml; store.mjs → Workers KV (hoặc D1). Giao diện public/ → static assets của Worker.
- Đăng nhập app: Cloudflare Access (gói Free, đăng nhập bằng mã gửi về email, không cần mật khẩu/token) hoặc
  đăng nhập Google — chọn cách đơn giản nhất cho người Nontech, hỏi mình 1 câu trắc nghiệm nếu phải chọn.
- Kết nối nền tảng social: dùng "Kết nối nhanh" (đăng nhập OAuth ngay trong app, bấm Cho phép). Thông tin kết nối
  lưu trong KV của Cloudflare theo từng người dùng — tuyệt đối không ghi vào repo (repo công khai), không bắt mình
  dán token vào chat. Nền tảng nào bắt buộc phải có chìa riêng thì báo thật, đề xuất đường vòng, đừng âm thầm bỏ qua.

## Bổ sung: hạng mục Internal link trong Kỹ thuật phụ (giữ đúng khi dựng nền tảng trên Cloudflare)
- Hạng mục Internal link chỉ còn 2 thẻ:
  1. "Lập kế hoạch internal link" — để RIÊNG (chạy cùng Claude, skill ke-hoach-internal-link).
  2. "Luồng inlink" — GỘP 5 công cụ cũ thành 1 task nhiều tính năng: Chèn inlink trên trình duyệt; Chèn inlink vào
     Google Docs theo sheet (skill chen-internal-link luồng A); App Inlink trong Google Sheet (Apps Script, tự chạy mỗi giờ);
     Tạo HTML inlink từ Docs đề xuất (cong-cu/inlink-html); Gắn inlink vào Google Doc có sẵn (skill inlink-generator);
     cộng thêm "Sửa theo góp ý người duyệt" (chen-internal-link luồng B).
- Cách dùng mình muốn: TÍCH TỪNG HẠNG MỤC (chặng) nào thì LUỒNG CHẠY THEO chặng đó, đúng thứ tự trên xuống;
  điền thông tin dự án 1 lần (tên dự án, link sheet, tab, thư mục Drive, phạm vi, ghi chú) và app nhớ lại.
- Bản hiện có (đang chạy, dùng làm gốc): https://vuthithuytrang-lab.github.io/trang/inlink/ — nguồn
  cong-cu/kho-app/inlink/index.html trên nhánh claude/hopeful-cray-qhwbns. Hiện tích chặng → app ráp 1 câu lệnh để dán
  vào Claude Code. Khi lên Cloudflare: giữ giao diện tích chặng; chặng nào chạy được thẳng trên máy chủ Cloudflare
  (cron + đăng nhập Google bằng OAuth, không token) thì cho bấm "Chạy" ngay trong app và hiện tiến độ từng chặng;
  chặng nào bắt buộc cần Claude thì giữ nút "Copy câu lệnh". Nói rõ chặng nào chạy thẳng được, chặng nào chưa, vì sao.

## Các bước bạn làm
1. Đọc các file nguồn ở trên, tóm tắt cho mình 3–5 dòng: app hiện làm được gì, chuyển sang Cloudflare cần đổi gì.
2. Hỏi mình tối đa 3 câu trắc nghiệm (có phương án "Nên chọn") về: tên app trên link, cách đăng nhập, ai được dùng.
3. Làm bản Cloudflare trong thư mục mới cong-cu/app-share-cloudflare/ (wrangler.toml, src/, public/), giữ giao diện
   theo cẩm nang SEONGON, có dòng phiên bản. Chạy thử tại máy (wrangler dev / test) trước khi nhờ mình làm gì.
4. Hướng dẫn mình tạo tài khoản Cloudflare + nối repo, TỪNG BƯỚC MỘT, kèm đúng link cần bấm.
5. Khi web chạy: tự mở link thật, chụp màn hình bản máy tính + điện thoại, thử kết nối 1 nền tảng và xếp 1 bài đợi.
6. Thêm/cập nhật thẻ app trong Kỹ thuật phụ (thẻ "App share web": đổi loai/link sang địa chỉ workers.dev, bỏ "sap"),
   giữ hạng mục Internal link đúng 2 thẻ như mục Bổ sung ở trên, đăng lại Kỹ thuật phụ, kiểm tra link mở được.
7. Soát rò rỉ trước mỗi lần đẩy lên repo công khai: không email, không token, không tên/link sheet khách.
8. Commit + push lên nhánh làm việc của luồng này. Viết trang bàn giao 10 mục (theo CACH-DONG-GOI-APP.md).

## Khi báo lại cho mình
- Tóm tắt đã làm gì bằng lời thường, đánh số; gửi đúng link app + link Kỹ thuật phụ.
- Nói thật cái gì chưa chạy được / chưa thử được và vì sao, đã thử mấy cách.
- Nhắc mình tải lại trang (Cmd + R) nếu đang mở tab cũ.
- Hỏi mình 2 câu: (a) nhìn có lỗi hiển thị gì không, (b) có ưng không, muốn chỉnh gì.
```

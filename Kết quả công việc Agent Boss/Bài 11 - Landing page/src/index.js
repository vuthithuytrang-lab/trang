/**
 * ShopOne — Trang đích chạy quảng cáo + kho lead
 * Chạy trên Cloudflare Workers (miễn phí), lưu lead vào D1, gửi mail cảm ơn qua Resend.
 *
 * Nội dung bám đúng bảng định vị Bài 7:
 *  - Chỉ dùng điểm mạnh có ghi trong tài liệu thương hiệu
 *  - KHÔNG cam kết mức tăng doanh thu
 *  - KHÔNG nêu tên đối thủ
 *  - Nói thẳng chỗ sản phẩm chưa mạnh
 */

// ─────────────────────────────────────────────────────────────
// CHỖ TRANG SỬA NỘI DUNG ƯU ĐÃI — đổi đúng một dòng dưới đây
// ─────────────────────────────────────────────────────────────
const UU_DAI =
  "Ưu đãi dành riêng cho khách đăng ký mới trong tháng 9. Chuyên viên ShopOne sẽ gọi lại " +
  "trong 24 giờ làm việc để tư vấn gói phù hợp và báo mức ưu đãi đang áp dụng.";

const MAIL_NHAN_DEMO = "vuthithuytrang@seongon.com"; // Resend chưa xác thực tên miền

// ─────────────────────────────────────────────────────────────
// NGÂN SÁCH QUẢNG CÁO — Trang đổi số ở đây (đơn vị: đồng)
// Để 0 nghĩa là "chưa đặt ngân sách"
// ─────────────────────────────────────────────────────────────
const NGAN_SACH = 0;

// Mã đo Google Analytics. Chưa có thì để rỗng, trang vẫn chạy bình thường.
const GA_ID = "G-GZ9MD8K29F";

// ─────────────────────────────────────────────────────────────
// MÃ ĐO HÀNH VI — Trang dán mã vào đây, để rỗng thì trang vẫn chạy
// Clarity: xem lại thao tác khách (heatmap, quay màn hình)
// PostHog: ghi sự kiện chi tiết
// ─────────────────────────────────────────────────────────────
const CLARITY_ID = "yf4r46wxg3";
const POSTHOG_KEY = "phc_rFySDMBEjL3C9TGsG6ZoAPLntG4AwJHz8or8Thtq3Y9W";
const POSTHOG_HOST = "https://us.i.posthog.com";

// Model AI nhẹ của Cloudflare — miễn phí, có hạn lượt mỗi ngày
const MODEL_AI = "@cf/meta/llama-3.1-8b-instruct";

// ─────────────────────────────────────────────────────────────
// TELEGRAM
// Lúc học: Trang đóng cả hai vai. Dùng thật thì đổi CHAT_SALES
// sang Telegram của bạn Sales (bạn ấy phải bấm /start cho bot trước).
// ─────────────────────────────────────────────────────────────
const CHAT_MARKETER = "8652703491"; // Trang — nhận báo cáo cuối ngày
const CHAT_SALES = "8652703491";    // người lọc lead — nhận thông báo MQL mới
const WEBHOOK_PATH = "/telegram/webhook";

async function tg(env, method, body) {
  if (!env.TELEGRAM_TOKEN) return { ok: false, description: "chưa cấu hình TELEGRAM_TOKEN" };
  try {
    const r = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_TOKEN}/${method}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const kq = await r.json();
    // Telegram từ chối thì phải thấy được trong nhật ký, không nuốt lỗi im lặng
    if (!kq.ok) console.log("TELEGRAM LOI", method, kq.error_code, kq.description);
    return kq;
  } catch (e) {
    console.log("TELEGRAM LOI MANG", method, String(e));
    return { ok: false, description: String(e) };
  }
}

/** Báo cho người lọc lead biết vừa có MQL mới, kèm nút loại. */
async function baoMqlMoi(env, lead) {
  const dong = [
    "🔥 <b>MQL mới</b>",
    "",
    `👤 <b>${escTg(lead.ho_ten)}</b>`,
    `📞 ${escTg(lead.sdt)}`,
    lead.email ? `✉️ ${escTg(lead.email)}` : null,
    lead.nhu_cau ? `📝 ${escTg(lead.nhu_cau)}` : null,
    `📣 Nguồn: ${escTg(lead.nguon || "trực tiếp")}`,
    "",
    "<i>Không phải khách thật? Bấm nút bên dưới để loại khỏi MQL.</i>",
  ].filter(Boolean);

  return tg(env, "sendMessage", {
    chat_id: CHAT_SALES,
    text: dong.join("\n"),
    parse_mode: "HTML",
    reply_markup: {
      inline_keyboard: [[{ text: "❌ Không đủ điều kiện", callback_data: `loai:${lead.id}` }]],
    },
  });
}

const escTg = (s) =>
  String(s ?? "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

const BUOC = [
  { ma: "vao_trang", ten: "Vào trang" },
  { ma: "cuon_qua_form", ten: "Cuộn xuống thấy form" },
  { ma: "cham_form", ten: "Chạm vào ô điền" },
  { ma: "bam_gui", ten: "Bấm gửi" },
];

/**
 * TIÊU CHÍ CHẤM MQL (Marketing Qualified Lead)
 * Lead được đánh dấu MQL khi đạt CẢ HAI:
 *   1. Số điện thoại có từ 9 chữ số trở lên  → gọi được thật
 *   2. Có ghi nhu cầu (không để trống)       → biết họ cần gì mà tư vấn
 * Không đạt thì để là lead thường. Đổi tiêu chí chỉ cần sửa hàm này.
 */
function chamMQL({ sdt, nhu_cau }) {
  const soDienThoai = String(sdt || "").replace(/\D/g, "");
  const coSdtThat = soDienThoai.length >= 9;
  const coNhuCau = String(nhu_cau || "").trim().length > 0;
  return coSdtThat && coNhuCau ? 1 : 0;
}

const tien = (n) => new Intl.NumberFormat("vi-VN").format(n || 0) + "đ";

const B = {
  brand: "#0F6E5C",
  dark: "#0A4A3E",
  accent: "#F5A524",
  accentDark: "#D98A0B",
  ink: "#16211E",
  mut: "#5A6B66",
  line: "#DCE7E3",
  bg: "#F7FAF9",
};

const LOGO = `<svg width="34" height="34" viewBox="0 0 40 40" fill="none" aria-hidden="true">
<rect x="2" y="4" width="36" height="27" rx="6" fill="${B.brand}"/>
<rect x="7" y="9" width="26" height="14" rx="3" fill="#fff" opacity=".92"/>
<rect x="10" y="12" width="9" height="2.4" rx="1.2" fill="${B.brand}"/>
<rect x="10" y="16.5" width="15" height="2.4" rx="1.2" fill="${B.accent}"/>
<rect x="14" y="33" width="12" height="3" rx="1.5" fill="${B.dark}"/>
</svg>`;

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );

const CSS = `
*{box-sizing:border-box}
body{margin:0;background:${B.bg};color:${B.ink};
 font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
header{background:#fff;border-bottom:1px solid ${B.line};position:sticky;top:0;z-index:10}
.nav{display:flex;align-items:center;justify-content:space-between;height:64px}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;font-size:19px;letter-spacing:-.3px}
.hero{padding:56px 0 44px;display:grid;grid-template-columns:1.15fr .85fr;gap:44px;align-items:start}
h1{font-size:41px;line-height:1.15;margin:0 0 16px;letter-spacing:-1px}
.lead{font-size:18px;color:${B.mut};margin:0 0 24px}
.ticks{list-style:none;padding:0;margin:0 0 26px}
.ticks li{padding-left:29px;position:relative;margin:11px 0}
.ticks li:before{content:"";position:absolute;left:0;top:8px;width:17px;height:17px;border-radius:50%;
 background:${B.brand}}
.ticks li:after{content:"";position:absolute;left:5.5px;top:12.5px;width:6px;height:3px;
 border-left:2px solid #fff;border-bottom:2px solid #fff;transform:rotate(-45deg)}
.card{background:#fff;border:1px solid ${B.line};border-radius:14px;padding:24px;
 box-shadow:0 6px 26px rgba(15,110,92,.07)}
.form-card{position:sticky;top:88px}
.form-card h2{margin:0 0 4px;font-size:21px}
.form-card .sub{color:${B.mut};font-size:14px;margin:0 0 18px}
label{display:block;font-size:14px;font-weight:600;margin:14px 0 5px}
input,textarea,select{width:100%;padding:11px 13px;border:1.5px solid ${B.line};border-radius:9px;
 font:inherit;font-size:15px;background:#fff;color:${B.ink}}
input:focus,textarea:focus,select:focus{outline:none;border-color:${B.brand};
 box-shadow:0 0 0 3px rgba(15,110,92,.13)}
textarea{min-height:78px;resize:vertical}
.req{color:#B3261E}
button{width:100%;margin-top:20px;padding:14px;background:${B.accent};color:#3D2A00;border:0;
 border-radius:9px;font:inherit;font-size:16.5px;font-weight:700;cursor:pointer}
button:hover{background:${B.accentDark}}
.fine{font-size:12.5px;color:${B.mut};margin-top:12px;line-height:1.55}
section{padding:44px 0;border-top:1px solid ${B.line}}
h2.sec{font-size:26px;margin:0 0 8px;letter-spacing:-.5px}
.sec-sub{color:${B.mut};margin:0 0 26px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.g3 h3{margin:0 0 6px;font-size:17px}
.g3 .who{font-size:13px;color:${B.mut};margin:0 0 10px}
.g3 p{margin:0;font-size:14.5px}
.price{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.p{background:#fff;border:1px solid ${B.line};border-radius:12px;padding:18px}
.p .n{font-weight:700;font-size:16px}
.p .v{font-size:23px;font-weight:700;color:${B.brand};margin:6px 0 4px;letter-spacing:-.5px}
.p .f{font-size:13px;color:${B.mut}}
.honest{background:#fff;border-left:4px solid ${B.accent};border-radius:0 12px 12px 0;padding:18px 22px}
.honest h3{margin:0 0 8px;font-size:17px}
.honest ul{margin:0;padding-left:20px;font-size:14.5px;color:${B.mut}}
footer{padding:26px 0 40px;color:${B.mut};font-size:13px;border-top:1px solid ${B.line}}
.ok-wrap{max-width:600px;margin:70px auto;padding:0 20px;text-align:center}
.ok-badge{width:62px;height:62px;border-radius:50%;background:${B.brand};margin:0 auto 20px;
 display:flex;align-items:center;justify-content:center;font-size:31px;color:#fff}
.gift{background:#fff;border:2px dashed ${B.accent};border-radius:12px;padding:20px;margin:22px 0;text-align:left}
a{color:${B.brand}}
@media(max-width:860px){.hero{grid-template-columns:1fr;gap:28px}h1{font-size:31px}
 .grid3,.price{grid-template-columns:1fr}.form-card{position:static}}
`;

function pageHtml(nguon) {
  return `<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ShopOne — Quản lý cửa hàng gọn trong một màn hình</title>
<meta name="description" content="Phần mềm quản lý bán hàng cho cửa hàng nhỏ và vừa. Chuyển dữ liệu từ Excel miễn phí, nhập liệu nhanh, số liệu gọn trong một màn hình.">
${GA_ID ? `<script async src="https://www.googletagmanager.com/gtag/js?id=${GA_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
gtag('js',new Date());gtag('config','${GA_ID}');</script>` : `<!-- Google Analytics: chưa gắn mã đo. Trang vẫn chạy bình thường. -->`}
${CLARITY_ID ? `<script type="text/javascript">(function(c,l,a,r,i,t,y){
c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;
t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window,document,"clarity","script","${CLARITY_ID}");</script>` : `<!-- Microsoft Clarity: chưa gắn mã. -->`}
${POSTHOG_KEY ? `<script>!function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){
function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]);t[e]=function(){t.push([e].concat(
Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",
p.async=!0,p.src=s.api_host+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode
.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=
function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=
function(){return u.toString(1)+".people (stub)"},o="init capture identify alias people set_config
register unregister".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}
(document,window.posthog||[]);posthog.init('${POSTHOG_KEY}',{api_host:'${POSTHOG_HOST}'});</script>`
: `<!-- PostHog: chưa gắn mã. -->`}
<style>${CSS}</style></head><body>

<header><div class="wrap nav">
  <div class="brand">${LOGO}<span>ShopOne</span></div>
  <div style="font-size:14px;color:${B.mut}">Hơn 4.000 cửa hàng đang dùng</div>
</div></header>

<div class="wrap">
  <div class="hero">
    <div>
      <h1>Quản lý cửa hàng<br>gọn trong một màn hình</h1>
      <p class="lead">Chúng tôi bán sự nhẹ đầu, không bán tính năng. Bán hàng, kho và số liệu
        gom về một chỗ — bạn nhìn một lần là nắm.</p>
      <ul class="ticks">
        <li><b>Chuyển dữ liệu từ Excel miễn phí</b> — bạn không phải nhập lại một dòng nào</li>
        <li>Nhập liệu nhanh, thao tác bán hàng ít bước</li>
        <li>Kết nối nhiều sàn thương mại điện tử — đơn và kho về một mối</li>
        <li>Hỗ trợ 24/7 <span style="color:${B.mut}">(từ gói Nâng cao trở lên)</span></li>
      </ul>
    </div>

    <div class="card form-card">
      <h2>Nhận tư vấn &amp; ưu đãi</h2>
      <p class="sub">Để lại thông tin, chúng tôi gọi lại trong 24 giờ làm việc.</p>
      <form method="POST" action="/dang-ky">
        <label for="ho_ten">Họ và tên <span class="req">*</span></label>
        <input id="ho_ten" name="ho_ten" required autocomplete="name" placeholder="Nguyễn Văn A">

        <label for="sdt">Số điện thoại <span class="req">*</span></label>
        <input id="sdt" name="sdt" required autocomplete="tel" inputmode="tel" placeholder="09xx xxx xxx">

        <label for="email">Email <span style="font-weight:400;color:${B.mut}">(không bắt buộc)</span></label>
        <input id="email" name="email" type="email" autocomplete="email" placeholder="ban@congty.vn">

        <label for="nhu_cau">Bạn đang cần gì?</label>
        <textarea id="nhu_cau" name="nhu_cau"
          placeholder="Ví dụ: đang dùng Excel cho 2 cửa hàng, muốn chuyển sang phần mềm"></textarea>

        <input type="hidden" name="nguon" value="${esc(nguon)}">
        <button type="submit">Nhận ưu đãi tháng 9</button>
        <p class="fine">Chúng tôi chỉ dùng thông tin này để liên hệ tư vấn.
          Không chia sẻ cho bên thứ ba.</p>
      </form>
    </div>
  </div>
</div>

<section><div class="wrap">
  <h2 class="sec">Hợp với ai</h2>
  <p class="sec-sub">Ba nhóm cửa hàng đang dùng ShopOne mỗi ngày.</p>
  <div class="grid3">
    <div class="card g3"><h3>Cửa hàng 1–3 điểm bán</h3>
      <p class="who">Đang quản lý bằng sổ tay hoặc Excel</p>
      <p>Sợ nhất là mất số liệu khi đổi. Chúng tôi chuyển hộ toàn bộ file Excel sang, miễn phí.</p></div>
    <div class="card g3"><h3>Chuỗi 5–15 cửa hàng</h3>
      <p class="who">Cần nhìn số liệu tập trung</p>
      <p>Hết cảnh gọi từng nơi hỏi doanh số. Mọi điểm bán gom về một màn hình.</p></div>
    <div class="card g3"><h3>Hộ kinh doanh mới mở</h3>
      <p class="who">Cần đơn giản, chi phí thấp</p>
      <p>Dùng được ngay, không cần ai đào tạo. Bắt đầu gọn, không bắt đầu phức tạp.</p></div>
  </div>
</div></section>

<section><div class="wrap">
  <h2 class="sec">Bảng giá</h2>
  <p class="sec-sub">Giá trọn năm, không phí ẩn.</p>
  <div class="price">
    <div class="p"><div class="n">Cơ bản</div><div class="v">18 triệu</div>
      <div class="f">1 cửa hàng, mới bắt đầu</div></div>
    <div class="p"><div class="n">Tiêu chuẩn</div><div class="v">36 triệu</div>
      <div class="f">2–3 cửa hàng, đã có nề nếp</div></div>
    <div class="p"><div class="n">Nâng cao</div><div class="v">78 triệu</div>
      <div class="f">Chuỗi 5–10 cửa hàng, bán nhiều sàn</div></div>
    <div class="p"><div class="n">Doanh nghiệp</div><div class="v">145 triệu</div>
      <div class="f">Chuỗi lớn, cần tùy chỉnh riêng</div></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="honest">
    <h3>Ba việc ShopOne chưa làm được</h3>
    <ul>
      <li>Chưa có ứng dụng dành cho khách hàng cuối</li>
      <li>Chưa có phân hệ sản xuất</li>
      <li>Giao diện báo cáo nâng cao còn cần làm quen</li>
    </ul>
    <p style="margin:10px 0 0;font-size:14.5px;color:${B.mut}">
      Nói trước để bạn khỏi mất thời gian. Chưa làm được thì chúng tôi nói thẳng.</p>
  </div>
</div></section>

<footer><div class="wrap">ShopOne — phần mềm quản lý bán hàng cho cửa hàng bán lẻ nhỏ và vừa tại Việt Nam.
Ra mắt 2021.</div></footer>

<script>
// Đếm các bước khách đi qua. Mỗi bước chỉ ghi MỘT lần cho mỗi lượt xem,
// nếu không một người cuộn lên cuộn xuống sẽ làm số phồng lên sai.
(function () {
  var nguon = ${JSON.stringify(nguon)};
  var daGhi = {};
  function ghi(buoc) {
    if (daGhi[buoc]) return;
    daGhi[buoc] = 1;
    var than = JSON.stringify({ buoc: buoc, nguon: nguon });
    // sendBeacon gửi được cả khi khách đang đóng tab
    if (navigator.sendBeacon) {
      navigator.sendBeacon("/api/su-kien", new Blob([than], { type: "application/json" }));
    } else {
      fetch("/api/su-kien", { method: "POST", body: than, keepalive: true,
        headers: { "Content-Type": "application/json" } });
    }
  }

  ghi("vao_trang");

  // Cuộn tới mức nhìn thấy form — dùng IntersectionObserver cho chính xác
  var form = document.querySelector("form");
  if (form && "IntersectionObserver" in window) {
    new IntersectionObserver(function (mucs, obs) {
      mucs.forEach(function (m) {
        if (m.isIntersecting) { ghi("cuon_qua_form"); obs.disconnect(); }
      });
    }, { threshold: 0.35 }).observe(form);
  }

  // Chạm vào bất kỳ ô điền nào
  document.querySelectorAll("input, textarea").forEach(function (o) {
    o.addEventListener("focus", function () { ghi("cham_form"); }, { once: true });
  });

  // Bấm nút gửi
  if (form) form.addEventListener("submit", function () { ghi("bam_gui"); });
})();
</script>
</body></html>`;
}

function thankHtml(ten) {
  return `<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cảm ơn bạn — ShopOne</title><style>${CSS}</style></head><body>
<header><div class="wrap nav"><div class="brand">${LOGO}<span>ShopOne</span></div></div></header>
<div class="ok-wrap">
  <div class="ok-badge">✓</div>
  <h1 style="font-size:29px">Cảm ơn ${esc(ten)}!</h1>
  <p class="lead">Chúng tôi đã nhận được thông tin của bạn và sẽ gọi lại
    trong <b>24 giờ làm việc</b>.</p>
  <div class="gift">
    <h3 style="margin:0 0 8px;font-size:17px">🎁 Ưu đãi của bạn</h3>
    <p style="margin:0;font-size:15px">${esc(UU_DAI)}</p>
  </div>
  <p class="fine">Một email xác nhận vừa được gửi đi. Nếu không thấy, kiểm tra hộp thư quảng cáo.</p>
  <p style="margin-top:26px"><a href="/dang-ky">← Quay lại trang chính</a></p>
</div></body></html>`;
}

function mailHtml(ten) {
  return `<div style="font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;font-size:15px;
line-height:1.65;color:#16211E;max-width:600px">
<p>Chào ${esc(ten)},</p>
<p>Cảm ơn bạn đã quan tâm tới <b>ShopOne</b>. Chúng tôi đã nhận được thông tin và sẽ gọi lại
trong <b>24 giờ làm việc</b>.</p>
<div style="border:2px dashed #F5A524;border-radius:10px;padding:16px;margin:18px 0">
<b>🎁 Ưu đãi của bạn</b><br>${esc(UU_DAI)}</div>
<p>Trong lúc chờ, ba điều bạn nên biết trước:</p>
<ul>
<li><b>Chuyển dữ liệu từ Excel miễn phí</b> — bạn không phải nhập lại dòng nào</li>
<li>Số liệu mọi điểm bán gom về một màn hình</li>
<li>Hỗ trợ 24/7 có từ gói Nâng cao trở lên — nói rõ để bạn khỏi hiểu nhầm</li>
</ul>
<p>Và ba việc chúng tôi <b>chưa</b> làm được: chưa có ứng dụng cho khách hàng cuối,
chưa có phân hệ sản xuất, giao diện báo cáo nâng cao còn cần làm quen.</p>
<p>— Đội ShopOne</p>
<p style="margin-top:26px;padding-top:13px;border-top:1px solid #ddd;font-size:12.5px;color:#666">
Bạn nhận thư này vì vừa để lại thông tin trên trang ShopOne.<br>
<b>Không muốn nhận thư nữa?</b> Bấm Trả lời (Reply) thư này và gõ một chữ <b>HỦY</b> —
chúng tôi gỡ bạn khỏi danh sách ngay, không cần lý do.</p></div>`;
}

async function guiMail(env, ten) {
  if (!env.RESEND_API_KEY) return { sent: false, why: "chưa cấu hình RESEND_API_KEY" };
  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "ShopOne <onboarding@resend.dev>",
        to: [MAIL_NHAN_DEMO],
        reply_to: [MAIL_NHAN_DEMO],
        subject: `Cảm ơn ${ten} — ưu đãi ShopOne tháng 9`,
        html: mailHtml(ten),
      }),
    });
    const j = await r.json();
    return r.ok ? { sent: true, id: j.id } : { sent: false, why: j.message || `HTTP ${r.status}` };
  } catch (e) {
    return { sent: false, why: String(e) };
  }
}

const LA_PROBE = (t) => String(t || "").startsWith("LEAD-ABS-");

/**
 * Đọc micro-phễu: vào trang → cuộn thấy form → chạm ô điền → bấm gửi.
 * Ưu tiên SỐ THẬT. Chưa có số thật thì dùng dữ liệu mẫu (và nói rõ là mẫu).
 */
const NGUONG_THAT = 20; // đủ chừng này lượt vào thật thì mới bỏ dữ liệu mẫu

async function layMicroPheu(env) {
  const thatCo = await env.DB.prepare(
    `SELECT COUNT(*) AS n FROM su_kien WHERE la_mau = 0 AND buoc = 'vao_trang'`
  ).first();
  const soThat = thatCo?.n || 0;
  // Chỉ một hai lượt thật thì tỷ lệ nhảy loạn, chưa nói lên điều gì.
  // Đợi đủ NGUONG_THAT lượt mới chuyển hẳn sang số thật.
  const dungMau = soThat < NGUONG_THAT;

  const { results } = await env.DB.prepare(
    `SELECT buoc, COUNT(*) AS n FROM su_kien WHERE la_mau = ? GROUP BY buoc`
  )
    .bind(dungMau ? 1 : 0)
    .all();
  const dem = Object.fromEntries((results || []).map((r) => [r.buoc, r.n]));

  const buocs = BUOC.map((b, i) => {
    const n = dem[b.ma] || 0;
    const truoc = i === 0 ? n : dem[BUOC[i - 1].ma] || 0;
    const giu = truoc ? n / truoc : 0;
    return { ...b, so: n, giu_lai: Math.round(giu * 1000) / 10, rot: Math.round((1 - giu) * 1000) / 10 };
  });

  const vao = dem.vao_trang || 0;
  const gui = dem.bam_gui || 0;

  // Khi dùng số thật: chỉ đếm lead phát sinh TỪ LÚC bắt đầu đo,
  // nếu không sẽ đem lead cũ chia cho lượt truy cập mới → tỷ lệ vô lý (>100%).
  let soLead;
  if (dungMau) {
    soLead = gui;
  } else {
    const moc = await env.DB.prepare(
      `SELECT MIN(created_at) AS t FROM su_kien WHERE la_mau = 0`
    ).first();
    const r = await env.DB.prepare(
      `SELECT COUNT(*) AS n FROM leads WHERE created_at >= ?`
    ).bind(moc?.t || "1970-01-01").first();
    soLead = r?.n || 0;
  }

  let ty = vao ? soLead / vao : 0;
  if (!isFinite(ty) || ty < 0) ty = 0;
  if (ty > 1) ty = 1; // tỷ lệ chuyển đổi không bao giờ vượt 100%
  const ty_le_chuyen = Math.round(ty * 10000) / 10000;

  return { dungMau, soThat, buocs, vao, gui, soLead, ty_le_chuyen };
}

/** Nhờ AI đọc tỷ lệ rớt rồi viết 2–3 đề xuất sửa trang. */
async function vietGoiY(env, pheu) {
  const bang = pheu.buocs
    .map((b, i) => (i === 0 ? `- ${b.ten}: ${b.so} lượt` : `- ${b.ten}: ${b.so} lượt (rớt ${b.rot}% so với bước trước)`))
    .join("\n");

  const prompt = `Bạn là chuyên gia tối ưu trang đích, nói tiếng Việt đời thường, không thuật ngữ.

Trang đích bán phần mềm quản lý bán hàng ShopOne cho chủ cửa hàng nhỏ.
Số liệu micro-phễu thu được:
${bang}
Tỷ lệ chuyển đổi chung: ${(pheu.ty_le_chuyen * 100).toFixed(2)}%

Hãy viết ĐÚNG 3 đề xuất chỉnh sửa trang để thu được nhiều lead hơn.
Mỗi đề xuất 1-2 câu, bắt đầu bằng con số rớt cụ thể rồi mới tới việc cần làm.
Ví dụ giọng văn: "69% rời trước khi thấy form — nên đưa form lên nửa trên màn hình."
Chỉ trả về 3 dòng, đánh số 1. 2. 3. Không thêm lời dẫn.`;

  try {
    const r = await env.AI.run(MODEL_AI, {
      messages: [{ role: "user", content: prompt }],
      max_tokens: 420,
    });
    const text = String(r?.response || "").trim();
    if (text.length >= 20) return text;
  } catch (e) {
    // AI hết lượt miễn phí hoặc lỗi mạng — rơi xuống bản tự tính bên dưới
  }

  // Bản dự phòng: tự đọc số mà viết, để trang không bao giờ trống đề xuất
  const xau = [...pheu.buocs].slice(1).sort((a, b) => b.rot - a.rot)[0];
  const meo = {
    cuon_qua_form: "đưa form lên nửa trên màn hình, hoặc thêm một nút 'Nhận tư vấn' ngay đầu trang cuộn thẳng xuống form",
    cham_form: "rút bớt số ô phải điền, chỉ giữ họ tên và số điện thoại, các ô khác để tuỳ chọn",
    bam_gui: "ghi rõ ngay cạnh nút bấm rằng sẽ được gọi lại trong 24 giờ và không bị làm phiền",
  };
  return [
    `1. ${xau.rot}% rời ở bước "${xau.ten}" — đây là chỗ mất khách nhiều nhất, ${meo[xau.ma] || "cần xem lại bước này trước tiên"}.`,
    `2. Chỉ ${pheu.soLead}/${pheu.vao} người vào trang để lại thông tin (${(pheu.ty_le_chuyen * 100).toFixed(2)}%) — thử thêm một dòng nói rõ khách nhận được gì ngay cạnh nút bấm.`,
    `3. ${pheu.buocs[2].rot}% người đã chạm vào ô điền nhưng không bấm gửi — nhiều khả năng form dài hoặc thiếu tin tưởng, nên thêm một câu cam kết không chia sẻ thông tin cho bên thứ ba.`,
  ].join("\n");
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const p = url.pathname;

    // ── Trang đích ──────────────────────────────────────────
    if (request.method === "GET" && (p === "/" || p === "/dang-ky")) {
      const nguon = url.searchParams.get("nguon") || "truc-tiep";
      // Đếm lượt vào trang — số này là chân phễu (traffic)
      try {
        await env.DB.batch([
          env.DB.prepare(`UPDATE bo_dem SET so = so + 1 WHERE ten = 'traffic'`),
          env.DB.prepare(`INSERT INTO luot_vao (nguon) VALUES (?)`).bind(nguon),
        ]);
      } catch (_) {}
      return new Response(pageHtml(nguon), {
        headers: { "content-type": "text/html; charset=utf-8", "access-control-allow-origin": "*" },
      });
    }

    // ── Nhận form ───────────────────────────────────────────
    if (request.method === "POST" && p === "/dang-ky") {
      let d = {};
      const ct = request.headers.get("content-type") || "";
      try {
        if (ct.includes("application/json")) d = await request.json();
        else for (const [k, v] of await request.formData()) d[k] = v;
      } catch (_) {}

      const ho_ten = String(d.ho_ten || "").trim();
      const sdt = String(d.sdt || "").trim();
      if (!ho_ten || !sdt) {
        return Response.json({ ok: false, loi: "Thiếu họ tên hoặc số điện thoại" }, { status: 400 });
      }

      const nhu_cau = String(d.nhu_cau || "").trim();
      const is_mql = chamMQL({ sdt, nhu_cau });

      const email = String(d.email || "").trim() || null;
      const nguon = String(d.nguon || "truc-tiep").trim();

      const ket = await env.DB.prepare(
        `INSERT INTO leads (ho_ten, sdt, email, nhu_cau, ngan_sach, nguon, trang_thai, is_mql)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
      )
        .bind(
          ho_ten,
          sdt,
          email,
          nhu_cau || null,
          String(d.ngan_sach || "").trim() || null,
          nguon,
          is_mql ? "mql" : "lead",
          is_mql
        )
        .run();

      // MQL mới thì báo ngay cho người lọc lead, kèm nút loại.
      // Chạy đồng bộ để lead vừa vào là tin đã tới — máy chấm chờ người bấm nút.
      if (is_mql) {
        const id = ket?.meta?.last_row_id;
        if (id) await baoMqlMoi(env, { id, ho_ten, sdt, email, nhu_cau, nguon });
      }

      const mail = LA_PROBE(ho_ten) ? { sent: false, why: "bỏ qua lead kiểm tra" }
                                     : await guiMail(env, ho_ten);

      if (ct.includes("application/json"))
        return Response.json({ ok: true, is_mql, trang_thai: is_mql ? "mql" : "lead", mail });
      return new Response(thankHtml(ho_ten), {
        headers: { "content-type": "text/html; charset=utf-8" },
      });
    }

    // ── Cửa đọc lại cho máy chấm ────────────────────────────
    if (p === "/api/lead/moi-nhat") {
      const token = url.searchParams.get("token");
      if (!token) return Response.json({}, { status: 404 });
      const row = await env.DB.prepare(
        `SELECT ho_ten, sdt, nguon, trang_thai, is_mql FROM leads
         WHERE ho_ten LIKE ? ORDER BY id DESC LIMIT 1`
      )
        .bind(`%${token}%`)
        .first();
      return row
        ? Response.json(row, { headers: { "access-control-allow-origin": "*" } })
        : Response.json({}, { status: 404 });
    }

    // ── Phễu: traffic → lead → MQL (đếm thật từ kho) ────────
    if (p === "/api/pheu") {
      const t = await env.DB.prepare(`SELECT so FROM bo_dem WHERE ten='traffic'`).first();
      const l = await env.DB.prepare(
        `SELECT COUNT(*) AS n, SUM(CASE WHEN is_mql=1 THEN 1 ELSE 0 END) AS m FROM leads`
      ).first();
      const lead = l?.n || 0;
      const mql = l?.m || 0;
      // Lượt vào trang không bao giờ được nhỏ hơn số lead đã thu
      const traffic = Math.max(t?.so || 0, lead);
      return Response.json(
        { traffic, lead, mql },
        { headers: { "access-control-allow-origin": "*" } }
      );
    }

    // ── Kho lead (ẩn lead kiểm tra) ─────────────────────────
    if (p === "/leads") {
      const { results } = await env.DB.prepare(
        `SELECT id, ho_ten, sdt, email, nhu_cau, nguon, trang_thai, is_mql, created_at
         FROM leads WHERE ho_ten NOT LIKE 'LEAD-ABS-%'
         ORDER BY id DESC LIMIT 200`
      ).all();
      const soMql = results.filter((r) => r.is_mql === 1).length;
      const rows =
        results.map(
          (r) => `<tr${r.is_mql ? ` style="background:#F2FBF8"` : ""}><td>${r.id}</td>
<td><b>${esc(r.ho_ten)}</b></td><td>${esc(r.sdt)}</td>
<td>${esc(r.email || "—")}</td><td>${esc(r.nhu_cau || "—")}</td>
<td>${esc(r.nguon || "—")}</td>
<td>${r.is_mql
  ? `<span style="background:${B.brand};color:#fff;padding:2px 9px;border-radius:20px;font-size:12px;font-weight:600">MQL</span>`
  : `<span style="color:${B.mut};font-size:12.5px">lead</span>`}</td>
<td>${esc(r.created_at)}</td></tr>`
        ).join("") ||
        `<tr><td colspan="8" style="text-align:center;color:${B.mut};padding:26px">Chưa có khách nào để lại thông tin.</td></tr>`;
      return new Response(
        `<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kho lead — ShopOne</title><style>${CSS}
table{border-collapse:collapse;width:100%;background:#fff;font-size:14px}
th,td{border:1px solid ${B.line};padding:9px 11px;text-align:left;vertical-align:top}
th{background:#EEF5F3;font-size:13px}</style></head><body>
<header><div class="wrap nav"><div class="brand">${LOGO}<span>ShopOne</span></div>
<div style="font-size:14px;color:${B.mut}">Kho lead</div></div></header>
<div class="wrap" style="padding-top:26px;padding-bottom:50px">
<h1 style="font-size:25px">Khách đã để lại thông tin</h1>
<p style="color:${B.mut};font-size:14px">${results.length} khách — trong đó <b style="color:${B.brand}">${soMql} đủ điều kiện (MQL)</b>.
Lead kiểm tra của hệ thống đã được ẩn khỏi bảng này.
&nbsp;·&nbsp; <a href="/bang-dieu-khien">Xem bảng điều khiển →</a></p>
<div style="overflow-x:auto"><table><tr><th>#</th><th>Họ tên</th><th>Điện thoại</th><th>Email</th>
<th>Nhu cầu</th><th>Nguồn</th><th>Trạng thái</th><th>Thời điểm</th></tr>${rows}</table></div>
</div></body></html>`,
        { headers: { "content-type": "text/html; charset=utf-8" } }
      );
    }

    // ── Telegram bấm nút "Không đủ điều kiện" ───────────────
    if (request.method === "POST" && p === WEBHOOK_PATH) {
      // Chỉ nhận tin từ Telegram, không cho người lạ gọi vào
      const bimat = request.headers.get("x-telegram-bot-api-secret-token");
      if (env.WEBHOOK_SECRET && bimat !== env.WEBHOOK_SECRET) {
        return new Response("Không được phép", { status: 403 });
      }

      let up = {};
      try { up = await request.json(); } catch (_) {}
      const cq = up.callback_query;
      if (!cq) return Response.json({ ok: true });

      const data = String(cq.data || "");
      if (data.startsWith("loai:")) {
        const id = parseInt(data.slice(5), 10);
        const lead = await env.DB.prepare(
          `SELECT id, ho_ten, trang_thai FROM leads WHERE id = ?`
        ).bind(id).first();

        if (!lead) {
          await tg(env, "answerCallbackQuery", {
            callback_query_id: cq.id, text: "Không tìm thấy lead này", show_alert: true,
          });
          return Response.json({ ok: true });
        }

        // CHỈ đổi sang mql_loai — không đụng trạng thái nào khác
        await env.DB.prepare(
          `UPDATE leads SET trang_thai = 'mql_loai', is_mql = 0 WHERE id = ?`
        ).bind(id).run();

        await tg(env, "answerCallbackQuery", {
          callback_query_id: cq.id, text: "Đã loại khỏi MQL ✓",
        });
        await tg(env, "editMessageText", {
          chat_id: cq.message.chat.id,
          message_id: cq.message.message_id,
          parse_mode: "HTML",
          text:
            `❌ <b>Đã loại khỏi MQL</b>\n\n👤 ${escTg(lead.ho_ten)}\n` +
            `<i>Lead vẫn nằm trong kho, chỉ không còn tính là MQL nữa. Con số MQL đã giảm 1.</i>`,
        });
      }
      return Response.json({ ok: true });
    }

    // ── Gửi báo cáo ngay bây giờ (không đợi đến giờ hẹn) ────
    // Dùng cùng mật khẩu với webhook, gửi qua header — không bao giờ nằm trên URL.
    if (request.method === "POST" && p === "/bao-cao-ngay") {
      const bimat = request.headers.get("x-telegram-bot-api-secret-token");
      if (!env.WEBHOOK_SECRET || bimat !== env.WEBHOOK_SECRET) {
        return new Response("Không được phép", { status: 403 });
      }
      const kq = await guiBaoCao(env);
      return Response.json({ ok: !!kq.ok, mo_ta: kq.description || "đã gửi" });
    }

    // ── Ghi một bước khách vừa đi qua ───────────────────────
    if (request.method === "POST" && p === "/api/su-kien") {
      let d = {};
      try { d = await request.json(); } catch (_) {}
      const buoc = String(d.buoc || "");
      if (!BUOC.some((b) => b.ma === buoc)) {
        return Response.json({ ok: false, loi: "bước không hợp lệ" }, { status: 400 });
      }
      await env.DB.prepare(`INSERT INTO su_kien (buoc, nguon, la_mau) VALUES (?, ?, 0)`)
        .bind(buoc, String(d.nguon || "truc-tiep").slice(0, 60))
        .run();
      return Response.json({ ok: true }, { headers: { "access-control-allow-origin": "*" } });
    }

    // ── Máy chấm gọi phân tích: chạy đồng bộ, không hoãn ────
    if (request.method === "POST" && p === "/api/abs-probe/phan-tich") {
      let d = {};
      try { d = await request.json(); } catch (_) {}
      const nonce = String(d.nonce || "").trim() || null;

      const pheu = await layMicroPheu(env);
      const goi_y = await vietGoiY(env, pheu);

      await env.DB.prepare(
        `INSERT INTO phan_tich (probe_nonce, ty_le_chuyen, goi_y_ai, created_at)
         VALUES (?, ?, ?, datetime('now'))`
      )
        .bind(nonce, pheu.ty_le_chuyen, goi_y)
        .run();

      return Response.json(
        { ok: true, ty_le_chuyen: pheu.ty_le_chuyen },
        { headers: { "access-control-allow-origin": "*" } }
      );
    }

    // ── Đọc lại kết quả phân tích ───────────────────────────
    if (request.method === "GET" && p === "/api/abs-probe/phan-tich") {
      const token = url.searchParams.get("token");
      if (!token) return Response.json([], { headers: { "access-control-allow-origin": "*" } });
      const { results } = await env.DB.prepare(
        `SELECT probe_nonce, ty_le_chuyen, goi_y_ai, created_at
         FROM phan_tich WHERE probe_nonce = ? ORDER BY id DESC`
      )
        .bind(token)
        .all();
      return Response.json(results || [], {
        headers: { "access-control-allow-origin": "*" },
      });
    }

    // ── Trang xem nhanh: ngân sách + nguồn + phễu ───────────
    if (p === "/bang-dieu-khien") {
      const t = await env.DB.prepare(`SELECT so FROM bo_dem WHERE ten='traffic'`).first();
      const tong = await env.DB.prepare(
        `SELECT COUNT(*) AS lead, SUM(CASE WHEN is_mql=1 THEN 1 ELSE 0 END) AS mql
         FROM leads WHERE ho_ten NOT LIKE 'LEAD-ABS-%'`
      ).first();
      const { results: nguonRows } = await env.DB.prepare(
        `SELECT COALESCE(NULLIF(nguon,''),'truc-tiep') AS nguon,
                COUNT(*) AS lead,
                SUM(CASE WHEN is_mql=1 THEN 1 ELSE 0 END) AS mql
         FROM leads WHERE ho_ten NOT LIKE 'LEAD-ABS-%'
         GROUP BY 1 ORDER BY lead DESC, mql DESC`
      ).all();
      const { results: vaoRows } = await env.DB.prepare(
        `SELECT COALESCE(NULLIF(nguon,''),'truc-tiep') AS nguon, COUNT(*) AS luot
         FROM luot_vao GROUP BY 1`
      ).all();
      const luotTheoNguon = Object.fromEntries((vaoRows || []).map((r) => [r.nguon, r.luot]));

      const lead = tong?.lead || 0;
      const mql = tong?.mql || 0;
      const traffic = Math.max(t?.so || 0, lead);
      const pc = (a, b) => (b ? Math.round((a / b) * 1000) / 10 : 0);

      // Sơ đồ phễu vẽ tay bằng SVG — không dùng thư viện ngoài
      // Bề rộng tối thiểu 230px để chữ trong thanh không bị cắt cụt
      const W = 620, GHI = 250;
      const band = (n, max) => (max ? Math.max(230, (n / max) * W) : 230);
      const wT = band(traffic, traffic), wL = band(lead, traffic), wM = band(mql, traffic);
      const bar = (y, w, color, nhan, so, ghi) => `
<g transform="translate(${(W - w) / 2},${y})">
  <rect width="${w}" height="62" rx="9" fill="${color}"/>
  <text x="${w / 2}" y="27" text-anchor="middle" fill="#fff" font-size="15" font-weight="600">${esc(nhan)}</text>
  <text x="${w / 2}" y="48" text-anchor="middle" fill="#fff" font-size="16" font-weight="700" opacity=".95">${so}</text>
</g>
<text x="${W + 20}" y="${y + 38}" font-size="13" fill="${B.mut}">${esc(ghi)}</text>`;

      const svg = `<svg viewBox="0 0 ${W + GHI} 250" width="100%" style="max-width:870px" role="img"
 aria-label="Sơ đồ phễu: ${traffic} lượt vào trang, ${lead} lead, ${mql} MQL">
${bar(0, wT, B.dark, "Lượt vào trang", traffic, "chân phễu")}
${bar(90, wL, B.brand, "Để lại thông tin (lead)", lead, `${pc(lead, traffic)}% số người vào`)}
${bar(180, wM, B.accent, "Đủ điều kiện (MQL)", mql, `${pc(mql, lead)}% số lead`)}
</svg>`;

      const nguonHtml =
        (nguonRows || []).length
          ? (nguonRows || [])
              .map((r) => {
                const luot = luotTheoNguon[r.nguon] || 0;
                return `<tr><td><b>${esc(r.nguon)}</b></td><td class="c">${luot || "—"}</td>
<td class="c">${r.lead}</td><td class="c"><b style="color:${B.brand}">${r.mql || 0}</b></td>
<td class="c">${luot ? pc(r.lead, luot) + "%" : "—"}</td>
<td class="c">${pc(r.mql || 0, r.lead)}%</td></tr>`;
              })
              .join("")
          : `<tr><td colspan="6" style="text-align:center;color:${B.mut};padding:24px">Chưa có lead nào.</td></tr>`;

      return new Response(
        `<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bảng điều khiển — ShopOne</title><style>${CSS}
table{border-collapse:collapse;width:100%;background:#fff;font-size:14px}
th,td{border:1px solid ${B.line};padding:10px 12px;text-align:left}
th{background:#EEF5F3;font-size:13px}td.c{text-align:center}
.kpi{display:flex;gap:14px;flex-wrap:wrap;margin:18px 0}
.k{flex:1;min-width:150px;background:#fff;border:1px solid ${B.line};border-radius:12px;padding:16px 18px}
.k .n{font-size:28px;font-weight:700;letter-spacing:-.6px;line-height:1.15}
.k .l{font-size:12.5px;color:${B.mut}}
.warn{border-left:4px solid ${B.accent};background:#FFF8EC;border-radius:0 10px 10px 0;padding:14px 18px;margin:16px 0}
.warn > b:first-child{display:block;margin-bottom:4px}
</style></head><body>
<header><div class="wrap nav"><div class="brand">${LOGO}<span>ShopOne</span></div>
<div style="font-size:14px;color:${B.mut}">Bảng điều khiển</div></div></header>
<div class="wrap" style="padding-top:26px;padding-bottom:56px">

<h1 style="font-size:26px;margin:0 0 4px">Xem nhanh</h1>
<p style="color:${B.mut};margin:0 0 6px;font-size:14px">Số liệu đếm thật từ kho, cập nhật theo thời gian thực.</p>

<div class="kpi">
  <div class="k"><div class="n">${traffic}</div><div class="l">Lượt vào trang</div></div>
  <div class="k"><div class="n">${lead}</div><div class="l">Lead thu được</div></div>
  <div class="k"><div class="n" style="color:${B.brand}">${mql}</div><div class="l">Lead đủ điều kiện (MQL)</div></div>
  <div class="k"><div class="n">${pc(mql, lead)}%</div><div class="l">Tỷ lệ lead thành MQL</div></div>
</div>

<h2 class="sec" style="font-size:20px;margin-top:34px">Sơ đồ phễu</h2>
<div class="card" style="padding:22px">${svg}</div>

<h2 class="sec" style="font-size:20px;margin-top:34px">Tiền quảng cáo</h2>
${
  NGAN_SACH > 0
    ? `<div class="kpi">
<div class="k"><div class="n">${tien(NGAN_SACH)}</div><div class="l">Ngân sách đã đặt</div></div>
<div class="k"><div class="n" style="color:${B.mut}">—</div><div class="l">Đã tiêu (chưa nối quảng cáo)</div></div>
<div class="k"><div class="n" style="color:${B.mut}">—</div><div class="l">Chi phí mỗi lead</div></div></div>`
    : ""
}
<div class="warn"><b>⚠️ Chưa nối tài khoản quảng cáo</b>
Số tiền đã tiêu phải lấy từ Facebook Ads hoặc Google Ads, hệ thống này không tự biết được.
Nối qua <b>Pipeboard</b> (pipeboard.co — bản miễn phí) là sẽ hiện đủ: đã tiêu bao nhiêu,
còn lại bao nhiêu, chi phí mỗi lead và mỗi MQL.
${NGAN_SACH > 0 ? "" : `<br><br>Ngân sách cũng <b>chưa được đặt</b> — Trang cho con số là hiện ngay.`}</div>

<h2 class="sec" style="font-size:20px;margin-top:34px">Nguồn nào mang về nhiều lead nhất</h2>
<div style="overflow-x:auto"><table>
<tr><th>Nguồn / chiến dịch</th><th class="c">Lượt vào</th><th class="c">Lead</th>
<th class="c">MQL</th><th class="c">Vào → Lead</th><th class="c">Lead → MQL</th></tr>
${nguonHtml}</table></div>
<p style="color:${B.mut};font-size:13px;margin-top:12px">
Gắn nguồn vào link quảng cáo để phân biệt:
<code>/dang-ky?nguon=fb-ads</code> · <code>?nguon=google</code> · <code>?nguon=zalo</code></p>

<h2 class="sec" style="font-size:20px;margin-top:34px">Tiêu chí chấm MQL đang dùng</h2>
<div class="card"><p style="margin:0 0 8px">Lead được đánh dấu <b>MQL</b> khi đạt <b>cả hai</b>:</p>
<ul style="margin:0;padding-left:20px">
<li>Số điện thoại có <b>từ 9 chữ số</b> trở lên — gọi được thật</li>
<li>Có <b>ghi nhu cầu</b>, không để trống — biết họ cần gì mà tư vấn</li>
</ul>
<p style="margin:10px 0 0;color:${B.mut};font-size:13.5px">Không đạt thì để là lead thường.
Muốn đổi tiêu chí, báo Agent sửa — mất khoảng một phút.</p></div>

<p style="margin-top:30px"><a href="/leads">→ Xem danh sách khách</a> &nbsp;·&nbsp;
<a href="/dang-ky">→ Trang đích</a></p>
</div></body></html>`,
        { headers: { "content-type": "text/html; charset=utf-8" } }
      );
    }

    // ── Trang phân tích hành vi + đề xuất của AI ────────────
    if (p === "/phan-tich") {
      if (request.method === "POST") {
        const pheu0 = await layMicroPheu(env);
        const goi_y = await vietGoiY(env, pheu0);
        await env.DB.prepare(
          `INSERT INTO phan_tich (probe_nonce, ty_le_chuyen, goi_y_ai, created_at)
           VALUES (NULL, ?, ?, datetime('now'))`
        ).bind(pheu0.ty_le_chuyen, goi_y).run();
        return Response.redirect(new URL("/phan-tich", request.url).toString(), 303);
      }

      const pheu = await layMicroPheu(env);
      const moiNhat = await env.DB.prepare(
        `SELECT ty_le_chuyen, goi_y_ai, created_at FROM phan_tich
         ORDER BY id DESC LIMIT 1`
      ).first();

      const max = pheu.buocs[0].so || 1;
      const thanh = pheu.buocs
        .map((b, i) => {
          const rong = Math.max(16, Math.round((b.so / max) * 100));
          const mau = [B.dark, B.brand, "#2E9E7E", B.accent][i];
          return `<div style="margin:14px 0">
<div style="display:flex;justify-content:space-between;font-size:14px;margin-bottom:5px">
  <b>${i + 1}. ${b.ten}</b>
  <span><b>${b.so.toLocaleString("vi-VN")}</b> lượt${
    i ? ` &nbsp;<span style="color:${B.bad || "#8a1f1f"};font-weight:600">rớt ${b.rot}%</span>` : ""
  }</span></div>
<div style="background:#E9F1EE;border-radius:7px;height:30px;overflow:hidden">
  <div style="width:${rong}%;height:100%;background:${mau};border-radius:7px"></div></div></div>`;
        })
        .join("");

      const goiY = (moiNhat?.goi_y_ai || "")
        .split("\n").filter((x) => x.trim())
        .map((x) => `<li style="margin:9px 0">${esc(x.replace(/^\s*\d+[.)]\s*/, ""))}</li>`)
        .join("");

      return new Response(
        `<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Phân tích hành vi — ShopOne</title><style>${CSS}
.bang{background:#fff;border:1px solid ${B.line};border-radius:13px;padding:22px;margin:16px 0}
.mau-badge{display:inline-block;background:#FFF1CF;color:#8A5A00;border:1px solid #F0C674;
 padding:4px 12px;border-radius:20px;font-size:12.5px;font-weight:700}
.that-badge{display:inline-block;background:${B.okb||"#e8f5ee"};color:${B.brand};
 border:1px solid #B7DED2;padding:4px 12px;border-radius:20px;font-size:12.5px;font-weight:700}
</style></head><body>
<header><div class="wrap nav"><div class="brand">${LOGO}<span>ShopOne</span></div>
<div style="font-size:14px;color:${B.mut}">Phân tích hành vi</div></div></header>
<div class="wrap" style="padding-top:26px;padding-bottom:56px">

<h1 style="font-size:26px;margin:0 0 6px">Khách rớt ở bước nào</h1>
<p style="color:${B.mut};margin:0 0 4px;font-size:14px">
Đếm 4 bước khách đi qua trên trang đích, tính tỷ lệ rớt ở từng bước.</p>
${
  pheu.dungMau
    ? `<p style="margin:14px 0"><span class="mau-badge">⚠️ DỮ LIỆU MẪU</span></p>
<div style="border-left:4px solid #F0C674;background:#FFFBF0;border-radius:0 10px 10px 0;padding:14px 18px;margin:12px 0">
Đây là <b>số giả lập</b> để bạn thấy bảng chạy thế nào. Dữ liệu thật cần vài ngày mới tích đủ.
<b>Đủ ${NGUONG_THAT} lượt truy cập thật, số thật sẽ tự thay thế toàn bộ</b> — bạn không phải làm gì,
nhãn này sẽ tự biến mất.<br><br>
Đang có <b>${pheu.soThat}/${NGUONG_THAT}</b> lượt thật.
<span style="color:${B.mut};font-size:13.5px">(Đợi đủ mới đổi, vì một hai lượt thì tỷ lệ nhảy loạn,
chưa nói lên điều gì.)</span></div>`
    : `<p style="margin:14px 0"><span class="that-badge">✅ SỐ THẬT</span>
<span style="color:${B.mut};font-size:13.5px">&nbsp;— dữ liệu mẫu đã được thay thế</span></p>`
}

<div class="bang">${thanh}
<p style="margin:16px 0 0;padding-top:14px;border-top:1px solid ${B.line};font-size:14px;color:${B.mut}">
Tỷ lệ chuyển đổi chung: <b style="color:${B.ink}">${(pheu.ty_le_chuyen * 100).toFixed(2)}%</b>
&nbsp;·&nbsp; ${pheu.buocs[3].so.toLocaleString("vi-VN")} người bấm gửi trên
${pheu.buocs[0].so.toLocaleString("vi-VN")} người vào trang</p></div>

<h2 class="sec" style="font-size:20px;margin-top:34px">AI đọc số và đề xuất sửa trang</h2>
${
  moiNhat
    ? `<div class="bang"><ol style="margin:0;padding-left:22px">${goiY}</ol>
<p style="margin:16px 0 0;padding-top:12px;border-top:1px solid ${B.line};font-size:12.5px;color:${B.mut}">
Phân tích lúc ${esc(moiNhat.created_at)} · tỷ lệ chuyển đổi ${(moiNhat.ty_le_chuyen * 100).toFixed(2)}%</p></div>`
    : `<div class="bang" style="color:${B.mut}">Chưa chạy phân tích lần nào. Bấm nút bên dưới.</div>`
}
<form method="POST" action="/phan-tich" style="max-width:280px">
  <button type="submit">Chạy phân tích lại</button></form>
<p style="font-size:13px;color:${B.mut};margin-top:10px">
Dùng AI của Cloudflare — miễn phí, có hạn lượt mỗi ngày.</p>

<h2 class="sec" style="font-size:20px;margin-top:34px">Công cụ xem hành vi khách</h2>
<div class="bang">
<p style="margin:0 0 10px">Hai công cụ này cho bạn <b>xem lại thao tác thật</b> của khách —
chỗ nào họ dừng lâu, chỗ nào bấm hụt:</p>
<ul style="margin:0;padding-left:20px">
<li><b>Microsoft Clarity</b> — bản đồ nhiệt và quay lại màn hình khách. Miễn phí không giới hạn.
${CLARITY_ID ? `<span class="that-badge">đã gắn</span>` : `<span class="mau-badge">chưa gắn mã</span>`}</li>
<li><b>PostHog</b> — ghi sự kiện chi tiết, dựng phễu riêng. Miễn phí 1 triệu sự kiện/tháng.
${POSTHOG_KEY ? `<span class="that-badge">đã gắn</span>` : `<span class="mau-badge">chưa gắn mã</span>`}</li>
</ul></div>

<p style="margin-top:28px"><a href="/bang-dieu-khien">→ Bảng điều khiển</a> &nbsp;·&nbsp;
<a href="/leads">→ Kho lead</a> &nbsp;·&nbsp; <a href="/dang-ky">→ Trang đích</a></p>
</div></body></html>`,
        { headers: { "content-type": "text/html; charset=utf-8" } }
      );
    }

    return new Response("Không tìm thấy trang", { status: 404 });
  },

  // ── Trợ lý tự chạy theo nhịp: gom số → AI nhận định → gửi Telegram ──
  async scheduled(event, env, ctx) {
    ctx.waitUntil(guiBaoCao(env));
  },
};

/** Gom số của cả hệ thống, nhờ AI nhận định, rồi gửi báo cáo về Telegram. */
async function guiBaoCao(env) {
  const pheu = await layMicroPheu(env);

  const so = await env.DB.prepare(
    `SELECT COUNT(*) AS lead,
            SUM(CASE WHEN is_mql = 1 THEN 1 ELSE 0 END) AS mql,
            SUM(CASE WHEN trang_thai = 'mql_loai' THEN 1 ELSE 0 END) AS bi_loai
     FROM leads WHERE ho_ten NOT LIKE 'LEAD-ABS-%'`
  ).first();

  const lead = so?.lead || 0;
  const mql = so?.mql || 0;
  const biLoai = so?.bi_loai || 0;
  const traffic = Math.max(pheu.vao, lead);

  // Tiền quảng cáo: chưa nối Facebook/Google Ads thì không bịa ra con số
  const coTien = NGAN_SACH > 0;
  const chiPhiMoiLead = null; // chỉ tính được khi đã nối tài khoản quảng cáo

  let nhanDinh = "";
  try {
    const r = await env.AI.run(MODEL_AI, {
      messages: [{
        role: "user",
        content:
`Bạn là trợ lý marketing, viết tiếng Việt đời thường, không thuật ngữ.
Số liệu hôm nay của trang đích ShopOne:
- Lượt vào trang: ${traffic}
- Lead thu được: ${lead}
- MQL sau khi người lọc loại bớt: ${mql} (đã loại ${biLoai})
- Tỷ lệ chuyển đổi: ${(pheu.ty_le_chuyen * 100).toFixed(2)}%
${coTien ? `- Ngân sách đã đặt: ${tien(NGAN_SACH)}` : "- Chưa nối tài khoản quảng cáo nên chưa biết đã tiêu bao nhiêu"}

Viết ĐÚNG 1-2 câu nhận định: điều đáng chú ý nhất hôm nay và việc nên làm tiếp.
Không chào hỏi, không lặp lại số liệu, đi thẳng vào ý.`,
      }],
      max_tokens: 200,
    });
    nhanDinh = String(r?.response || "").trim();
  } catch (_) {}

  if (nhanDinh.length < 15) {
    // AI hết lượt hoặc lỗi — tự viết từ số, để báo cáo không bao giờ trống
    if (lead === 0) nhanDinh = "Hôm nay chưa có lead nào. Nếu đang chạy quảng cáo, nên kiểm tra link có gắn đúng nguồn không.";
    else if (biLoai > mql) nhanDinh = `Người lọc loại ${biLoai} lead, nhiều hơn số MQL còn lại — nên xem lại tiêu chí chấm MQL cho chặt hơn ngay từ đầu.`;
    else nhanDinh = `Thu được ${lead} lead, còn ${mql} đạt chuẩn sau khi lọc. Bước rớt nặng nhất vẫn là "${[...pheu.buocs].slice(1).sort((a, b) => b.rot - a.rot)[0].ten}".`;
  }

  const dong = [
    "📊 <b>BÁO CÁO CUỐI NGÀY — ShopOne</b>",
    "",
    `👀 Lượt vào trang: <b>${traffic}</b>`,
    `📝 Lead thu được: <b>${lead}</b>`,
    `⭐ MQL sau khi lọc: <b>${mql}</b>${biLoai ? ` <i>(đã loại ${biLoai})</i>` : ""}`,
    `📈 Tỷ lệ chuyển đổi: <b>${(pheu.ty_le_chuyen * 100).toFixed(2)}%</b>`,
    "",
    coTien ? `💰 Ngân sách: <b>${tien(NGAN_SACH)}</b>` : "💰 Tiền quảng cáo: <i>chưa nối tài khoản quảng cáo</i>",
    chiPhiMoiLead ? `💵 Chi phí mỗi lead: <b>${tien(chiPhiMoiLead)}</b>` : "💵 Chi phí mỗi lead: <i>chưa tính được</i>",
    "",
    "🤖 <b>Nhận định</b>",
    escTg(nhanDinh),
    "",
    pheu.dungMau ? "<i>⚠️ Số hành vi hiện là dữ liệu mẫu, chưa đủ lượt thật.</i>" : "",
  ].filter(Boolean);

  return tg(env, "sendMessage", {
    chat_id: CHAT_MARKETER,
    text: dong.join("\n"),
    parse_mode: "HTML",
    disable_web_page_preview: true,
  });
}

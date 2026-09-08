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
const GA_ID = "";

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

      await env.DB.prepare(
        `INSERT INTO leads (ho_ten, sdt, email, nhu_cau, ngan_sach, nguon, trang_thai, is_mql)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
      )
        .bind(
          ho_ten,
          sdt,
          String(d.email || "").trim() || null,
          nhu_cau || null,
          String(d.ngan_sach || "").trim() || null,
          String(d.nguon || "truc-tiep").trim(),
          is_mql ? "mql" : "lead",
          is_mql
        )
        .run();

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

    return new Response("Không tìm thấy trang", { status: 404 });
  },
};

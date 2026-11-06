// Ghép dữ liệu vào bộ khung web vệ tinh (đã chạy thật ở AIG, VIB, Techcombank, Sun Life).
// Luật WordPress.com gói Free: chỉ style inline, màu hex (không rgba), flex-wrap thay media query,
// đầu/chân trang bằng <div>, bọc trong group full-width blockGap 0.
const SL_Gen = (() => {
  const F = "font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;";
  const EXT = ' target="_blank" rel="noopener"';
  const esc = (s) => String(s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  // nối 2 chữ cuối để không rớt 1 chữ lẻ xuống dòng
  const nb = (s) => { s = esc(s).trim(); const i = s.lastIndexOf(" "); return i > 0 ? s.slice(0, i) + "&nbsp;" + s.slice(i + 1) : s; };
  const rgb = (h) => { h = h.replace("#", ""); if (h.length === 3) h = h.split("").map((c) => c + c).join(""); return [0, 2, 4].map((i) => parseInt(h.substr(i, 2), 16)); };
  const lum = (h) => { const [r, g, b] = rgb(h).map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  const up = (h) => "#" + rgb(h).map((x) => x.toString(16).padStart(2, "0")).join("").toUpperCase();

  function palette(d) {
    let [c1, c2] = [up(d.color1 || "#1A1A1A"), up(d.color2 || d.color1 || "#1A1A1A")];
    const K = lum(c1) <= lum(c2) ? c1 : c2;          // màu đậm: nền mở đầu, tiêu đề, chân trang
    const A = K === c1 ? c2 : c1;                     // màu còn lại: nút bấm, chấm phá
    const darkK = lum(K) < 0.2;
    const ink = darkK ? K : "#1A1A1A";                // màu chữ chính trên nền trắng
    const onK = lum(K) > 0.45 ? "#1A1A1A" : "#FFFFFF";
    const onA = lum(A) > 0.45 ? (darkK ? K : "#1A1A1A") : "#FFFFFF";
    const eyebrowLight = lum(A) > 0.55 ? ink : A;     // chữ nhỏ trên nền trắng: màu phụ nếu đủ đậm
    const eyebrowDark = lum(A) < 0.2 && onK === "#FFFFFF" ? "#FFFFFF" : A;
    return { K, A, ink, onK, onA, eyebrowLight, eyebrowDark, muted: ink + "B3", line: ink + "1F", soft: K + "0D" };
  }

  function build(d) {
    const P = palette(d);
    const M = d.official || "#";
    const logo = (w, extra = "") => d.logo ? `<img src="${esc(d.logo)}" alt="Logo ${esc(d.brand)}" width="${w}" style="width:${w}px;max-height:64px;height:auto;display:block;object-fit:contain;${extra}" />` : `<span style="font-size:22px;font-weight:800;color:${P.ink};">${esc(d.brand)}</span>`;
    const cards = (d.cards || []).filter((c) => c.title);
    const hasContact = (d.phones || []).length || (d.emails || []).length || (d.addresses || []).length;

    const header = (home) => {
      const pre = home ? "" : "/";
      const a = (h, t) => `<a href="${h}" style="color:${P.ink};text-decoration:none;padding:4px 0;">${t}</a>`;
      return `<div style="background:#ffffff;border-bottom:4px solid ${P.A};padding:14px 20px;${F}">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px 28px;">
<a href="/" style="display:flex;align-items:center;text-decoration:none;">${logo(170)}</a>
<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-start;gap:6px 24px;font-size:15px;font-weight:600;">
${a(pre + "#gioi-thieu", "Giới thiệu")}
${cards.length ? a(pre + "#san-pham", "Sản phẩm") : ""}
${a("/tin-tuc/", "Tin tức")}
${a(pre + "#lien-he", "Liên hệ")}
<a href="${esc(M)}"${EXT} style="background:${P.A};color:${P.onA};text-decoration:none;padding:9px 18px;border-radius:999px;font-weight:700;">Website chính thức</a>
</div>
</div>
</div>
`;
    };

    const footer = () => {
      const links = (d.footerLinks || []).filter((l) => l.text).slice(0, 6);
      const col = links.length ? `<div style="flex:1 1 180px;min-width:0;">
<p style="margin:0 0 14px;color:${P.ink};font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;">Khám phá</p>
${links.map((l) => `<p style="margin:0 0 8px;"><a href="${esc(l.href || M)}"${EXT} style="color:${P.muted};text-decoration:none;">${esc(l.text)}</a></p>`).join("\n")}
</div>` : "";
      const c = [];
      (d.addresses || []).forEach((x) => c.push(`<p style="margin:0 0 8px;">${esc(x)}</p>`));
      (d.phones || []).forEach((x) => c.push(`<p style="margin:0 0 8px;"><strong style="color:${P.ink};">Điện thoại:</strong> <a href="tel:${esc(x.replace(/[^\d+]/g, ""))}" style="color:${P.muted};text-decoration:none;">${esc(x)}</a></p>`));
      (d.emails || []).forEach((x) => c.push(`<p style="margin:0 0 8px;"><strong style="color:${P.ink};">Email:</strong> <a href="mailto:${esc(x)}" style="color:${P.muted};text-decoration:none;">${esc(x)}</a></p>`));
      const contactCol = c.length ? `<div style="flex:1.3 1 260px;min-width:0;">
<p style="margin:0 0 14px;color:${P.ink};font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;">Liên hệ</p>
${c.join("\n")}
</div>` : "";
      return `<div style="background:${P.soft};border-top:4px solid ${P.A};color:${P.muted};padding:52px 20px 0;font-size:15px;line-height:1.65;${F}">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;gap:32px 44px;padding-bottom:36px;">
<div style="flex:1.6 1 300px;min-width:0;">
<div style="margin-bottom:18px;">${logo(160)}</div>
<p style="margin:0 0 12px;">${esc(d.footerAbout || d.lead)}</p>
<p style="margin:0;">Website chính thức: <a href="${esc(M)}"${EXT} style="color:${P.ink};text-decoration:none;font-weight:800;border-bottom:2px solid ${P.A};">${esc((M.replace(/^https?:\/\//, "").replace(/\/$/, "")))}</a></p>
</div>
${col}
${contactCol}
</div>
<div style="max-width:1200px;margin:0 auto;border-top:1px solid ${P.line};padding:18px 0 22px;display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 24px;font-size:14px;color:${P.muted};">
<p style="margin:0;">© ${new Date().getFullYear()} ${esc(d.brand)}</p>
<p style="margin:0;"><a href="${esc(M)}"${EXT} style="color:${P.ink};text-decoration:none;font-weight:700;">Truy cập website chính thức →</a></p>
</div>
</div>
`;
    };

    const eyebrow = (t, center, dark) => `<p style="margin:0 0 10px;color:${dark ? P.eyebrowDark : P.eyebrowLight};font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;${center ? "text-align:center;" : ""}">${esc(t)}</p>`;
    const h2 = (t, center, mb, color) => `<h2 style="margin:0 0 ${mb}px;color:${color || P.ink};font-size:clamp(26px,3.4vw,38px);line-height:1.2;font-weight:800;max-width:780px;${center ? "text-align:center;margin-left:auto;margin-right:auto;" : ""}">${nb(t)}</h2>`;
    const btn = (t, bg, color, href) => `<a href="${esc(href || M)}"${EXT} style="display:inline-block;background:${bg};color:${color};text-decoration:none;font-weight:800;padding:13px 26px;border-radius:999px;">${esc(t)}</a>`;
    const section = (inner, bg, id) => `<section${id ? ` id="${id}"` : ""} style="padding:clamp(56px,8vw,92px) 20px;background:${bg};">
<div style="max-width:1200px;margin:0 auto;">
${inner}
</div>
</section>
`;
    const paras = (t, color) => String(t || "").split(/\n+/).map((x) => x.trim()).filter(Boolean)
      .map((x) => `<p style="margin:0 0 16px;color:${color};font-size:17px;">${esc(x)}</p>`).join("\n");

    const hero = `<section style="background:${P.K};color:${P.onK};padding:clamp(44px,7vw,84px) 20px;">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:40px;">
<div style="flex:1 1 420px;min-width:0;">
${d.eyebrow ? `<p style="display:inline-block;margin:0 0 18px;padding:6px 14px;border:1px solid ${P.A};border-radius:999px;color:${P.eyebrowDark};font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;">${esc(d.eyebrow)}</p>` : ""}
<h1 style="margin:0 0 18px;color:${P.onK};font-size:clamp(30px,4.6vw,50px);line-height:1.15;font-weight:800;">${nb(d.h1 || d.brand)}</h1>
${d.lead ? `<p style="margin:0 0 28px;font-size:clamp(16px,1.6vw,19px);color:${P.onK};opacity:.9;max-width:560px;">${nb(d.lead)}</p>` : ""}
<div style="display:flex;flex-wrap:wrap;gap:12px;">
${btn(d.ctaText || "Khám phá ngay", P.A, P.onA)}
<a href="#lien-he" style="border:1.5px solid ${P.onK};color:${P.onK};text-decoration:none;font-weight:700;padding:12px 26px;border-radius:999px;">Liên hệ</a>
</div>
</div>
${d.heroImg ? `<div style="flex:1 1 440px;min-width:0;">
<img src="${esc(d.heroImg)}" alt="${esc(d.brand)}" style="width:100%;height:auto;display:block;border-radius:16px;border-bottom:6px solid ${P.A};" />
</div>` : ""}
</div>
</section>
`;

    const about = section(`<div style="display:flex;flex-wrap:wrap;gap:40px;align-items:center;">
${d.aboutImg ? `<div style="flex:1 1 380px;min-width:0;">
<img src="${esc(d.aboutImg)}" alt="Giới thiệu ${esc(d.brand)}" style="width:100%;height:auto;display:block;border-radius:16px;" />
</div>` : ""}
<div style="flex:1.2 1 420px;min-width:0;">
${eyebrow("Giới thiệu")}
${h2(d.aboutTitle || "Về " + d.brand, false, 18)}
${paras(d.aboutText || d.description, P.muted)}
${btn("Xem thêm về " + d.brand, P.K, P.onK)}
</div>
</div>`, "#ffffff", "gioi-thieu");

    const products = cards.length ? section(`${eyebrow("Sản phẩm & dịch vụ", true)}
${h2(d.cardsTitle || "Sản phẩm và dịch vụ nổi bật", true, 36)}
<div style="display:flex;flex-wrap:wrap;gap:20px;">
${cards.map((c, i) => `<a href="${esc(c.href || M)}"${EXT} style="flex:1 1 300px;min-width:0;display:flex;flex-direction:column;gap:10px;text-decoration:none;background:#ffffff;border-radius:16px;padding:26px 24px;border-top:5px solid ${i % 2 ? P.K : P.A};box-shadow:0 6px 20px ${P.ink}14;">
<h3 style="margin:0;color:${P.ink};font-size:20px;line-height:1.3;font-weight:800;">${nb(c.title)}</h3>
${c.text ? `<p style="margin:0;color:${P.muted};font-size:15px;flex:1 1 auto;">${esc(c.text)}</p>` : ""}
<span style="color:${P.ink};font-weight:800;font-size:15px;">Tìm hiểu →</span>
</a>`).join("\n")}
</div>`, P.soft, "san-pham") : "";

    const box = (title, lines) => `<div style="flex:1 1 240px;min-width:0;background:#ffffff;border-radius:14px;padding:22px 24px;color:${P.ink};font-size:15px;"><p style="margin:0 0 10px;font-weight:800;">${title}</p>${lines}</div>`;
    const contact = `<section id="lien-he" style="padding:clamp(56px,8vw,92px) 20px;background:#ffffff;">
<div style="max-width:1200px;margin:0 auto;background:${P.K};border-radius:20px;padding:clamp(32px,5vw,56px);display:flex;flex-wrap:wrap;gap:24px;align-items:center;">
<div style="flex:1.2 1 320px;min-width:0;">
${h2("Liên hệ " + d.brand, false, 14, P.onK)}
<p style="margin:0 0 22px;color:${P.onK};opacity:.9;font-size:17px;">Tìm hiểu sản phẩm, dịch vụ và nhận hỗ trợ trên website chính thức của ${esc(d.brand)}.</p>
${btn("Truy cập website chính thức", P.A, P.onA)}
</div>
${(d.phones || []).length ? box("Hotline", d.phones.map((p) => `<p style="margin:0 0 6px;"><a href="tel:${esc(p.replace(/[^\d+]/g, ""))}" style="color:${P.ink};text-decoration:none;">${esc(p)}</a></p>`).join("")) : ""}
${(d.emails || []).length || (d.addresses || []).length ? box("Email & địa chỉ", (d.emails || []).map((e) => `<p style="margin:0 0 6px;"><a href="mailto:${esc(e)}" style="color:${P.ink};text-decoration:none;">${esc(e)}</a></p>`).join("") + (d.addresses || []).map((a) => `<p style="margin:0 0 6px;">${esc(a)}</p>`).join("")) : ""}
</div>
</section>
`;

    const html = (x) => "<!-- wp:html -->\n" + x + "<!-- /wp:html -->\n";
    const group = (x) => '<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"0","bottom":"0","left":"0","right":"0"},"blockGap":"0"}},"layout":{"type":"default"}} -->\n'
      + '<div class="wp-block-group alignfull" style="padding-top:0;padding-right:0;padding-bottom:0;padding-left:0">' + x + "</div>\n<!-- /wp:group -->\n";

    const homeInner = `<div style="${F}color:${P.ink};line-height:1.65;background:#ffffff;margin:0;">\n` + header(true) + hero + about + products + contact + footer() + "</div>\n";

    const newsTop = `<div style="background:${P.K};color:${P.onK};padding:clamp(44px,7vw,80px) 20px;${F}">
<div style="max-width:1200px;margin:0 auto;">
<p style="margin:0 0 10px;color:${P.eyebrowDark};font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;">Tin tức &amp; Chia sẻ</p>
<h1 style="margin:0 0 12px;color:${P.onK};font-size:clamp(30px,4.4vw,46px);line-height:1.15;font-weight:800;">${nb("Tin tức " + d.brand)}</h1>
<p style="margin:0;color:${P.onK};opacity:.9;font-size:17px;max-width:660px;">${nb(d.newsLead || "Cập nhật tin tức, sự kiện và kiến thức mới nhất từ " + d.brand + ".")}</p>
</div>
</div>
`;
    const linkC = P.eyebrowLight;
    const query = `<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"56px","bottom":"72px","left":"20px","right":"20px"}},"color":{"background":"#f6f7f8"}},"layout":{"type":"constrained","contentSize":"1200px"}} -->
<div class="wp-block-group alignfull has-background" style="background-color:#f6f7f8;padding-top:56px;padding-right:20px;padding-bottom:72px;padding-left:20px"><!-- wp:query {"queryId":7,"query":{"perPage":20,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","author":"","search":"","exclude":[],"sticky":"","inherit":false}} -->
<div class="wp-block-query"><!-- wp:post-template {"style":{"spacing":{"blockGap":"28px"}},"layout":{"type":"grid","columnCount":4}} -->
<!-- wp:post-featured-image {"isLink":true,"aspectRatio":"16/9","style":{"border":{"radius":"14px"}}} /-->

<!-- wp:post-date {"style":{"color":{"text":"${linkC}"},"typography":{"fontSize":"14px","fontWeight":"700"},"spacing":{"margin":{"top":"14px"}}}} /-->

<!-- wp:post-title {"level":3,"isLink":true,"style":{"typography":{"fontSize":"20px","fontWeight":"800","lineHeight":"1.35"},"elements":{"link":{"color":{"text":"${P.ink}"}}},"color":{"text":"${P.ink}"},"spacing":{"margin":{"top":"6px","bottom":"8px"}}}} /-->

<!-- wp:post-excerpt {"moreText":"Đọc tiếp →","excerptLength":28,"style":{"typography":{"fontSize":"15px"},"elements":{"link":{"color":{"text":"${linkC}"}}}}} /-->
<!-- /wp:post-template -->

<!-- wp:query-no-results -->
<!-- wp:paragraph -->
<p>Chưa có bài viết nào. Bài bạn đăng sẽ tự hiện ở đây.</p>
<!-- /wp:paragraph -->
<!-- /wp:query-no-results -->

<!-- wp:query-pagination {"paginationArrow":"arrow","layout":{"type":"flex","justifyContent":"center"}} -->
<!-- wp:query-pagination-previous {"label":"Trang trước"} /-->

<!-- wp:query-pagination-numbers /-->

<!-- wp:query-pagination-next {"label":"Trang sau"} /-->
<!-- /wp:query-pagination --></div>
<!-- /wp:query --></div>
<!-- /wp:group -->
`;
    const single = `<!-- wp:group {"tagName":"main","style":{"spacing":{"margin":{"top":"0"},"padding":{"top":"48px","bottom":"64px","left":"20px","right":"20px"}}},"layout":{"type":"constrained","contentSize":"780px"}} -->
<main class="wp-block-group" style="margin-top:0;padding-top:48px;padding-right:20px;padding-bottom:64px;padding-left:20px"><!-- wp:post-date {"style":{"color":{"text":"${linkC}"},"typography":{"fontSize":"14px","fontWeight":"700"}}} /-->

<!-- wp:post-title {"level":1,"style":{"color":{"text":"${P.ink}"},"typography":{"fontSize":"36px","fontWeight":"800","lineHeight":"1.25"}}} /-->

<!-- wp:post-featured-image {"style":{"border":{"radius":"14px"}}} /-->

<!-- wp:post-content {"layout":{"type":"constrained"}} /-->

<!-- wp:paragraph -->
<p><a href="/tin-tuc/">← Quay lại trang Tin tức</a></p>
<!-- /wp:paragraph --></main>
<!-- /wp:group -->
`;
    const pages3 = `<!-- wp:group {"tagName":"main","style":{"spacing":{"blockGap":"0","margin":{"top":"0"}}},"layout":{"type":"default"}} -->
<main class="wp-block-group" style="margin-top:0"><!-- wp:post-content {"layout":{"type":"constrained"}} /--></main>
<!-- /wp:group -->
`;
    return {
      palette: P,
      home: group(html(homeInner)),
      news: group(html(header(false) + newsTop) + "\n" + query + "\n" + html(footer())),
      single: group(html(header(false)) + "\n" + single + "\n" + html(footer())),
      pages: pages3,
      preview: `<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0;">${homeInner}</body></html>`
    };
  }

  // Dữ liệu thô từ trang -> bản nháp để Trang sửa trong ô
  function draft(raw, colors) {
    const sec = (raw.sections || []).filter((s) => !/cookie|đăng nhập|login|newsletter|tìm kiếm|search/i.test(s.title));
    const withText = sec.filter((s) => s.text);
    const imgs = raw.images || [];
    const logo = (raw.logos || [])[0];
    return {
      brand: raw.brand || "", official: raw.origin + "/", logo: logo ? logo.url : "",
      color1: colors[0] || "", color2: colors[1] || "",
      eyebrow: raw.brand || "", h1: raw.h1 && raw.h1.length < 90 ? raw.h1 : raw.brand,
      lead: raw.description || "", ctaText: "Khám phá ngay",
      heroImg: imgs[0] ? imgs[0].url : "", aboutImg: imgs[1] ? imgs[1].url : "",
      aboutTitle: "Về " + (raw.brand || ""), aboutText: (withText[0] && withText[0].text) || raw.description || "",
      cardsTitle: "Sản phẩm và dịch vụ nổi bật",
      cards: (withText.length >= 4 ? withText.slice(1) : withText.slice(1).concat(sec.filter((s) => !s.text && !/tin tức|news|liên hệ|contact/i.test(s.title))))
        .slice(0, 6).map((s) => ({ title: s.title.replace(/[.:]$/, ""), text: s.text, href: s.href || "" })),
      phones: raw.phones || [], emails: raw.emails || [], addresses: raw.addresses || [],
      footerLinks: (raw.footerLinks && raw.footerLinks.length ? raw.footerLinks : raw.nav || []).slice(0, 6),
      footerAbout: raw.description || "", newsLead: ""
    };
  }

  return { build, draft, palette };
})();
if (typeof module !== "undefined") module.exports = SL_Gen;

// Chạy BÊN TRONG trang web mẫu (qua chrome.scripting.executeScript).
// Hàm phải tự đủ — không dùng biến bên ngoài.
function extractPageData() {
  const abs = (u) => { try { return new URL(u, location.href).href; } catch (e) { return ""; } };
  const clean = (t) => (t || "").replace(/\s+/g, " ").trim();
  const meta = (sel) => clean((document.querySelector(sel) || {}).content || "");
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none";
  };

  // ---- Tên thương hiệu
  const title = clean(document.title);
  let brand = meta('meta[property="og:site_name"]');
  if (!brand) {
    const parts = title.split(/\s[|–—-]\s/).map(clean).filter(Boolean);
    brand = parts.length > 1 ? parts.reduce((a, b) => (a.length <= b.length ? a : b)) : parts[0] || location.hostname;
  }
  const description = meta('meta[name="description"]') || meta('meta[property="og:description"]');

  // ---- Logo: ảnh/svg có chữ "logo" ở đầu trang
  const logos = [];
  const pushLogo = (url, why) => { url = abs(url); if (url && !logos.some((l) => l.url === url)) logos.push({ url, why }); };
  const headerZone = document.querySelector("header, [class*=header], [id*=header], nav") || document.body;
  document.querySelectorAll("img, image, source").forEach((el) => {
    const src = el.currentSrc || el.src || el.getAttribute("href") || el.getAttribute("xlink:href") || el.srcset || "";
    const hint = [src, el.alt, el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className, el.id,
      (el.closest("a") || {}).className, (el.parentElement || {}).className].join(" ").toLowerCase();
    if (/logo/.test(hint) && src) {
      const first = src.split(",")[0].trim().split(" ")[0];
      pushLogo(first, headerZone.contains(el) ? "logo ở đầu trang" : "ảnh có chữ logo");
    }
  });
  // logo bằng thẻ <svg> nằm trong đầu trang -> chuyển thành ảnh dữ liệu để đo màu (không dùng làm link)
  // chỉ nhận <svg> thật sự là logo (có chữ "logo" ở chính nó hoặc khung bọc), bỏ biểu tượng nhỏ (kính lúp, mũi tên…)
  let inlineSvgLogo = "";
  const svgEl = [...document.querySelectorAll("svg")].find((sv) => {
    const box = sv.getBoundingClientRect();
    const hint = [sv.id, sv.getAttribute("class"), sv.getAttribute("aria-label"), (sv.closest("[class*=logo],[id*=logo]") ? "logo" : "")].join(" ").toLowerCase();
    return /logo/.test(hint) && box.width >= 60;
  });
  if (svgEl) inlineSvgLogo = svgEl.outerHTML.slice(0, 200000);
  const ogImage = meta('meta[property="og:image"]');
  const icons = [...document.querySelectorAll('link[rel*=icon]')].map((l) => abs(l.href));
  icons.forEach((u) => pushLogo(u, "biểu tượng trang (icon)"));
  if (ogImage) pushLogo(ogImage, "ảnh chia sẻ (og:image)");

  // ---- Màu nút bấm/đầu trang (dự phòng khi không đo được logo)
  const colorCount = {};
  document.querySelectorAll("header a, header button, nav a, a[class*=btn], button, [class*=button]").forEach((el) => {
    if (!visible(el)) return;
    [getComputedStyle(el).backgroundColor, getComputedStyle(el).color].forEach((c) => {
      const m = c.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?/);
      if (!m || (m[4] !== undefined && +m[4] < 0.5)) return;
      const hex = "#" + [m[1], m[2], m[3]].map((x) => (+x).toString(16).padStart(2, "0")).join("").toUpperCase();
      colorCount[hex] = (colorCount[hex] || 0) + 1;
    });
  });
  const themeColor = meta('meta[name="theme-color"]');

  // ---- Menu
  const sameSite = (u) => { try { return new URL(u).hostname.replace(/^www\./, "") === location.hostname.replace(/^www\./, ""); } catch (e) { return false; } };
  const nav = [];
  document.querySelectorAll("header a, nav a").forEach((a) => {
    const t = clean(a.innerText); const h = abs(a.getAttribute("href"));
    if (t.length >= 2 && t.length <= 30 && h && sameSite(h) && !/^javascript|#$/.test(h) && !nav.some((n) => n.text === t)) nav.push({ text: t, href: h });
  });

  // ---- Ảnh lớn
  const images = [];
  document.querySelectorAll("img").forEach((img) => {
    const src = img.currentSrc || img.src;
    if (!src || src.startsWith("data:") || /logo|icon|sprite|avatar/i.test(src)) return;
    if ((img.naturalWidth || 0) >= 480 && (img.naturalHeight || 0) >= 240 && !images.some((i) => i.url === src))
      images.push({ url: src, alt: clean(img.alt), w: img.naturalWidth, h: img.naturalHeight });
  });

  // ---- Các mục nội dung: tiêu đề + đoạn mô tả gần nhất + link
  const h1 = clean((document.querySelector("h1") || {}).innerText);
  const sections = [];
  document.querySelectorAll("h2, h3, h4").forEach((h) => {
    if (!visible(h) || h.closest("footer, nav")) return;
    const t = clean(h.innerText);
    if (t.length < 3 || t.length > 90 || sections.some((s) => s.title === t)) return;
    let p = "", node = h;
    for (let i = 0; i < 4 && node && !p; i++) {
      const cand = node.parentElement ? node.parentElement.querySelector("p") : null;
      if (cand && clean(cand.innerText).length > 30) p = clean(cand.innerText);
      node = node.parentElement;
    }
    const a = h.closest("a") || (h.parentElement && h.parentElement.querySelector("a[href]"));
    const cut = (x, n) => x.length <= n ? x : x.slice(0, x.lastIndexOf(" ", n)).replace(/[,;:.\s]+$/, "") + "…";
    sections.push({ title: t, text: cut(p, 240), href: a ? abs(a.getAttribute("href")) : "", tag: h.tagName });
  });

  // ---- Liên hệ (lấy từ chữ trên trang, ưu tiên chân trang)
  const footer = document.querySelector("footer, [class*=footer], [id*=footer]");
  const allText = document.body.innerText || "";
  const footText = footer ? footer.innerText : allText;
  const uniq = (arr) => [...new Set(arr.map(clean))].filter(Boolean);
  const phoneRe = /(?:\+?84|0)[\s.]?\d{2,3}(?:[\s.]?\d{3,4}){2}|1[89]00[\s.]?\d{3,4}(?:[\s.]?\d{3})?/g;
  const phones = uniq((footText.match(phoneRe) || []).concat(allText.match(phoneRe) || [])).slice(0, 4);
  const emails = uniq(allText.match(/[\w.+-]+@[\w-]+(?:\.[\w-]+)+/g) || []).filter((e) => !/\.(png|jpg|webp|svg)$/i.test(e)).slice(0, 3);
  const addresses = uniq(allText.split("\n").filter((l) => /(địa chỉ|trụ sở|hội sở|văn phòng|address|head office)/i.test(l) && l.length < 220)).slice(0, 3);

  const footerLinks = [];
  if (footer) footer.querySelectorAll("a").forEach((a) => {
    const t = clean(a.innerText); const h = abs(a.getAttribute("href"));
    if (t.length >= 2 && t.length <= 40 && h && sameSite(h) && !footerLinks.some((f) => f.text === t)) footerLinks.push({ text: t, href: h });
  });

  return {
    url: location.href, origin: location.origin, title, brand, description, h1,
    logos: logos.filter((l) => !l.url.startsWith("data:")).map((l) => {
      const u = l.url.toLowerCase(); let sc = 0;
      if (/logo/.test(u)) sc += 3; if (/\.svg(\?|$)/.test(u)) sc += 2; if (/đầu trang/.test(l.why)) sc += 1;
      if (/mobile|favicon|\.ico|32x32|16x16|white|trang|negative|reverse/.test(u)) sc -= 3; if (/og:image/.test(l.why)) sc -= 4;
      return Object.assign(l, { score: sc });
    }).sort((a, b) => b.score - a.score).slice(0, 8), inlineSvgLogo, themeColor, colorCount,
    nav: nav.slice(0, 10), images: images.slice(0, 10), sections: sections.slice(0, 16),
    phones, emails, addresses, footerLinks: footerLinks.slice(0, 16), lang: document.documentElement.lang || ""
  };
}
if (typeof module !== "undefined") module.exports = { extractPageData };

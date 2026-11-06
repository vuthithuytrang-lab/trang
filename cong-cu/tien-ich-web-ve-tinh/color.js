// Đo màu thương hiệu từ file logo (chạy trong trang tiện ích, có quyền tải ảnh từ mọi web).
const SL_Color = (() => {
  const hex = (r, g, b) => "#" + [r, g, b].map((x) => Math.round(x).toString(16).padStart(2, "0")).join("").toUpperCase();
  const rgb = (h) => { h = h.replace("#", ""); if (h.length === 3) h = h.split("").map((c) => c + c).join(""); return [0, 2, 4].map((i) => parseInt(h.substr(i, 2), 16)); };
  const lum = (h) => { const [r, g, b] = rgb(h).map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  const sat = (h) => { const [r, g, b] = rgb(h); const mx = Math.max(r, g, b), mn = Math.min(r, g, b); return mx === 0 ? 0 : (mx - mn) / mx; };
  const dist = (a, b) => { const A = rgb(a), B = rgb(b); return Math.hypot(A[0] - B[0], A[1] - B[1], A[2] - B[2]); };
  // loại trắng / gần trắng / xám nhạt; giữ màu tối (navy, đen-xanh) vì là màu chữ logo
  const usable = (h) => { const L = lum(h); return L < 0.9 && !(sat(h) < 0.08 && L > 0.25); };

  function pickTwo(counts) {
    const list = Object.entries(counts).filter(([h]) => usable(h)).sort((a, b) => b[1] - a[1]).map(([h]) => h);
    const out = [];
    for (const h of list) { if (out.every((o) => dist(o, h) > 60)) out.push(h); if (out.length === 2) break; }
    return out;
  }

  function fromSvgText(svg) {
    const counts = {};
    const add = (h, n = 1) => { h = h.toUpperCase(); if (h.length === 4) h = "#" + h.slice(1).split("").map((c) => c + c).join(""); counts[h] = (counts[h] || 0) + n; };
    (svg.match(/#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b/g) || []).forEach((h) => add(h));
    (svg.match(/rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)/g) || []).forEach((c) => { const m = c.match(/\d+/g); add(hex(+m[0], +m[1], +m[2])); });
    return pickTwo(counts);
  }

  async function fromBitmap(blob) {
    const bmp = await createImageBitmap(blob);
    const W = Math.min(240, bmp.width), H = Math.max(1, Math.round(bmp.height * W / bmp.width));
    const cv = new OffscreenCanvas(W, H); const ctx = cv.getContext("2d");
    ctx.drawImage(bmp, 0, 0, W, H);
    const d = ctx.getImageData(0, 0, W, H).data; const counts = {}, sums = {};
    for (let i = 0; i < d.length; i += 4) {
      if (d[i + 3] < 200) continue;
      const q = (v) => Math.min(255, Math.round(v / 12) * 12);
      const h = hex(q(d[i]), q(d[i + 1]), q(d[i + 2]));
      counts[h] = (counts[h] || 0) + 1;
      const s = sums[h] || (sums[h] = [0, 0, 0]); s[0] += d[i]; s[1] += d[i + 1]; s[2] += d[i + 2];
    }
    // trả về màu trung bình thật của nhóm (không phải màu đã làm tròn)
    return pickTwo(counts).map((h) => { const s = sums[h], n = counts[h]; return hex(s[0] / n, s[1] / n, s[2] / n); });
  }

  async function fromUrl(url) {
    if (!url) return [];
    if (url.startsWith("data:image/svg")) return fromSvgText(decodeURIComponent(url.split(",")[1] || ""));
    const res = await fetch(url, { credentials: "omit" });
    if (!res.ok) throw new Error("Không tải được logo (" + res.status + ")");
    const type = res.headers.get("content-type") || "";
    if (type.includes("svg") || /\.svg(\?|$)/i.test(url)) return fromSvgText(await res.text());
    return fromBitmap(await res.blob());
  }

  return { fromUrl, fromSvgText, pickTwo, lum, rgb, hex, usable };
})();
if (typeof module !== "undefined") module.exports = SL_Color;

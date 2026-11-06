// Trang chỉnh sửa: nhận dữ liệu thô -> đo màu logo -> bản nháp -> Trang sửa -> ra 4 mã dán.
const $ = (id) => document.getElementById(id);
const FIELDS = ["brand", "official", "logo", "color1", "color2", "eyebrow", "h1", "lead", "ctaText", "heroImg",
  "aboutTitle", "aboutText", "aboutImg", "cardsTitle", "footerAbout", "newsLead"];
const LISTS = ["phones", "emails", "addresses"];
let data = null, raw = null, timer = null;

let wp = { host: "", theme: "assembler", homeIsPage: null, homePageId: null };
const CODES = [
  { key: "home", title: "Mã 1 – Trang chủ",
    where: () => wp.homeIsPage === false
      ? "Trang chủ của bạn là mẫu \"Blog Home\": bấm nút xanh → ⋮ → Code editor → Ctrl + A → Delete → dán → Save."
      : wp.homeIsPage ? "Bấm nút xanh → ⋮ → Code editor → bấm vào ô nội dung (dưới ô tên trang) → Ctrl + A → Delete → dán → Save."
      : "Bấm nút đúng với trang của bạn (không chắc thì thử nút xanh trước: tìm trang tên \"Home\" / trang chủ → Edit) → ⋮ → Code editor → Ctrl + A → Delete → dán → Save.",
    links: () => wp.homeIsPage === false ? [["Mở mẫu Blog Home", tpl("home")], ["Link dự phòng", tplOld("home")]]
      : wp.homePageId ? [["Mở trang chủ để sửa", `https://${wp.host}/wp-admin/post.php?post=${wp.homePageId}&action=edit`], ["Danh sách trang (Pages)", `https://${wp.host}/wp-admin/edit.php?post_type=page`]]
      : [["Trang chủ là 1 trang → mở danh sách Pages", `https://${wp.host}/wp-admin/edit.php?post_type=page`], ["Trang chủ là mẫu → mở Blog Home", tpl("home")]] },
  { key: "news", title: "Mã 2 – Trang Tin tức",
    where: () => "Bấm nút xanh (tạo trang mới) → gõ tên \"Tin tức\" → ⋮ → Code editor → dán vào ô nội dung → Publish. Địa chỉ sẽ là /tin-tuc/.",
    links: () => [["Tạo trang mới", `https://${wp.host}/wp-admin/post-new.php?post_type=page`], ["Danh sách trang (Pages)", `https://${wp.host}/wp-admin/edit.php?post_type=page`]] },
  { key: "single", title: "Mã 3 – Trang chi tiết bài viết",
    where: () => "Bấm nút xanh → ⋮ → Code editor → Ctrl + A → Delete (ô trống hẳn) → dán → Save.",
    links: () => [["Mở mẫu Single Posts", tpl("single")], ["Link dự phòng", tplOld("single")]] },
  { key: "pages", title: "Mã 4 – 3 dòng mẫu \"Pages\" (dán 1 lần)",
    where: () => "Bấm nút xanh → ⋮ → Code editor → Ctrl + A → Delete (ô trống hẳn) → dán đúng 3 dòng → Save. Không có bước này sẽ bị đầu trang/chân trang mẫu hoặc nhân đôi.",
    links: () => [["Mở mẫu Pages", tpl("page")], ["Link dự phòng", tplOld("page")]] }
];
const tpl = (slug) => `https://${wp.host}/wp-admin/site-editor.php?p=%2Fwp_template%2Fpub%2F${wp.theme}%2F%2F${slug}&canvas=edit`;
const tplOld = (slug) => `https://${wp.host}/wp-admin/site-editor.php?postType=wp_template&postId=pub%2F${wp.theme}%2F%2F${slug}&canvas=edit`;
const cleanHost = (v) => (v || "").trim().replace(/^https?:\/\//, "").split(/[/?#]/)[0].toLowerCase();

async function detectWp() {
  wp.host = cleanHost($("wpSite").value); wp.homeIsPage = null; wp.homePageId = null; wp.theme = "assembler";
  if (!wp.host) { $("wpNote").textContent = "Dán địa chỉ trang WordPress cần làm để có nút mở thẳng chỗ dán."; update(); return; }
  try { chrome.storage.local.set({ wpSite: wp.host }); } catch (e) {}
  $("wpNote").textContent = "Đang kiểm tra " + wp.host + "…"; update();
  try {
    const html = await (await fetch(`https://${wp.host}/?x=${Date.now()}`, { credentials: "omit" })).text();
    const body = (html.match(/<body[^>]*class="([^"]*)"/) || [])[1] || "";
    const th = body.match(/wp-theme-pub([a-z0-9-]+)/) || body.match(/wp-theme-([a-z0-9-]+)/);
    if (th) wp.theme = th[1];
    if (/\bhome\b/.test(body)) { wp.homeIsPage = /\bpage-id-(\d+)/.test(body); const m = body.match(/page-id-(\d+)/); wp.homePageId = m ? m[1] : null; }
    let coming = false;
    try {
      const info = await (await fetch(`https://public-api.wordpress.com/rest/v1.1/sites/${wp.host}`, { credentials: "omit" })).json();
      coming = !!(info.is_coming_soon || info.launch_status === "unlaunched");
    } catch (e) { coming = /coming soon|sắp ra mắt/i.test(html) && !/\bhome\b/.test(body); }
    $("wpNote").textContent = `Đã kiểm tra: giao diện "${wp.theme}", trang chủ là ${wp.homeIsPage ? "một trang (Page)" : wp.homeIsPage === false ? "mẫu Blog Home" : "chưa rõ (WordPress đang chặn kiểm tra) – Mã 1 có 2 nút, bấm nút đúng với trang của bạn"}.`
      + (coming ? " ⚠️ Trang đang ở chế độ \"Sắp có\" – cần bấm \"Khởi động blog\" để mọi người xem được." : "");
  } catch (e) {
    $("wpNote").textContent = "Không mở được " + wp.host + " để kiểm tra (vẫn tạo nút theo giao diện mặc định \"assembler\").";
  }
  update();
}


function fill(sel, items, current) {
  sel.innerHTML = '<option value="">— chọn —</option>' + items.map((it, i) =>
    `<option value="${i}">${(it.label || it.url).slice(0, 80)}</option>`).join("");
  const idx = items.findIndex((it) => it.url === current); if (idx >= 0) sel.value = String(idx);
  sel.onchange = () => { if (sel.value !== "") { $(sel.dataset.target).value = items[+sel.value].url; update(); } };
}

function renderCards() {
  $("cards").innerHTML = "";
  data.cards.forEach((c, i) => {
    const d = document.createElement("div"); d.className = "card";
    d.innerHTML = `<button class="x" type="button">Xoá</button>
<label>Tiêu đề ô ${i + 1}</label><input data-k="title">
<label>Mô tả</label><textarea data-k="text"></textarea>
<label>Link (để trống = website chính thức)</label><input data-k="href">`;
    d.querySelectorAll("[data-k]").forEach((el) => { el.value = c[el.dataset.k] || ""; el.oninput = () => { c[el.dataset.k] = el.value; schedule(); }; });
    d.querySelector(".x").onclick = () => { data.cards.splice(i, 1); renderCards(); update(); };
    $("cards").appendChild(d);
  });
}

function readForm() {
  FIELDS.forEach((f) => (data[f] = $(f).value.trim()));
  LISTS.forEach((f) => (data[f] = $(f).value.split("\n").map((x) => x.trim()).filter(Boolean)));
}
function writeForm() {
  FIELDS.forEach((f) => ($(f).value = data[f] || ""));
  LISTS.forEach((f) => ($(f).value = (data[f] || []).join("\n")));
  const okHex = (h) => /^#[0-9A-Fa-f]{6}$/.test(h || "");
  $("c1p").value = okHex(data.color1) ? data.color1 : "#1A1A1A";
  $("c2p").value = okHex(data.color2) ? data.color2 : "#1A1A1A";
  renderCards();
}

function update() {
  readForm();
  const okHex = (h) => /^#[0-9A-Fa-f]{6}$/.test(h || "");
  if (!okHex(data.color1)) data.color1 = "#1A1A1A";
  if (!okHex(data.color2)) data.color2 = data.color1;
  const out = SL_Gen.build(data);
  $("pv").srcdoc = out.preview;
  const linkHtml = (c) => wp.host ? c.links().map(([t, u], i) => `<a class="go${i ? " alt" : ""}" href="${u}" target="_blank" rel="noopener">${i ? "" : "↗ "}${t}</a>`).join("") + "<br>"
    : `<p class="note" style="margin:0 0 8px">Dán địa chỉ trang WordPress ở mục 0 (bên trái) để có nút mở thẳng chỗ dán.</p>`;
  $("t-codes").innerHTML = CODES.map((c) => `<div class="code"><h3>${c.title}</h3><p class="where">${c.where()}</p>${linkHtml(c)}
<button class="btn" data-copy="${c.key}" type="button">Copy mã</button><span class="copied" id="ok-${c.key}"></span>
<textarea readonly id="code-${c.key}" style="margin-top:8px"></textarea></div>`).join("")
    + `<p class="note">Nhớ: dải quảng cáo "Create your own website…" và dòng "Blog at WordPress.com" là bắt buộc ở gói miễn phí, không tắt được. Xoá bài mẫu "Hello World" và đặt ảnh đại diện cho mỗi bài để trang Tin tức đẹp.</p>`;
  CODES.forEach((c) => ($("code-" + c.key).value = out[c.key]));
  document.querySelectorAll("[data-copy]").forEach((b) => (b.onclick = async () => {
    const k = b.dataset.copy; const ta = $("code-" + k);
    try { await navigator.clipboard.writeText(ta.value); } catch (e) { ta.select(); document.execCommand("copy"); }
    $("ok-" + k).textContent = "Đã copy ✓"; setTimeout(() => ($("ok-" + k).textContent = ""), 2500);
  }));
  try { chrome.storage.local.set({ draft: data }); } catch (e) {}
}
const schedule = () => { clearTimeout(timer); timer = setTimeout(update, 250); };

async function measureColors() {
  // Ưu tiên file logo (đã xếp hạng), rồi logo SVG trên trang; thiếu màu thứ 2 thì bù từ nguồn kế tiếp.
  const tries = (raw.logos || []).map((l) => ({ how: "file logo " + l.url.split("/").pop().slice(0, 60), run: () => SL_Color.fromUrl(l.url) }));
  if (raw.inlineSvgLogo) tries.push({ how: "logo dạng SVG trên trang", run: async () => SL_Color.fromSvgText(raw.inlineSvgLogo) });
  let colors = [], how = "";
  for (const t of tries) {
    try {
      const c = await t.run();
      c.forEach((h) => { if (colors.length < 2 && !colors.includes(h)) colors.push(h); });
      if (c.length && !how) how = t.how;
      if (colors.length >= 2) break;
    } catch (e) { /* thử nguồn khác */ }
  }
  if (colors.length < 2) {
    const extra = SL_Color.pickTwo(raw.colorCount || {}).filter((h) => SL_Color.usable(h) && !colors.includes(h));
    if (extra.length) { colors.push(extra[0]); how += (how ? " + " : "") + "màu nút bấm trên trang (kiểm tra lại)"; }
  }
  if (!colors.length && raw.themeColor) { colors = [raw.themeColor]; how = "màu theme của trang (kiểm tra lại)"; }
  return { colors: colors.slice(0, 2), how: how || "không đo được – hãy tự nhập mã màu" };
}

(async function init() {
  const st = await chrome.storage.local.get(["raw"]);
  raw = st.raw;
  if (!raw) { $("status").textContent = "Chưa có dữ liệu. Mở website mẫu rồi bấm biểu tượng tiện ích → \"Lấy dữ liệu trang này\"."; return; }
  $("src").textContent = "Nguồn: " + raw.url;
  const m = await measureColors();
  data = SL_Gen.draft(raw, m.colors);
  $("colorNote").textContent = "Lấy từ: " + m.how + ". Màu đậm hơn dùng cho nền/tiêu đề, màu còn lại cho nút bấm.";
  const miss = [];
  if (!data.logo) miss.push("logo");
  if (!data.phones.length && !data.emails.length) miss.push("hotline/email");
  if (!data.cards.length) miss.push("các ô sản phẩm");
  $("status").textContent = miss.length
    ? "Đã lấy dữ liệu. Chưa tìm thấy: " + miss.join(", ") + " – bổ sung tay nếu cần (lấy từ trang Liên hệ / Giới thiệu của website mẫu)."
    : "Đã lấy dữ liệu. Kiểm tra lại chữ, màu, ảnh trước khi copy.";
  writeForm();
  const logoItems = (raw.logos || []).map((l) => ({ url: l.url, label: l.why + " – " + l.url.split("/").pop() }));
  const imgItems = (raw.images || []).map((i) => ({ url: i.url, label: (i.alt || i.url.split("/").pop()) + ` (${i.w}×${i.h})` }));
  $("logoPick").dataset.target = "logo"; fill($("logoPick"), logoItems, data.logo);
  $("heroPick").dataset.target = "heroImg"; fill($("heroPick"), imgItems, data.heroImg);
  $("aboutPick").dataset.target = "aboutImg"; fill($("aboutPick"), imgItems, data.aboutImg);
  FIELDS.concat(LISTS).forEach((f) => ($(f).oninput = schedule));
  const saved = await chrome.storage.local.get(["wpSite"]);
  if (saved.wpSite) $("wpSite").value = saved.wpSite;
  $("wpSite").onchange = detectWp;
  $("c1p").oninput = () => { $("color1").value = $("c1p").value.toUpperCase(); schedule(); };
  $("c2p").oninput = () => { $("color2").value = $("c2p").value.toUpperCase(); schedule(); };
  $("addCard").onclick = () => { data.cards.push({ title: "", text: "", href: "" }); renderCards(); };
  document.querySelectorAll("#tabs button").forEach((b) => (b.onclick = () => {
    document.querySelectorAll("#tabs button").forEach((x) => x.classList.toggle("on", x === b));
    $("t-preview").classList.toggle("hide", b.dataset.t !== "preview");
    $("t-codes").classList.toggle("hide", b.dataset.t !== "codes");
  }));
  update();
  if ($("wpSite").value) detectWp();
})();

// Trang chỉnh sửa: nhận dữ liệu thô -> đo màu logo -> bản nháp -> Trang sửa -> ra 4 mã dán.
const $ = (id) => document.getElementById(id);
const FIELDS = ["brand", "official", "logo", "color1", "color2", "eyebrow", "h1", "lead", "ctaText", "heroImg",
  "aboutTitle", "aboutText", "aboutImg", "cardsTitle", "footerAbout", "newsLead"];
const LISTS = ["phones", "emails", "addresses"];
let data = null, raw = null, timer = null;

const CODES = [
  { key: "home", title: "Mã 1 – Trang chủ",
    where: "Mở trang chủ trong WordPress → ⋮ → Code editor → Ctrl + A → Delete → dán → Save. (Nếu trang chủ là mẫu \"Blog Home\" thì dán vào mẫu đó.)" },
  { key: "news", title: "Mã 2 – Trang Tin tức",
    where: "Pages → Add Page → tên \"Tin tức\" → Code editor → dán vào ô nội dung → Publish. Địa chỉ sẽ là /tin-tuc/." },
  { key: "single", title: "Mã 3 – Trang chi tiết bài viết",
    where: "Appearance → Editor → Templates → \"Single Posts\" → ⋮ → Code editor → Ctrl + A → Delete → dán → Save." },
  { key: "pages", title: "Mã 4 – 3 dòng mẫu \"Pages\" (dán 1 lần)",
    where: "Appearance → Editor → Templates → \"Pages\" → ⋮ → Code editor → Ctrl + A → Delete (ô trống hẳn) → dán → Save. Không có bước này sẽ bị đầu trang/chân trang mẫu hoặc nhân đôi." }
];

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
  $("t-codes").innerHTML = CODES.map((c) => `<div class="code"><h3>${c.title}</h3><p class="where">${c.where}</p>
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
  $("c1p").oninput = () => { $("color1").value = $("c1p").value.toUpperCase(); schedule(); };
  $("c2p").oninput = () => { $("color2").value = $("c2p").value.toUpperCase(); schedule(); };
  $("addCard").onclick = () => { data.cards.push({ title: "", text: "", href: "" }); renderCards(); };
  document.querySelectorAll("#tabs button").forEach((b) => (b.onclick = () => {
    document.querySelectorAll("#tabs button").forEach((x) => x.classList.toggle("on", x === b));
    $("t-preview").classList.toggle("hide", b.dataset.t !== "preview");
    $("t-codes").classList.toggle("hide", b.dataset.t !== "codes");
  }));
  update();
})();

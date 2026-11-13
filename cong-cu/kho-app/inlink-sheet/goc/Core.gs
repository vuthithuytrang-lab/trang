/**
 * Core.gs — các hàm xử lý thuần (không gọi dịch vụ Google), chạy thử được bằng node: test/chay-thu.js
 * Port từ cong-cu/tao-docs-tu-url/build.py + chen.py + kiemtra.py.
 */

var YELLOW = '#ffff00';
var RED = '#ff0000';
var LINK_BLUE = '#0000ee';

/** Bỏ dấu tiếng Việt, chữ thường (để so slug). */
function boDau(t) {
  return String(t).replace(/đ/g, 'd').replace(/Đ/g, 'D')
    .normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
}

function chuanHoa(t) {
  return String(t || '').replace(/ /g, ' ').replace(/\s+/g, ' ').trim().normalize('NFC');
}

function giaiMa(t) {
  return String(t || '')
    .replace(/&#(\d+);/g, function (_, n) { return String.fromCharCode(+n); })
    .replace(/&#x([0-9a-f]+);/gi, function (_, n) { return String.fromCharCode(parseInt(n, 16)); })
    .replace(/&quot;/g, '"').replace(/&apos;|&#39;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&');
}

/** Lấy title + meta description + h1 từ HTML trang. */
function layThongTinTrang(html) {
  var t = (html.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1] || '';
  var m = (html.match(/<meta[^>]+name=["']description["'][^>]*>/i) || [])[0] || '';
  var md = (m.match(/content=["']([\s\S]*?)["']/i) || [])[1] || '';
  var h1 = (html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i) || [])[1] || '';
  return {
    title: chuanHoa(giaiMa(t)),
    meta: chuanHoa(giaiMa(md)),
    h1: chuanHoa(giaiMa(h1.replace(/<[^>]+>/g, '')))
  };
}

/**
 * Cắt khối HTML bắt đầu ở thẻ khớp `moTag` (regex trên thẻ mở), đếm cặp cùng tên thẻ để tìm thẻ đóng.
 * Trả về {start, end, inner} hoặc null.
 */
function catKhoi(html, moTag, tu) {
  moTag.lastIndex = 0;
  var re = new RegExp(moTag.source, 'gi');
  re.lastIndex = tu || 0;
  var m = re.exec(html);
  if (!m) return null;
  var ten = (m[0].match(/^<([a-z0-9]+)/i) || [])[1];
  if (!ten) return null;
  var tag = new RegExp('<(/?)' + ten + '\\b[^>]*>', 'gi');
  tag.lastIndex = m.index + m[0].length;
  var sau = 1, x;
  while ((x = tag.exec(html))) {
    if (x[0].slice(-2) === '/>') continue;
    sau += x[1] ? -1 : 1;
    if (sau === 0) {
      return { start: m.index, end: x.index + x[0].length, inner: html.slice(m.index + m[0].length, x.index) };
    }
  }
  return null;
}

/** Xoá mọi khối khớp thẻ mở `moTag` (VD công cụ quy đổi tiền trong bài Techcombank). */
function xoaKhoi(html, moTag) {
  var k;
  var vong = 0;
  while ((k = catKhoi(html, moTag)) && vong++ < 200) html = html.slice(0, k.start) + html.slice(k.end);
  return html;
}

function tuyetDoi(u, base) {
  if (!u) return u;
  u = giaiMa(u.trim());
  if (/^https?:\/\//i.test(u) || /^mailto:/i.test(u)) return u;
  if (/^\/\//.test(u)) return 'https:' + u;
  if (u.charAt(0) === '/') return base.replace(/\/$/, '') + u;
  return base.replace(/\/$/, '') + '/' + u;
}

/**
 * Làm sạch thân bài → HTML gọn để Google Docs tự chuyển: giữ tiêu đề, đoạn, danh sách, bảng, ảnh, link, đậm/nghiêng.
 */
function lamSachThanBai(frag, base) {
  var h = frag;
  ['script', 'style', 'noscript', 'button', 'svg', 'form', 'iframe', 'template'].forEach(function (t) {
    h = h.replace(new RegExp('<' + t + '\\b[\\s\\S]*?<\\/' + t + '>', 'gi'), '');
  });
  h = h.replace(/<!--[\s\S]*?-->/g, '');
  // ảnh: lấy src thật (Wix: bỏ phần /v1/... để có ảnh gốc, không bị mờ)
  h = h.replace(/<img\b[^>]*>/gi, function (img) {
    var src = (img.match(/\ssrc=["']([^"']+)["']/i) || [])[1] || (img.match(/data-src=["']([^"']+)["']/i) || [])[1];
    if (!src || /^data:/i.test(src) || /\.svg(\?|$)/i.test(src)) return '';
    src = tuyetDoi(src, base);
    if (/static\.wixstatic\.com\/media\//.test(src) && src.indexOf('/v1/') > 0) src = src.split('/v1/')[0];
    return '<img src="' + src + '" width="500">';
  });
  // link
  h = h.replace(/<a\b[^>]*>/gi, function (a) {
    var href = (a.match(/\shref=["']([^"']*)["']/i) || [])[1];
    return href ? '<a href="' + tuyetDoi(href, base).replace(/"/g, '&quot;') + '">' : '<a>';
  });
  // giữ thẻ cần thiết, bỏ thuộc tính; thẻ khác thì bỏ vỏ
  var GIU = { p: 1, h2: 1, h3: 1, h4: 1, h5: 1, ul: 1, ol: 1, li: 1, b: 1, strong: 1, i: 1, em: 1, u: 1, a: 1, table: 1, tbody: 1, thead: 1, tr: 1, td: 1, th: 1, img: 1, br: 1, sup: 1, sub: 1 };
  h = h.replace(/<(\/?)([a-z0-9]+)\b([^>]*)>/gi, function (all, cl, ten, at) {
    ten = ten.toLowerCase();
    if (!GIU[ten]) return '';
    if (ten === 'a' || ten === 'img') return all;
    if (cl) return '</' + ten + '>';
    if (ten === 'td' || ten === 'th') {
      var span = '';
      var cs = at.match(/colspan=["']?(\d+)/i), rs = at.match(/rowspan=["']?(\d+)/i);
      if (cs) span += ' colspan="' + cs[1] + '"';
      if (rs) span += ' rowspan="' + rs[1] + '"';
      return '<' + ten + span + '>';
    }
    if (ten === 'table') return '<table border="1" style="border-collapse:collapse;width:100%">';
    if (ten === 'p' || ten === 'li' || /^h\d$/.test(ten)) return '<' + ten + ' style="text-align:justify;">';
    return '<' + ten + '>';
  });
  // đoạn chỉ chứa ảnh → căn giữa
  h = h.replace(/<p style="text-align:justify;">(\s*<img[^>]*>\s*)<\/p>/gi, '<p style="text-align:center;">$1</p>');
  h = h.replace(/(<p style="text-align:justify;">\s*<\/p>\s*){2,}/gi, '');
  return h;
}

/** Tự tìm khung thân bài trên mọi website: thử các khung bài viết phổ biến, chọn khung có nhiều đoạn <p> nhất. */
var KHUNG_THAN_BAI = [
  /<div[^>]*itemprop=["']articleBody["'][^>]*>/, /<(?:div|section)[^>]*data-hook=["']post-description["'][^>]*>/,
  /<div[^>]*class=["'][^"']*\b(?:entry-content|post-content|article-content|article-body|article__content|article-text|blog-content|blog-detail|post-body|single-content|content-detail|detail-content|news-content|td-post-content|rich-text|prose)\b[^"']*["'][^>]*>/,
  /<article\b[^>]*>/, /<main\b[^>]*>/
];
function timThanBai(html) {
  var tot = null, diem = 0;
  KHUNG_THAN_BAI.forEach(function (re) {
    var tu = 0, vong = 0, k;
    while ((k = catKhoi(html, re, tu)) && vong++ < 30) {
      var p = (k.inner.match(/<p[\s>]/gi) || []).length;
      if (p > diem) { diem = p; tot = k; }
      tu = k.start + 1;
    }
  });
  if (tot && diem >= 3) return tot.inner;
  var b = (html.match(/<body[^>]*>([\s\S]*)<\/body>/i) || [])[1] || html;
  ['header', 'footer', 'nav', 'aside'].forEach(function (t) { b = b.replace(new RegExp('<' + t + '\\b[\\s\\S]*?<\\/' + t + '>', 'gi'), ''); });
  return (b.match(/<p[\s>]/gi) || []).length >= 3 ? b : null;
}

/** Phân loại 1 luật viết bằng lời: trả về các từ cấm app tự chặn được (giống app web Luồng inlink). */
function tuCamTrongLuat(x) {
  var t = String(x || '').trim(), cam = [], m, re = /["“«']([^"”»']{2,60})["”»']/g;
  var phuDinh = /^(không|đừng|tránh|né|cấm|bỏ qua)(?=\s|$)/i.test(t);
  while ((m = re.exec(t))) cam.push(m[1].trim().toLowerCase());
  if (cam.length && !phuDinh) cam = [];
  if (!cam.length && phuDinh) {
    var m2 = t.match(/đoạn\s+(?:có|chứa|nói về|về)\s+(?:chữ|từ|cụm|cụm từ)?\s*(.+)$/i);
    if (m2) cam = m2[1].split(/,|;|\s+(?:và|hoặc|hay)\s+/).map(function (c) { return c.replace(/[."“”«»']/g, '').trim().toLowerCase(); }).filter(function (c) { return c && c.split(/\s+/).length <= 5; });
  }
  if (!cam.length && !phuDinh && t && t.split(/\s+/).length <= 4 && !/^(câu|tối đa|tối thiểu|chỉ|luôn|ưu tiên|viết|dùng|giữ|người)(?=\s|$)/i.test(t)) cam = [t.replace(/["“”«»']/g, '').toLowerCase()];
  return cam;
}

/** Từ khoá chính từ slug, khớp lại chữ có dấu trong H1/title/meta (port keyword() của build.py). */
function tuKhoaTuSlug(url, texts) {
  var slug = url.split('?')[0].replace(/\/$/, '').split('/').pop();
  var words = slug.split('-');
  for (var t = 0; t < texts.length; t++) {
    var toks = String(texts[t] || '').match(/[0-9A-Za-zÀ-ỹ]+/g) || [];
    for (var i = 0; i + words.length <= toks.length; i++) {
      var ok = true;
      for (var j = 0; j < words.length; j++) if (boDau(toks[i + j]) !== words[j]) { ok = false; break; }
      if (ok) {
        var k = toks.slice(i, i + words.length).join(' ');
        return k.charAt(0).toUpperCase() + k.slice(1).toLowerCase();
      }
    }
  }
  var s = slug.replace(/-/g, ' ');
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/** HTML đầy đủ để tải lên Drive (Google tự chuyển thành Docs) — đúng mẫu Trang đã duyệt. */
function dungHtmlDoc(url, info, than) {
  function e(x) { return String(x).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  return '<html><head><meta charset="utf-8"></head><body style="font-family:Arial">' +
    '<p>URL: <a href="' + url + '">' + url + '</a></p><p></p>' +
    '<p style="text-align:center"><b>' + e(info.title) + '</b></p><p></p>' +
    '<p style="text-align:center;color:#888888">' + e(info.meta) + '</p><p></p>' +
    than + '</body></html>';
}

/* ----------------------------- CHỌN CHỖ CHÈN ----------------------------- */

/**
 * doan: [{text, heading:bool, list:bool, table:bool, link:[url...]}] theo thứ tự thân bài (đã bỏ 6 đoạn đầu URL/title/meta).
 * Trả về mảng % vị trí tính theo số ký tự (giống blocks.py bodypct).
 */
function viTriPhanTram(doan) {
  var tong = 0;
  doan.forEach(function (d) { tong += d.text.length; });
  var acc = 0;
  return doan.map(function (d) { var p = tong ? acc * 100 / tong : 0; acc += d.text.length; return p; });
}

function laDoanGhiChu(t) { return /^\s*\[(Nội dung gốc trước khi chèn|Đề xuất viết thêm đoạn mới)/.test(t); }

/** Đoạn có được phép chèn không: ≥25%, không tiêu đề, không bước hướng dẫn, không định nghĩa, không bảng, không ghi chú. */
var CAM_DU_AN = [];   // từ cấm lấy từ "Quy tắc riêng của dự án" + ghi chú từng dòng (đặt lại mỗi lần chạy)
function coTuCam(t) { t = String(t || '').toLowerCase(); for (var i = 0; i < CAM_DU_AN.length; i++) if (t.indexOf(CAM_DU_AN[i]) >= 0) return CAM_DU_AN[i]; return ''; }
var LUAT_PHAP = /(luật|nghị định|thông tư|điều \d+|khoản \d+|quyết định số|bộ luật|nđ-cp|tt-nhnn|tt-btc)/i;

function duocChen(doan, pct, i) {
  var d = doan[i];
  if (!d || d.heading || d.table) return false;
  if (pct[i] < 25) return false;
  var t = d.text.trim();
  if (!t || t.length < 40) return false;
  if (coTuCam(t)) return false;
  if (LUAT_PHAP.test(t)) return false;
  if (laDoanGhiChu(t)) return false;
  if (/^(Bước|B\s?\d)\s*\d*\s*[:.]/i.test(t)) return false;
  if (/^(Lưu ý|Khách hàng lưu ý|Thông tin trong bài viết)/i.test(t)) return false;
  return true;
}

/** Đoạn i có kề đoạn đã có link không (bỏ qua tiêu đề khi xét kề). */
function keLink(doan, i) {
  function ben(j, d) {
    j += d;
    while (j >= 0 && j < doan.length && doan[j].heading) j += d;
    return j;
  }
  var a = ben(i, -1), b = ben(i, 1);
  return (doan[i].link && doan[i].link.length) ||
    (a >= 0 && doan[a].link && doan[a].link.length) ||
    (b < doan.length && doan[b] && doan[b].link && doan[b].link.length);
}

/** Vị trí đầu tiên của cụm (khớp nguyên cụm) KHÔNG nằm đè lên link có sẵn. links: [{start,end}] */
function timCum(text, cum, links) {
  var re = new RegExp('(^|[^0-9A-Za-zÀ-ỹ])(' + cum.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')(?![0-9A-Za-zÀ-ỹ])', 'g');
  var m;
  while ((m = re.exec(text))) {
    var a = m.index + m[1].length, b = a + cum.length;
    var de = (links || []).some(function (l) { return a < l.end && b > l.start; });
    if (!de) return a;
    re.lastIndex = m.index + 1;
  }
  return -1;
}

/** Tìm đoạn có sẵn cụm anchor (khớp nguyên văn, phân biệt hoa/thường) để gắn link. Ưu tiên đoạn không kề link. */
function timCumCoSan(doan, anchor) {
  var pct = viTriPhanTram(doan);
  var tot = -1, du = -1;
  for (var i = 0; i < doan.length; i++) {
    if (!duocChen(doan, pct, i) && !(doan[i].list && pct[i] >= 25 && !doan[i].table && !/^(Bước)/i.test(doan[i].text) && !coTuCam(doan[i].text))) continue;
    var k = timCum(doan[i].text, anchor, doan[i].links);
    if (k < 0) continue;
    if (new RegExp(anchor.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s+là\\b').test(doan[i].text)) continue; // câu định nghĩa
    if (!keLink(doan, i)) { tot = i; break; }
    if (du < 0) du = i;
  }
  var i2 = tot >= 0 ? tot : du;
  return i2 < 0 ? null : { i: i2, offset: timCum(doan[i2].text, anchor, doan[i2].links) };
}

var CUM_CAM = ['Bên cạnh đó, bạn cũng có thể tham khảo', 'Ngoài ra, bạn có thể tìm hiểu thêm', 'để có thêm thông tin',
  'để hiểu rõ hơn', 'một cách hiệu quả', 'vô cùng', 'hữu ích', 'tham khảo ngay', 'đừng quên', 'chắc chắn', 'tại đây'];

/**
 * Kiểm tra câu AI viết trước khi chèn. Trả về '' nếu ổn, hoặc lý do bị loại.
 * nguon = chữ bài gốc + trang đích (để soát con số không bịa).
 */
function kiemTraCauChen(cau, anchor, nguon) {
  if (!cau) return 'trống';
  var n = cau.split(anchor).length - 1;
  if (n !== 1) return 'anchor phải xuất hiện đúng 1 lần, nguyên văn';
  if (cau.length > 400) return 'câu quá dài';
  if (/[!?]/.test(cau.replace(/^>>>\s*/, ''))) return 'không dùng dấu ! hoặc ?';
  for (var i = 0; i < CUM_CAM.length; i++) if (cau.toLowerCase().indexOf(CUM_CAM[i].toLowerCase()) >= 0) return 'có cụm bị cấm: ' + CUM_CAM[i];
  var so = (cau.replace(anchor, ' ').match(/\d[\d.,]*/g) || []);
  for (var j = 0; j < so.length; j++) if (String(nguon).indexOf(so[j]) < 0) return 'có con số không có trong bài/trang đích: ' + so[j];
  return '';
}

/** Phần chữ mới cần tô vàng khi viết lại đoạn: cắt phần đầu/cuối giống nhau (theo từ). */
function phanKhacNhau(cu, moi) {
  var a = 0;
  while (a < cu.length && a < moi.length && cu.charAt(a) === moi.charAt(a)) a++;
  while (a > 0 && /\S/.test(moi.charAt(a - 1))) a--;
  var b = 0;
  while (b < cu.length - a && b < moi.length - a && cu.charAt(cu.length - 1 - b) === moi.charAt(moi.length - 1 - b)) b++;
  while (b > 0 && /\S/.test(moi.charAt(moi.length - b))) b--;
  return { start: a, end: moi.length - b };
}

/** Ghi chú cột Ghi chú (E) — cùng mẫu đã dùng. */
function ghiChuE(tong, ketQua) {
  var moi = ketQua.filter(function (k) { return k.ok && k.cach !== 'có sẵn link đúng anchor'; });
  var san = ketQua.filter(function (k) { return k.ok && k.cach === 'có sẵn link đúng anchor'; });
  var thieu = ketQua.filter(function (k) { return !k.ok; });
  var s = 'Đủ ' + (moi.length + san.length) + '/' + tong + ' anchor (đúng nguyên văn sheet).';
  if (moi.length) s += '\nĐã chèn mới (' + moi.length + '): ' + moi.map(function (k) { return k.anchor + ' (' + k.cach + ')'; }).join('; ') + '.';
  if (san.length) s += '\nBài đã có sẵn link đúng URL, giữ nguyên (' + san.length + '): ' + san.map(function (k) { return k.anchor; }).join('; ') + '.';
  s += '\nThiếu: ' + (thieu.length ? thieu.map(function (k) { return k.anchor + ' — ' + k.ly_do; }).join('; ') : 'không') + '.';
  s += '\n[App inlink]';
  return s;
}

if (typeof module !== 'undefined') {
  module.exports = { boDau: boDau, chuanHoa: chuanHoa, layThongTinTrang: layThongTinTrang, catKhoi: catKhoi, xoaKhoi: xoaKhoi,
    lamSachThanBai: lamSachThanBai, tuKhoaTuSlug: tuKhoaTuSlug, dungHtmlDoc: dungHtmlDoc, viTriPhanTram: viTriPhanTram,
    duocChen: duocChen, timCumCoSan: timCumCoSan, kiemTraCauChen: kiemTraCauChen, phanKhacNhau: phanKhacNhau, ghiChuE: ghiChuE,
    laDoanGhiChu: laDoanGhiChu, keLink: keLink };
}

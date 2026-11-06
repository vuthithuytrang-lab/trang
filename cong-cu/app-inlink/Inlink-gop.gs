// ===== App Inlink — bản gộp tự động từ cong-cu/app-inlink/*.gs. Sửa file gốc rồi chạy gop.sh =====

// ----- CauHinh.gs -----
/**
 * CauHinh.gs — mỗi dự án 1 mục. Thêm dự án mới: chép 1 mục, đổi sheet/tab/thư mục/tên cột.
 * Tên cột tìm theo CHỮ ở hàng 1 (không theo vị trí) → sheet có chèn/đổi cột vẫn chạy đúng.
 */
var DU_AN = [
  {
    ten: 'Techcombank',
    sheetId: '1KqFQ7DIRFM3vwozccCYZrlsRybOAsieAKm_MVsM2Lnc',
    tab: 'Plan internal links - Tổng',
    thuMuc: '1qLQU6FfkXcOvAsUvKZ-KsVeXWC5RLgHH',
    goc: 'https://techcombank.com',
    taiQua: function (u) { return u.replace('//techcombank.com', '//www.techcombank.com').split('?')[0]; },
    thanBai: /<div[^>]*class=["'][^"']*\barticle-text\b[^"']*["'][^>]*>/,
    boKhoi: [/<div[^>]*class=["'][^"']*\bcurrency-converter\b[^"']*["'][^>]*>/, /<div[^>]*class=["'][^"']*\blist-?tiles?\b[^"']*["'][^>]*>/],
    cot: {
      url: /^URL$/i, file: /^FILE BLOG$/i, ghiChu: /^Ghi chú$/i, duyet: /^Chị Lộc duyệt$/i,
      tyGiaAnchor: /^Anchor text \(Trang tỷ giá\)$/i, tyGiaUrl: /^URL đích \(Trang tỷ giá\)$/i,
      demo: /^Demo nội dung chèn ACT Tỷ giá$/i, xf: /^Chèn XF$/i,
      capAnchor: /^Anchor ?text ?(\d)$/i, capUrl: /^URL đích (\d)$/i
    },
    boQuaTyGia: function (h) { return /tiết kiệm/i.test(h.xf || '') || /XF Tiết kiệm/i.test(h.ghiChu || ''); },
    boQuaDong: function (h) { return false; },
    nguoiDuyet: 'Lộc',
    tuChay: true
  },
  {
    ten: 'Okamura',
    sheetId: '1xKnPX-uf7av3FpSocVjy9wKJiNeygrsZLVmdcMC7np8',
    tab: 'Trang tính146',
    thuMuc: '1dfPI34Qf5mFI1ALHl5vWU8MUKrqVnwiU',
    goc: 'https://www.okamura.com.vn',
    taiQua: function (u) { return u.split('?')[0]; },
    thanBai: /<(?:div|section)[^>]*data-hook=["']post-description["'][^>]*>/,
    boKhoi: [],
    cot: {
      url: /^Landingpage chính xác$/i, file: /^Fie Blog$|^File Blog$/i, ghiChu: null, duyet: null, tinhTrang: /^Tình trạng$/i,
      tyGiaAnchor: null, tyGiaUrl: null, demo: null, xf: null,
      capAnchor: /^Anchotext 0?(\d)/i, capUrl: /^URL 0?(\d)$/i
    },
    boQuaTyGia: function () { return true; },
    boQuaDong: function (h) { return /đã done|^-$/i.test(String(h.tinhTrang || '').trim()); },
    nguoiDuyet: 'Lộc',
    tuChay: false
  }
];

var UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36';
var GIOI_HAN_GIAY = 300;          // Apps Script cho tối đa 6 phút mỗi lần chạy; dừng ở 5 phút cho an toàn
var TAB_GOP_Y = 'Sổ góp ý';
var TAB_NHAT_KY = 'Nhật ký app';

// ----- Core.gs -----
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
function duocChen(doan, pct, i) {
  var d = doan[i];
  if (!d || d.heading || d.table) return false;
  if (pct[i] < 25) return false;
  var t = d.text.trim();
  if (!t || t.length < 40) return false;
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
    if (!duocChen(doan, pct, i) && !(doan[i].list && pct[i] >= 25 && !doan[i].table && !/^(Bước)/i.test(doan[i].text))) continue;
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


// ----- Sheet.gs -----
/** Sheet.gs — đọc cột theo tên ở hàng 1, gom anchor của từng dòng, ghi từng ô một (chỉ ô trống). */

function moSheet(pj) {
  var sh = SpreadsheetApp.openById(pj.sheetId).getSheetByName(pj.tab);
  if (!sh) throw new Error('Không thấy tab "' + pj.tab + '" trong sheet ' + pj.ten);
  return sh;
}

/** Bản đồ cột: {url: 2, file: 11, ..., cap: [{anchor: 16, url: 17}, ...]} (đánh số từ 1). */
function banDoCot(pj, sh) {
  var hang1 = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0].map(function (x) { return String(x).replace(/\s+/g, ' ').trim(); });
  var m = { cap: [] };
  var capA = {}, capU = {};
  hang1.forEach(function (ten, j) {
    Object.keys(pj.cot).forEach(function (k) {
      var re = pj.cot[k];
      if (!re || k === 'capAnchor' || k === 'capUrl') return;
      if (re.test(ten) && !m[k]) m[k] = j + 1;
    });
    var a = ten.match(pj.cot.capAnchor), u = ten.match(pj.cot.capUrl);
    if (a) capA[a[1]] = j + 1;
    if (u) capU[u[1]] = j + 1;
  });
  Object.keys(capA).sort().forEach(function (n) { if (capU[n]) m.cap.push({ anchor: capA[n], url: capU[n] }); });
  if (!m.url || !m.file) throw new Error(pj.ten + ': không tìm thấy cột URL hoặc cột FILE ở hàng 1');
  return m;
}

function giaTriDong(m, dong) {
  var h = {};
  Object.keys(m).forEach(function (k) { if (k !== 'cap') h[k] = m[k] ? String(dong[m[k] - 1] || '').trim() : ''; });
  return h;
}

/** Danh sách anchor cần chèn của 1 dòng, đúng thứ tự sheet: cặp tỷ giá trước, rồi các cặp 1..5. */
function anchorCuaDong(pj, m, dong) {
  var h = giaTriDong(m, dong), ds = [], thieu = [];
  if (m.tyGiaAnchor && m.tyGiaUrl && !pj.boQuaTyGia(h)) {
    var a = String(dong[m.tyGiaAnchor - 1] || '').trim(), u = String(dong[m.tyGiaUrl - 1] || '').trim();
    if (a && u) ds.push({ anchor: a, url: u, tyGia: true });
    else if (u && !a) thieu.push(u);
  }
  m.cap.forEach(function (c) {
    var a = String(dong[c.anchor - 1] || '').trim(), u = String(dong[c.url - 1] || '').trim();
    if (a && u) ds.push({ anchor: a, url: u });
    else if (u && !a) thieu.push(u);
  });
  return { ds: ds, thieuAnchor: thieu, h: h };
}

/** Ghi 1 ô, chỉ khi ô đang trống. Trả về true nếu đã ghi. */
function ghiOTrong(sh, r, c, giaTri) {
  var o = sh.getRange(r, c);
  if (String(o.getValue()).trim() !== '') return false;
  o.setValue(giaTri);
  return true;
}

function nhatKy(viec, duAn, dong, ketQua) {
  var ss = SpreadsheetApp.openById(DU_AN[0].sheetId);
  var t = ss.getSheetByName(TAB_NHAT_KY) || ss.insertSheet(TAB_NHAT_KY);
  if (t.getLastRow() === 0) t.appendRow(['Thời gian', 'Việc', 'Dự án', 'Dòng', 'Kết quả']);
  t.appendRow([new Date(), viec, duAn, dong, String(ketQua).slice(0, 4000)]);
}

function idTuLink(link) { var m = String(link).match(/\/d\/([\w-]{20,})/); return m ? m[1] : ''; }
function slugCua(u) { return String(u).split('?')[0].replace(/\/$/, '').split('/').pop(); }

// ----- TaoFile.gs -----
/**
 * TaoFile.gs — tạo file Docs từ URL bài và chèn đủ anchor theo sheet.
 * Thứ tự cho mỗi anchor: cột Demo "Sau khi chèn" (tỷ giá) → link có sẵn đúng anchor → cụm có sẵn → AI viết 1 câu / dòng Xem thêm.
 * Không chèn được thì để thiếu và ghi rõ lý do (không ép câu gượng — bài học từ góp ý chị Lộc).
 */

function taiTrang(url) {
  var r = UrlFetchApp.fetch(url, {
    muteHttpExceptions: true, followRedirects: true,
    headers: { 'User-Agent': UA, 'Accept': 'text/html', 'Accept-Language': 'vi-VN,vi;q=0.9' }
  });
  return { ma: r.getResponseCode(), html: r.getContentText('UTF-8') };
}

/** Bước 1: tải bài, dựng HTML, tải lên Drive thành Google Docs. */
function taoDocTuUrl(pj, url) {
  var t = taiTrang(pj.taiQua(url));
  if (t.ma !== 200) return { loi: 'không tải được bài (mã ' + t.ma + ')' };
  var info = layThongTinTrang(t.html);
  if (/Không tìm thấy/i.test(info.title)) return { loi: 'bài đã bị gỡ (Không tìm thấy trang)' };
  var k = catKhoi(t.html, pj.thanBai);
  if (!k) return { loi: 'không tìm thấy khung thân bài (có thể là trang sản phẩm) — cần làm tay' };
  var than = k.inner;
  pj.boKhoi.forEach(function (re) { than = xoaKhoi(than, re); });
  than = lamSachThanBai(than, pj.goc);
  var chu = than.replace(/<[^>]+>/g, ' ');
  var ten = tuKhoaTuSlug(url, [info.h1, info.title, info.meta, chu]);
  var html = dungHtmlDoc(url, info, than);
  var f = Drive.Files.create({ name: ten, mimeType: MimeType.GOOGLE_DOCS, parents: [pj.thuMuc] },
    Utilities.newBlob(html, 'text/html', ten + '.html'), { fields: 'id' });
  return { id: f.id, ten: ten, chuBai: chuanHoa(chu) };
}

/* ------------------------- đọc cấu trúc file Docs ------------------------- */

function linkTrongDoan(el) {
  var out = [];
  var tx = el.editAsText(), s = tx.getText();
  if (!s.length) return out;
  var idx = tx.getTextAttributeIndices(), cur = null;
  for (var i = 0; i < idx.length; i++) {
    var a = idx[i], b = i + 1 < idx.length ? idx[i + 1] : s.length;
    var u = tx.getLinkUrl(a);
    if (u && cur && cur.url === u && cur.end === a) { cur.end = b; continue; }
    if (cur) out.push(cur);
    cur = u ? { url: u, start: a, end: b } : null;
  }
  if (cur) out.push(cur);
  out.forEach(function (l) { l.text = s.slice(l.start, l.end); });
  return out;
}

/** Danh sách đoạn thân bài (bỏ 6 đoạn đầu: URL, title, meta). */
function docDoan(body) {
  var ds = [];
  for (var i = 6; i < body.getNumChildren(); i++) {
    var el = body.getChild(i), ty = el.getType();
    if (ty === DocumentApp.ElementType.PARAGRAPH || ty === DocumentApp.ElementType.LIST_ITEM) {
      var p = ty === DocumentApp.ElementType.PARAGRAPH ? el.asParagraph() : el.asListItem();
      var links = linkTrongDoan(p);
      ds.push({ el: p, text: p.getText(), heading: p.getHeading() !== DocumentApp.ParagraphHeading.NORMAL,
        list: ty === DocumentApp.ElementType.LIST_ITEM, table: false, link: links.map(function (l) { return l.url; }), links: links });
    } else if (ty === DocumentApp.ElementType.TABLE) {
      ds.push({ el: el, text: el.asTable().getText(), heading: false, list: false, table: true, link: [], links: [] });
    }
  }
  return ds;
}

function chenGhiChu(body, el, noiDung) {
  var i = body.getChildIndex(el);
  var p = body.insertParagraph(i + 1, noiDung);
  p.setHeading(DocumentApp.ParagraphHeading.NORMAL).setAlignment(DocumentApp.HorizontalAlignment.JUSTIFY);
  p.editAsText().setLinkUrl(null).setBackgroundColor(null).setBold(false).setItalic(true).setForegroundColor(RED);
  return p;
}

function toLink(tx, a, b, url) {
  tx.setLinkUrl(a, b - 1, url).setUnderline(a, b - 1, true).setForegroundColor(a, b - 1, LINK_BLUE).setBackgroundColor(a, b - 1, YELLOW);
}

/** Phần tử cuối của danh sách chứa el (để chèn đoạn mới sau cả danh sách). */
function cuoiDanhSach(body, el) {
  var i = body.getChildIndex(el);
  while (i + 1 < body.getNumChildren() && body.getChild(i + 1).getType() === DocumentApp.ElementType.LIST_ITEM) i++;
  return body.getChild(i);
}

/* ------------------------------ các cách chèn ------------------------------ */

function chenTheoDemo(body, doan, a, demo) {
  var mT = demo.match(/Trước khi chèn:\s*([\s\S]*?)\s*Sau khi chèn:\s*([\s\S]*)$/i);
  if (!mT) return null;
  var boGach = function (x) { return chuanHoa(x).replace(/^[-•+*–]\s*/, ''); };
  var truoc0 = boGach(mT[1]).replace(/\.$/, ''), sau0 = boGach(mT[2]);
  if (sau0.indexOf(a.anchor) < 0) return null;
  // thử cả câu; nếu không khớp thì thử phần sau nhãn "...:" (nhãn in đậm đầu gạch đầu dòng)
  var thu = [[truoc0, sau0]];
  var c1 = truoc0.indexOf(': '), c2 = sau0.indexOf(': ');
  if (c1 > 0 && c2 > 0 && truoc0.slice(0, c1) === sau0.slice(0, c2)) thu.push([truoc0.slice(c1 + 2), sau0.slice(c2 + 2)]);
  for (var i = 0; i < doan.length; i++) {
    var d = doan[i];
    if (d.table || d.heading) continue;
    var s = d.text.replace(/\u00a0/g, ' ').replace(/[ \t]+/g, ' ').normalize('NFC');
    var k = -1, truoc = '', sau = '';
    for (var t = 0; t < thu.length && k < 0; t++) { k = s.indexOf(thu[t][0]); truoc = thu[t][0]; sau = thu[t][1]; }
    if (k < 0 || sau.indexOf(a.anchor) < 0) continue;
    if (s.length !== d.text.length) continue;   // văn bản có khoảng trắng lạ → vị trí lệch, để làm tay
    var goc = d.text, tx = d.el.editAsText();
    var het = k + truoc.length;
    if (s.charAt(het) === '.' && /\.$/.test(sau)) het++;
    tx.deleteText(k, het - 1);
    tx.insertText(k, sau);
    var kh = phanKhacNhau(truoc, sau);
    tx.setBackgroundColor(k + kh.start, k + kh.end - 1, YELLOW);
    var ai = sau.indexOf(a.anchor);
    toLink(tx, k + ai, k + ai + a.anchor.length, a.url);
    chenGhiChu(body, d.el, '[Nội dung gốc trước khi chèn: ' + chuanHoa(goc) + ']');
    return 'cột Demo';
  }
  return 'khong_thay';
}

function chenLinkCoSan(body, doan, a) {
  for (var i = 0; i < doan.length; i++) {
    var ls = doan[i].links;
    for (var j = 0; j < ls.length; j++) {
      if (slugCua(ls[j].url) === slugCua(a.url) && chuanHoa(ls[j].text) === a.anchor) {
        doan[i].el.editAsText().setBackgroundColor(ls[j].start, ls[j].end - 1, YELLOW);
        chenGhiChu(body, doan[i].el, '[Bài gốc đã có sẵn link đúng anchor và URL đích — giữ nguyên]');
        return 'có sẵn link đúng anchor';
      }
    }
  }
  return null;
}

function chenCumCoSan(body, doan, a) {
  var hit = timCumCoSan(doan, a.anchor);
  if (!hit) return null;
  var d = doan[hit.i], goc = chuanHoa(d.text);
  toLink(d.el.editAsText(), hit.offset, hit.offset + a.anchor.length, a.url);
  chenGhiChu(body, d.el, '[Nội dung gốc trước khi chèn: ' + goc + ']');
  return 'gắn cụm có sẵn';
}

function chenCauAI(body, doan, a, ngCanh) {
  var pct = viTriPhanTram(doan), ung = [];
  for (var i = 0; i < doan.length; i++) if (duocChen(doan, pct, i) && !keLink(doan, i)) ung.push(i);
  if (!ung.length) return { ly_do: 'không còn đoạn hợp lệ (≥25%, không kề link)' };
  var g = aiChonCho(a, doan, pct, ung, ngCanh);
  if (!g.ok) return { ly_do: g.ly_do };
  var d = doan[g.i], goc = chuanHoa(d.text);
  if (g.cach === 'xemthem') {
    var sau = d.list ? cuoiDanhSach(body, d.el) : d.el;
    var ghi = chenGhiChu(body, sau, '[Đề xuất viết thêm đoạn mới]');
    var p = body.insertParagraph(body.getChildIndex(ghi) + 1, g.cau);
    p.setHeading(DocumentApp.ParagraphHeading.NORMAL).setAlignment(DocumentApp.HorizontalAlignment.JUSTIFY);
    var tx = p.editAsText();
    tx.setLinkUrl(null).setForegroundColor(null).setBold(true).setItalic(true).setBackgroundColor(YELLOW);
    var k = g.cau.indexOf(a.anchor);
    toLink(tx, k, k + a.anchor.length, a.url);
    return { cach: 'xem thêm' };
  }
  var tx2 = d.el.editAsText(), s = tx2.getText().replace(/\s+$/, '');
  var them = (/[.:;!?…]$/.test(s) ? '' : '.') + ' ' + g.cau;
  var bd = s.length;
  tx2.insertText(bd, them);
  tx2.setBackgroundColor(bd + 1, bd + them.length - 1, YELLOW).setLinkUrl(bd, bd + them.length - 1, null);
  var k2 = bd + them.indexOf(a.anchor);
  toLink(tx2, k2, k2 + a.anchor.length, a.url);
  chenGhiChu(body, d.el, '[Nội dung gốc trước khi chèn: ' + goc + ']');
  return { cach: 'viết thêm 1 câu' };
}

/* ------------------------------- soát cuối ------------------------------- */

function soatFile(body, ds) {
  var doan = docDoan(body), pct = viTriPhanTram(doan);
  return ds.map(function (a) {
    for (var i = 0; i < doan.length; i++) {
      var ls = doan[i].links;
      for (var j = 0; j < ls.length; j++) {
        if (slugCua(ls[j].url) === slugCua(a.url) && chuanHoa(ls[j].text) === a.anchor) {
          var vang = doan[i].el.editAsText().getBackgroundColor(ls[j].start) === YELLOW;
          return { anchor: a.anchor, ok: vang, vang: vang, pct: pct[i], heading: doan[i].heading };
        }
      }
    }
    return { anchor: a.anchor, ok: false };
  });
}

/** Xử lý trọn 1 dòng sheet. Trả về {id, ketQua, loi}. */
function xuLyDong(pj, url, ds, demo) {
  var tao = taoDocTuUrl(pj, url);
  if (tao.loi) return tao;
  var doc = DocumentApp.openById(tao.id), body = doc.getBody();
  var ngCanh = { chuBai: tao.chuBai, tieuDe: tao.ten };
  var ketQua = [];
  ds.forEach(function (a) {
    var doan = docDoan(body), cach = null, lyDo = '';
    if (a.tyGia && demo) {
      cach = chenTheoDemo(body, doan, a, demo);
      if (cach === 'khong_thay') { ketQua.push({ anchor: a.anchor, ok: false, ly_do: 'không thấy câu gốc của cột Demo trong bài' }); return; }
      doan = docDoan(body);
    }
    if (!cach) cach = chenLinkCoSan(body, doan, a);
    if (!cach) cach = chenCumCoSan(body, doan, a);
    if (!cach) {
      var r = chenCauAI(body, docDoan(body), a, ngCanh);
      cach = r.cach || null; lyDo = r.ly_do || '';
    }
    ketQua.push({ anchor: a.anchor, ok: !!cach, cach: cach, ly_do: lyDo });
  });
  doc.saveAndClose();
  var soat = soatFile(DocumentApp.openById(tao.id).getBody(), ds);
  soat.forEach(function (s, i) {
    if (ketQua[i].ok && !s.ok) { ketQua[i].ok = false; ketQua[i].ly_do = 'soát lại không thấy link/tô vàng'; }
  });
  return { id: tao.id, ketQua: ketQua };
}

/** Chạy cho mọi dòng có URL mà cột FILE trống (lần lượt, dừng trước giới hạn thời gian). */
function chayChenLink() {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(1000)) return;
  var batDau = Date.now();
  try {
    DU_AN.filter(function (pj) { return pj.tuChay || chayChenLink.tatCa; }).forEach(function (pj) {
      var sh = moSheet(pj), m = banDoCot(pj, sh);
      var data = sh.getRange(1, 1, sh.getLastRow(), sh.getLastColumn()).getValues();
      for (var r = 2; r <= data.length; r++) {
        if ((Date.now() - batDau) / 1000 > GIOI_HAN_GIAY) return;
        var dong = data[r - 1], url = String(dong[m.url - 1]).trim();
        if (!/^https?:\/\//.test(url) || String(dong[m.file - 1]).trim()) continue;
        var g = anchorCuaDong(pj, m, dong);
        if (pj.boQuaDong(g.h)) continue;
        if (!g.ds.length) { nhatKy('Chèn link', pj.ten, r, 'bỏ qua: dòng không có anchor nào'); continue; }
        var demo = m.demo ? String(dong[m.demo - 1] || '') : '';
        var kq;
        try { kq = xuLyDong(pj, url, g.ds, demo); } catch (e) { kq = { loi: 'lỗi: ' + e.message }; }
        if (kq.loi) { nhatKy('Chèn link', pj.ten, r, kq.loi); continue; }
        var link = 'https://docs.google.com/document/d/' + kq.id + '/edit';
        ghiOTrong(sh, r, m.file, link);
        var e = ghiChuE(g.ds.length, kq.ketQua);
        if (g.thieuAnchor.length) e += '\nCó URL nhưng thiếu anchor, không chèn: ' + g.thieuAnchor.join(', ');
        if (m.ghiChu) ghiOTrong(sh, r, m.ghiChu, e);
        nhatKy('Chèn link', pj.ten, r, e);
      }
    });
  } finally { lock.releaseLock(); }
}

// ----- Gemini.gs -----
/**
 * Gemini.gs — phần duy nhất cần AI: chọn đoạn và viết 1 câu chứa anchor.
 * Khóa Gemini lưu trong "thuộc tính người dùng" của app (menu Inlink → Cài khóa Gemini), không nằm trong code/sheet.
 * Sổ bài học (BAI-HOC-GOP-Y.md) được tải mới mỗi lần chạy từ kho GitHub công khai → bài học mới tự vào lời dặn AI.
 */

var NGUON_BAI_HOC = [
  'https://raw.githubusercontent.com/vuthithuytrang-lab/trang/main/cong-cu/tao-docs-tu-url/BAI-HOC-GOP-Y.md',
  'https://raw.githubusercontent.com/vuthithuytrang-lab/trang/claude/confident-hopper-wh5wrt/cong-cu/tao-docs-tu-url/BAI-HOC-GOP-Y.md'
];

var QUY_TAC = [
  'Bạn là biên tập viên nội dung tiếng Việt cấp cao cho blog doanh nghiệp (ngân hàng / nội thất…).',
  'Nhiệm vụ: chèn MỘT internal link sao cho người đọc không nhận ra là câu chèn thêm.',
  'Quy tắc bắt buộc:',
  '- Câu viết ra phải chứa ANCHOR đúng nguyên văn, đúng hoa/thường, đúng 1 lần, là một phần tự nhiên của câu (tân ngữ/bổ ngữ), không phải nhãn treo.',
  '- Chỉ chọn đoạn ĐANG nói đúng chủ đề của trang đích. Nếu phải đổi chủ đề mới nhét được anchor thì chỗ đó sai.',
  '- Câu phải nối logic với câu ngay trước (nguyên nhân → hệ quả, bước trước → bước sau), cùng ngôi xưng (bạn / khách hàng / doanh nghiệp) và giọng của bài.',
  '- Câu phải nói rõ vì sao trang đích giúp người đọc ở đúng lúc này, cụ thể theo đoạn, không chung chung kiểu "tham khảo thêm".',
  '- Không bịa con số, lãi suất, phí, khuyến mãi, tính năng sản phẩm. Chỉ dùng điều có trong bài gốc hoặc thông tin trang đích được cung cấp.',
  '- Không so sánh trực diện sản phẩm. Không dấu chấm than, không câu hỏi tu từ, không từ quảng cáo.',
  '- Cấm các cụm: "Bên cạnh đó, bạn cũng có thể tham khảo", "Ngoài ra, bạn có thể tìm hiểu thêm", "để có thêm thông tin", "để hiểu rõ hơn", "một cách hiệu quả", "vô cùng", "hữu ích", "tham khảo ngay", "đừng quên", "chắc chắn", "tại đây".',
  '- cach = "sentence": 1 câu ngắn (≤ 35 từ) nối vào CUỐI đoạn đã chọn. cach = "xemthem": 1 dòng riêng sau đoạn, bắt đầu ">>> Xem thêm: " + cụm như tiêu đề bài có chứa anchor (≤ 20 từ). Anchor có chữ "2026", "hiện nay", "top", "tổng hợp", "các mẫu" thì nên dùng xemthem.',
  '- Nếu KHÔNG có đoạn nào thật sự hợp ngữ cảnh: trả về i = -1 và ly_do. Bỏ link tốt hơn chèn gượng (người duyệt đã nói rõ điều này).',
  'Chỉ trả về JSON: {"i": số đoạn, "cach": "sentence" | "xemthem", "cau": "câu tiếng Việt có dấu"} hoặc {"i": -1, "ly_do": "..."}'
].join('\n');

function baiHoc() {
  var c = CacheService.getScriptCache(), x = c.get('baiHoc');
  if (x) return x;
  for (var i = 0; i < NGUON_BAI_HOC.length; i++) {
    try {
      var r = UrlFetchApp.fetch(NGUON_BAI_HOC[i], { muteHttpExceptions: true });
      if (r.getResponseCode() === 200) { x = r.getContentText('UTF-8').slice(0, 20000); c.put('baiHoc', x, 21600); return x; }
    } catch (e) {}
  }
  return '';
}

function goiGemini(prompt) {
  var p = PropertiesService.getUserProperties();
  var key = p.getProperty('GEMINI_KEY');
  if (!key) throw new Error('Chưa cài khóa Gemini (menu Inlink → Cài khóa Gemini)');
  var model = p.getProperty('GEMINI_MODEL') || 'gemini-2.5-flash';
  var r = UrlFetchApp.fetch('https://generativelanguage.googleapis.com/v1beta/models/' + model + ':generateContent', {
    method: 'post', contentType: 'application/json', muteHttpExceptions: true,
    headers: { 'x-goog-api-key': key },
    payload: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { responseMimeType: 'application/json', temperature: 0.4 } })
  });
  if (r.getResponseCode() !== 200) throw new Error('Gemini trả lỗi ' + r.getResponseCode() + ': ' + r.getContentText().slice(0, 300));
  var j = JSON.parse(r.getContentText());
  var t = j.candidates && j.candidates[0] && j.candidates[0].content.parts.map(function (x) { return x.text || ''; }).join('');
  return JSON.parse(String(t).replace(/^```json\s*|```\s*$/g, ''));
}

/** Thông tin trang đích (tiêu đề + mô tả + đoạn đầu) để AI biết link dẫn tới đâu. */
function thongTinDich(url) {
  var c = CacheService.getScriptCache(), k = 'dich_' + Utilities.base64EncodeWebSafe(url).slice(0, 200), x = c.get(k);
  if (x) return x;
  var s = 'Trang đích: ' + url;
  try {
    var t = taiTrang(url.replace('//techcombank.com', '//www.techcombank.com'));
    if (t.ma === 200) {
      var info = layThongTinTrang(t.html);
      var h2 = (t.html.match(/<h2[^>]*>[\s\S]*?<\/h2>/gi) || []).slice(0, 8).map(function (h) { return chuanHoa(h.replace(/<[^>]+>/g, '')); });
      s += '\nTiêu đề: ' + info.title + '\nMô tả: ' + info.meta + '\nCác mục: ' + h2.join(' | ');
    }
  } catch (e) {}
  c.put(k, s, 21600);
  return s;
}

/** Hỏi AI chỗ chèn + câu; tự soát, sai thì hỏi lại 1 lần kèm lý do. */
function aiChonCho(a, doan, pct, ung, ngCanh) {
  var ds = ung.map(function (i) { return '[' + i + '] (' + Math.round(pct[i]) + '%) ' + doan[i].text.slice(0, 450); }).join('\n');
  var dich = thongTinDich(a.url);
  var hoi = QUY_TAC + '\n\nSỔ BÀI HỌC TỪ NGƯỜI DUYỆT (phải tránh):\n' + baiHoc() +
    '\n\nBÀI: ' + ngCanh.tieuDe + '\nANCHOR: "' + a.anchor + '"\n' + dich +
    '\n\nCÁC ĐOẠN ĐƯỢC PHÉP CHÈN (số trong ngoặc vuông là i):\n' + ds;
  var lyDo = '';
  for (var lan = 0; lan < 2; lan++) {
    var g;
    try { g = goiGemini(hoi + (lyDo ? '\n\nLần trước bị loại vì: ' + lyDo + '. Viết lại.' : '')); }
    catch (e) { return { ok: false, ly_do: e.message }; }
    if (g.i === -1 || g.i === '-1') return { ok: false, ly_do: 'AI thấy không có chỗ hợp ngữ cảnh: ' + (g.ly_do || '') };
    var i = parseInt(g.i, 10);
    if (ung.indexOf(i) < 0) { lyDo = 'i không nằm trong danh sách được phép'; continue; }
    var cau = chuanHoa(g.cau || '');
    var cach = g.cach === 'xemthem' ? 'xemthem' : 'sentence';
    if (cach === 'xemthem' && cau.indexOf('>>>') !== 0) cau = '>>> Xem thêm: ' + cau;
    lyDo = kiemTraCauChen(cau, a.anchor, ngCanh.chuBai + ' ' + dich);
    if (!lyDo) return { ok: true, i: i, cach: cach, cau: cau };
  }
  return { ok: false, ly_do: 'câu AI viết không đạt: ' + lyDo };
}

// ----- GopY.gs -----
/**
 * GopY.gs — sổ góp ý người duyệt + gửi phản hồi THẲNG dưới comment (Drive API, thay cho cách thêm comment mới).
 * Tab "Sổ góp ý" trong sheet Techcombank: mỗi comment 1 dòng (không trùng). Điền cột "Phản hồi" → app tự trả lời dưới comment đó.
 */

var COT_GOP_Y = ['Ngày ghi', 'Dự án', 'Dòng', 'Bài', 'Comment ID', 'Doc ID', 'Đoạn được comment', 'Nhận xét', 'Trạng thái',
  'Nhóm lỗi', 'Phản hồi (điền để app gửi)', 'Đã gửi'];

function tabGopY() {
  var ss = SpreadsheetApp.openById(DU_AN[0].sheetId);
  var t = ss.getSheetByName(TAB_GOP_Y);
  if (!t) { t = ss.insertSheet(TAB_GOP_Y); t.appendRow(COT_GOP_Y); t.setFrozenRows(1); }
  return t;
}

var NHOM_LOI = 'A sai ngữ cảnh đoạn | B chèn gượng | C chen giữa câu/liệt kê | D sai nghiệp vụ/sản phẩm/đối tượng | E so sánh trực diện | F sai vị trí trong bài | G lỗi bài gốc | H chính tả';

function phanNhom(nhanXet) {
  try {
    var g = goiGemini('Phân loại nhận xét của người duyệt nội dung vào đúng 1 nhóm: ' + NHOM_LOI +
      '\nNhận xét: "' + nhanXet + '"\nChỉ trả JSON {"nhom":"A-sai-ngu-canh"} (chữ cái + tên ngắn không dấu).');
    return g.nhom || '';
  } catch (e) { return ''; }
}

/** Quét comment mới của người duyệt ở mọi dòng có cột duyệt ≠ "ok". */
function quetGopY() {
  var t = tabGopY();
  var daCo = {};
  if (t.getLastRow() > 1) t.getRange(2, 5, t.getLastRow() - 1, 1).getValues().forEach(function (x) { daCo[x[0]] = 1; });
  var moi = 0;
  DU_AN.forEach(function (pj) {
    var sh = moSheet(pj), m = banDoCot(pj, sh);
    if (!m.duyet) return;
    var data = sh.getRange(1, 1, sh.getLastRow(), sh.getLastColumn()).getValues();
    for (var r = 2; r <= data.length; r++) {
      var dong = data[r - 1], duyet = String(dong[m.duyet - 1]).trim(), id = idTuLink(dong[m.file - 1]);
      if (!duyet || /^ok$/i.test(duyet) || !id) continue;
      var bai = slugCua(dong[m.url - 1]);
      if (!/cần s|câần|cầ̀n|đã sửa/i.test(duyet)) {         // ghi chú viết thẳng trong ô duyệt
        var kid = 'O' + r + '-' + Utilities.base64EncodeWebSafe(Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, duyet)).slice(0, 8);
        if (!daCo[kid]) { t.appendRow([new Date(), pj.ten, r, bai, kid, id, '(ô duyệt trên sheet)', duyet, 'ghi chú ô', phanNhom(duyet), '', '']); daCo[kid] = 1; moi++; }
      }
      var res;
      try {
        res = Drive.Comments.list(id, { pageSize: 100, fields: 'comments(id,content,author(displayName),quotedFileContent(value),resolved,createdTime)' });
      } catch (e) { nhatKy('Quét góp ý', pj.ten, r, 'không đọc được comment: ' + e.message); continue; }
      (res.comments || []).forEach(function (c) {
        if (daCo[c.id] || !c.author || c.author.displayName.indexOf(pj.nguoiDuyet) < 0) return;
        t.appendRow([new Date(c.createdTime), pj.ten, r, bai, c.id, id, (c.quotedFileContent && c.quotedFileContent.value || '').slice(0, 300),
          c.content, c.resolved ? 'đã đóng' : 'mở', phanNhom(c.content), '', '']);
        daCo[c.id] = 1; moi++;
      });
    }
  });
  nhatKy('Quét góp ý', 'tất cả', '', 'thêm ' + moi + ' nhận xét mới');
  return moi;
}

/** Gửi mọi phản hồi đã điền mà chưa gửi — trả lời ngay dưới comment gốc. */
function guiPhanHoi() {
  var t = tabGopY();
  if (t.getLastRow() < 2) return 0;
  var v = t.getRange(2, 1, t.getLastRow() - 1, COT_GOP_Y.length).getValues(), gui = 0;
  v.forEach(function (x, k) {
    var cid = String(x[4]), doc = String(x[5]), noiDung = String(x[10]).trim(), daGui = String(x[11]).trim();
    if (!noiDung || daGui || /^O\d/.test(cid)) return;
    try {
      Drive.Replies.create({ content: noiDung }, doc, cid, { fields: 'id' });
      t.getRange(k + 2, 12).setValue(new Date()); gui++;
    } catch (e) { t.getRange(k + 2, 12).setValue('lỗi: ' + e.message); }
  });
  nhatKy('Gửi phản hồi', 'tất cả', '', 'đã gửi ' + gui + ' phản hồi');
  return gui;
}

function chayHangNgay() { quetGopY(); guiPhanHoi(); }

// ----- Main.gs -----
/** Main.gs — menu "Inlink" trên sheet + cài lịch tự chạy. */

function onOpen() {
  SpreadsheetApp.getUi().createMenu('🔗 Inlink')
    .addItem('Chèn link cho các dòng còn trống', 'menuChenLink')
    .addItem('Chèn link — dòng đang chọn', 'menuThu1Dong')
    .addItem('Chạy thử dòng đang chọn (không ghi sheet, để so sánh)', 'menuThuKhongGhi')
    .addSeparator()
    .addItem('Quét góp ý chị Lộc', 'menuQuetGopY')
    .addItem('Gửi phản hồi comment', 'menuGuiPhanHoi')
    .addSeparator()
    .addItem('Cài khóa Gemini', 'caiKhoaGemini')
    .addItem('Cài lịch tự chạy', 'caiLich')
    .addToUi();
}

function baoXong(s) { try { SpreadsheetApp.getActive().toast(s, 'Inlink', 8); } catch (e) {} }

function menuChenLink() { chayChenLink.tatCa = true; chayChenLink(); chayChenLink.tatCa = false; baoXong('Đã chạy xong — xem tab "' + TAB_NHAT_KY + '"'); }
function menuQuetGopY() { baoXong('Thêm ' + quetGopY() + ' nhận xét mới vào tab "' + TAB_GOP_Y + '"'); }
function menuGuiPhanHoi() { baoXong('Đã gửi ' + guiPhanHoi() + ' phản hồi'); }

/** Chạy thử đúng dòng đang chọn trên sheet (không ghi đè ô đã có). */
function menuThu1Dong() {
  var sh = SpreadsheetApp.getActiveSheet(), r = sh.getActiveRange().getRow();
  var pj = DU_AN.filter(function (p) { return p.sheetId === sh.getParent().getId() && p.tab === sh.getName(); })[0];
  if (!pj) { baoXong('Tab này chưa có trong cấu hình'); return; }
  var m = banDoCot(pj, sh), dong = sh.getRange(r, 1, 1, sh.getLastColumn()).getValues()[0];
  var url = String(dong[m.url - 1]).trim(), g = anchorCuaDong(pj, m, dong);
  if (String(dong[m.file - 1]).trim()) { baoXong('Dòng ' + r + ' đã có file'); return; }
  var kq = xuLyDong(pj, url, g.ds, m.demo ? String(dong[m.demo - 1] || '') : '');
  if (kq.loi) { nhatKy('Thử 1 dòng', pj.ten, r, kq.loi); baoXong(kq.loi); return; }
  ghiOTrong(sh, r, m.file, 'https://docs.google.com/document/d/' + kq.id + '/edit');
  var e = ghiChuE(g.ds.length, kq.ketQua);
  if (m.ghiChu) ghiOTrong(sh, r, m.ghiChu, e);
  nhatKy('Thử 1 dòng', pj.ten, r, e);
  baoXong('Xong dòng ' + r);
}

/** Tạo file thử cho dòng đang chọn kể cả khi đã có file; KHÔNG ghi sheet. Link file thử ghi ở tab Nhật ký app. */
function menuThuKhongGhi() {
  var sh = SpreadsheetApp.getActiveSheet(), r = sh.getActiveRange().getRow();
  var pj = DU_AN.filter(function (p) { return p.sheetId === sh.getParent().getId() && p.tab === sh.getName(); })[0];
  if (!pj) { baoXong('Tab này chưa có trong cấu hình'); return; }
  var m = banDoCot(pj, sh), dong = sh.getRange(r, 1, 1, sh.getLastColumn()).getValues()[0];
  var g = anchorCuaDong(pj, m, dong);
  var kq = xuLyDong(pj, String(dong[m.url - 1]).trim(), g.ds, m.demo ? String(dong[m.demo - 1] || '') : '');
  var s = kq.loi ? kq.loi : 'FILE THỬ: https://docs.google.com/document/d/' + kq.id + '/edit\n' + ghiChuE(g.ds.length, kq.ketQua);
  nhatKy('Chạy thử (không ghi sheet)', pj.ten, r, s);
  baoXong('Xong — link file thử ở tab "' + TAB_NHAT_KY + '"');
}

function caiKhoaGemini() {
  var ui = SpreadsheetApp.getUi();
  var r = ui.prompt('Khóa Gemini', 'Dán khóa Gemini (lấy miễn phí ở aistudio.google.com → Get API key). Khóa chỉ lưu trong tài khoản của bạn, không hiện trên sheet.', ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK || !r.getResponseText().trim()) return;
  PropertiesService.getUserProperties().setProperty('GEMINI_KEY', r.getResponseText().trim());
  try { goiGemini('Trả JSON {"ok":true}'); baoXong('Khóa Gemini hoạt động tốt ✓'); }
  catch (e) { ui.alert('Khóa chưa dùng được: ' + e.message); }
}

/** Mỗi giờ: tạo file cho dòng mới (dự án tuChay). Mỗi ngày 16:47: quét góp ý + gửi phản hồi. */
function caiLich() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (['chayChenLink', 'chayHangNgay'].indexOf(t.getHandlerFunction()) >= 0) ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('chayChenLink').timeBased().everyHours(1).create();
  ScriptApp.newTrigger('chayHangNgay').timeBased().atHour(16).nearMinute(47).everyDays(1).inTimezone('Asia/Ho_Chi_Minh').create();
  baoXong('Đã cài lịch: chèn link mỗi giờ, quét góp ý mỗi ngày lúc ~16:47');
}

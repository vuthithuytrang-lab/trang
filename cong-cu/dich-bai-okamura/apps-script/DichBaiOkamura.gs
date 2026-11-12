/**
 * DỊCH BÀI OKAMURA VIỆT → ANH — chạy trong Google Sheet, không cần Claude.
 *
 * Bấm menu "🌐 Dịch bài Okamura" → "Dịch bài theo link Doc…" → dán link Google Doc → chờ 1-3 phút.
 * Kết quả: trong Doc có thêm tab "Bản dịch EN" (trang ngang, bảng 2 cột: trái bản Việt, phải bản Anh).
 * Tab tiếng Việt gốc KHÔNG bị sửa.
 *
 * Máy dịch:
 *  - Mặc định: Google Dịch (miễn phí, không cần cài gì).
 *  - Tốt hơn (vẫn miễn phí): Gemini. Vào menu "Cài khóa Gemini (tuỳ chọn)" và dán khóa lấy ở
 *    https://aistudio.google.com/apikey . Gemini dịch tự nhiên hơn, theo checklist SEO.
 *
 * Cần bật 1 dịch vụ: trong trình sửa Apps Script → "Dịch vụ" (Services) → thêm "Google Docs API".
 */

var TEN_TAB = 'Bản dịch EN';
var GEMINI_MODEL_MAC_DINH = 'gemini-2.5-flash';

function onOpen() {
  SpreadsheetApp.getUi().createMenu('🌐 Dịch bài Okamura')
    .addItem('Dịch bài theo link Doc…', 'menuDichTheoLink')
    .addItem('Dịch bài ở dòng đang chọn (cột W)', 'menuDichDongDangChon')
    .addSeparator()
    .addItem('Cài khóa Gemini (tuỳ chọn)', 'menuCaiKhoaGemini')
    .addToUi();
}

// ---------------- MENU ----------------
function menuDichTheoLink() {
  var ui = SpreadsheetApp.getUi();
  var r = ui.prompt('Dịch bài Okamura', 'Dán link Google Doc bài tiếng Việt:', ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK) return;
  chayDich_(r.getResponseText());
}

function menuDichDongDangChon() {
  var sh = SpreadsheetApp.getActiveSheet();
  var row = sh.getActiveRange().getRow();
  var cell = sh.getRange(row, 23); // cột W
  var link = null;
  var rt = cell.getRichTextValue();
  if (rt) {
    link = rt.getLinkUrl();
    if (!link) rt.getRuns().forEach(function (x) { if (!link && x.getLinkUrl()) link = x.getLinkUrl(); });
  }
  if (!link && /docs\.google\.com/.test(cell.getDisplayValue())) link = cell.getDisplayValue();
  if (!link) {
    // ô dạng "chip" — Apps Script không đọc được link trong chip, nhờ dán tay
    var ui = SpreadsheetApp.getUi();
    var r = ui.prompt('Không đọc được link trong ô W' + row,
      'Bấm vào ô đó, copy link Doc rồi dán vào đây:', ui.ButtonSet.OK_CANCEL);
    if (r.getSelectedButton() !== ui.Button.OK) return;
    link = r.getResponseText();
  }
  chayDich_(link);
}

function menuCaiKhoaGemini() {
  var ui = SpreadsheetApp.getUi();
  var r = ui.prompt('Khóa Gemini (miễn phí)',
    'Dán khóa lấy ở aistudio.google.com/apikey. Để trống rồi OK = xoá khóa, quay về Google Dịch.',
    ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK) return;
  var k = r.getResponseText().trim();
  var p = PropertiesService.getUserProperties();
  if (k) { p.setProperty('GEMINI_KEY', k); ui.alert('Đã lưu khóa. Từ giờ dùng Gemini để dịch.'); }
  else { p.deleteProperty('GEMINI_KEY'); ui.alert('Đã xoá khóa. Dùng Google Dịch.'); }
}

// ---------------- CHÍNH ----------------
function chayDich_(link) {
  var ui = SpreadsheetApp.getUi();
  var m = String(link).match(/\/d\/([a-zA-Z0-9_-]{20,})/);
  if (!m) { ui.alert('Link không đúng dạng Google Doc.'); return; }
  var docId = m[1];
  if (typeof Docs === 'undefined') {
    ui.alert('Chưa bật dịch vụ "Google Docs API".\nVào Tiện ích mở rộng → Apps Script → Dịch vụ (+) → chọn Google Docs API → Thêm.');
    return;
  }
  SpreadsheetApp.getActive().toast('Đang dịch… (1-3 phút)', 'Dịch bài Okamura', 300);
  var kq = dichBai(docId);
  SpreadsheetApp.getActive().toast('Xong!', 'Dịch bài Okamura', 5);
  ui.alert('Xong bản dịch (' + kq.may + ')\n\n' + kq.url + '\n\n' + (kq.ghiChu.length ? 'Lưu ý:\n- ' + kq.ghiChu.join('\n- ') : '') +
    '\n\nNhớ đọc soát lại bản Anh trước khi gửi khách.');
}

function dichBai(docId) {
  var ghiChu = [];
  var doc = DocumentApp.openById(docId);
  var tabs = doc.getTabs();
  var nguon = tabs[0].asDocumentTab().getBody();

  // Tên tab không trùng
  var ten = TEN_TAB, n = 2;
  var tenCo = tabs.map(function (t) { return t.getTitle(); });
  while (tenCo.indexOf(ten) >= 0) ten = TEN_TAB + ' (' + (n++) + ')';

  // 1) Tạo tab mới + xoay ngang
  var res = Docs.Documents.batchUpdate({ requests: [{ addDocumentTab: { tabProperties: { title: ten } } }] }, docId);
  var tabId = res.replies[0].addDocumentTab.tabProperties.tabId;
  Docs.Documents.batchUpdate({ requests: [{ updateDocumentStyle: {
    documentStyle: { flipPageOrientation: true }, fields: 'flipPageOrientation', tabId: tabId } }] }, docId);

  doc = DocumentApp.openById(docId);
  var body = doc.getTab(tabId).asDocumentTab().getBody();
  var bang = body.appendTable([['', '']]);
  var oTrai = bang.getCell(0, 0), oPhai = bang.getCell(0, 1);

  // 2) Chép nguyên bản Việt sang cả 2 ô
  saoChep_(nguon, oTrai);
  saoChep_(nguon, oPhai);
  doc.saveAndClose();

  // 3) Dịch ô phải
  doc = DocumentApp.openById(docId);
  body = doc.getTab(tabId).asDocumentTab().getBody();
  oPhai = body.getTables()[0].getCell(0, 1);
  var viec = [];
  thuThapText_(oPhai, viec);
  var html = viec.map(function (v) { return v.html; });
  var dich = dichNhieu_(html, ghiChu);
  for (var i = 0; i < viec.length; i++) ghiLai_(viec[i], dich[i]);

  // 4) Luật checklist
  apChecklist_(oPhai, ghiChu);
  doc.saveAndClose();

  return { url: 'https://docs.google.com/document/d/' + docId + '/edit?tab=' + tabId,
           may: PropertiesService.getUserProperties().getProperty('GEMINI_KEY') ? 'Gemini' : 'Google Dịch',
           ghiChu: ghiChu };
}

function saoChep_(nguon, o) {
  for (var i = 0; i < nguon.getNumChildren(); i++) {
    var el = nguon.getChild(i), t = el.getType();
    if (t === DocumentApp.ElementType.PARAGRAPH) o.appendParagraph(el.copy());
    else if (t === DocumentApp.ElementType.LIST_ITEM) o.appendListItem(el.copy());
    else if (t === DocumentApp.ElementType.TABLE) o.appendTable(el.copy());
  }
  // bỏ đoạn trống có sẵn đầu ô
  var dau = o.getChild(0);
  if (o.getNumChildren() > 1 && dau.getType() === DocumentApp.ElementType.PARAGRAPH && dau.asParagraph().getText() === '' &&
      dau.asParagraph().getNumChildren() === 0) dau.removeFromParent();
}

// ---------------- CHUYỂN ĐỊNH DẠNG <-> HTML ----------------
function esc_(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function unesc_(s) {
  return s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/&#(\d+);/g, function (_, d) { return String.fromCharCode(+d); }).replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&');
}

function thuThapText_(el, out) {
  var t = el.getType();
  if (t === DocumentApp.ElementType.TEXT) {
    var txt = el.asText(), s = txt.getText();
    if (!s.trim()) return;
    var idx = txt.getTextAttributeIndices(), links = [], h = '';
    for (var k = 0; k < idx.length; k++) {
      var a = idx[k], b = k + 1 < idx.length ? idx[k + 1] : s.length;
      var part = esc_(s.substring(a, b));
      var url = txt.getLinkUrl(a);
      if (url) { links.push(url); part = '<a id="' + (links.length - 1) + '">' + part + '</a>'; }
      if (txt.isItalic(a)) part = '<i>' + part + '</i>';
      if (txt.isBold(a)) part = '<b>' + part + '</b>';
      h += part;
    }
    h = h.replace(/<\/b><b>/g, '').replace(/<\/i><i>/g, '');
    out.push({ el: txt, html: h, links: links });
    return;
  }
  if (el.getNumChildren) for (var i = 0; i < el.getNumChildren(); i++) thuThapText_(el.getChild(i), out);
}

function ghiLai_(v, html) {
  if (!html) return;
  var runs = [], b = 0, it = 0, link = null, re = /<(\/?)(b|i|a)(?:\s+id="?(\d+)"?)?\s*>|([^<]+)|</g, m;
  while ((m = re.exec(html))) {
    if (m[4] !== undefined || m[0] === '<') { runs.push({ t: unesc_(m[4] || '<'), b: b > 0, i: it > 0, link: link }); continue; }
    var dong = m[1] === '/';
    if (m[2] === 'b') b += dong ? -1 : 1;
    else if (m[2] === 'i') it += dong ? -1 : 1;
    else link = dong ? null : (v.links[+m[3]] || v.links[0] || null);
  }
  var plain = runs.map(function (r) { return r.t; }).join('');
  if (!plain) return;
  var t = v.el;
  t.setText(plain);
  var end = plain.length - 1;
  t.setAttributes(0, end, kieuTrang_());
  var p = 0;
  runs.forEach(function (r) {
    if (!r.t) return;
    var a = p, z = p + r.t.length - 1; p += r.t.length;
    if (r.b) t.setBold(a, z, true);
    if (r.i) t.setItalic(a, z, true);
    if (r.link) t.setLinkUrl(a, z, r.link).setUnderline(a, z, true).setForegroundColor(a, z, '#1155cc');
  });
}

function kieuTrang_() {
  var a = {}, A = DocumentApp.Attribute;
  a[A.BOLD] = false; a[A.ITALIC] = false; a[A.UNDERLINE] = false; a[A.LINK_URL] = null; a[A.FOREGROUND_COLOR] = null;
  return a;
}

// ---------------- MÁY DỊCH ----------------
function dichNhieu_(arr, ghiChu) {
  var key = PropertiesService.getUserProperties().getProperty('GEMINI_KEY');
  if (key) {
    try { return dichGemini_(arr, key); }
    catch (e) { ghiChu.push('Gemini lỗi (' + String(e).slice(0, 120) + ') → đã chuyển sang Google Dịch.'); }
  }
  return arr.map(function (h) {
    try { return LanguageApp.translate(h, 'vi', 'en', { contentType: 'html' }); }
    catch (e) { Utilities.sleep(1500); return LanguageApp.translate(h, 'vi', 'en', { contentType: 'html' }); }
  });
}

var LUAT_DICH =
  'You translate Vietnamese SEO articles for Okamura (Japanese premium office furniture brand) into natural, fluent US English.\n' +
  'Input: a JSON array of HTML fragments. Output: ONLY a JSON array of the same length, same order, each item the English translation.\n' +
  'Rules:\n- Keep every tag <b>, <i>, <a id="N"> exactly, around the matching translated words. Do not add or remove tags.\n' +
  '- Product names (Legender, Contessa II, Choral, Sylphy, Finora, DN Mobile, KD Storage System, Personal Locker...) and brand names stay unchanged.\n' +
  '- Headings: sentence case (capitalize only the first word and proper nouns; after " - " capitalize if the source does). Keep numbering like "2.1." and "1 - ".\n' +
  '- Use "..." instead of "etc". Color names in lowercase. Decimal point (658,5 -> 658.5).\n' +
  '- Vietnam addresses: transliterate without diacritics (Liễu Giai -> Lieu Giai Street, TP. Hồ Chí Minh -> Ho Chi Minh City).\n' +
  '- Use one consistent English keyword for the article topic. "Tóm tắt nội dung chính bài viết:" = "Key takeaways:".\n' +
  '- Translate faithfully, do not add or drop information.';

function dichGemini_(arr, key) {
  var model = PropertiesService.getUserProperties().getProperty('GEMINI_MODEL') || GEMINI_MODEL_MAC_DINH;
  var out = [], CHUNK = 40;
  for (var s = 0; s < arr.length; s += CHUNK) {
    var phan = arr.slice(s, s + CHUNK);
    var resp = UrlFetchApp.fetch('https://generativelanguage.googleapis.com/v1beta/models/' + model + ':generateContent', {
      method: 'post', contentType: 'application/json', muteHttpExceptions: true,
      headers: { 'x-goog-api-key': key },
      payload: JSON.stringify({
        systemInstruction: { parts: [{ text: LUAT_DICH }] },
        contents: [{ role: 'user', parts: [{ text: JSON.stringify(phan) }] }],
        generationConfig: { temperature: 0.2, responseMimeType: 'application/json' }
      })
    });
    if (resp.getResponseCode() !== 200) throw new Error('HTTP ' + resp.getResponseCode() + ' ' + resp.getContentText().slice(0, 200));
    var txt = JSON.parse(resp.getContentText()).candidates[0].content.parts.map(function (p) { return p.text || ''; }).join('');
    var mang = JSON.parse(txt.replace(/^```(json)?|```$/g, '').trim());
    if (!Array.isArray(mang) || mang.length !== phan.length) throw new Error('Gemini trả về sai số đoạn');
    out = out.concat(mang.map(String));
  }
  return out;
}

// ---------------- CHECKLIST ----------------
function apChecklist_(o, ghiChu) {
  var C = DocumentApp.ElementType, H = DocumentApp.ParagraphHeading;
  // etc -> ...
  o.replaceText('\\s*,?\\s*\\betc\\b\\.?', '...');
  duyetDoan_(o, function (p) {
    p.setLineSpacing(1.5).setSpacingBefore(10).setSpacingAfter(10);
    var txt = p.editAsText(), s = txt.getText();
    // link okamura /vi/ -> bản Anh
    var idx = txt.getTextAttributeIndices();
    for (var k = 0; k < idx.length; k++) {
      var u = s.length ? txt.getLinkUrl(idx[k]) : null;
      if (u && /okamura\.com\.vn\/vi(\/|$)/.test(u)) {
        var z = (k + 1 < idx.length ? idx[k + 1] : s.length) - 1;
        txt.setLinkUrl(idx[k], z, u.replace(/(okamura\.com\.vn)\/vi(\/|$)/, '$1/'));
      }
    }
    if (!s.trim()) return;
    var hd = p.getHeading();
    if (hd !== H.NORMAL) { txt.setBold(0, s.length - 1, false); return; }
    if (p.getAlignment() === DocumentApp.HorizontalAlignment.CENTER) {
      // chú thích ảnh: nghiêng, bỏ link Drive, có dấu chấm
      txt.setItalic(0, s.length - 1, true);
      for (var j = 0; j < s.length; j++) {
        var lu = txt.getLinkUrl(j);
        if (lu && /drive\.google\.com|wixstatic\.com/.test(lu)) {
          var a0 = {}; a0[DocumentApp.Attribute.LINK_URL] = null; a0[DocumentApp.Attribute.UNDERLINE] = false;
          a0[DocumentApp.Attribute.FOREGROUND_COLOR] = null; txt.setAttributes(j, j, a0);
        }
      }
      var tr = s.replace(/\s+$/, '');
      if (tr && !/[.!?]$/.test(tr)) {
        if (tr.length < s.length) txt.deleteText(tr.length, s.length - 1);
        txt.appendText('.'); txt.setItalic(tr.length, tr.length, true);
      }
    }
  });
  // xoá dòng trống thừa (không chữ, không ảnh)
  for (var i = o.getNumChildren() - 2; i >= 0; i--) {
    var el = o.getChild(i);
    if ((el.getType() === C.PARAGRAPH || el.getType() === C.LIST_ITEM) && !el.asText().getText().trim() &&
        !el.findElement(C.INLINE_IMAGE) && (i + 1 < o.getNumChildren() && o.getChild(i + 1).getType() !== C.TABLE)) {
      try { el.removeFromParent(); } catch (e) {}
    }
  }
}

function duyetDoan_(el, fn) {
  var t = el.getType();
  if (t === DocumentApp.ElementType.PARAGRAPH || t === DocumentApp.ElementType.LIST_ITEM) { fn(el); return; }
  if (el.getNumChildren) for (var i = 0; i < el.getNumChildren(); i++) duyetDoan_(el.getChild(i), fn);
}

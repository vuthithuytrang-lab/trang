/**
 * TRUNG TÂM DỊCH BÀI VIỆT → ANH — chạy trong Google Sheet, dùng cho nhiều dự án, không cần Claude.
 *
 * Bảng "Cài đặt dự án": mỗi dòng 1 dự án — file Sheet danh sách bài, tab, cột link Doc, cột duyệt,
 * cột ghi link bản dịch... Công cụ tự quét: dòng nào có link Doc + đã duyệt + cột kết quả còn trống
 * → dịch, tạo tab "Bản dịch EN" (trang ngang, bảng 2 cột Việt | Anh) trong chính Doc đó, rồi ghi link vào cột kết quả.
 * Tab tiếng Việt gốc KHÔNG bị sửa.
 *
 * Máy dịch: Gemini (miễn phí, chìa ở aistudio.google.com/apikey) — lỗi/hết lượt thì tự chuyển Google Dịch.
 * Cần bật 2 dịch vụ trong trình sửa Apps Script: "Google Docs API" và "Google Sheets API".
 */

var TEN_TAB = 'Bản dịch EN';
var TAB_CAI_DAT = 'Cài đặt dự án';
var TAB_NHAT_KY = 'Nhật ký dịch';
var GEMINI_MODELS = ['gemini-flash-latest', 'gemini-2.5-flash', 'gemini-2.0-flash']; // thử lần lượt
var GIOI_HAN_GIAY = 270; // Google cho chạy tối đa 6 phút/lượt — dừng sớm để an toàn, phần còn lại chạy lượt sau

var COT_CAI_DAT = ['Bật', 'Tên dự án', 'Link file Sheet danh sách bài', 'Tên tab', 'Dòng tiêu đề (số)',
  'Cột link Doc', 'Cột duyệt', 'Giá trị được coi là duyệt', 'Cột từ khóa', 'Cột ghi link bản dịch',
  'Đổi link: tìm', 'Đổi link: thay bằng', 'Giới thiệu thương hiệu (cho máy dịch)', 'Bỏ qua nếu cột này đã có chữ'];
var MAU_OKAMURA = [true, 'Okamura', 'https://docs.google.com/spreadsheets/d/1ednWlho_Iw1ANJdwf6wD6ed_JhZpwt68f-worBBc0So/edit',
  '2. Danh sách bài SEO | 2026', 1, 'W', 'Z', 'Duyệt', 'B', 'AP', 'okamura.com.vn/vi/', 'okamura.com.vn/',
  'Okamura — Japanese premium office furniture brand (office chairs, desks, storage) in Vietnam', 'AG'];

function onOpen() {
  SpreadsheetApp.getUi().createMenu('🌐 Dịch bài')
    .addItem('① Tạo bảng cài đặt dự án', 'menuTaoBangCaiDat')
    .addItem('② Cài khóa Gemini', 'menuCaiKhoaGemini')
    .addSeparator()
    .addItem('Dịch tất cả bài chờ dịch', 'menuDichTatCa')
    .addItem('Dịch 1 bài theo link Doc…', 'menuDichTheoLink')
    .addSeparator()
    .addItem('Bật tự chạy mỗi tối (22h)', 'menuBatTuChay')
    .addItem('Tắt tự chạy', 'menuTatTuChay')
    .addToUi();
}

// ---------------- CÀI ĐẶT ----------------
function menuTaoBangCaiDat() {
  var ss = SpreadsheetApp.getActive(), sh = ss.getSheetByName(TAB_CAI_DAT);
  if (!sh) {
    sh = ss.insertSheet(TAB_CAI_DAT);
    sh.getRange(1, 1, 1, COT_CAI_DAT.length).setValues([COT_CAI_DAT]).setFontWeight('bold')
      .setBackground('#004AEF').setFontColor('#ffffff').setWrap(true);
    sh.getRange(2, 1, 1, MAU_OKAMURA.length).setValues([MAU_OKAMURA]);
    sh.getRange('A2:A50').insertCheckboxes();
    sh.setFrozenRows(1); sh.setColumnWidths(1, COT_CAI_DAT.length, 150); sh.setColumnWidth(1, 50);
    sh.getRange(4, 2).setValue('Ghi chú: Cột = chữ cái cột (W, Z, AP...). "Cột duyệt" để trống = chỉ cần có link là dịch. ' +
      '"Cột ghi link bản dịch" phải là cột trống — dòng nào đã có chữ ở cột này sẽ được bỏ qua (không dịch trùng). ' +
      '"Bỏ qua nếu cột này đã có chữ": ví dụ cột link bài đăng tiếng Anh — bài đã đăng bản Anh thì không dịch lại. ' +
      'Thêm dự án mới: điền 1 dòng mới, tích ô "Bật".').setFontColor('#666666');
  }
  if (!ss.getSheetByName(TAB_NHAT_KY)) {
    ss.insertSheet(TAB_NHAT_KY).getRange(1, 1, 1, 5).setValues([['Thời gian', 'Dự án', 'Dòng', 'Kết quả', 'Ghi chú']])
      .setFontWeight('bold');
  }
  ss.setActiveSheet(sh);
  SpreadsheetApp.getUi().alert('Đã tạo bảng "' + TAB_CAI_DAT + '". Dòng 2 là mẫu dự án Okamura — kiểm tra lại từng ô rồi điền thêm dự án khác nếu cần.');
}

function menuCaiKhoaGemini() {
  var ui = SpreadsheetApp.getUi();
  var r = ui.prompt('Khóa Gemini (miễn phí)',
    'Dán khóa lấy ở aistudio.google.com/apikey. Để trống rồi OK = xoá khóa, dùng Google Dịch.', ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK) return;
  var k = r.getResponseText().trim(), p = PropertiesService.getUserProperties();
  if (k) { p.setProperty('GEMINI_KEY', k); ui.alert('Đã lưu khóa. Từ giờ dùng Gemini để dịch.'); }
  else { p.deleteProperty('GEMINI_KEY'); ui.alert('Đã xoá khóa. Dùng Google Dịch.'); }
}

function docCaiDat_() {
  var sh = SpreadsheetApp.getActive().getSheetByName(TAB_CAI_DAT);
  if (!sh) throw new Error('Chưa có bảng cài đặt — bấm menu "① Tạo bảng cài đặt dự án".');
  var v = sh.getDataRange().getValues(), out = [];
  for (var i = 1; i < v.length; i++) {
    var r = v[i];
    if (r[0] !== true || !r[2]) continue;
    out.push({ ten: String(r[1]), sheetUrl: String(r[2]), tab: String(r[3]), dongTieuDe: Number(r[4]) || 1,
      cotLink: String(r[5]).trim(), cotDuyet: String(r[6]).trim(), giaTriDuyet: String(r[7]).trim(),
      cotTuKhoa: String(r[8]).trim(), cotKetQua: String(r[9]).trim(),
      doiLink: [{ tim: String(r[10]).trim(), thay: String(r[11]).trim() }], thuongHieu: String(r[12]), cotBoQua: String(r[13] || '').trim() });
  }
  return out;
}

function soCot_(chu) { // "AP" -> 42
  chu = String(chu).toUpperCase().replace(/[^A-Z]/g, ''); var n = 0;
  for (var i = 0; i < chu.length; i++) n = n * 26 + chu.charCodeAt(i) - 64;
  return n;
}

// ---------------- QUÉT & DỊCH ----------------
function menuDichTatCa() {
  var kq = dichTatCa_();
  SpreadsheetApp.getUi().alert(kq);
}

function chayTuDong() { dichTatCa_(); } // hàm cho hẹn giờ

function dichTatCa_() {
  var batDau = Date.now(), daDich = 0, loi = 0, conLai = 0;
  docCaiDat_().forEach(function (cf) {
    var ss = SpreadsheetApp.openByUrl(cf.sheetUrl), sh = ss.getSheetByName(cf.tab);
    if (!sh) { nhatKy_(cf.ten, '', 'Lỗi', 'Không thấy tab "' + cf.tab + '"'); loi++; return; }
    var cLink = soCot_(cf.cotLink), cKq = soCot_(cf.cotKetQua), cDuyet = cf.cotDuyet ? soCot_(cf.cotDuyet) : 0,
        cTk = cf.cotTuKhoa ? soCot_(cf.cotTuKhoa) : 0, cBq = cf.cotBoQua ? soCot_(cf.cotBoQua) : 0;
    var last = sh.getLastRow(); if (last <= cf.dongTieuDe) return;
    var n = last - cf.dongTieuDe, maxC = Math.max(cLink, cKq, cDuyet, cTk, cBq);
    var vals = sh.getRange(cf.dongTieuDe + 1, 1, n, maxC).getDisplayValues();
    for (var i = 0; i < n; i++) {
      var row = cf.dongTieuDe + 1 + i, r = vals[i];
      if (String(r[cKq - 1]).trim()) continue;                       // đã có bản dịch / đang có ghi chú
      if (!String(r[cLink - 1]).trim()) continue;                    // chưa có link Doc
      if (cBq && String(r[cBq - 1]).trim()) continue;                // ví dụ: đã đăng bản tiếng Anh rồi
      if (cDuyet && String(r[cDuyet - 1]).trim().toLowerCase() !== cf.giaTriDuyet.toLowerCase()) continue; // chưa duyệt
      if ((Date.now() - batDau) / 1000 > GIOI_HAN_GIAY) { conLai++; continue; }
      var link = layLinkDoc_(ss, sh, row, cLink);
      if (!link) { sh.getRange(row, cKq).setValue('Lỗi: không đọc được link Doc'); loi++; continue; }
      try {
        var kq = dichBai(link.match(/\/d\/([a-zA-Z0-9_-]{20,})/)[1],
          { tuKhoa: cTk ? r[cTk - 1] : '', thuongHieu: cf.thuongHieu, doiLink: cf.doiLink });
        sh.getRange(row, cKq).setRichTextValue(SpreadsheetApp.newRichTextValue()
          .setText('Bản dịch EN').setLinkUrl(kq.url).build());
        nhatKy_(cf.ten, row, 'Xong (' + kq.may + ')', kq.url + (kq.ghiChu.length ? ' | ' + kq.ghiChu.join('; ') : ''));
        daDich++;
      } catch (e) {
        sh.getRange(row, cKq).setValue('Lỗi: ' + String(e.message || e).slice(0, 150));
        nhatKy_(cf.ten, row, 'Lỗi', String(e.stack || e).slice(0, 500)); loi++;
      }
      SpreadsheetApp.flush();
    }
  });
  if (conLai) { // hết giờ lượt này: hẹn chạy tiếp sau 1 phút
    ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'chayTiep') ScriptApp.deleteTrigger(t); });
    ScriptApp.newTrigger('chayTiep').timeBased().after(60 * 1000).create();
  }
  return 'Đã dịch: ' + daDich + ' bài. Lỗi: ' + loi + '.' + (conLai ? '\nCòn ' + conLai + ' bài — công cụ tự chạy tiếp sau 1 phút.' : '') +
    '\nXem chi tiết ở tab "' + TAB_NHAT_KY + '".';
}

function chayTiep() {
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'chayTiep') ScriptApp.deleteTrigger(t); });
  dichTatCa_();
}

function layLinkDoc_(ss, sh, row, col) {
  var cell = sh.getRange(row, col), link = null, rt = cell.getRichTextValue();
  if (rt) {
    link = rt.getLinkUrl();
    if (!link) rt.getRuns().forEach(function (x) { if (!link && x.getLinkUrl()) link = x.getLinkUrl(); });
  }
  if (!link && /docs\.google\.com\/document/.test(cell.getDisplayValue())) link = cell.getDisplayValue();
  if (!link) { // ô dạng "chip" — đọc qua Google Sheets API
    try {
      var a1 = "'" + sh.getName() + "'!" + cell.getA1Notation();
      var r = Sheets.Spreadsheets.get(ss.getId(), { ranges: [a1], includeGridData: true,
        fields: 'sheets.data.rowData.values.chipRuns,sheets.data.rowData.values.hyperlink' });
      var v = r.sheets[0].data[0].rowData[0].values[0];
      if (v.hyperlink) link = v.hyperlink;
      (v.chipRuns || []).forEach(function (c) {
        if (!link && c.chip && c.chip.richLinkProperties) link = c.chip.richLinkProperties.uri;
      });
    } catch (e) { Logger.log(e); }
  }
  return link && /\/document\/d\//.test(link) ? link : null;
}

function nhatKy_(duAn, dong, kq, ghiChu) {
  var sh = SpreadsheetApp.getActive().getSheetByName(TAB_NHAT_KY);
  if (sh) sh.appendRow([new Date(), duAn, dong, kq, ghiChu]);
}

function menuDichTheoLink() {
  var ui = SpreadsheetApp.getUi();
  var r = ui.prompt('Dịch 1 bài', 'Dán link Google Doc bài tiếng Việt:', ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK) return;
  var m = r.getResponseText().match(/\/d\/([a-zA-Z0-9_-]{20,})/);
  if (!m) { ui.alert('Link không đúng dạng Google Doc.'); return; }
  var cfs = []; try { cfs = docCaiDat_(); } catch (e) {}
  var cf = cfs[0] || { thuongHieu: '', doiLink: [] }; // dùng cài đặt của dự án đầu tiên đang bật
  var kq = dichBai(m[1], { tuKhoa: '', thuongHieu: cf.thuongHieu, doiLink: cf.doiLink });
  nhatKy_('(theo link)', '', 'Xong (' + kq.may + ')', kq.url);
  ui.alert('Xong bản dịch (' + kq.may + '):\n' + kq.url + (kq.ghiChu.length ? '\n\nLưu ý:\n- ' + kq.ghiChu.join('\n- ') : '') +
    '\n\nNhớ đọc soát bản Anh trước khi gửi khách.');
}

function menuBatTuChay() {
  menuTatTuChay(true);
  ScriptApp.newTrigger('chayTuDong').timeBased().everyDays(1).atHour(22).create();
  SpreadsheetApp.getUi().alert('Đã bật: mỗi tối khoảng 22h công cụ tự quét và dịch các bài chờ dịch.');
}

function menuTatTuChay(imLang) {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'chayTuDong') ScriptApp.deleteTrigger(t);
  });
  if (imLang !== true) SpreadsheetApp.getUi().alert('Đã tắt tự chạy.');
}

// ---------------- DỊCH 1 BÀI ----------------
function dichBai(docId, opt) {
  var ghiChu = [];
  if (typeof Docs === 'undefined') throw new Error('Chưa bật dịch vụ "Google Docs API" trong Apps Script.');
  var doc = DocumentApp.openById(docId);
  var tabs = doc.getTabs();
  var nguon = tabs[0].asDocumentTab().getBody();

  var ten = TEN_TAB, n = 2, tenCo = tabs.map(function (t) { return t.getTitle(); });
  while (tenCo.indexOf(ten) >= 0) ten = TEN_TAB + ' (' + (n++) + ')';

  var res = Docs.Documents.batchUpdate({ requests: [{ addDocumentTab: { tabProperties: { title: ten } } }] }, docId);
  var tabId = res.replies[0].addDocumentTab.tabProperties.tabId;
  Docs.Documents.batchUpdate({ requests: [{ updateDocumentStyle: {
    documentStyle: { flipPageOrientation: true }, fields: 'flipPageOrientation', tabId: tabId } }] }, docId);

  doc = DocumentApp.openById(docId);
  var body = doc.getTab(tabId).asDocumentTab().getBody();
  var bang = body.appendTable([['', '']]);
  saoChep_(nguon, bang.getCell(0, 0));
  saoChep_(nguon, bang.getCell(0, 1));
  doc.saveAndClose();

  doc = DocumentApp.openById(docId);
  body = doc.getTab(tabId).asDocumentTab().getBody();
  var oPhai = body.getTables()[0].getCell(0, 1);
  var viec = [];
  thuThapText_(oPhai, viec);
  var tieuDe = nguon.getParagraphs().map(function (x) { return x.getText().trim(); }).filter(String)[0] || '';
  var dich = dichNhieu_(viec.map(function (v) { return v.html; }), ghiChu,
    { tieuDe: tieuDe, tuKhoa: opt.tuKhoa || '', thuongHieu: opt.thuongHieu || '' });
  for (var i = 0; i < viec.length; i++) ghiLai_(viec[i], dich[i]);
  apChecklist_(oPhai, ghiChu, opt.doiLink || []);
  doc.saveAndClose();

  return { url: 'https://docs.google.com/document/d/' + docId + '/edit?tab=' + tabId,
           may: PropertiesService.getUserProperties().getProperty('GEMINI_KEY') ? 'Gemini' : 'Google Dịch', ghiChu: ghiChu };
}

function saoChep_(nguon, o) {
  for (var i = 0; i < nguon.getNumChildren(); i++) {
    var el = nguon.getChild(i), t = el.getType();
    if (t === DocumentApp.ElementType.PARAGRAPH) o.appendParagraph(el.asParagraph().copy());
    else if (t === DocumentApp.ElementType.LIST_ITEM) o.appendListItem(el.asListItem().copy());
    else if (t === DocumentApp.ElementType.TABLE) o.appendTable(el.asTable().copy());
  }
  // bỏ đoạn trống có sẵn đầu ô
  var dau = o.getChild(0);
  if (o.getNumChildren() > 1 && dau.getType() === DocumentApp.ElementType.PARAGRAPH && dau.asParagraph().getText() === '' &&
      dau.asParagraph().getNumChildren() === 0) dau.asParagraph().removeFromParent();
}

// Đổi phần tử chung thành đúng kiểu để gọi được hàm riêng của nó
function kieu_(el) {
  var T = DocumentApp.ElementType, t = el.getType();
  if (t === T.PARAGRAPH) return el.asParagraph();
  if (t === T.LIST_ITEM) return el.asListItem();
  if (t === T.TABLE) return el.asTable();
  if (t === T.TABLE_ROW) return el.asTableRow();
  if (t === T.TABLE_CELL) return el.asTableCell();
  if (t === T.TEXT) return el.asText();
  if (t === T.BODY_SECTION) return el.asBody();
  return null;
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
  var c = kieu_(el);
  if (c && c.getNumChildren) for (var i = 0; i < c.getNumChildren(); i++) thuThapText_(c.getChild(i), out);
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
function dichNhieu_(arr, ghiChu, ngucanh) {
  var key = PropertiesService.getUserProperties().getProperty('GEMINI_KEY');
  if (key) {
    try { return dichGemini_(arr, key, ngucanh); }
    catch (e) { ghiChu.push('Gemini lỗi (' + String(e).slice(0, 120) + ') → đã chuyển sang Google Dịch.'); }
  }
  return arr.map(function (h) {
    try { return LanguageApp.translate(h, 'vi', 'en', { contentType: 'html' }); }
    catch (e) { Utilities.sleep(1500); return LanguageApp.translate(h, 'vi', 'en', { contentType: 'html' }); }
  });
}

var LUAT_DICH =
  'You translate Vietnamese SEO articles into natural, fluent US English for the brand described below.\n' +
  'Input: a JSON array of HTML fragments. Output: ONLY a JSON array of the same length, same order, each item the English translation.\n' +
  'Rules:\n- Keep every tag <b>, <i>, <a id="N"> exactly, around the matching translated words. Do not add or remove tags.\n' +
  '- Product names, model names and brand names stay unchanged.\n' +
  '- Headings: sentence case (capitalize only the first word and proper nouns; after " - " capitalize if the source does). Keep numbering like "2.1." and "1 - ".\n' +
  '- Use "..." instead of "etc". Color names in lowercase. Decimal point (658,5 -> 658.5).\n' +
  '- Vietnam addresses: transliterate without diacritics (Liễu Giai -> Lieu Giai Street, TP. Hồ Chí Minh -> Ho Chi Minh City).\n' +
  '- Use one consistent English keyword for the article topic. "Tóm tắt nội dung chính bài viết:" = "Key takeaways:".\n' +
  '- Translate faithfully, do not add or drop information.';

function dichGemini_(arr, key, ngucanh) {
  var p = PropertiesService.getUserProperties();
  var models = (p.getProperty('GEMINI_MODEL') ? [p.getProperty('GEMINI_MODEL')] : []).concat(GEMINI_MODELS);
  var boiCanh = (ngucanh.thuongHieu ? 'Brand: ' + ngucanh.thuongHieu + '\n' : '') + 'Article title (Vietnamese): ' + ngucanh.tieuDe +
    (ngucanh.tuKhoa ? '\nMain keyword (Vietnamese or English): ' + ngucanh.tuKhoa +
      ' — choose ONE natural English keyword for it and use it consistently; if it is already English keep it exactly.' : '');
  var out = [], CHUNK = 40;
  for (var s = 0; s < arr.length; s += CHUNK) {
    var phan = arr.slice(s, s + CHUNK), loi = '', lanThu = 0;
    for (var mi = 0; mi < models.length; mi++) {
      var resp = UrlFetchApp.fetch('https://generativelanguage.googleapis.com/v1beta/models/' + models[mi] + ':generateContent', {
        method: 'post', contentType: 'application/json', muteHttpExceptions: true,
        headers: { 'x-goog-api-key': key },
        payload: JSON.stringify({
          systemInstruction: { parts: [{ text: LUAT_DICH + '\n\n' + boiCanh }] },
          contents: [{ role: 'user', parts: [{ text: JSON.stringify(phan) }] }],
          generationConfig: { temperature: 0.2, responseMimeType: 'application/json' }
        })
      });
      var code = resp.getResponseCode();
      if (code === 404 || code === 400 && /not found|not supported/i.test(resp.getContentText())) { loi = models[mi] + ' không còn'; continue; }
      if (code === 429 && (lanThu = (lanThu || 0) + 1) <= 3) { Utilities.sleep(20000); mi--; continue; } // chờ rồi thử lại
      if (code !== 200) throw new Error('HTTP ' + code + ' ' + resp.getContentText().slice(0, 200));
      var parts = JSON.parse(resp.getContentText()).candidates[0].content.parts;
      var txt = parts.filter(function (x) { return !x.thought; }).map(function (x) { return x.text || ''; }).join('');
      var mang = JSON.parse(txt.replace(/^\s*```(json)?/, '').replace(/```\s*$/, '').trim());
      if (!Array.isArray(mang) || mang.length !== phan.length) throw new Error('Gemini trả về sai số đoạn');
      out = out.concat(mang.map(String));
      loi = null; break;
    }
    if (loi) throw new Error(loi);
  }
  return out;
}

// ---------------- CHECKLIST ----------------
function apChecklist_(o, ghiChu, doiLink) {
  var C = DocumentApp.ElementType, H = DocumentApp.ParagraphHeading;
  // etc -> ...
  o.replaceText('\\s*,?\\s*\\betc\\b\\.?', '...');
  duyetDoan_(o, function (p) {
    p.setLineSpacing(1.5).setSpacingBefore(10).setSpacingAfter(10);
    var txt = p.editAsText(), s = txt.getText();
    // đổi link bản Việt -> bản Anh (theo bảng cài đặt)
    var idx = txt.getTextAttributeIndices();
    for (var k = 0; k < idx.length; k++) {
      var u = s.length ? txt.getLinkUrl(idx[k]) : null;
      var u2 = u ? doiLink_(u, doiLink) : u;
      if (u2 && u2 !== u) {
        var z = (k + 1 < idx.length ? idx[k + 1] : s.length) - 1;
        txt.setLinkUrl(idx[k], z, u2);
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
    var el = kieu_(o.getChild(i));
    if (el && (o.getChild(i).getType() === C.PARAGRAPH || o.getChild(i).getType() === C.LIST_ITEM) && !el.getText().trim() &&
        !el.findElement(C.INLINE_IMAGE) && (i + 1 < o.getNumChildren() && o.getChild(i + 1).getType() !== C.TABLE)) {
      try { el.removeFromParent(); } catch (e) {}
    }
  }
}

function duyetDoan_(el, fn) {
  var t = el.getType();
  if (t === DocumentApp.ElementType.PARAGRAPH || t === DocumentApp.ElementType.LIST_ITEM) { fn(kieu_(el)); return; }
  var c = kieu_(el);
  if (c && c.getNumChildren) for (var i = 0; i < c.getNumChildren(); i++) duyetDoan_(c.getChild(i), fn);
}

// Đổi link bản Việt -> bản Anh theo cặp "tìm -> thay" trong bảng cài đặt
function doiLink_(u, doiLink) {
  for (var i = 0; i < doiLink.length; i++) {
    var tim = doiLink[i].tim, thay = doiLink[i].thay;
    if (!tim) continue;
    if (u.indexOf(tim) >= 0) return u.split(tim).join(thay);
    var timCut = tim.replace(/\/$/, ''), thayCut = thay.replace(/\/$/, '');
    if (timCut && u.slice(-timCut.length) === timCut) return u.slice(0, u.length - timCut.length) + thayCut;
  }
  return u;
}

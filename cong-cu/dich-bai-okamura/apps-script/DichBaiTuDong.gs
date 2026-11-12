/**
 * TRUNG TÂM DỊCH BÀI VIỆT → ANH — chạy trong Google Sheet, dùng cho nhiều dự án, không cần Claude.
 *
 * Bảng "Cài đặt dự án", mỗi dòng 1 việc. Dán link vào cột C rồi tích ô "Bật" → công cụ TỰ CHẠY:
 *   - Link Google Doc  → dịch ngay bài đó.
 *   - Link Google Sheet (danh sách bài) → quét, dịch mọi bài đã duyệt chưa có bản dịch, ghi link về Sheet đó.
 * Mỗi bài dịch xong có thêm tab "Bản dịch EN" (trang ngang, bảng 2 cột Việt | Anh). Tab tiếng Việt gốc KHÔNG bị sửa.
 * Kết quả / lỗi ghi ở cột "Kết quả" (cột O) và tab "Nhật ký dịch".
 *
 * Máy dịch: Gemini (miễn phí) — lỗi/hết lượt thì tự chuyển Google Dịch.
 * Cần bật 2 dịch vụ trong trình sửa Apps Script: "Google Docs API" và "Google Sheets API".
 */

var TEN_TAB = 'Bản dịch EN';
var TAB_CAI_DAT = 'Cài đặt dự án';
var TAB_NHAT_KY = 'Nhật ký dịch';
var GEMINI_MODELS = ['gemini-flash-latest', 'gemini-2.5-flash', 'gemini-2.0-flash']; // thử lần lượt
var GIOI_HAN_GIAY = 270; // Google cho chạy tối đa 6 phút/lượt — dừng sớm để an toàn, phần còn lại chạy lượt sau

var COT_CAI_DAT = ['Bật', 'Tên dự án', 'Link (Google Doc 1 bài, hoặc Sheet danh sách bài)', 'Tên tab', 'Dòng tiêu đề (số)',
  'Cột link Doc', 'Cột duyệt', 'Giá trị được coi là duyệt', 'Cột từ khóa', 'Cột ghi link bản dịch',
  'Đổi link: tìm', 'Đổi link: thay bằng', 'Giới thiệu thương hiệu (cho máy dịch)', 'Bỏ qua nếu cột này đã có chữ',
  'Kết quả (công cụ tự ghi)'];
var COT_KET_QUA = 15; // cột O
var MAU_OKAMURA = [false, 'Okamura', 'https://docs.google.com/spreadsheets/d/1ednWlho_Iw1ANJdwf6wD6ed_JhZpwt68f-worBBc0So/edit',
  '2. Danh sách bài SEO | 2026', 1, 'W', 'Z', 'Duyệt', 'B', 'AP', 'okamura.com.vn/vi/', 'okamura.com.vn/',
  'Okamura — Japanese premium office furniture brand (office chairs, desks, storage) in Vietnam', 'AG', ''];

var HUONG_DAN_CHIA =
  'CÁCH LẤY CHÌA (miễn phí, 2 phút):\n' +
  '1. Mở tab mới, vào: aistudio.google.com/apikey\n' +
  '2. Đăng nhập Gmail (dùng chính Gmail đang mở file này). Lần đầu: tích đồng ý điều khoản → Continue.\n' +
  '3. Bấm nút xanh "Create API key" (Tạo khoá API). Nếu được hỏi dự án: chọn dự án có sẵn hoặc "Create project".\n' +
  '4. Chìa hiện trong danh sách (bắt đầu bằng "AQ." hoặc "AIza…", đều đúng) → bấm biểu tượng copy (hình 2 tờ giấy) cạnh chìa.\n' +
  '5. Quay lại đây, dán vào ô dưới → OK.\n\n' +
  'Lưu ý: không gửi chìa cho ai, không dán vào chat. Để trống rồi OK = xoá chìa, dùng Google Dịch.';

function onOpen() {
  SpreadsheetApp.getUi().createMenu('🌐 Dịch bài')
    .addItem('⚙️ Cài đặt (làm 1 lần)', 'menuCaiDat')
    .addItem('Đổi chìa Gemini', 'menuCaiKhoaGemini')
    .addSeparator()
    .addItem('Chạy ngay các dòng đang tích "Bật"', 'menuDichTatCa')
    .addSeparator()
    .addItem('Bật tự quét mỗi tối (22h)', 'menuBatTuChay')
    .addItem('Tắt tự quét mỗi tối', 'menuTatTuChay')
    .addToUi();
}

// ---------------- CÀI ĐẶT ----------------
// Một nút làm hết: tạo bảng + bật "tích là chạy" + hỏi chìa Gemini (bỏ qua được)
function menuCaiDat() {
  menuTaoBangCaiDat(true);
  var co = PropertiesService.getUserProperties().getProperty('GEMINI_KEY');
  if (!co) menuCaiKhoaGemini(true);
  SpreadsheetApp.getUi().alert('✅ Cài xong!\n\nCÁCH DÙNG: dán link Google Doc vào cột C, cột B ghi tên dự án, rồi tích ô "Bật" ở cột A ' +
    '→ 1-3 phút sau cột O hiện "✅ Bản dịch EN".\n\nMáy dịch: ' +
    (PropertiesService.getUserProperties().getProperty('GEMINI_KEY') ? 'Gemini.' : 'Google Dịch (có thể thêm chìa Gemini sau ở menu "Đổi chìa Gemini").'));
}

function menuTaoBangCaiDat(imLang) {
  var ss = SpreadsheetApp.getActive(), sh = ss.getSheetByName(TAB_CAI_DAT);
  if (!sh) {
    sh = ss.insertSheet(TAB_CAI_DAT);
    sh.getRange(2, 1, 1, MAU_OKAMURA.length).setValues([MAU_OKAMURA]);
    sh.getRange('A2:A100').insertCheckboxes();
    sh.setFrozenRows(1); sh.setColumnWidths(1, COT_CAI_DAT.length, 150); sh.setColumnWidth(1, 50);
    sh.setColumnWidth(3, 260); sh.setColumnWidth(COT_KET_QUA, 320);
  }
  // luôn cập nhật dòng tiêu đề (bảng tạo từ bản cũ sẽ được thêm cột "Kết quả")
  sh.getRange(1, 1, 1, COT_CAI_DAT.length).setValues([COT_CAI_DAT]).setFontWeight('bold')
    .setBackground('#004AEF').setFontColor('#ffffff').setWrap(true);
  if (!ss.getSheetByName(TAB_NHAT_KY)) {
    ss.insertSheet(TAB_NHAT_KY).getRange(1, 1, 1, 5).setValues([['Thời gian', 'Dự án', 'Dòng', 'Kết quả', 'Ghi chú']])
      .setFontWeight('bold');
  }
  batTichLaChay_();
  ss.setActiveSheet(sh);
  if (imLang === true) return;
  SpreadsheetApp.getUi().alert('Đã sẵn sàng!\n\n' +
    'CÁCH DÙNG: dán link vào cột C rồi tích ô "Bật" ở cột A → công cụ tự chạy (1-3 phút/bài).\n' +
    '- Link Google Doc: dịch ngay bài đó.\n' +
    '- Link Google Sheet danh sách bài: điền thêm các cột D → N (xem dòng mẫu Okamura).\n\n' +
    'Mẹo: dòng bài lẻ nên điền cùng "Tên dự án" với dòng dự án (ví dụ Okamura) — công cụ tự mượn cách đổi link, ' +
    'giới thiệu thương hiệu của dự án đó.\n\nNhớ bấm "② Cài chìa Gemini" nếu chưa cài.');
}

function batTichLaChay_() {
  var ss = SpreadsheetApp.getActive();
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'khiSua') ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('khiSua').forSpreadsheet(ss).onEdit().create();
}

function menuCaiKhoaGemini(trongCaiDat) {
  var ui = SpreadsheetApp.getUi();
  var r = ui.prompt('Chìa Gemini (miễn phí, KHÔNG bắt buộc)', HUONG_DAN_CHIA +
    (trongCaiDat === true ? '\n\nChưa muốn lấy chìa? Bấm Huỷ — công cụ dùng Google Dịch, thêm chìa sau cũng được.' : ''), ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK) return;
  var k = r.getResponseText().trim(), p = PropertiesService.getUserProperties();
  if (!k) { p.deleteProperty('GEMINI_KEY'); ui.alert('Đã xoá chìa. Dùng Google Dịch.'); return; }
  k = k.replace(/\s+/g, '');
  if (k.length < 20) { ui.alert('Chìa có vẻ bị thiếu — bạn bấm biểu tượng copy cạnh chìa rồi dán lại nhé.'); return; }
  p.setProperty('GEMINI_KEY', k);
  var thu = thuChiaGemini_(k);
  ui.alert(thu === true ? 'Đã lưu chìa và thử thành công. Từ giờ dùng Gemini để dịch.' : 'Đã lưu chìa.\n\n' + thu);
}

function thuChiaGemini_(k) {
  try { dichGemini_(['<b>Xin chào</b>'], k, { tieuDe: 'Thử', tuKhoa: '', thuongHieu: '' }); return true; }
  catch (e) {
    var m = String(e.message || e);
    if (/quá tải|503|500|UNAVAILABLE/.test(m)) return 'Chìa ĐÚNG, nhưng máy chủ Gemini đang quá tải tạm thời. Lúc dịch công cụ sẽ tự chờ và thử lại; nếu vẫn quá tải sẽ dùng Google Dịch.';
    if (/API_KEY_INVALID|API key not valid|400|403/.test(m)) return 'Chìa KHÔNG đúng hoặc chưa kích hoạt — copy lại chìa (biểu tượng 2 tờ giấy) rồi cài lại.';
    return m.slice(0, 200);
  }
}

function docCaiDat_() {
  var sh = SpreadsheetApp.getActive().getSheetByName(TAB_CAI_DAT);
  if (!sh) throw new Error('Chưa có bảng cài đặt — bấm menu "① Tạo bảng cài đặt".');
  var v = sh.getRange(1, 1, Math.max(sh.getLastRow(), 2), COT_CAI_DAT.length).getValues(), out = [];
  for (var i = 1; i < v.length; i++) {
    var r = v[i], link = String(r[2]).trim();
    if (!link) continue;
    out.push({ dong: i + 1, bat: r[0] === true, ten: String(r[1]).trim(), link: link,
      loai: /\/document\/d\//.test(link) ? 'doc' : (/\/spreadsheets\/d\//.test(link) ? 'sheet' : 'sai'),
      tab: String(r[3]), dongTieuDe: Number(r[4]) || 1,
      cotLink: String(r[5]).trim(), cotDuyet: String(r[6]).trim(), giaTriDuyet: String(r[7]).trim(),
      cotTuKhoa: String(r[8]).trim(), cotKetQua: String(r[9]).trim(),
      tim: String(r[10]).trim(), thay: String(r[11]).trim(), thuongHieu: String(r[12]).trim(),
      cotBoQua: String(r[13] || '').trim(), ketQua: String(r[14] || '') });
  }
  // dòng thiếu "đổi link"/"thương hiệu" thì mượn của dòng cùng tên dự án
  out.forEach(function (c) {
    out.forEach(function (d) {
      if (d === c || !c.ten || d.ten.toLowerCase() !== c.ten.toLowerCase()) return;
      if (!c.tim && d.tim) { c.tim = d.tim; c.thay = d.thay; }
      if (!c.thuongHieu && d.thuongHieu) c.thuongHieu = d.thuongHieu;
    });
    c.doiLink = [{ tim: c.tim, thay: c.thay }];
  });
  return out;
}

function soCot_(chu) { // "AP" -> 42
  chu = String(chu).toUpperCase().replace(/[^A-Z]/g, ''); var n = 0;
  for (var i = 0; i < chu.length; i++) n = n * 26 + chu.charCodeAt(i) - 64;
  return n;
}

function ghiKetQua_(dong, chu, url) {
  var c = SpreadsheetApp.getActive().getSheetByName(TAB_CAI_DAT).getRange(dong, COT_KET_QUA);
  if (url) c.setRichTextValue(SpreadsheetApp.newRichTextValue().setText(chu).setLinkUrl(0, chu.length, url).build());
  else c.setValue(chu);
  SpreadsheetApp.flush();
}

function gio_() { return Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'dd/MM HH:mm'); }

function loiDeHieu_(e) {
  var m = String(e && e.message || e);
  if (/Docs is not defined|Sheets is not defined|Google Docs API|Google Sheets API/.test(m))
    return 'Chưa bật dịch vụ Google Docs API / Google Sheets API trong Apps Script (mục Dịch vụ +).';
  if (/Illegal spreadsheet id|Unexpected error while getting the method or property openByUrl/.test(m))
    return 'Link ở cột C không phải link Google Sheet/Doc hợp lệ.';
  if (/permission|quyền|Access denied|not have permission/i.test(m))
    return 'Không có quyền mở/sửa file này — cần quyền Chỉnh sửa với file đó.';
  if (/Requested entity was not found|not found/i.test(m)) return 'Không tìm thấy file — kiểm tra lại link.';
  return m.slice(0, 200);
}

// ---------------- TỰ CHẠY KHI TÍCH / DÁN LINK ----------------
function khiSua(e) {
  try {
    var r = e.range, sh = r.getSheet();
    if (sh.getName() !== TAB_CAI_DAT || r.getRow() < 2) return;
    var c1 = r.getColumn(), c2 = r.getLastColumn();
    if (c2 < 1 || c1 > 3) return; // chỉ quan tâm khi sửa cột A (Bật) hoặc C (Link)
    var lock = LockService.getScriptLock();
    if (!lock.tryLock(5000)) return;
    try {
      var batDau = Date.now();
      for (var row = r.getRow(); row <= r.getLastRow(); row++) {
        var cf = docCaiDat_().filter(function (x) { return x.dong === row; })[0];
        if (!cf || !cf.bat) continue;
        xuLyDong_(cf, batDau, false);
      }
    } finally { lock.releaseLock(); }
  } catch (err) { Logger.log(err); }
}

function xuLyDong_(cf, batDau, quetLai) {
  try {
    if (cf.loai === 'sai') { ghiKetQua_(cf.dong, '⚠️ Link ở cột C không phải Google Doc / Google Sheet'); return 0; }
    if (cf.loai === 'doc') {
      if (/^✅/.test(cf.ketQua) && !quetLai) return 0; // đã dịch rồi — muốn dịch lại thì xoá ô Kết quả
      ghiKetQua_(cf.dong, '⏳ Đang dịch… (1-3 phút) — ' + gio_());
      var kq = dichBai(cf.link.match(/\/d\/([a-zA-Z0-9_-]{20,})/)[1],
        { tuKhoa: '', thuongHieu: cf.thuongHieu, doiLink: cf.doiLink });
      ghiKetQua_(cf.dong, '✅ Bản dịch EN (' + kq.may + ', ' + gio_() + ')' + (kq.ghiChu.length ? ' — ' + kq.ghiChu.join('; ') : ''), kq.url);
      nhatKy_(cf.ten, cf.dong, 'Xong (' + kq.may + ')', kq.url);
      return 1;
    }
    ghiKetQua_(cf.dong, '⏳ Đang quét danh sách… — ' + gio_());
    var t = quetDuAn_(cf, batDau);
    ghiKetQua_(cf.dong, (t.loi ? '⚠️ ' : '✅ ') + gio_() + ': dịch ' + t.daDich + ' bài' + (t.loi ? ', lỗi ' + t.loi + ' (xem Nhật ký dịch)' : '') +
      (t.conLai ? ', còn ' + t.conLai + ' bài — tự chạy tiếp sau 1 phút' : '') + (t.daDich + t.loi + t.conLai === 0 ? ' — không có bài nào chờ dịch' : ''));
    return t.conLai;
  } catch (e) {
    ghiKetQua_(cf.dong, '❌ Lỗi: ' + loiDeHieu_(e));
    nhatKy_(cf.ten, cf.dong, 'Lỗi', String(e && e.stack || e).slice(0, 500));
    return 0;
  }
}

function quetDuAn_(cf, batDau) {
  var daDich = 0, loi = 0, conLai = 0;
  var ss = SpreadsheetApp.openByUrl(cf.link), sh = ss.getSheetByName(cf.tab);
  if (!sh) throw new Error('Không thấy tab "' + cf.tab + '" trong file Sheet (cột D phải đúng tên tab).');
  if (!cf.cotLink || !cf.cotKetQua) throw new Error('Thiếu "Cột link Doc" (F) hoặc "Cột ghi link bản dịch" (J).');
  var cLink = soCot_(cf.cotLink), cKq = soCot_(cf.cotKetQua), cDuyet = cf.cotDuyet ? soCot_(cf.cotDuyet) : 0,
      cTk = cf.cotTuKhoa ? soCot_(cf.cotTuKhoa) : 0, cBq = cf.cotBoQua ? soCot_(cf.cotBoQua) : 0;
  var last = sh.getLastRow(); if (last <= cf.dongTieuDe) return { daDich: 0, loi: 0, conLai: 0 };
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
      sh.getRange(row, cKq).setRichTextValue(SpreadsheetApp.newRichTextValue().setText('Bản dịch EN').setLinkUrl(kq.url).build());
      nhatKy_(cf.ten, cf.tab + ' dòng ' + row, 'Xong (' + kq.may + ')', kq.url + (kq.ghiChu.length ? ' | ' + kq.ghiChu.join('; ') : ''));
      daDich++;
    } catch (e) {
      sh.getRange(row, cKq).setValue('Lỗi: ' + loiDeHieu_(e));
      nhatKy_(cf.ten, cf.tab + ' dòng ' + row, 'Lỗi', String(e && e.stack || e).slice(0, 500)); loi++;
    }
    SpreadsheetApp.flush();
  }
  if (conLai) henChayTiep_();
  return { daDich: daDich, loi: loi, conLai: conLai };
}

function henChayTiep_() {
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'chayTiep') ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('chayTiep').timeBased().after(60 * 1000).create();
}

// ---------------- CHẠY TẤT CẢ / HẸN GIỜ ----------------
function menuDichTatCa() {
  var ui = SpreadsheetApp.getUi();
  var ds = docCaiDat_().filter(function (c) { return c.bat; });
  if (!ds.length) { ui.alert('Chưa có dòng nào tích "Bật" và có link ở cột C.'); return; }
  SpreadsheetApp.getActive().toast('Đang chạy ' + ds.length + ' dòng… xem cột "Kết quả".', 'Dịch bài', 10);
  chayCacDong_(ds, true);
  ui.alert('Xong lượt chạy. Xem cột "Kết quả" (cột O) và tab "' + TAB_NHAT_KY + '".');
}

function chayTuDong() { chayCacDong_(docCaiDat_().filter(function (c) { return c.bat && c.loai === 'sheet'; }), false); }

function chayTiep() {
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'chayTiep') ScriptApp.deleteTrigger(t); });
  chayCacDong_(docCaiDat_().filter(function (c) { return c.bat && c.loai === 'sheet'; }), false);
}

function chayCacDong_(ds, tuMenu) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(10000)) return;
  try {
    var batDau = Date.now();
    ds.forEach(function (cf) {
      if ((Date.now() - batDau) / 1000 > GIOI_HAN_GIAY) { henChayTiep_(); return; }
      xuLyDong_(cf, batDau, false);
    });
  } finally { lock.releaseLock(); }
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

function menuBatTuChay() {
  menuTatTuChay(true);
  ScriptApp.newTrigger('chayTuDong').timeBased().everyDays(1).atHour(22).create();
  SpreadsheetApp.getUi().alert('Đã bật: mỗi tối khoảng 22h công cụ tự quét các dòng dự án (link Sheet) đang tích "Bật".');
}

function menuTatTuChay(imLang) {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'chayTuDong') ScriptApp.deleteTrigger(t);
  });
  if (imLang !== true) SpreadsheetApp.getUi().alert('Đã tắt tự quét mỗi tối.');
}

// ---------------- DỊCH 1 BÀI ----------------
function dichBai(docId, opt) {
  var ghiChu = [];
  if (typeof Docs === 'undefined') throw new Error('Chưa bật dịch vụ Google Docs API');
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
      if ((code === 429 || code >= 500) && (lanThu = (lanThu || 0) + 1) <= 2) { // quá tải: chờ rồi thử lại
        Utilities.sleep(code === 429 ? 20000 : 5000); mi--; continue;
      }
      if (code === 429 || code >= 500) { loi = models[mi] + ' đang quá tải (HTTP ' + code + ')'; lanThu = 0; continue; } // sang bản khác
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

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

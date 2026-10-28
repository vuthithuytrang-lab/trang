/**
 * Check Publish TCB — chạy ngay trong Google Sheet "Theo dõi publish TCB" (Apps Script).
 * Chạy trên máy chủ Google: miễn phí, không cần Claude, không tốn token.
 *
 * - Mỗi tối khoảng 19:00 (giờ VN) tự mở từng link ở cột B, đọc ngày đang hiện, ghi vào cặp cột
 *   "dd/mm/yyyy | Kiểm tra lúc". Từ 18:00 trở đi so với NGÀY MAI (bài phải sang ngày hôm sau từ tối).
 * - Xong gửi tin vào Lark: hết thì "Done", còn thiếu thì soạn sẵn tin nhờ chị Tú Anh publish lại.
 * - Gõ "UD" vào nhóm Lark → trong khoảng 1 phút máy kiểm và trả lời ngay trong nhóm.
 * - Trong ngày đã có lần kiểm thấy đủ hết (UD / Kiểm tra ngay) thì lần tự kiểm 19:00 bỏ qua, không nhắn.
 * - App Check Publish ghi yêu cầu vào tab "Điều khiển" ô B1 → trong khoảng 1 phút máy tự kiểm.
 * - Menu "Check publish" trên thanh công cụ của sheet: Kiểm tra ngay, cài Lark, bật/tắt lịch.
 */

var TAB = 'Untitled';
var TAB_DK = 'Điều khiển';
var TZ = 'Asia/Ho_Chi_Minh';
var GIO_CHUYEN_NGAY = 18;
var GIO_TU_KIEM = 19;
var LARK_API = 'https://open.larksuite.com/open-apis';
var UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36';

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Check publish')
    .addItem('Kiểm tra ngay', 'kiemTay')
    .addSeparator()
    .addItem('Bước 1 · Cài link Lark', 'caiLark')
    .addItem('Bước 2 · Bật lịch tự động', 'batLich')
    .addItem('Bước 3 · Cài nhận lệnh UD từ Lark', 'caiUD')
    .addSeparator()
    .addItem('Gửi thử tin Lark', 'guiThu')
    .addItem('Tắt lịch tự động', 'tatLich')
    .addToUi();
}

/* ---------- Các nút trong menu ---------- */

function kiemTay() {
  var kq = kiem_();
  SpreadsheetApp.getUi().alert(kq ? kq.tomTat + '\n\nLark: ' + kq.lark : 'Đang có một lần kiểm khác chạy, thử lại sau 1 phút.');
}

function caiLark() {
  var ui = SpreadsheetApp.getUi();
  var tl = ui.prompt('Cài link Lark',
    'Dán link webhook của bot Lark (bắt đầu bằng https://open.larksuite.com/open-apis/bot/...).\n' +
    'Link được cất kín trong sheet này, không hiện ra ở ô nào.', ui.ButtonSet.OK_CANCEL);
  if (tl.getSelectedButton() !== ui.Button.OK) return;
  var url = tl.getResponseText().trim();
  if (!/^https:\/\/[^\s]+\/open-apis\/bot\/v2\/hook\/[\w-]+$/.test(url)) {
    ui.alert('Link chưa đúng dạng. Link đúng trông như: https://open.larksuite.com/open-apis/bot/v2/hook/xxxxxxxx');
    return;
  }
  PropertiesService.getScriptProperties().setProperty('LARK_WEBHOOK', url);
  var kq = guiLark_('Check publish TCB đã kết nối Lark thành công.');
  ui.alert(kq === 'ok' ? 'Đã lưu. Bạn mở Lark xem có tin nhắn thử chưa nhé.' : 'Đã lưu nhưng gửi thử chưa được: ' + kq);
}

function guiThu() {
  var kq = guiLark_('Tin nhắn thử từ Check publish TCB.');
  SpreadsheetApp.getUi().alert(kq === 'ok' ? 'Đã gửi tin thử vào Lark.' : 'Chưa gửi được: ' + kq);
}

function batLich() {
  tatLich_();
  ScriptApp.newTrigger('kiemTheoLich').timeBased().atHour(GIO_TU_KIEM).nearMinute(0).everyDays(1).inTimezone(TZ).create();
  ScriptApp.newTrigger('moiPhut').timeBased().everyMinutes(1).create();
  bangDieuKhien_();
  SpreadsheetApp.getUi().alert('Đã bật. Mỗi tối khoảng ' + GIO_TU_KIEM + ':00 máy tự kiểm và nhắn Lark ' +
    '(bỏ qua nếu trong ngày đã kiểm thấy đủ).\nGõ "UD" trong nhóm Lark hoặc bấm "Kiểm tra ngay" trên app: máy chạy trong khoảng 1 phút.');
}

function tatLich() {
  tatLich_();
  SpreadsheetApp.getUi().alert('Đã tắt lịch tự động. Bấm "Bước 2 · Bật lịch tự động" để bật lại.');
}

/** Bước 3: cất App ID + App Secret của ứng dụng Lark, tìm nhóm có bot, thử đọc tin. */
function caiUD() {
  var ui = SpreadsheetApp.getUi();
  var a = ui.prompt('Cài nhận lệnh UD (1/2)', 'Dán App ID của ứng dụng Lark (bắt đầu bằng cli_...).', ui.ButtonSet.OK_CANCEL);
  if (a.getSelectedButton() !== ui.Button.OK) return;
  var b = ui.prompt('Cài nhận lệnh UD (2/2)', 'Dán App Secret của ứng dụng Lark.\nĐược cất kín trong sheet này, không hiện ra ở ô nào.', ui.ButtonSet.OK_CANCEL);
  if (b.getSelectedButton() !== ui.Button.OK) return;
  var pr = PropertiesService.getScriptProperties();
  pr.setProperties({LARK_APP_ID: a.getResponseText().trim(), LARK_APP_SECRET: b.getResponseText().trim()});
  CacheService.getScriptCache().remove('LARK_TOKEN');
  try {
    var nhom = goiLark_('GET', '/im/v1/chats?page_size=50').data.items || [];
    if (!nhom.length) { ui.alert('Đã lưu, nhưng bot của ứng dụng chưa ở trong nhóm nào. Thêm bot vào nhóm "Check publish TCB" rồi bấm lại Bước 3.'); return; }
    var chon = nhom.filter(function (n) { return /check\s*publish/i.test(n.name || ''); })[0] || nhom[0];
    pr.setProperty('LARK_CHAT_ID', chon.chat_id);
    pr.setProperty('LARK_DA_DOC', String(Date.now()));  // chỉ nghe tin gửi từ bây giờ
    ui.alert('Xong. Máy sẽ nghe lệnh UD trong nhóm "' + chon.name + '".\nNhớ bấm "Bước 2 · Bật lịch tự động" nếu chưa bật.');
  } catch (e) {
    ui.alert('Đã lưu nhưng chưa kết nối được Lark: ' + e.message);
  }
}

/* ---------- Chạy theo lịch ---------- */

/** Tự kiểm buổi tối — bỏ qua nếu trong ngày đã có lần kiểm thấy đủ hết. */
function kiemTheoLich() {
  var homNay = Utilities.formatDate(new Date(), TZ, 'yyyyMMdd');
  if (PropertiesService.getScriptProperties().getProperty('DONE_NGAY') === homNay) {
    bangDieuKhien_().getRange('B4').setValue('Bỏ qua lần tự kiểm tối ' + Utilities.formatDate(new Date(), TZ, 'dd/MM') + ' vì trong ngày đã kiểm thấy đủ');
    return;
  }
  kiem_();
}

/** Mỗi phút: có lệnh UD trong nhóm Lark, hoặc app bấm "Kiểm tra ngay" (Điều khiển!B1), thì kiểm. */
function moiPhut() {
  var can = false;
  var dk = bangDieuKhien_();
  if (String(dk.getRange('B1').getDisplayValue()).trim()) { dk.getRange('B1').setValue(''); can = true; }
  if (ngheLark_()) can = true;
  if (can) {
    guiLark_('Đang check publish, khoảng 1–2 phút nữa có kết quả.');
    kiem_();
  }
}
function xuLyYeuCau() { moiPhut(); }  // tên cũ, giữ cho lịch cài trước đó

/** Đọc tin mới trong nhóm Lark; có tin "UD" của người (không phải bot) thì trả về true. */
function ngheLark_() {
  var pr = PropertiesService.getScriptProperties();
  var chat = pr.getProperty('LARK_CHAT_ID');
  if (!chat || !pr.getProperty('LARK_APP_ID')) return false;
  var tu = Number(pr.getProperty('LARK_DA_DOC') || Date.now());
  var co = false, moiNhat = tu;
  try {
    var kq = goiLark_('GET', '/im/v1/messages?container_id_type=chat&container_id=' + encodeURIComponent(chat) +
      '&start_time=' + Math.floor(tu / 1000) + '&sort_type=ByCreateTimeAsc&page_size=50');
    (kq.data.items || []).forEach(function (m) {
      var t = Number(m.create_time);
      if (t <= tu) return;
      if (t > moiNhat) moiNhat = t;
      if (!m.sender || m.sender.sender_type !== 'user' || m.msg_type !== 'text') return;
      var chu = '';
      try { chu = JSON.parse(m.body.content).text || ''; } catch (e) {}
      chu = chu.replace(/@_user_\d+|@_all/g, '').trim().toUpperCase();
      if (chu === 'UD') co = true;
    });
  } catch (e) {
    bangDieuKhien_().getRange('B5').setValue('Lỗi nghe Lark lúc ' + Utilities.formatDate(new Date(), TZ, 'HH:mm dd/MM') + ': ' + e.message);
    return false;
  }
  pr.setProperty('LARK_DA_DOC', String(moiNhat));
  return co;
}

function goiLark_(cach, duong) {
  var r = UrlFetchApp.fetch(LARK_API + duong, {
    method: cach.toLowerCase(), muteHttpExceptions: true,
    headers: {Authorization: 'Bearer ' + tokenLark_()}
  });
  var body = JSON.parse(r.getContentText() || '{}');
  if (body.code !== 0) throw new Error((body.msg || ('HTTP ' + r.getResponseCode())) + ' (mã ' + body.code + ')');
  return body;
}

function tokenLark_() {
  var cache = CacheService.getScriptCache();
  var tk = cache.get('LARK_TOKEN');
  if (tk) return tk;
  var pr = PropertiesService.getScriptProperties();
  var r = UrlFetchApp.fetch(LARK_API + '/auth/v3/tenant_access_token/internal', {
    method: 'post', contentType: 'application/json', muteHttpExceptions: true,
    payload: JSON.stringify({app_id: pr.getProperty('LARK_APP_ID'), app_secret: pr.getProperty('LARK_APP_SECRET')})
  });
  var b = JSON.parse(r.getContentText() || '{}');
  if (b.code !== 0) throw new Error('App ID/Secret chưa đúng: ' + (b.msg || r.getResponseCode()));
  cache.put('LARK_TOKEN', b.tenant_access_token, Math.min(5400, (b.expire || 7200) - 300));
  return b.tenant_access_token;
}

/* ---------- Phần chính ---------- */

function kiem_() {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(2000)) return null;
  try {
    var ss = SpreadsheetApp.getActive();
    var sh = ss.getSheetByName(TAB);
    var bay = new Date();
    var gio = Number(Utilities.formatDate(bay, TZ, 'H'));
    var ngay = new Date(bay.getTime() + (gio >= GIO_CHUYEN_NGAY ? 86400000 : 0));
    var nhanNgay = Utilities.formatDate(ngay, TZ, 'dd/MM/yyyy');
    var soNgay = Number(Utilities.formatDate(ngay, TZ, 'yyyyMMdd'));
    var gioKiem = Utilities.formatDate(bay, TZ, 'HH:mm dd/MM/yyyy');

    var soHang = sh.getLastRow();
    var tieuDe = sh.getRange(1, 1, 1, Math.max(2, sh.getLastColumn())).getDisplayValues()[0];
    var hang = soHang > 1 ? sh.getRange(2, 1, soHang - 1, 2).getDisplayValues() : [];

    // Cặp cột của ngày cần kiểm: có rồi thì ghi đè, chưa có thì thêm bên phải (C, E, G...)
    var c = tieuDe.indexOf(nhanNgay, 2);
    if (c < 0) {
      var n = tieuDe.length;
      while (n > 2 && !String(tieuDe[n - 1]).trim()) n--;
      c = Math.max(2, n);
      if (c % 2) c++;
    }
    if (c + 2 > sh.getMaxColumns()) sh.insertColumnsAfter(sh.getMaxColumns(), c + 2 - sh.getMaxColumns() + 10);
    if (c !== 2) sh.getRange(1, 3, Math.max(soHang, 2), 2)
      .copyTo(sh.getRange(1, c + 1, Math.max(soHang, 2), 2), SpreadsheetApp.CopyPasteType.PASTE_FORMAT, false);

    var urls = hang.map(function (r) { return String(r[1]).trim(); });
    var kq = layNgay_(urls);

    var giaTri = [[nhanNgay, 'Kiểm tra lúc']];
    var xong = 0, tre = [], loi = [], tong = 0;
    kq.forEach(function (o, i) {
      if (o.bo) { giaTri.push(['', '']); return; }
      tong++;
      if (o.loi) { giaTri.push([o.loi, gioKiem]); loi.push(urls[i]); return; }
      if (!o.ngay) { giaTri.push(['Không có ngày', gioKiem]); loi.push(urls[i]); return; }
      giaTri.push([o.chu, gioKiem]);
      if (o.so >= soNgay) xong++; else tre.push(urls[i]);
    });
    var vung = sh.getRange(1, c + 1, giaTri.length, 2);
    vung.setNumberFormat('@');
    vung.setValues(giaTri);

    var tomTat = 'Kiểm lúc ' + gioKiem + ' (so với ngày ' + nhanNgay + '): đã cập nhật ' + xong + '/' + tong +
      ', chưa cập nhật ' + tre.length + ', lỗi ' + loi.length + '.';

    var tin;
    if (!tre.length && !loi.length) {
      tin = 'Done';
    } else {
      var ds = tre.concat(loi);
      tin = 'Chị Tú Anh ơi team đã check và thấy còn ' + ds.length +
        ' bài chưa được publish nhờ chị publish lại giúp team ạ.\nDanh sách url chưa publish tại đây:\n' + ds.join('\n');
    }
    var lark = guiLark_(tin);
    if (tin === 'Done') PropertiesService.getScriptProperties().setProperty('DONE_NGAY', Utilities.formatDate(bay, TZ, 'yyyyMMdd'));

    var dk = bangDieuKhien_();
    dk.getRange('B2:B4').setValues([[gioKiem], [tomTat], [lark === 'ok' ? 'Đã gửi Lark' : 'Chưa gửi Lark: ' + lark]]);
    return {tomTat: tomTat, lark: lark === 'ok' ? 'đã gửi' : lark};
  } finally {
    lock.releaseLock();
  }
}

/** Mở từng link (10 link một lượt), trang lỗi mạng thì thử lại 1 lần. */
function layNgay_(urls) {
  var out = urls.map(function (u) { return /^https?:\/\//.test(u) ? null : {bo: true}; });
  for (var lan = 0; lan < 2; lan++) {
    var can = [];
    out.forEach(function (o, i) { if (!o || o.loi) can.push(i); });
    if (!can.length) break;
    if (lan) Utilities.sleep(4000);
    for (var k = 0; k < can.length; k += 10) {
      var nhom = can.slice(k, k + 10);
      var yc = nhom.map(function (i) { return yeuCau_(urls[i]); });
      var tl;
      try {
        tl = UrlFetchApp.fetchAll(yc);
      } catch (e) {  // một link hỏng làm cả lượt lỗi → mở riêng từng link
        tl = yc.map(function (r) { try { return UrlFetchApp.fetch(r.url, r); } catch (e2) { return null; } });
      }
      tl.forEach(function (r, j) {
        var i = nhom[j];
        if (!r) { out[i] = {loi: 'Lỗi: không vào được'}; return; }
        var ma = r.getResponseCode();
        if (ma !== 200) { out[i] = {loi: 'Lỗi: ' + ma}; return; }
        out[i] = tachNgay_(urls[i], r.getContentText('UTF-8')) || {ngay: false};
      });
    }
  }
  return out;
}

function yeuCau_(url) {
  return {
    url: url + (url.indexOf('?') < 0 ? '?' : '&') + '_kiem=' + Math.floor(Math.random() * 1e9),  // vượt bản lưu tạm
    muteHttpExceptions: true, followRedirects: true,
    headers: {'User-Agent': UA, 'Accept-Language': 'vi-VN,vi;q=0.9', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
  };
}

/** Blog: ngày ISO trong khung dưới tiêu đề bài. Trang khác: dd/mm/yyyy trong <title>, hoặc "(dd/mm)". */
function tachNgay_(url, html) {
  var d, m, y;
  if (url.indexOf('/thong-tin/blog/') >= 0) {
    var a = html.match(/article-header-body--date[^>]*>\s*(\d{4})-(\d{2})-(\d{2})/);
    if (!a) return null;
    y = +a[1]; m = +a[2]; d = +a[3];
  } else {
    var t = (html.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1] || '';
    var b = t.match(/(?:^|[^\d\/])(\d{1,2})\/(\d{1,2})\/(\d{4})(?![\d])/);
    if (b) { d = +b[1]; m = +b[2]; y = +b[3]; }
    else {
      var c = t.match(/\((\d{1,2})\/(\d{1,2})\)/);
      if (!c) return null;
      d = +c[1]; m = +c[2];
      var nam = Number(Utilities.formatDate(new Date(), TZ, 'yyyy'));
      var homNay = new Date(nam, Number(Utilities.formatDate(new Date(), TZ, 'M')) - 1, Number(Utilities.formatDate(new Date(), TZ, 'd')));
      y = [nam - 1, nam, nam + 1].reduce(function (tot, n) {
        return Math.abs(new Date(n, m - 1, d) - homNay) < Math.abs(new Date(tot, m - 1, d) - homNay) ? n : tot;
      }, nam);
    }
  }
  if (m < 1 || m > 12 || d < 1 || d > 31) return null;
  var p = function (x) { return (x < 10 ? '0' : '') + x; };
  return {ngay: true, chu: p(d) + '/' + p(m) + '/' + y, so: y * 10000 + m * 100 + d};
}

function guiLark_(text) {
  var url = PropertiesService.getScriptProperties().getProperty('LARK_WEBHOOK');
  if (!url) return 'chưa cài link Lark (menu Check publish → Bước 1)';
  try {
    var r = UrlFetchApp.fetch(url, {
      method: 'post', contentType: 'application/json', muteHttpExceptions: true,
      payload: JSON.stringify({msg_type: 'text', content: {text: text}})
    });
    var body = {};
    try { body = JSON.parse(r.getContentText()); } catch (e) {}
    if (r.getResponseCode() === 200 && (body.code === 0 || body.StatusCode === 0)) return 'ok';
    return 'Lark trả lời ' + r.getResponseCode() + ' ' + (body.msg || r.getContentText()).toString().slice(0, 150);
  } catch (e) {
    return 'không gửi được (' + e.message + ')';
  }
}

function bangDieuKhien_() {
  var ss = SpreadsheetApp.getActive();
  var dk = ss.getSheetByName(TAB_DK);
  if (!dk) {
    dk = ss.insertSheet(TAB_DK);
    dk.getRange('A1:A5').setValues([['Yêu cầu kiểm tra (app ghi vào đây)'], ['Lần kiểm gần nhất'], ['Kết quả'], ['Lark'], ['Nghe lệnh UD']]);
    dk.getRange('A1:A5').setFontWeight('bold');
    dk.setColumnWidth(1, 260); dk.setColumnWidth(2, 520);
  }
  return dk;
}

function tatLich_() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    var f = t.getHandlerFunction();
    if (f === 'kiemTheoLich' || f === 'xuLyYeuCau' || f === 'moiPhut') ScriptApp.deleteTrigger(t);
  });
}

/**
 * APP SHARE BÀI — chạy trong Google Sheet (Apps Script), không cần AI để đăng.
 * - AI (skill chay-luong-share) chỉ viết bài + tải sẵn ảnh, đổ vào tab "Hàng đợi".
 * - App tự đăng đúng giờ hẹn (Wix, WordPress), giữ nhịp an toàn, ghi link về sheet dự án,
 *   kiểm tra trang còn sống, tự dừng khi trang bị khóa, làm tab "Báo cáo" và email tóm tắt mỗi tối.
 * Chìa đăng nhập cất trong Thuộc tính tập lệnh (Script Properties), KHÔNG nằm trong sheet.
 */

var TAB_CFG = 'Cấu hình', TAB_Q = 'Hàng đợi', TAB_RP = 'Báo cáo', TAB_LOG = 'Nhật ký';
var Q_HEAD = ['STT', 'Nền tảng', 'Tài khoản', 'Dòng sheet dự án', 'URL bài gốc', 'Tiêu đề', 'Slug',
  'Nội dung HTML', 'Ảnh (media ID)', 'Giờ hẹn', 'Trạng thái', 'Link đã đăng', 'Giờ đăng', 'Ghi chú'];
var C = {}; Q_HEAD.forEach(function (h, i) { C[h] = i; });
var TZ = 'Asia/Ho_Chi_Minh';

/* ================= MENU ================= */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('🚀 App share bài')
    .addItem('1. Tạo các tab (lần đầu)', 'setupTabs')
    .addItem('2. Cài chìa Wix', 'setWixKey')
    .addItem('2. Cài chìa WordPress', 'setWpKey')
    .addSeparator()
    .addItem('3. Bật tự động đăng', 'enableAuto')
    .addItem('Tắt tự động đăng', 'disableAuto')
    .addSeparator()
    .addItem('Chạy 1 lượt ngay', 'runQueue')
    .addItem('Kiểm tra các trang còn sống', 'healthCheckMenu')
    .addItem('Cập nhật báo cáo', 'buildReport')
    .addToUi();
}

function setupTabs() {
  var ss = SpreadsheetApp.getActive();
  var cfg = ss.getSheetByName(TAB_CFG) || ss.insertSheet(TAB_CFG);
  if (cfg.getLastRow() < 2) {
    cfg.getRange(1, 1, 14, 3).setValues([
      ['Khóa', 'Giá trị', 'Giải thích'],
      ['SHEET_DU_AN_ID', '', 'ID file sheet dự án để ghi link về (đoạn giữa /d/ và /edit)'],
      ['TAB_DU_AN', 'Share social GP', 'Tên tab trong sheet dự án'],
      ['COT_URL_GOC', 'B', 'Cột chứa URL bài gốc (để tìm lại dòng)'],
      ['COT_LINK', 'D', 'Cột ghi link đã đăng'],
      ['COT_GIO', 'E', 'Cột ghi giờ đăng'],
      ['GIO_BAT_DAU', '7', 'Chỉ đăng từ giờ này'],
      ['GIO_KET_THUC', '23', 'Không đăng sau giờ này'],
      ['CACH_NHAU_PHUT', '120', 'Mỗi tài khoản: 2 bài cách nhau ít nhất bấy nhiêu phút'],
      ['TOI_DA_MOI_NGAY', '6', 'Mỗi tài khoản tối đa bấy nhiêu bài/ngày'],
      ['EMAIL_BAO_CAO', Session.getActiveUser().getEmail() || '', 'Gửi tóm tắt mỗi tối + báo khi trang bị khóa'],
      ['WIX_TRANG_CHU', '', 'Ví dụ https://trangjena3.wixsite.com/techcombankvietnam'],
      ['WIX_URL_BAI', '', 'Ví dụ https://trangjena3.wixsite.com/techcombankvietnam/b-i-ng/'],
      ['WP_SITE', '', 'Ví dụ tenblog.wordpress.com (bỏ trống nếu không dùng)']
    ]);
    cfg.getRange(1, 1, 1, 3).setFontWeight('bold'); cfg.setColumnWidth(1, 170); cfg.setColumnWidth(2, 330); cfg.setColumnWidth(3, 420);
  }
  var q = ss.getSheetByName(TAB_Q) || ss.insertSheet(TAB_Q);
  if (q.getLastRow() < 1) { q.appendRow(Q_HEAD); q.getRange(1, 1, 1, Q_HEAD.length).setFontWeight('bold'); q.setFrozenRows(1); }
  var lg = ss.getSheetByName(TAB_LOG) || ss.insertSheet(TAB_LOG);
  if (lg.getLastRow() < 1) lg.appendRow(['Thời gian', 'Việc', 'Chi tiết']);
  (ss.getSheetByName(TAB_RP) || ss.insertSheet(TAB_RP));
  buildReport();
  SpreadsheetApp.getUi().alert('Đã tạo các tab. Bước tiếp: điền tab "Cấu hình", rồi cài chìa ở menu 🚀 App share bài.');
}

function setWixKey() {
  var ui = SpreadsheetApp.getUi(), p = PropertiesService.getScriptProperties();
  var k = ui.prompt('Chìa Wix (API Key, bắt đầu bằng IST.)', ui.ButtonSet.OK_CANCEL); if (k.getSelectedButton() != ui.Button.OK) return;
  var s = ui.prompt('Site ID của Wix', ui.ButtonSet.OK_CANCEL); if (s.getSelectedButton() != ui.Button.OK) return;
  var m = ui.prompt('Member ID (tác giả bài viết)', ui.ButtonSet.OK_CANCEL); if (m.getSelectedButton() != ui.Button.OK) return;
  p.setProperties({ WIX_API_KEY: k.getResponseText().trim(), WIX_SITE_ID: s.getResponseText().trim(), WIX_MEMBER_ID: m.getResponseText().trim() });
  ui.alert('Đã lưu chìa Wix (cất trong cài đặt bí mật, không nằm trong sheet).');
}
function setWpKey() {
  var ui = SpreadsheetApp.getUi();
  var k = ui.prompt('Access token WordPress.com', ui.ButtonSet.OK_CANCEL); if (k.getSelectedButton() != ui.Button.OK) return;
  PropertiesService.getScriptProperties().setProperty('WP_TOKEN', k.getResponseText().trim());
  ui.alert('Đã lưu chìa WordPress.');
}

function enableAuto() {
  disableAuto(true);
  ScriptApp.newTrigger('runQueue').timeBased().everyMinutes(10).create();
  ScriptApp.newTrigger('dailyMorning').timeBased().atHour(6).nearMinute(45).everyDays(1).inTimezone(TZ).create();
  ScriptApp.newTrigger('dailyEvening').timeBased().atHour(22).nearMinute(30).everyDays(1).inTimezone(TZ).create();
  SpreadsheetApp.getUi().alert('Đã bật: kiểm tra hàng đợi mỗi 10 phút, kiểm tra trang lúc 6:45, gửi báo cáo lúc 22:30.');
}
function disableAuto(silent) {
  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
  if (silent !== true) SpreadsheetApp.getUi().alert('Đã tắt tự động đăng.');
}

/* ================= TIỆN ÍCH ================= */
function cfg_() {
  var v = SpreadsheetApp.getActive().getSheetByName(TAB_CFG).getDataRange().getValues(), o = {};
  v.slice(1).forEach(function (r) { if (r[0]) o[r[0]] = String(r[1]).trim(); });
  return o;
}
function log_(what, detail) {
  SpreadsheetApp.getActive().getSheetByName(TAB_LOG).appendRow([new Date(), what, String(detail).slice(0, 500)]);
}
function fmt_(d) { return Utilities.formatDate(d, TZ, 'HH:mm dd/MM/yyyy'); }
function parseVN_(s) { // "HH:mm dd/MM/yyyy" hoặc ô ngày giờ
  if (s instanceof Date) return s;
  var m = String(s).match(/(\d{1,2}):(\d{2})\s+(\d{1,2})\/(\d{1,2})\/(\d{4})/); if (!m) return null;
  return new Date(Date.UTC(+m[5], +m[4] - 1, +m[3], +m[1] - 7, +m[2]));
}
function vnHour_(d) { return +Utilities.formatDate(d, TZ, 'H'); }
function vnDay_(d) { return Utilities.formatDate(d, TZ, 'dd/MM/yyyy'); }
function paused_(plat) { return PropertiesService.getScriptProperties().getProperty('PAUSE_' + plat) === '1'; }
function setPaused_(plat, on) { PropertiesService.getScriptProperties().setProperty('PAUSE_' + plat, on ? '1' : '0'); }

/* ================= KIỂM TRA TRANG ================= */
function siteAlive_(plat, cfg) {
  var url = plat === 'wix' ? cfg.WIX_TRANG_CHU : (cfg.WP_SITE ? 'https://' + cfg.WP_SITE + '/' : '');
  if (!url) return true;
  try {
    var r = UrlFetchApp.fetch(url, { muteHttpExceptions: true, followRedirects: true });
    var code = r.getResponseCode();
    return !(code === 410 || code === 404 || code === 451 || (code !== 200 && /suspended/i.test(r.getContentText())));
  } catch (e) { return true; } // lỗi mạng tạm thời: không coi là bị khóa
}
function healthCheck_() {
  var cfg = cfg_(), out = {};
  ['wix', 'wp'].forEach(function (p) {
    var alive = siteAlive_(p, cfg); out[p] = alive;
    if (!alive && !paused_(p)) {
      setPaused_(p, true); log_('TRANG BỊ KHÓA', p);
      if (cfg.EMAIL_BAO_CAO) MailApp.sendEmail(cfg.EMAIL_BAO_CAO, '⚠️ Trang ' + p + ' có dấu hiệu bị khóa — app đã dừng đăng',
        'App share bài đã tự dừng đăng lên ' + p + '. Kiểm tra trang và báo AI khi cần chạy lại.');
    }
  });
  return out;
}
function healthCheckMenu() { var h = healthCheck_(); SpreadsheetApp.getUi().alert('Wix: ' + (h.wix ? 'sống' : 'BỊ KHÓA') + '\nWordPress: ' + (h.wp ? 'sống' : 'BỊ KHÓA / không dùng')); buildReport(); }

/* ================= VÒNG ĐĂNG ================= */
function runQueue() {
  var lock = LockService.getScriptLock(); if (!lock.tryLock(5000)) return;
  try {
    var cfg = cfg_(), now = new Date(), h = vnHour_(now);
    if (h < +cfg.GIO_BAT_DAU || h >= +cfg.GIO_KET_THUC) return;
    var q = SpreadsheetApp.getActive().getSheetByName(TAB_Q), data = q.getDataRange().getValues();
    var lastPost = {}, today = {}, todayKey = vnDay_(now);
    for (var i = 1; i < data.length; i++) {
      var r = data[i]; if (r[C['Trạng thái']] !== 'Đã đăng') continue;
      var acc = r[C['Nền tảng']] + '|' + r[C['Tài khoản']], t = parseVN_(r[C['Giờ đăng']]); if (!t) continue;
      if (!lastPost[acc] || t > lastPost[acc]) lastPost[acc] = t;
      if (vnDay_(t) === todayKey) today[acc] = (today[acc] || 0) + 1;
    }
    for (var j = 1; j < data.length; j++) {
      var row = data[j], st = row[C['Trạng thái']];
      if (st && st !== 'Chờ') continue;
      var plat = String(row[C['Nền tảng']]).toLowerCase(), key = plat + '|' + row[C['Tài khoản']];
      var due = parseVN_(row[C['Giờ hẹn']]); if (!due || due > now) continue;
      if (paused_(plat)) continue;
      if (lastPost[key] && (now - lastPost[key]) / 60000 < +cfg.CACH_NHAU_PHUT) continue;
      if ((today[key] || 0) >= +cfg.TOI_DA_MOI_NGAY) continue;
      if (!siteAlive_(plat, cfg)) { healthCheck_(); continue; }
      publishRow_(q, j + 1, row, plat, cfg);
      return; // mỗi lượt chỉ đăng 1 bài — giữ nhịp an toàn
    }
  } finally { lock.releaseLock(); }
}

function publishRow_(q, rowNum, row, plat, cfg) {
  q.getRange(rowNum, C['Trạng thái'] + 1).setValue('Đang đăng');
  try {
    var res = plat === 'wix' ? publishWix_(row, cfg) : publishWp_(row, cfg);
    var when = fmt_(new Date());
    q.getRange(rowNum, C['Trạng thái'] + 1, 1, 3).setValues([['Đã đăng', res.url, when]]);
    log_('ĐĂNG', plat + ' ' + res.url);
    writeBack_(row[C['URL bài gốc']], res.url, when, cfg);
  } catch (e) {
    q.getRange(rowNum, C['Trạng thái'] + 1).setValue('Lỗi');
    q.getRange(rowNum, C['Ghi chú'] + 1).setValue(String(e).slice(0, 300));
    log_('LỖI', plat + ' dòng ' + rowNum + ': ' + e);
  }
}

/* ---- Wix: đăng thẳng 1 lệnh (publish: true), không tạo nháp ---- */
function wixFetch_(method, url, body) {
  var p = PropertiesService.getScriptProperties();
  var r = UrlFetchApp.fetch(url, { method: method, contentType: 'application/json', muteHttpExceptions: true,
    headers: { Authorization: p.getProperty('WIX_API_KEY'), 'wix-site-id': p.getProperty('WIX_SITE_ID') },
    payload: body ? JSON.stringify(body) : undefined });
  return { code: r.getResponseCode(), json: (function () { try { return JSON.parse(r.getContentText()); } catch (e) { return {}; } })() };
}
function wixTotal_() { var r = wixFetch_('post', 'https://www.wixapis.com/blog/v3/posts/query', { paging: { limit: 1 } }); return (r.json.metaData || {}).total; }
function publishWix_(row, cfg) {
  var before = wixTotal_();
  var draft = { title: row[C['Tiêu đề']], memberId: PropertiesService.getScriptProperties().getProperty('WIX_MEMBER_ID'),
    richContent: { nodes: toRicos_(row[C['Nội dung HTML']]) }, seoSlug: row[C['Slug']] };
  if (row[C['Ảnh (media ID)']]) draft.media = { wixMedia: { image: { id: row[C['Ảnh (media ID)']] } }, displayed: true, custom: true };
  var r = wixFetch_('post', 'https://www.wixapis.com/blog/v3/draft-posts', { draftPost: draft, publish: true });
  if (r.code !== 200) {
    Utilities.sleep(20000);
    if (wixTotal_() > before) throw new Error('Wix báo lỗi ' + r.code + ' nhưng bài có thể đã lên — kiểm tra tay, KHÔNG đăng lại');
    throw new Error('Wix lỗi ' + r.code + ': ' + JSON.stringify(r.json).slice(0, 200));
  }
  var id = r.json.draftPost.id, url = cfg.WIX_URL_BAI + row[C['Slug']];
  var g = wixFetch_('get', 'https://www.wixapis.com/blog/v3/posts/' + id + '?fieldsets=URL');
  var u = ((g.json.post || {}).url) || {}; if (u.base && u.path) url = u.base + u.path;
  return { url: url };
}
function inline_(s) {
  var nodes = [], re = /<(\/?)(strong|b|a)([^>]*)>/g, pos = 0, bold = false, link = null, m;
  function push(t) { if (!t) return; var dec = []; if (bold) dec.push({ type: 'BOLD', fontWeightValue: 700 });
    if (link) dec.push({ type: 'LINK', linkData: { link: { url: link, target: 'BLANK', rel: { noreferrer: true } } } });
    nodes.push({ type: 'TEXT', id: '', nodes: [], textData: { text: decode_(t), decorations: dec } }); }
  while ((m = re.exec(s))) { push(s.slice(pos, m.index)); var close = m[1] === '/';
    if (m[2] !== 'a') bold = !close; else link = close ? null : ((m[3].match(/href="([^"]+)"/) || [])[1] || null); pos = re.lastIndex; }
  push(s.slice(pos)); return nodes;
}
function decode_(t) { return t.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'"); }
function nid_() { return Utilities.getUuid().slice(0, 8); }
function toRicos_(html) {
  var out = [], cur = null;
  String(html).split(/\n/).map(function (l) { return l.trim(); }).filter(String).forEach(function (l) {
    var m = l.match(/^<(p|h2|h3|li)>([\s\S]*)<\/\1>$/);
    if (l === '<ul>' || l === '<ol>') cur = l === '<ul>' ? { type: 'BULLETED_LIST', id: nid_(), nodes: [], bulletedListData: { indentation: 0 } } : { type: 'ORDERED_LIST', id: nid_(), nodes: [], orderedListData: { indentation: 0 } };
    else if (l === '</ul>' || l === '</ol>') { if (cur) out.push(cur); cur = null; }
    else if (m && m[1] === 'li' && cur) cur.nodes.push({ type: 'LIST_ITEM', id: nid_(), nodes: [{ type: 'PARAGRAPH', id: nid_(), nodes: inline_(m[2]), paragraphData: {} }] });
    else if (m && m[1] === 'p') out.push({ type: 'PARAGRAPH', id: nid_(), nodes: inline_(m[2]), paragraphData: {} });
    else if (m) out.push({ type: 'HEADING', id: nid_(), nodes: inline_(m[2]), headingData: { level: +m[1].slice(1) } });
    else out.push({ type: 'PARAGRAPH', id: nid_(), nodes: inline_(l.replace(/<[^>]+>/g, '')), paragraphData: {} });
  });
  return out;
}

/* ---- WordPress.com: đăng thẳng status=publish ---- */
function publishWp_(row, cfg) {
  var tok = PropertiesService.getScriptProperties().getProperty('WP_TOKEN');
  var body = { title: row[C['Tiêu đề']], content: toGutenberg_(row[C['Nội dung HTML']]), slug: row[C['Slug']], status: 'publish' };
  if (row[C['Ảnh (media ID)']]) body.featured_image = row[C['Ảnh (media ID)']];
  var r = UrlFetchApp.fetch('https://public-api.wordpress.com/rest/v1.1/sites/' + cfg.WP_SITE + '/posts/new',
    { method: 'post', contentType: 'application/json', payload: JSON.stringify(body), headers: { Authorization: 'Bearer ' + tok }, muteHttpExceptions: true });
  if (r.getResponseCode() !== 200) throw new Error('WordPress lỗi ' + r.getResponseCode() + ': ' + r.getContentText().slice(0, 200));
  return { url: JSON.parse(r.getContentText()).URL };
}
function toGutenberg_(html) {
  return String(html).split(/\n/).map(function (l) { return l.trim(); }).filter(String).map(function (l) {
    if (/^<p/.test(l)) return '<!-- wp:paragraph -->\n' + l + '\n<!-- /wp:paragraph -->';
    if (/^<h2/.test(l)) return '<!-- wp:heading {"style":{"typography":{"fontSize":"26px"}}} -->\n' + l.replace('<h2>', '<h2 class="wp-block-heading" style="font-size:26px">') + '\n<!-- /wp:heading -->';
    if (/^<h3/.test(l)) return '<!-- wp:heading {"level":3,"style":{"typography":{"fontSize":"21px"}}} -->\n' + l.replace('<h3>', '<h3 class="wp-block-heading" style="font-size:21px">') + '\n<!-- /wp:heading -->';
    if (l === '<ul>') return '<!-- wp:list -->\n<ul class="wp-block-list">';
    if (l === '<ol>') return '<!-- wp:list {"ordered":true} -->\n<ol class="wp-block-list">';
    if (l === '</ul>') return '</ul>\n<!-- /wp:list -->';
    if (l === '</ol>') return '</ol>\n<!-- /wp:list -->';
    if (/^<li/.test(l)) return '<!-- wp:list-item -->\n' + l + '\n<!-- /wp:list-item -->';
    return l;
  }).join('\n\n');
}

/* ---- Ghi link về sheet dự án: tìm lại dòng theo URL bài gốc, chỉ ghi khi ô link đang trống ---- */
function writeBack_(srcUrl, url, when, cfg) {
  if (!cfg.SHEET_DU_AN_ID) return;
  var sh = SpreadsheetApp.openById(cfg.SHEET_DU_AN_ID).getSheetByName(cfg.TAB_DU_AN);
  var colU = colNum_(cfg.COT_URL_GOC), colL = colNum_(cfg.COT_LINK), colT = colNum_(cfg.COT_GIO);
  var vals = sh.getRange(1, colU, sh.getLastRow(), 1).getValues();
  for (var i = 0; i < vals.length; i++) {
    if (String(vals[i][0]).trim() === String(srcUrl).trim()) {
      var cell = sh.getRange(i + 1, colL);
      if (cell.getValue()) { log_('KHÔNG GHI ĐÈ', 'Dòng ' + (i + 1) + ' đã có link'); return; }
      cell.setValue(url); sh.getRange(i + 1, colT).setValue(when); return;
    }
  }
  log_('KHÔNG TÌM THẤY DÒNG', srcUrl);
}
function colNum_(letter) { var n = 0; String(letter).toUpperCase().split('').forEach(function (c) { n = n * 26 + c.charCodeAt(0) - 64; }); return n; }

/* ================= BÁO CÁO ================= */
function buildReport() {
  var ss = SpreadsheetApp.getActive(), q = ss.getSheetByName(TAB_Q), rp = ss.getSheetByName(TAB_RP); if (!q || !rp) return;
  var data = q.getDataRange().getValues().slice(1), now = new Date(), todayKey = vnDay_(now), cfg = cfg_();
  var acc = {}, days = {};
  data.forEach(function (r) {
    if (!r[C['Nền tảng']]) return;
    var k = r[C['Nền tảng']] + ' · ' + r[C['Tài khoản']];
    acc[k] = acc[k] || { tong: 0, da: 0, homnay: 0, cho: 0, loi: 0 };
    var a = acc[k]; a.tong++;
    var st = r[C['Trạng thái']] || 'Chờ';
    if (st === 'Đã đăng') { a.da++; var t = parseVN_(r[C['Giờ đăng']]); if (t) { var dk = vnDay_(t); days[dk] = days[dk] || {}; days[dk][k] = (days[dk][k] || 0) + 1; if (dk === todayKey) a.homnay++; } }
    else if (st === 'Lỗi') a.loi++; else a.cho++;
  });
  var rows = [['Báo cáo share — cập nhật ' + fmt_(now), '', '', '', '', '', '', ''], ['', '', '', '', '', '', '', ''],
    ['Tài khoản', 'Trang', 'Tổng bài', 'Đã đăng', 'Hôm nay', 'Còn chờ', 'Lỗi', '% xong']];
  Object.keys(acc).sort().forEach(function (k) {
    var a = acc[k], plat = k.split(' · ')[0].toLowerCase();
    rows.push([k, paused_(plat) ? 'ĐÃ DỪNG (trang có dấu hiệu bị khóa)' : 'Đang chạy', a.tong, a.da, a.homnay, a.cho, a.loi, a.tong ? Math.round(a.da * 100 / a.tong) + '%' : '']);
  });
  rows.push(['', '', '', '', '', '', '', '']); rows.push(['Theo ngày', 'Tài khoản', 'Số bài đã đăng', '', '', '', '', '']);
  Object.keys(days).sort(function (x, y) { return parseVN_('00:00 ' + x) - parseVN_('00:00 ' + y); }).forEach(function (d) {
    Object.keys(days[d]).sort().forEach(function (k) { rows.push([d, k, days[d][k], '', '', '', '', '']); });
  });
  rp.clear(); rp.getRange(1, 1, rows.length, 8).setValues(rows);
  rp.getRange(1, 1).setFontWeight('bold').setFontSize(13); rp.getRange(3, 1, 1, 8).setFontWeight('bold').setBackground('#e8eefc');
  rp.setColumnWidth(1, 260); rp.setColumnWidth(2, 260);
  return acc;
}
function dailyMorning() { healthCheck_(); buildReport(); }
function dailyEvening() {
  var acc = buildReport(), cfg = cfg_(); if (!cfg.EMAIL_BAO_CAO || !acc) return;
  var lines = Object.keys(acc).sort().map(function (k) { var a = acc[k]; return '• ' + k + ': hôm nay ' + a.homnay + ' bài, tổng đã đăng ' + a.da + '/' + a.tong + ', còn chờ ' + a.cho + (a.loi ? ', lỗi ' + a.loi : ''); });
  MailApp.sendEmail(cfg.EMAIL_BAO_CAO, 'Báo cáo share ngày ' + vnDay_(new Date()), lines.join('\n') + '\n\nXem chi tiết: ' + SpreadsheetApp.getActive().getUrl());
}

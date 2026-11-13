/**
 * CauHinh.gs — App Inlink bản dùng chung: đọc mọi cấu hình từ CHÍNH file Sheet (không sửa code cho từng dự án).
 * Tab "Thông tin dự án": cột A = mục, cột B = giá trị. Tab "Kế hoạch inlink": tìm cột theo chữ ở hàng 1.
 */
var TAB_THONG_TIN = 'Thông tin dự án';
var TAB_KE_HOACH = 'Kế hoạch inlink';
var TAB_NHAT_KY = 'Nhật ký app';
var TAB_GOP_Y = 'Sổ góp ý';
var UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36';
var GIOI_HAN_GIAY = 270;   // Google cho tối đa 6 phút mỗi lần chạy; dừng sớm, bấm Chạy tiếp tự nối

var COT = {
  url: /^URL bài viết/i, file: /^File Google Docs/i, du: /^Đủ anchor/i, ghiChu: /^Ghi chú/i, duyet: /^Duyệt/i,
  phanHoi: /^Phản hồi/i, html: /^HTML/i, tinhTrang: /^Tình trạng/i, capAnchor: /^Anchor\s*(\d+)/i, capUrl: /^Link chèn\s*(\d+)/i
};

function ss_() { return SpreadsheetApp.getActive(); }

function docThongTin_() {
  var t = ss_().getSheetByName(TAB_THONG_TIN), o = {};
  if (!t) return o;
  t.getRange(1, 1, Math.max(t.getLastRow(), 1), 2).getValues().forEach(function (r) { o[String(r[0]).trim()] = String(r[1]).trim(); });
  return o;
}
function ghiThongTin_(muc, giaTri) {
  var t = ss_().getSheetByName(TAB_THONG_TIN); if (!t) return;
  var v = t.getRange(1, 1, t.getLastRow(), 1).getValues();
  for (var i = 0; i < v.length; i++) if (String(v[i][0]).trim().indexOf(muc) === 0) { t.getRange(i + 1, 2).setValue(giaTri); return; }
}
function layTT_(o, dau) { var k = Object.keys(o).filter(function (x) { return x.indexOf(dau) === 0; })[0]; return k ? o[k] : ''; }

/** Cấu hình dự án đang chạy. Thư mục Drive để trống → tự tạo "Inlink – <tên dự án>" và ghi link lại vào ô. */
function cauHinh() {
  var o = docThongTin_();
  var ten = layTT_(o, 'Tên dự án') || ss_().getName();
  var luat = layTT_(o, 'Quy tắc riêng').split(/\n|;/).map(function (x) { return x.trim(); }).filter(Boolean);
  var pj = { ten: ten, website: layTT_(o, 'Website'), nguoiDuyet: layTT_(o, 'Người duyệt'), giongVan: layTT_(o, 'Giọng văn'),
    toiDa: parseInt(layTT_(o, 'Tối đa anchor'), 10) || 5, luat: luat, thuMuc: '' };
  var tm = layTT_(o, 'Thư mục Google Drive'), id = (tm.match(/folders\/([\w-]{15,})/) || tm.match(/^([\w-]{25,})$/) || [])[1];
  pj.thuMucId_ = id || '';
  CAM_DU_AN = [];
  luat.forEach(function (x) { tuCamTrongLuat(x).forEach(function (c) { if (CAM_DU_AN.indexOf(c) < 0) CAM_DU_AN.push(c); }); });
  return pj;
}
function thuMucCua(pj) {
  if (pj.thuMuc) return pj.thuMuc;
  if (pj.thuMucId_) { try { DriveApp.getFolderById(pj.thuMucId_); pj.thuMuc = pj.thuMucId_; return pj.thuMuc; } catch (e) {} }
  var f = DriveApp.createFolder('Inlink – ' + pj.ten);
  ghiThongTin_('Thư mục Google Drive', f.getUrl());
  pj.thuMuc = f.getId();
  return pj.thuMuc;
}

function tabKeHoach() {
  var sh = ss_().getSheetByName(TAB_KE_HOACH) || ss_().getSheets().filter(function (s) { return banDoCotThu_(s); })[0];
  if (!sh) throw new Error('Không thấy tab "' + TAB_KE_HOACH + '" (cần cột "URL bài viết", "Anchor 1", "Link chèn 1"…)');
  return sh;
}
function banDoCotThu_(sh) { try { banDoCot(sh); return true; } catch (e) { return false; } }

/** Bản đồ cột {url: 2, file: 14, ..., cap: [{anchor, url}]} — đánh số từ 1. Thiếu cột kết quả thì tự thêm vào cuối. */
function banDoCot(sh) {
  var n = Math.max(sh.getLastColumn(), 1);
  var hang1 = sh.getRange(1, 1, 1, n).getValues()[0].map(function (x) { return String(x).replace(/\s+/g, ' ').trim(); });
  var m = { cap: [] }, capA = {}, capU = {};
  hang1.forEach(function (ten, j) {
    Object.keys(COT).forEach(function (k) { if (k !== 'capAnchor' && k !== 'capUrl' && COT[k].test(ten) && !m[k]) m[k] = j + 1; });
    var a = ten.match(COT.capAnchor), u = ten.match(COT.capUrl);
    if (a) capA[a[1]] = j + 1;
    if (u) capU[u[1]] = j + 1;
  });
  Object.keys(capA).sort(function (x, y) { return x - y; }).forEach(function (k) { if (capU[k]) m.cap.push({ anchor: capA[k], url: capU[k] }); });
  if (!m.url || !m.cap.length) throw new Error('tab "' + sh.getName() + '" thiếu cột "URL bài viết" hoặc cặp "Anchor 1" / "Link chèn 1"');
  var them = { file: 'File Google Docs (tự điền)', du: 'Đủ anchor (tự điền)', duyet: 'Duyệt (ok / cần sửa)', phanHoi: 'Phản hồi KT (tự điền)', html: 'HTML dán CMS (tự điền)', tinhTrang: 'Tình trạng' };
  Object.keys(them).forEach(function (k) { if (!m[k]) { var c = sh.getLastColumn() + 1; sh.getRange(1, c).setValue(them[k]).setFontWeight('bold'); m[k] = c; } });
  return m;
}

function o_(dong, c) { return c ? String(dong[c - 1] == null ? '' : dong[c - 1]).trim() : ''; }

/** Anchor của 1 dòng theo thứ tự cặp 1..N, cắt theo "Tối đa anchor mỗi bài". */
function anchorCuaDong(pj, m, dong) {
  var ds = [], thieu = [];
  m.cap.forEach(function (c) {
    var a = o_(dong, c.anchor), u = o_(dong, c.url);
    if (a && u) ds.push({ anchor: a, url: u }); else if (u && !a) thieu.push(u);
  });
  var bo = ds.length > pj.toiDa ? ds.slice(pj.toiDa).map(function (x) { return x.anchor; }) : [];
  return { ds: ds.slice(0, pj.toiDa), thieuAnchor: thieu, boVuot: bo };
}

function ghiOTrong(sh, r, c, giaTri) {
  var o = sh.getRange(r, c);
  if (String(o.getValue()).trim() !== '') return false;
  o.setValue(giaTri);
  return true;
}

function nhatKy(viec, dong, ketQua) {
  var t = ss_().getSheetByName(TAB_NHAT_KY) || ss_().insertSheet(TAB_NHAT_KY);
  if (t.getLastRow() === 0) { t.appendRow(['Thời gian', 'Việc', 'Dòng', 'Kết quả']); t.setFrozenRows(1); t.getRange(1, 1, 1, 4).setFontWeight('bold'); }
  t.appendRow([new Date(), viec, dong, String(ketQua).slice(0, 4000)]);
}

function idTuLink(link) { var m = String(link).match(/\/d\/([\w-]{20,})/); return m ? m[1] : ''; }
function slugCua(u) { return String(u).split('?')[0].replace(/\/$/, '').split('/').pop(); }

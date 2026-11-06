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

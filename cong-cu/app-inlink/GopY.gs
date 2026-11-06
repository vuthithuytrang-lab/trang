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

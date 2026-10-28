/**
 * Cập nhật bài Techcombank TỰ ĐỘNG — chạy trên máy chủ Google, không cần Claude, không tốn token.
 *
 * Cách hoạt động:
 *  1. Máy chủ miễn phí của GitHub (GitHub Actions) chạy công thức của từng bài mỗi giờ:
 *     đọc bài mới nhất, lấy giá từ nguồn, sửa số + ngày, tô vàng → để sẵn file HTML ở nhánh "tu-dong-ket-qua".
 *  2. Script này (chạy 10 phút/lần dưới tài khoản Google của Trang) xem Sheet "Update":
 *     dòng nào được tích mà có bản dựng sẵn mới → tạo Google Docs trong thư mục chung, chia sẻ quyền sửa,
 *     dán link vào cột hôm nay, bỏ tích.
 *  3. Dòng được tích nhưng chưa có công thức tự động → để nguyên, Claude xử lý như cũ.
 *
 * Cài lần đầu: dán file này vào Apps Script, chọn hàm "caiDat" → Chạy → Cho phép. Xong.
 */
const CAU_HINH = {
  SHEET_ID: '1pG0TA0nwiOkF086eAhbukUJ375oZRfuJpQy4bEUiVck',
  THU_MUC_ID: '1FXvxKb6TvSsbMeK6I3utnLvRZ4Y_vXxI',          // "Cập nhật bài Techcombank (Claude)"
  KHO: 'https://raw.githubusercontent.com/vuthithuytrang-lab/trang/tu-dong-ket-qua/',
  TUOI_TOI_DA_PHUT: 150,                                     // bản dựng cũ hơn → chờ lần chạy sau
};
// đoạn cuối link bài TCB → mã công thức tự động
const CONG_THUC = {
  'gia-ca-phe-hom-nay': 'gia-ca-phe', 'gia-xang-dau-hom-nay': 'gia-xang-dau', 'vang-24k': 'vang-24k',
  'vang-14k-gia-hom-nay': 'vang-14k', 'vang-18k': 'vang-18k', 'vang-10k': 'vang-10k',
  '1-chi-vang-bao-nhieu-tien': '1-chi-vang', 'gia-vang-16k-hom-nay': 'vang-16k', 'vang-610-la-vang-gi': 'vang-610',
};
const TZ = 'Asia/Ho_Chi_Minh';

function onOpen() {
  SpreadsheetApp.getUi().createMenu('⚡ Cập nhật tự động')
    .addItem('Chạy ngay các dòng đã tích', 'kiemTra')
    .addToUi();
}

/** Chạy 1 lần khi cài: tạo lịch 10 phút/lần. */
function caiDat() {
  ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === 'kiemTra')
    .forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('kiemTra').timeBased().everyMinutes(10).create();
  DriveApp.getFolderById(CAU_HINH.THU_MUC_ID);              // để Google hỏi quyền Drive ngay lúc cài
  kiemTra();
}

function kiemTra() {
  const khoa = LockService.getScriptLock();
  if (!khoa.tryLock(1000)) return;                          // lần trước còn đang chạy
  try { chay_(); } finally { khoa.releaseLock(); }
}

function chay_() {
  const ss = SpreadsheetApp.openById(CAU_HINH.SHEET_ID);
  const sh = ss.getSheets()[0];
  const du = sh.getRange(1, 1, sh.getLastRow(), 5).getValues();
  const can = [];
  for (let r = 1; r < du.length; r++) {
    if (du[r][4] !== true || !du[r][1]) continue;
    const ma = CONG_THUC[String(du[r][1]).trim().replace(/\/+$/, '').split('/').pop()];
    if (ma) can.push({ dong: r + 1, ma });
  }
  if (!can.length) return;

  const trangThai = JSON.parse(UrlFetchApp.fetch(CAU_HINH.KHO + 'trang-thai.json?t=' + Date.now()).getContentText());
  const homNay = new Date();
  const ngayMai = Utilities.formatDate(new Date(homNay.getTime() + 864e5), TZ, 'dd/MM/yyyy');
  const cot = cotHomNay_(sh, homNay);
  const emails = ss.getSheetByName('Hướng dẫn').getRange('B11:B20').getValues().flat()
    .map(x => String(x).trim()).filter(x => /@/.test(x));

  for (const c of can) {
    const tt = trangThai[c.ma];
    const tuoi = tt ? (Date.now() - new Date(tt.luc).getTime()) / 6e4 : 1e9;
    if (!tt || tt.ngay !== ngayMai || tuoi > CAU_HINH.TUOI_TOI_DA_PHUT) continue;  // chưa có bản mới, đợi lần sau
    const o = sh.getRange(c.dong, cot);
    try {
      if (!tt.ok) throw new Error(tt.loi || 'công thức chạy lỗi');
      const html = UrlFetchApp.fetch(CAU_HINH.KHO + c.ma + '.html?t=' + Date.now()).getContentText('UTF-8');
      let ten = tt.ten;
      if (DriveApp.getFolderById(CAU_HINH.THU_MUC_ID).getFilesByName(ten).hasNext())
        ten += ' (cập nhật ' + Utilities.formatDate(homNay, TZ, "HH'h'mm") + ')';
      const id = taoDocs_(ten, html);
      emails.forEach(e => chiaSe_(id, e));
      const link = 'https://docs.google.com/document/d/' + id + '/edit';
      o.setRichTextValue(SpreadsheetApp.newRichTextValue().setText(ten).setLinkUrl(link).build());
      o.setNote(tt.can_duyet ? 'Cần xem lại: ' + tt.can_duyet : null);
    } catch (e) {
      o.setValue('⚠️ Lỗi: ' + String(e.message || e).slice(0, 150));
    }
    sh.getRange(c.dong, 5).setValue(false);                  // luôn bỏ tích để không chạy lặp
  }
}

/** Cột có tiêu đề = hôm nay; chưa có thì chèn tại F (ngày mới nhất ở F). */
function cotHomNay_(sh, homNay) {
  const d = Utilities.formatDate(homNay, TZ, 'yyyy-MM-dd');
  const f1 = sh.getRange(1, 6).getValue();
  if (f1 instanceof Date && Utilities.formatDate(f1, TZ, 'yyyy-MM-dd') === d) return 6;
  sh.insertColumnBefore(6);
  sh.getRange(1, 7, sh.getMaxRows(), 1).copyTo(sh.getRange(1, 6, sh.getMaxRows(), 1), SpreadsheetApp.CopyPasteType.PASTE_FORMAT, false);
  sh.getRange(1, 6, sh.getMaxRows(), 1).clearContent();
  const [y, m, dd] = d.split('-').map(Number);
  sh.getRange(1, 6).setValue(new Date(y, m - 1, dd)).setNumberFormat('d/m').setFontWeight('bold').setHorizontalAlignment('center');
  return 6;
}

/** Tải HTML lên Drive, Google tự chuyển thành Google Docs (giữ tô vàng, bảng, ảnh). */
function taoDocs_(ten, html) {
  const ranh = 'ranh' + Date.now();
  const meta = JSON.stringify({ name: ten, mimeType: 'application/vnd.google-apps.document', parents: [CAU_HINH.THU_MUC_ID] });
  const than = '--' + ranh + '\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n' + meta +
    '\r\n--' + ranh + '\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n' + html + '\r\n--' + ranh + '--';
  const r = UrlFetchApp.fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true', {
    method: 'post', contentType: 'multipart/related; boundary=' + ranh,
    payload: Utilities.newBlob(than).setContentType('multipart/related').getBytes(),
    headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() }, muteHttpExceptions: true,
  });
  if (r.getResponseCode() !== 200) throw new Error('Drive ' + r.getResponseCode() + ': ' + r.getContentText().slice(0, 100));
  return JSON.parse(r.getContentText()).id;
}

function chiaSe_(id, email) {
  UrlFetchApp.fetch('https://www.googleapis.com/drive/v3/files/' + id + '/permissions?sendNotificationEmail=false&supportsAllDrives=true', {
    method: 'post', contentType: 'application/json', muteHttpExceptions: true,
    payload: JSON.stringify({ role: 'writer', type: 'user', emailAddress: email }),
    headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() },
  });
}

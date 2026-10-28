/**
 * Cập nhật bài Techcombank TỰ ĐỘNG — chạy trên máy chủ Google, không cần Claude, không tốn token.
 * Chỉ chạy khi có người tích ô (Trang dặn 28/10/2026: không đặt lịch chạy, bấm mới chạy).
 *
 * Cách hoạt động (mỗi phút xem Sheet 1 lần — chỉ đọc, không tốn gì):
 *  1. Có dòng được tích (từ app hoặc tích tay trong Sheet) → ghi "⏳ Đang chạy…" vào cột hôm nay
 *     và ghi phiếu yêu cầu (file yeu-cau-tu-dong.json trong thư mục Drive chung).
 *  2. Máy chủ miễn phí của GitHub thấy phiếu mới → chạy công thức đúng các bài đó: đọc bài mới nhất, lấy giá,
 *     sửa số + ngày, tô vàng → để kết quả ở nhánh "tu-dong-ket-qua".
 *  3. Có kết quả mới → tạo Google Docs trong thư mục chung, chia sẻ quyền sửa, dán link vào Sheet + tab "app", bỏ tích.
 *  Dòng được tích nhưng chưa có công thức tự động → để nguyên, Claude xử lý như cũ.
 *
 * Cài lần đầu: Sheet "Update" → Tiện ích mở rộng → Apps Script → dán file này → Lưu → chọn hàm "caiDat" → Chạy → Cho phép.
 */
const CAU_HINH = {
  SHEET_ID: '1pG0TA0nwiOkF086eAhbukUJ375oZRfuJpQy4bEUiVck',
  THU_MUC_ID: '1FXvxKb6TvSsbMeK6I3utnLvRZ4Y_vXxI',          // "Cập nhật bài Techcombank (Claude)"
  PHIEU_ID: '1wrO0bArJtokvfFvOzFNFqvJhrLrPD2VI',            // yeu-cau-tu-dong.json — máy chủ GitHub đọc file này
  KHO: 'https://raw.githubusercontent.com/vuthithuytrang-lab/trang/tu-dong-ket-qua/',
  CHO_TOI_DA_PHUT: 45,                                       // quá lâu chưa có kết quả → báo lỗi, bỏ tích
  TAB_APP: 'app',                                            // tab app đọc: A STT · B tên file · C link · D lúc · E ghi chú
};
// đoạn cuối link bài TCB → mã công thức tự động
const CONG_THUC = {
  'gia-ca-phe-hom-nay': 'gia-ca-phe', 'gia-xang-dau-hom-nay': 'gia-xang-dau', 'vang-24k': 'vang-24k',
  'vang-14k-gia-hom-nay': 'vang-14k', 'vang-18k': 'vang-18k', 'vang-10k': 'vang-10k',
  '1-chi-vang-bao-nhieu-tien': '1-chi-vang', 'gia-vang-16k-hom-nay': 'vang-16k', 'vang-610-la-vang-gi': 'vang-610',
};
const TZ = 'Asia/Ho_Chi_Minh';

/** Chạy 1 lần khi cài: mỗi phút xem Sheet 1 lần. */
function caiDat() {
  ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === 'kiemTra')
    .forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('kiemTra').timeBased().everyMinutes(1).create();
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
  const app = tabApp_(ss);
  const homNay = new Date();
  app.getRange('H1').setValue('Máy tự động chạy lúc ' + Utilities.formatDate(homNay, TZ, 'HH:mm dd/MM/yyyy'));

  const du = sh.getRange(1, 1, sh.getLastRow(), 5).getValues();
  const tich = [];
  for (let r = 1; r < du.length; r++) {
    if (du[r][4] !== true || !du[r][1]) continue;
    const ma = CONG_THUC[String(du[r][1]).trim().replace(/\/+$/, '').split('/').pop()];
    if (ma) tich.push({ dong: r + 1, stt: du[r][0], ma });
  }
  const kho = PropertiesService.getScriptProperties();
  const cho = JSON.parse(kho.getProperty('cho') || '{}');   // mã bài → lúc thấy được tích lần đầu
  Object.keys(cho).forEach(ma => { if (!tich.some(t => t.ma === ma)) delete cho[ma]; });   // đã bỏ tích tay
  if (!tich.length) { kho.setProperty('cho', '{}'); return; }

  let cot = 0;
  const cotNay = () => (cot = cot || cotHomNay_(sh, homNay));
  for (const t of tich) if (!cho[t.ma]) {
    cho[t.ma] = homNay.toISOString();
    sh.getRange(t.dong, cotNay()).setValue('⏳ Đang chạy…');
    ghiApp_(app, t.stt, ['', '', Utilities.formatDate(homNay, TZ, 'HH:mm dd/MM'), 'dang_chay']);
  }

  const trangThai = JSON.parse(UrlFetchApp.fetch(CAU_HINH.KHO + 'trang-thai.json?t=' + Date.now(),
    { muteHttpExceptions: true }).getContentText() || '{}');
  const ngayMai = Utilities.formatDate(new Date(homNay.getTime() + 864e5), TZ, 'dd/MM/yyyy');
  let emails = null;
  for (const t of tich) {
    const tt = trangThai[t.ma];
    const moi = tt && new Date(tt.luc) > new Date(cho[t.ma]) && (!tt.ok || tt.ngay === ngayMai);
    const quaLau = (homNay - new Date(cho[t.ma])) / 6e4 > CAU_HINH.CHO_TOI_DA_PHUT;
    if (!moi && !quaLau) continue;
    const o = sh.getRange(t.dong, cotNay());
    try {
      if (!moi) throw new Error('máy chủ chưa chạy xong sau ' + CAU_HINH.CHO_TOI_DA_PHUT + ' phút – tích lại để thử lại');
      if (!tt.ok) throw new Error(tt.loi || 'công thức chạy lỗi');
      const html = UrlFetchApp.fetch(CAU_HINH.KHO + t.ma + '.html?t=' + Date.now()).getContentText('UTF-8');
      let ten = tt.ten;
      if (DriveApp.getFolderById(CAU_HINH.THU_MUC_ID).getFilesByName(ten).hasNext())
        ten += ' (cập nhật ' + Utilities.formatDate(homNay, TZ, "HH'h'mm") + ')';
      const id = taoDocs_(ten, html);
      emails = emails || ss.getSheetByName('Hướng dẫn').getRange('B11:B20').getValues().flat()
        .map(x => String(x).trim()).filter(x => /@/.test(x));
      emails.forEach(e => chiaSe_(id, e));
      const link = 'https://docs.google.com/document/d/' + id + '/edit';
      o.setRichTextValue(SpreadsheetApp.newRichTextValue().setText(ten).setLinkUrl(link).build());
      o.setNote(tt.can_duyet ? 'Cần xem lại: ' + tt.can_duyet : null);
      ghiApp_(app, t.stt, [ten, link, Utilities.formatDate(homNay, TZ, 'HH:mm dd/MM'), tt.can_duyet ? 'Cần xem lại: ' + tt.can_duyet : 'xong']);
    } catch (e) {
      const loi = '⚠️ Lỗi: ' + String(e.message || e).slice(0, 150);
      o.setValue(loi);
      ghiApp_(app, t.stt, ['', '', Utilities.formatDate(homNay, TZ, 'HH:mm dd/MM'), loi]);
    }
    sh.getRange(t.dong, 5).setValue(false);                  // luôn bỏ tích để không chạy lặp
    delete cho[t.ma];
  }
  kho.setProperty('cho', JSON.stringify(cho));

  // bài còn chờ mà phiếu hiện tại chưa nhắc tới → ghi phiếu mới cho máy chủ GitHub
  const conCho = Object.keys(cho);
  if (!conCho.length) return;
  const fPhieu = DriveApp.getFileById(CAU_HINH.PHIEU_ID);
  const phieu = JSON.parse(fPhieu.getBlob().getDataAsString() || '{}');
  const daCo = phieu.ma && phieu.ma !== trangThai._yeu_cau &&
    conCho.every(ma => (phieu.bai || []).indexOf(ma) >= 0 && new Date(phieu.luc) >= new Date(cho[ma]));
  if (!daCo) fPhieu.setContent(JSON.stringify({ ma: 'yc-' + homNay.getTime(), luc: homNay.toISOString(), bai: conCho }));
}

/** Tab "app" — app trên claude.ai đọc tab này để hiện trạng thái + link. Dòng = STT + 1 (giống tab đầu). */
function tabApp_(ss) {
  let t = ss.getSheetByName(CAU_HINH.TAB_APP);
  if (!t) {
    t = ss.insertSheet(CAU_HINH.TAB_APP);
    t.getRange('A1:E1').setValues([['STT', 'Tên file', 'Link', 'Lúc', 'Trạng thái / ghi chú']]).setFontWeight('bold');
  }
  return t;
}
function ghiApp_(t, stt, giaTri) {
  const n = Number(stt);
  if (n > 0) t.getRange(n + 1, 1, 1, 5).setValues([[n].concat(giaTri)]);
}

/** Cột có tiêu đề = hôm nay; chưa có thì chèn tại F (ngày mới nhất ở F). */
function cotHomNay_(sh, homNay) {
  if (sh.getRange(1, 6).getDisplayValue() === Utilities.formatDate(homNay, TZ, 'd/M')) return 6;
  sh.insertColumnBefore(6);
  sh.getRange(1, 7, sh.getMaxRows(), 1).copyTo(sh.getRange(1, 6, sh.getMaxRows(), 1), SpreadsheetApp.CopyPasteType.PASTE_FORMAT, false);
  sh.getRange(1, 6, sh.getMaxRows(), 1).clearContent();
  const [y, m, d] = Utilities.formatDate(homNay, TZ, 'yyyy-M-d').split('-').map(Number);
  const soNgay = Date.UTC(y, m - 1, d) / 864e5 + 25569;      // số ngày kiểu Sheets (tính từ 30/12/1899)
  sh.getRange(1, 6).setValue(soNgay).setNumberFormat('d/m').setFontWeight('bold').setHorizontalAlignment('center');
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

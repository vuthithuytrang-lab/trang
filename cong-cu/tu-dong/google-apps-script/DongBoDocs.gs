/**
 * ĐỒNG BỘ DOCS cho app "Cập nhật bài Techcombank" (12/11/2026) — chạy trên tài khoản Google của Trang, miễn phí,
 * không cần Claude.
 *
 * Bấm "Mở file Docs" trên app → app gọi trang web nhỏ này với mã bài → trang này lấy BẢN MỚI NHẤT máy vừa chạy
 * (đúng nội dung nút "Chép để dán vào Docs"), chép đè vào file Docs CỐ ĐỊNH của bài (link không đổi, bản cũ vẫn xem
 * được ở Tệp → Lịch sử phiên bản), rồi trả link để app mở. Bản mới đã chép rồi thì không chép lại (giữ chỗ người
 * dùng đã sửa tay trong Docs cho tới lần chạy mới).
 *
 * Kiêm HỘP THƯ HTML cho tính năng "Cập nhật số vào HTML của bạn" (doPost / ?hop=), thay hàm Netlify khi Netlify hết lượt.
 *
 * Cài 1 lần (Claude hướng dẫn từng bước): script.google.com → Dự án mới → dán file này → Lưu → Triển khai →
 * Tùy chọn triển khai mới → Loại: Ứng dụng web → Thực thi với tư cách: Tôi; Ai có quyền truy cập: Bất kỳ ai →
 * Triển khai → Cho phép quyền → chép "URL ứng dụng web" gửi Claude (dán vào app).
 */
const DB = {
  THU_MUC_ID: '1FXvxKb6TvSsbMeK6I3utnLvRZ4Y_vXxI',   // "Cập nhật bài Techcombank (Claude)" – mở "ai có link đều sửa được"
  // đọc kết quả qua hàm Netlify (raw.githubusercontent giữ bản cũ tới 5 phút)
  KQ: 'https://vttt-sn.netlify.app/.netlify/functions/kq?f=',
  FILE_CO_DINH: 'https://raw.githubusercontent.com/vuthithuytrang-lab/trang/claude/vibrant-keller-rk0i98/cong-cu/tu-dong/file-co-dinh.json',
};

/* ---------- Hộp thư HTML (12/11/2026): app gửi HTML cần ghép số vào đây; máy GitHub lấy về khi chạy bài ---------- */
function doPost(e) {
  try {
    const d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    const ma = String(d.ma || ''), id = String(d.id || ''), html = String(d.html || '');
    if (!/^[a-z0-9-]{2,40}$/.test(ma) || !/^[a-z0-9]{8,20}$/.test(id)) return traVe_({loi: 'Mã không hợp lệ'});
    if (!/^[A-Za-z0-9+/]+=*$/.test(html) || html.length > 90000) return traVe_({loi: 'HTML quá dài hoặc hỏng'});
    const khoa = LockService.getScriptLock(); khoa.waitLock(20000);
    try {
      const c = CacheService.getScriptCache();
      c.put('h_' + id, html, 21600);                                        // giữ 6 tiếng
      const ds = JSON.parse(c.get('ds_' + ma) || '[]').filter(x => x !== id).concat([id]).slice(-20);
      c.put('ds_' + ma, JSON.stringify(ds), 21600);
    } finally { khoa.releaseLock(); }
    return traVe_({ok: true});
  } catch (err) {
    return traVe_({loi: String(err && err.message || err).slice(0, 200)});
  }
}

/** Máy GitHub gọi ?hop=<mã bài>: trả các HTML đang chờ của bài đó rồi xóa khỏi hộp thư. */
function layHop_(ma) {
  const c = CacheService.getScriptCache();
  const ds = JSON.parse(c.get('ds_' + ma) || '[]');
  const ra = ds.map(id => ({id: id, html: c.get('h_' + id) || ''})).filter(x => x.html);
  c.remove('ds_' + ma);
  return {ds: ra};
}

function doGet(e) {
  const hop = String((e && e.parameter && e.parameter.hop) || '');
  if (hop) return traVe_(/^[a-z0-9-]{2,40}$/.test(hop) ? layHop_(hop) : {loi: 'Mã bài không hợp lệ'});
  const ma = String((e && e.parameter && e.parameter.ma) || '');
  if (!/^[a-z0-9-]{2,40}$/.test(ma)) return traVe_({loi: 'Mã bài không hợp lệ'});
  const khoa = LockService.getScriptLock();
  try {
    khoa.waitLock(25000);
    return traVe_(dongBo_(ma));
  } catch (err) {
    return traVe_({loi: String(err && err.message || err).slice(0, 300)});
  } finally {
    try { khoa.releaseLock(); } catch (x) {}
  }
}

function dongBo_(ma) {
  const tt = JSON.parse(UrlFetchApp.fetch(DB.KQ + 'trang-thai.json&t=' + Date.now()).getContentText('UTF-8'));
  const t = tt[ma];
  if (!t || !t.ok) return {loi: 'Bài này chưa có bản mới – bấm "↻ Chạy bài này" trước.'};
  const p = PropertiesService.getScriptProperties();
  let id = p.getProperty('id_' + ma);
  if (!id) {
    try { id = JSON.parse(UrlFetchApp.fetch(DB.FILE_CO_DINH + '?t=' + Date.now()).getContentText())[ma] || ''; } catch (x) { id = ''; }
  }
  if (id) {
    try { if (DriveApp.getFileById(id).isTrashed()) id = ''; } catch (x) { id = ''; }
  }
  const moi = p.getProperty('luc_' + ma) !== t.luc || !id;
  if (moi) {
    const html = UrlFetchApp.fetch(DB.KQ + encodeURIComponent(ma + '.html') + '&t=' + Date.now()).getContentText('UTF-8');
    id = id ? ghiDe_(id, t.ten, html) : taoMoi_(t.ten, html);
    p.setProperty('id_' + ma, id);
    p.setProperty('luc_' + ma, t.luc);
  }
  return {url: 'https://docs.google.com/document/d/' + id + '/edit', ten: t.ten, luc: t.luc, ngay: t.ngay, vua_chep: moi};
}

function taiLen_(phuongThuc, url, meta, html) {
  const ranh = 'ranh' + Date.now();
  const than = '--' + ranh + '\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n' + JSON.stringify(meta) + '\r\n--' + ranh
    + '\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n' + html + '\r\n--' + ranh + '--';
  const r = UrlFetchApp.fetch(url, {
    method: phuongThuc, contentType: 'multipart/related; boundary=' + ranh, payload: Utilities.newBlob(than).getBytes(),
    headers: {Authorization: 'Bearer ' + ScriptApp.getOAuthToken()}, muteHttpExceptions: true,
  });
  if (r.getResponseCode() >= 300) throw new Error('Google Drive báo lỗi ' + r.getResponseCode() + ': ' + r.getContentText().slice(0, 200));
  return JSON.parse(r.getContentText()).id;
}

/** Chép đè nội dung mới vào file Docs có sẵn (giữ link, giữ lịch sử phiên bản). */
function ghiDe_(id, ten, html) {
  return taiLen_('patch', 'https://www.googleapis.com/upload/drive/v3/files/' + id + '?uploadType=multipart&supportsAllDrives=true',
    {name: ten}, html);
}

function taoMoi_(ten, html) {
  return taiLen_('post', 'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true',
    {name: ten, mimeType: 'application/vnd.google-apps.document', parents: [DB.THU_MUC_ID]}, html);
}

function traVe_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/** Chạy thử trong trình soạn mã (chọn hàm "thu" → Chạy): Google hỏi quyền Drive + mạng, rồi đồng bộ bài cà phê. */
function thu() {
  DriveApp.getFolderById(DB.THU_MUC_ID);
  Logger.log(JSON.stringify(dongBo_('gia-ca-phe')));
}

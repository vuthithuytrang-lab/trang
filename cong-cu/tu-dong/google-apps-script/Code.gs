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
// đoạn cuối link bài TCB → mã công thức tự động. Danh sách mới nhất đọc từ kho (cong-cu/tu-dong/danh-sach.json) mỗi lần chạy,
// nên thêm bài tự động mới KHÔNG cần dán lại mã; danh sách dưới đây chỉ dùng khi không đọc được kho.
const DANH_SACH = 'https://raw.githubusercontent.com/vuthithuytrang-lab/trang/claude/vibrant-keller-rk0i98/cong-cu/tu-dong/danh-sach.json';
const CONG_THUC_DU_PHONG = {
  'gia-ca-phe-hom-nay': 'gia-ca-phe', 'gia-xang-dau-hom-nay': 'gia-xang-dau', 'vang-24k': 'vang-24k',
  'vang-14k-gia-hom-nay': 'vang-14k', 'vang-18k': 'vang-18k', 'vang-10k': 'vang-10k',
  '1-chi-vang-bao-nhieu-tien': '1-chi-vang', 'gia-vang-16k-hom-nay': 'vang-16k', 'vang-610-la-vang-gi': 'vang-610',
  'lai-suat-tiet-kiem': 'lai-suat-1', 'cach-tinh-lai-suat-tien-gui-tiet-kiem': 'lai-suat-2',
};
const TZ = 'Asia/Ho_Chi_Minh';
// Mỗi bài 1 file Docs CỐ ĐỊNH (Trang chốt 29/10/2026): lần sau chép nội dung mới đè vào chính file đó, link không đổi,
// bản cũ vẫn xem được trong Lịch sử phiên bản của Docs. Danh sách mã bài → id file ở kho (file-co-dinh.json).
const FILE_CO_DINH = 'https://raw.githubusercontent.com/vuthithuytrang-lab/trang/claude/vibrant-keller-rk0i98/cong-cu/tu-dong/file-co-dinh.json';

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

  let CONG_THUC = CONG_THUC_DU_PHONG;
  try { CONG_THUC = JSON.parse(UrlFetchApp.fetch(DANH_SACH + '?t=' + Date.now()).getContentText()); } catch (e) {}
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
      const ten = tt.ten;
      const id = ghiDocs_(t.ma, ten, html);
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

/** File cố định của bài: còn dùng được → chép nội dung mới đè vào (đổi tên theo ngày mới); chưa có / đã xóa → tạo file mới và nhớ lại. */
function ghiDocs_(ma, ten, html) {
  const kho = PropertiesService.getScriptProperties();
  const ds = JSON.parse(kho.getProperty('fileCoDinh') || '{}');
  if (!ds[ma]) {
    try { ds[ma] = JSON.parse(UrlFetchApp.fetch(FILE_CO_DINH + '?t=' + Date.now()).getContentText())[ma]; } catch (e) {}
  }
  if (ds[ma]) {
    try {
      if (!DriveApp.getFileById(ds[ma]).isTrashed()) { ghiDe_(ds[ma], ten, html); return ds[ma]; }
    } catch (e) {}
  }
  ds[ma] = taoDocs_(ten, html);
  kho.setProperty('fileCoDinh', JSON.stringify(ds));
  return ds[ma];
}

/** Chép HTML mới đè vào file Google Docs có sẵn (giữ nguyên id/link, Docs lưu bản cũ trong Lịch sử phiên bản). */
function ghiDe_(id, ten, html) {
  const ranh = 'ranh' + Date.now();
  const meta = JSON.stringify({ name: ten });
  const than = '--' + ranh + '\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n' + meta +
    '\r\n--' + ranh + '\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n' + html + '\r\n--' + ranh + '--';
  const r = UrlFetchApp.fetch('https://www.googleapis.com/upload/drive/v3/files/' + id + '?uploadType=multipart&supportsAllDrives=true', {
    method: 'patch', contentType: 'multipart/related; boundary=' + ranh,
    payload: Utilities.newBlob(than).setContentType('multipart/related').getBytes(),
    headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() }, muteHttpExceptions: true,
  });
  if (r.getResponseCode() !== 200) throw new Error('Drive ' + r.getResponseCode() + ': ' + r.getContentText().slice(0, 100));
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

/* ===================== TRANG APP CHO MỌI NGƯỜI (không cần tài khoản Claude) =====================
 * Triển khai 1 lần: Apps Script → Triển khai → Tùy chọn triển khai mới → Loại: Ứng dụng web →
 * Thực thi dưới dạng: Tôi · Người có quyền truy cập: Bất kỳ ai → Triển khai → copy link "Ứng dụng web".
 * Ai có link đều mở được, tích bài, bấm "Chạy cập nhật" → trang tích ô trong Sheet (máy tự động lo phần còn lại).
 */
function doGet() {
  return HtmlService.createHtmlOutput(TRANG_APP_)
    .setTitle('Cập nhật bài Techcombank')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/** Danh sách bài + trạng thái cho trang app. */
function layDanhSach() {
  const ss = SpreadsheetApp.openById(CAU_HINH.SHEET_ID);
  const sh = ss.getSheets()[0];
  const du = sh.getRange(1, 1, sh.getLastRow(), 6).getDisplayValues();
  const app = ss.getSheetByName(CAU_HINH.TAB_APP);
  const ttApp = app ? app.getRange(1, 1, Math.max(app.getLastRow(), 1), 5).getDisplayValues() : [];
  const theoStt = {};
  ttApp.slice(1).forEach(r => { if (Number(r[0])) theoStt[Number(r[0])] = r; });
  let mienPhi = CONG_THUC_DU_PHONG;
  try { mienPhi = JSON.parse(UrlFetchApp.fetch(DANH_SACH + '?t=' + Date.now()).getContentText()); } catch (e) {}
  const homNay = Utilities.formatDate(new Date(), TZ, 'd/M');
  return du.slice(1).filter(r => Number(r[0]) && r[1]).map(r => {
    const a = theoStt[Number(r[0])] || [];
    const duoi = String(r[1]).trim().replace(/\/+$/, '').split('/').pop();
    return { stt: Number(r[0]), ten: String(r[2]).trim(), url: r[1], tich: r[4] === 'TRUE',
             mienPhi: !!mienPhi[duoi], tenFile: a[1] || '', link: a[2] || '', luc: a[3] || '', ghiChu: a[4] || '',
             homNay: du[0][5] === homNay ? r[5] : '' };
  });
}

/** Tích ô "Chạy update" cho các STT được chọn (chỉ cột E, chỉ dòng có bài). */
function tichBai(dsStt) {
  const sh = SpreadsheetApp.openById(CAU_HINH.SHEET_ID).getSheets()[0];
  const du = sh.getRange(1, 1, sh.getLastRow(), 2).getValues();
  let n = 0;
  (dsStt || []).slice(0, 50).forEach(stt => {
    const r = du.findIndex((row, i) => i > 0 && Number(row[0]) === Number(stt) && row[1]);
    if (r > 0) { sh.getRange(r + 1, 5).setValue(true); n++; }
  });
  return n;
}

const TRANG_APP_ = `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600&family=Montserrat:wght@700;800&display=swap" rel="stylesheet">
<style>
:root{--xanh:#004AEF;--navy:#002992;--mint:#07EF9C;--nen:#F3F3F6;--vien:#DCDCDC;--chu:#151515;--phu:#5A6B66;--cam:#F68B1F;--vang:#FFCE00}
*{box-sizing:border-box}body{margin:0;background:var(--nen);color:var(--chu);font:15px/1.55 "Be Vietnam Pro",Arial,sans-serif;padding:20px 16px 110px}
.w{max-width:900px;margin:0 auto}h1{font:800 clamp(22px,4vw,30px)/1.2 Montserrat,Arial,sans-serif;color:var(--navy);margin:0 0 4px}
.dau{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:center;justify-content:space-between;margin-bottom:14px}
.logo{background:#fff;border-radius:10px;padding:8px 12px}.logo img{width:160px;display:block}
p.l{margin:0;color:var(--phu);max-width:60ch}
.ds{background:#fff;border:1px solid var(--vien);border-radius:12px;overflow:hidden}
label.d{display:grid;grid-template-columns:24px 1fr auto;gap:2px 12px;align-items:center;padding:11px 14px;border-top:1px solid var(--vien);cursor:pointer}
label.d:first-child{border-top:0}label.d.on{background:#EAF0FF}input{width:18px;height:18px;accent-color:var(--xanh)}
.t{font-weight:600}.mp{font-size:11px;background:#d4fbe9;border-radius:99px;padding:1px 8px;margin-left:6px;font-weight:600}
.c{font-size:12px;font-weight:600;border-radius:99px;padding:3px 10px;background:#E8EDFB;white-space:nowrap}
.c.xong{background:#c9f9e4}.c.cho{background:#fff0b3}.c.loi{background:#fde0c4}
.m{grid-column:2/4;font-size:13px;color:var(--phu);display:flex;flex-wrap:wrap;gap:2px 14px}.m a{color:var(--xanh);font-weight:600;text-decoration:none}
.bar{position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:1px solid var(--vien);padding:12px 16px}
.bi{max-width:900px;margin:0 auto;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
#msg{flex:1;min-width:0;font-size:14px}button{font:700 15px Montserrat,Arial,sans-serif;background:var(--xanh);color:#fff;border:0;border-radius:10px;padding:12px 22px;cursor:pointer}
button[disabled]{opacity:.45;cursor:default}
</style></head><body><div class="w">
<div class="dau"><div><h1>Cập nhật bài Techcombank</h1><p class="l">Tích bài cần cập nhật rồi bấm <b>Chạy cập nhật</b>. Khoảng 10–20 phút sau, link file Google Docs hiện ngay tại đây. Ngày ghi trong bài là ngày hôm sau.</p></div>
<span class="logo"><img alt="SEONGON" src="https://raw.githubusercontent.com/vuthithuytrang-lab/trang/claude/vibrant-keller-rk0i98/cong-cu/nhan-dien-thuong-hieu/logo-goc/SEONGON-logo-ngang.webp"></span></div>
<div class="ds" id="ds"><div style="padding:24px;text-align:center;color:#5A6B66">Đang tải danh sách bài…</div></div></div>
<div class="bar"><div class="bi"><div id="msg">Chưa chọn bài nào.</div><button id="chay" disabled>Chạy cập nhật</button></div></div>
<script>
var ds=[],chon={},dangGui=false;
function e(s){return String(s||'').replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function tt(b){if(b.tich)return['cho','Đang chạy'];if(/^⚠️/.test(b.ghiChu))return['loi','Lỗi'];if(/^Cần xem lại/.test(b.ghiChu))return['loi','Cần xem lại'];if(b.link||b.homNay)return['xong','Đã xong'];return['','Sẵn sàng']}
function ve(){document.getElementById('ds').innerHTML=ds.map(function(b){var t=tt(b),on=chon[b.stt];
return '<label class="d'+(on?' on':'')+'"><input type="checkbox" data-s="'+b.stt+'"'+(on?' checked':'')+'><span class="t">'+e(b.ten)+(b.mienPhi?'<span class="mp">Miễn phí</span>':'')+'</span><span class="c '+t[0]+'">'+t[1]+'</span>'
+'<span class="m">'+(b.link?'<span>'+e(b.luc)+'</span><a target="_blank" href="'+e(b.link)+'">Mở file Docs ↗</a>':(b.homNay&&!/^⏳/.test(b.homNay)?'<span>Hôm nay: '+e(b.homNay)+'</span>':'<span>Chưa có bản mới</span>'))
+'<a target="_blank" href="'+e(b.url)+'">Bài trên web ↗</a>'+(/^(⚠️|Cần xem lại)/.test(b.ghiChu)?'<span style="flex-basis:100%">'+e(b.ghiChu.slice(0,300))+'</span>':'')+'</span></label>'}).join('');
var n=Object.keys(chon).length;var bt=document.getElementById('chay');if(!dangGui){bt.disabled=!n;bt.textContent=n?'Chạy cập nhật ('+n+' bài)':'Chạy cập nhật'}}
function tai(){google.script.run.withSuccessHandler(function(d){ds=d;ve()}).withFailureHandler(function(){document.getElementById('msg').textContent='Chưa tải được danh sách – thử tải lại trang.'}).layDanhSach()}
document.getElementById('ds').addEventListener('change',function(ev){var s=ev.target.getAttribute('data-s');if(!s)return;if(ev.target.checked)chon[s]=1;else delete chon[s];document.getElementById('msg').textContent=Object.keys(chon).length?'Đã chọn '+Object.keys(chon).length+' bài.':'Chưa chọn bài nào.';ve()});
document.getElementById('chay').onclick=function(){var s=Object.keys(chon);if(!s.length||dangGui)return;dangGui=true;var bt=this;bt.disabled=true;bt.textContent='Đang gửi…';
google.script.run.withSuccessHandler(function(n){dangGui=false;chon={};document.getElementById('msg').textContent='Đã gửi '+n+' bài. Khoảng 10–20 phút sau link file sẽ hiện ở đây.';tai()})
.withFailureHandler(function(err){dangGui=false;document.getElementById('msg').textContent='Chưa gửi được: '+err.message;ve()}).tichBai(s.map(Number))};
tai();setInterval(tai,60000);
</script></body></html>`;

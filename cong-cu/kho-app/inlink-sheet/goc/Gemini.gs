/**
 * Gemini.gs — phần duy nhất cần AI: chọn đoạn và viết 1 câu chứa anchor.
 * Khóa Gemini lưu trong "thuộc tính người dùng" của app (menu Inlink → Cài khóa Gemini), không nằm trong code/sheet.
 * Sổ bài học (BAI-HOC-GOP-Y.md) được tải mới mỗi lần chạy từ kho GitHub công khai → bài học mới tự vào lời dặn AI.
 */

var NGUON_BAI_HOC = [
  'https://raw.githubusercontent.com/vuthithuytrang-lab/trang/main/cong-cu/tao-docs-tu-url/BAI-HOC-GOP-Y.md',
  'https://raw.githubusercontent.com/vuthithuytrang-lab/trang/claude/confident-hopper-wh5wrt/cong-cu/tao-docs-tu-url/BAI-HOC-GOP-Y.md'
];

var QUY_TAC = [
  'Bạn là biên tập viên nội dung tiếng Việt cấp cao cho blog doanh nghiệp (ngân hàng / nội thất…).',
  'Nhiệm vụ: chèn MỘT internal link sao cho người đọc không nhận ra là câu chèn thêm.',
  'Quy tắc bắt buộc:',
  '- Câu viết ra phải chứa ANCHOR đúng nguyên văn, đúng hoa/thường, đúng 1 lần, là một phần tự nhiên của câu (tân ngữ/bổ ngữ), không phải nhãn treo.',
  '- Chỉ chọn đoạn ĐANG nói đúng chủ đề của trang đích. Nếu phải đổi chủ đề mới nhét được anchor thì chỗ đó sai.',
  '- Câu phải nối logic với câu ngay trước (nguyên nhân → hệ quả, bước trước → bước sau), cùng ngôi xưng (bạn / khách hàng / doanh nghiệp) và giọng của bài.',
  '- Câu phải nói rõ vì sao trang đích giúp người đọc ở đúng lúc này, cụ thể theo đoạn, không chung chung kiểu "tham khảo thêm".',
  '- Không bịa con số, lãi suất, phí, khuyến mãi, tính năng sản phẩm. Chỉ dùng điều có trong bài gốc hoặc thông tin trang đích được cung cấp.',
  '- Không so sánh trực diện sản phẩm. Không dấu chấm than, không câu hỏi tu từ, không từ quảng cáo.',
  '- Cấm các cụm: "Bên cạnh đó, bạn cũng có thể tham khảo", "Ngoài ra, bạn có thể tìm hiểu thêm", "để có thêm thông tin", "để hiểu rõ hơn", "một cách hiệu quả", "vô cùng", "hữu ích", "tham khảo ngay", "đừng quên", "chắc chắn", "tại đây".',
  '- cach = "sentence": 1 câu ngắn (≤ 35 từ) nối vào CUỐI đoạn đã chọn. cach = "xemthem": 1 dòng riêng sau đoạn, bắt đầu ">>> " + MỘT CÂU HOÀN CHỈNH nối ý đoạn ngay trên (cấm dòng cụt kiểu "Xem thêm: <cụm>").',
  '- Nếu KHÔNG có đoạn nào thật sự hợp ngữ cảnh: trả về i = -1 và ly_do. Bỏ link tốt hơn chèn gượng (người duyệt đã nói rõ điều này).',
  'Chỉ trả về JSON: {"i": số đoạn, "cach": "sentence" | "xemthem", "cau": "câu tiếng Việt có dấu"} hoặc {"i": -1, "ly_do": "..."}'
].join('\n');

function baiHoc() {
  var c = CacheService.getScriptCache(), x = c.get('baiHoc');
  if (x) return x;
  for (var i = 0; i < NGUON_BAI_HOC.length; i++) {
    try {
      var r = UrlFetchApp.fetch(NGUON_BAI_HOC[i], { muteHttpExceptions: true });
      if (r.getResponseCode() === 200) { x = r.getContentText('UTF-8').slice(0, 20000); c.put('baiHoc', x, 21600); return x; }
    } catch (e) {}
  }
  return '';
}

function goiGemini(prompt) {
  var p = PropertiesService.getUserProperties();
  var key = p.getProperty('GEMINI_KEY');
  if (!key) throw new Error('chưa cài khoá Gemini nên không viết được câu mới (bảng điều khiển → Khoá AI)');
  var model = p.getProperty('GEMINI_MODEL') || 'gemini-2.5-flash';
  var r = UrlFetchApp.fetch('https://generativelanguage.googleapis.com/v1beta/models/' + model + ':generateContent', {
    method: 'post', contentType: 'application/json', muteHttpExceptions: true,
    headers: { 'x-goog-api-key': key },
    payload: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { responseMimeType: 'application/json', temperature: 0.4 } })
  });
  if (r.getResponseCode() !== 200) throw new Error('Gemini trả lỗi ' + r.getResponseCode() + ': ' + r.getContentText().slice(0, 300));
  var j = JSON.parse(r.getContentText());
  var t = j.candidates && j.candidates[0] && j.candidates[0].content.parts.map(function (x) { return x.text || ''; }).join('');
  return JSON.parse(String(t).replace(/^```json\s*|```\s*$/g, ''));
}

/** Thông tin trang đích (tiêu đề + mô tả + đoạn đầu) để AI biết link dẫn tới đâu. */
function thongTinDich(url) {
  var c = CacheService.getScriptCache(), k = 'dich_' + Utilities.base64EncodeWebSafe(url).slice(0, 200), x = c.get(k);
  if (x) return x;
  var s = 'Trang đích: ' + url;
  try {
    var t = taiTrang(url);
    if (t.ma === 200) {
      var info = layThongTinTrang(t.html);
      var h2 = (t.html.match(/<h2[^>]*>[\s\S]*?<\/h2>/gi) || []).slice(0, 8).map(function (h) { return chuanHoa(h.replace(/<[^>]+>/g, '')); });
      s += '\nTiêu đề: ' + info.title + '\nMô tả: ' + info.meta + '\nCác mục: ' + h2.join(' | ');
    }
  } catch (e) {}
  c.put(k, s, 21600);
  return s;
}

/** Hỏi AI chỗ chèn + câu; tự soát, sai thì hỏi lại 1 lần kèm lý do. */
function aiChonCho(a, doan, pct, ung, ngCanh) {
  var ds = ung.map(function (i) { return '[' + i + '] (' + Math.round(pct[i]) + '%) ' + doan[i].text.slice(0, 450); }).join('\n');
  var dich = thongTinDich(a.url);
  var hoi = QUY_TAC + '\n\nSỔ BÀI HỌC TỪ NGƯỜI DUYỆT (phải tránh):\n' + baiHoc() +
    (ngCanh.luat && ngCanh.luat.length ? '\n\nLUẬT RIÊNG CỦA DỰ ÁN (bắt buộc, ưu tiên hơn quy tắc chung; vi phạm thì trả i = -1):\n- ' + ngCanh.luat.join('\n- ') : '') +
    (ngCanh.giongVan ? '\nGIỌNG VĂN: ' + ngCanh.giongVan : '') + (ngCanh.ghiChuDong ? '\nGHI CHÚ RIÊNG BÀI NÀY: ' + ngCanh.ghiChuDong : '') +
    '\n\nBÀI: ' + ngCanh.tieuDe + '\nANCHOR: "' + a.anchor + '"\n' + dich +
    '\n\nCÁC ĐOẠN ĐƯỢC PHÉP CHÈN (số trong ngoặc vuông là i):\n' + ds;
  var lyDo = '';
  for (var lan = 0; lan < 2; lan++) {
    var g;
    try { g = goiGemini(hoi + (lyDo ? '\n\nLần trước bị loại vì: ' + lyDo + '. Viết lại.' : '')); }
    catch (e) { return { ok: false, ly_do: e.message }; }
    if (g.i === -1 || g.i === '-1') return { ok: false, ly_do: 'AI thấy không có chỗ hợp ngữ cảnh: ' + (g.ly_do || '') };
    var i = parseInt(g.i, 10);
    if (ung.indexOf(i) < 0) { lyDo = 'i không nằm trong danh sách được phép'; continue; }
    var cau = chuanHoa(g.cau || '');
    var cach = g.cach === 'xemthem' ? 'xemthem' : 'sentence';
    if (cach === 'xemthem' && cau.indexOf('>>>') !== 0) cau = '>>> Xem thêm: ' + cau;
    lyDo = kiemTraCauChen(cau, a.anchor, ngCanh.chuBai + ' ' + dich);
    if (!lyDo) return { ok: true, i: i, cach: cach, cau: cau };
  }
  return { ok: false, ly_do: 'câu AI viết không đạt: ' + lyDo };
}

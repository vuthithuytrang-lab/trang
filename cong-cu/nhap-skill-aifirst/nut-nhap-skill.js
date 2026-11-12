(async () => {
  if (window.__dangNhapSkill) return; window.__dangNhapSkill = 1;
  if (!/aifirst\.seongon\.com$/.test(location.hostname)) { alert('Bạn mở trang aifirst.seongon.com và đăng nhập trước, rồi bấm lại nút này nhé.'); return; }
  const DS = [
    { loai: 'skill', ten: 'Phân loại dự án SEO (PLDA / TLDA)', phut: 120, khoa: ['plda', 'tlda', 'phan loai du an', 'thao luan du an'],
      dung_cho: 'Nhận đề bài của BD/Account, đánh giá thương hiệu, SEO, offpage, technical, content, đối thủ; kết luận làm được không, KPI cam kết, ngân sách sản xuất (A/B/C); xuất bài trả BD và file Excel đánh giá chủ đề.' },
    { loai: 'skill', ten: 'Tổng hợp KLCV và tính lương thực tập sinh', phut: 90, khoa: ['klcv', 'luong tts', 'luong thuc tap', 'khoi luong cong viec'],
      dung_cho: 'Đọc file log công việc hằng tháng của TTS, quy đổi từng loại task ra phút theo quy chuẩn SEONGON, nhân hệ số ngoài giờ, so KPI và ra bảng lương.' },
    { loai: 'skill', ten: 'Tối ưu Title & Meta SEO', phut: 20, khoa: ['title', 'meta'],
      dung_cho: 'Viết tiêu đề (title) và mô tả (meta description) chuẩn SEO theo insight người tìm, không cam kết quá mức với nội dung ngân hàng/tài chính.' },
    { loai: 'skill', ten: 'Chèn từ khoá on-page (nội dung ngân hàng)', phut: 30, khoa: ['chen tu khoa', 'onpage', 'on-page'],
      dung_cho: 'Chèn từ khoá SEO vào bài viết ngân hàng đúng vị trí ưu tiên, giữ ngôn ngữ pháp lý và không cam kết sai về sản phẩm.' },
    { loai: 'skill', ten: 'Lịch nội dung tuần (brief + email nhóm khách)', phut: 180, khoa: ['lich noi dung', 'brief'],
      dung_cho: 'Đọc lịch đăng tuần, bung brief gửi thiết kế (hạn lùi 3 ngày, né cuối tuần), soạn email riêng từng nhóm khách, chờ duyệt rồi gửi, xuất bảng theo dõi cho sếp.' },
    { loai: 'automation', ten: 'Bản tin Marketing sáng qua Telegram', phut: 30, khoa: ['ban tin'],
      dung_cho: 'Tự động 7h sáng mỗi ngày gom tin marketing/SEO mới và gửi bản tin tóm tắt vào Telegram.' },
  ];
  const bo = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/\s+/g, ' ');
  const goi = async (path, opts = {}) => {
    const r = await fetch(path, { method: opts.method || 'GET', credentials: 'same-origin',
      headers: opts.body ? { 'Content-Type': 'application/json' } : {}, body: opts.body ? JSON.stringify(opts.body) : undefined });
    let d = {}; try { d = await r.json(); } catch (e) {}
    if (r.status === 401) throw new Error('Bạn chưa đăng nhập. Đăng nhập xong rồi bấm lại nút nhé.');
    if (!r.ok) throw new Error(d.error || ('Lỗi ' + r.status));
    return d;
  };
  try {
    const { agents = [] } = await goi('/api/agent');
    const coRoi = agents.map((a) => bo(a.ten + ' ' + (a.dung_cho || '')));
    const daCo = [], canNhap = [];
    for (const s of DS) (coRoi.some((t) => t.includes(bo(s.ten)) || s.khoa.some((k) => t.includes(k))) ? daCo : canNhap).push(s);
    if (!canNhap.length) { alert('Tất cả skill đều đã có trên Bản đồ việc. Không cần nhập thêm gì.'); return; }
    if (!confirm('Sẽ NHẬP ' + canNhap.length + ' mục:\n- ' + canNhap.map((s) => s.ten).join('\n- ') +
      (daCo.length ? '\n\nBỎ QUA vì đã có (' + daCo.length + '):\n- ' + daCo.map((s) => s.ten).join('\n- ') : '') +
      '\n\nBấm OK để bắt đầu. Mỗi mục sẽ hỏi bạn 1 con số.')) return;
    const xong = [], loi = [];
    for (const s of canNhap) {
      const tl = prompt('"' + s.ten + '"\n\nTrước đây làm tay mất bao nhiêu PHÚT mỗi lần?\n(Số điền sẵn chỉ là gợi ý, bạn sửa cho đúng thực tế rồi bấm OK. Bấm Huỷ để bỏ qua mục này.)', s.phut);
      if (tl === null) continue;
      const phut = Math.max(1, Math.min(6000, parseInt(tl, 10) || s.phut));
      try { await goi('/api/agent', { method: 'POST', body: { loai: s.loai, ten: s.ten, phut_truoc: phut, dung_cho: s.dung_cho, link: '', dung_chung: [] } }); xong.push(s.ten); }
      catch (e) { loi.push(s.ten + ': ' + e.message); }
    }
    alert('Đã nhập ' + xong.length + ' mục.' + (xong.length ? '\n- ' + xong.join('\n- ') : '') + (loi.length ? '\n\nLỖI:\n- ' + loi.join('\n- ') : '') + '\n\nTrang sẽ tự tải lại.');
    location.hash = '#/agent'; location.reload();
  } catch (e) { alert('Chưa nhập được: ' + e.message); }
  finally { window.__dangNhapSkill = 0; }
})();

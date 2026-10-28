// Lấy giá cà phê nhân xô 4 tỉnh Tây Nguyên cho bài TCB "Giá cà phê Đắk Lắk hôm nay".
// Nguồn chính (Trang chọn): giacaphe.com – trang từng tỉnh. Số giá trên giacaphe.com được hiển thị bằng CSS (::after),
//   bản tải thường ra ô trống → phải mở bằng Chromium và đọc chữ đang hiển thị (getComputedStyle), không giải mã gì thêm.
// Nguồn dự phòng: Nhà Bè Agri (bảng "Khu vực | Giá | Thay đổi") – CÙNG giá nhân xô 4 tỉnh trong ngày (đối chiếu 28/10/2026: trùng cả 4 tỉnh),
//   nhưng KHÔNG có lịch sử theo ngày đáng tin → chỉ dùng cho giá mới nhất khi giacaphe.com chặn (vd 403 từ GitHub Actions).
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36';
const TINH = {
  dak_lak:  { ten: 'Đắk Lắk',  url: 'https://giacaphe.com/gia-ca-phe-dak-lak/' },
  lam_dong: { ten: 'Lâm Đồng', url: 'https://giacaphe.com/gia-ca-phe-lam-dong/' },
  gia_lai:  { ten: 'Gia Lai',  url: 'https://giacaphe.com/gia-ca-phe-gia-lai/' },
  dak_nong: { ten: 'Đắk Nông', url: 'https://giacaphe.com/gia-ca-phe-dak-nong/' },
};
const NHA_BE = 'https://nhabeagri.com/gia-nong-san/gia-ca-phe/';
const so = s => { const m = (s || '').replace(/[−–]/g, '-').match(/[+-]?\d[\d.,]*/); if (!m) return null;
  const v = parseInt(m[0].replace(/[.,]/g, ''), 10); return Number.isFinite(v) ? v : null; };

async function trang(b, url) {
  const pg = await b.newPage({ userAgent: UA });
  // Chromium không tin chứng chỉ proxy của máy chủ → mọi lượt tải đi qua Node (vẫn kiểm tra chứng chỉ bằng CA của proxy)
  await pg.route('**/*', async r => { try { await r.fulfill({ response: await r.fetch() }); } catch (e) { await r.abort().catch(() => {}); } });
  const res = await pg.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  return { pg, status: res ? res.status() : 0 };
}

async function doc_giacaphe(b, t) {
  const { pg, status } = await trang(b, t.url);
  try {
    if (status >= 400) throw new Error('HTTP ' + status);
    let d = null;
    for (let i = 0; i < 6; i++) {
      await pg.waitForTimeout(i ? 3000 : 1500);
      d = await pg.evaluate(() => {
        const hien = el => {               // chữ đang hiển thị của ô: chữ thường + chữ CSS ::before/::after
          let s = '';
          const walk = n => {
            if (n.nodeType === 3) { s += n.textContent; return; }
            if (n.nodeType !== 1) return;
            const cs = getComputedStyle(n);
            if (cs.display === 'none' || cs.visibility === 'hidden') return;
            const ps = w => { const c = getComputedStyle(n, w).content; return c && c !== 'none' && c !== 'normal' ? c.replace(/^["']|["']$/g, '') : ''; };
            s += ps('::before'); n.childNodes.forEach(walk); s += ps('::after');
          };
          walk(el);
          return s.replace(/\s+/g, ' ').trim();
        };
        const rows = [...document.querySelectorAll('table.price-table tbody tr, table tbody tr')]
          .map(tr => [...tr.cells].map(hien))
          .filter(c => c.length >= 3 && /^\d{2}\/\d{2}\/\d{4}$/.test(c[0]));
        const md = (document.querySelector('meta[name="description"]') || {}).content || '';
        const tb = document.querySelector('._trung-binh-gia');
        return { rows, tieu_de: document.title, mo_ta: md, gia_dau: tb ? hien(tb) : '' };
      });
      if (d.rows.length && d.rows.every(r => /\d/.test(r[1]))) break;
    }
    const lich_su = [], seen = new Set();
    for (const r of d.rows) {
      if (seen.has(r[0])) continue; seen.add(r[0]);
      const gia = so(r[1]), doi = so(r[2]);
      if (gia == null || gia < 10000) continue;
      if (doi == null) continue;
      lich_su.push({ ngay: r[0], gia, thay_doi: doi, chu_nguon: r.join(' | ') });
    }
    if (!lich_su.length) throw new Error('không thấy số trong bảng giá theo ngày');
    const m = d.mo_ta.match(/cập nhật lúc (\d{1,2}\/\d{1,2}\/\d{4})(?: lúc (\d{1,2}:\d{2}))?/i);
    return { ten: t.ten, nguon: t.url, ngay: lich_su[0].ngay, gia: lich_su[0].gia, thay_doi: lich_su[0].thay_doi,
             cap_nhat: m ? (m[2] ? m[2] + ' ' : '') + m[1] : lich_su[0].ngay, lich_su };
  } finally { await pg.close(); }
}

async function doc_nha_be(b) {
  const { pg, status } = await trang(b, NHA_BE);
  try {
    if (status >= 400) throw new Error('HTTP ' + status);
    await pg.waitForTimeout(2000);
    const d = await pg.evaluate(() => ({
      rows: [...document.querySelectorAll('tr')].map(tr => [...tr.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim())),
      text: document.body.innerText,
    }));
    const ngay = (d.text.match(/Giá cà phê hôm nay (\d{1,2}\/\d{1,2}\/\d{4})/i) || [])[1] || null;
    const cn = (d.text.match(/Cập nhật gần nhất:\s*([^\n]+)/i) || [])[1] || '?';
    const kq = {};
    for (const [ma, t] of Object.entries(TINH)) {
      const r = d.rows.find(c => c.length >= 2 && c[0].normalize('NFC') === t.ten);
      const gia = r ? so(r[1]) : null;
      if (gia && gia > 10000) kq[ma] = { ten: t.ten, gia, ngay, cap_nhat: cn.trim(), nguon: NHA_BE, chu_nguon: r.join(' | ') };
    }
    if (!Object.keys(kq).length) throw new Error('không thấy bảng Khu vực');
    return kq;
  } finally { await pg.close(); }
}

(async () => {
  const out = process.argv[2] || 'gia.json';
  const b = await chromium.launch({ args: ['--no-sandbox'], ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
  const kq = { giacaphe: {}, nha_be: null };
  for (const [ma, t] of Object.entries(TINH)) {
    try { kq.giacaphe[ma] = await doc_giacaphe(b, t); }
    catch (e) { kq.giacaphe[ma] = null; console.error(`giacaphe ${t.ten} LỖI`, e.message.slice(0, 120)); }
  }
  try { kq.nha_be = await doc_nha_be(b); }
  catch (e) { console.error('Nhà Bè Agri LỖI', e.message.slice(0, 120)); }
  await b.close();
  fs.writeFileSync(out, JSON.stringify(kq, null, 1));
  const f = v => v == null ? '-' : v.toLocaleString('en-US');
  for (const [ma, t] of Object.entries(TINH)) {
    const v = kq.giacaphe[ma];
    console.log(`giacaphe ${t.ten.padEnd(8)}`, v ? `${v.ngay} ${f(v.gia)} (${v.thay_doi >= 0 ? '+' : ''}${f(v.thay_doi)}) | ${v.lich_su.length} ngày | cập nhật ${v.cap_nhat}` : 'KHÔNG ĐỌC ĐƯỢC');
  }
  if (kq.nha_be) for (const v of Object.values(kq.nha_be)) console.log(`Nhà Bè   ${v.ten.padEnd(8)} ${v.ngay || '?'} ${f(v.gia)} | cập nhật ${v.cap_nhat}`);
  else console.log('Nhà Bè Agri KHÔNG ĐỌC ĐƯỢC');
  if (Object.values(kq.giacaphe).some(v => !v) || !kq.nha_be) process.exit(1);
})();

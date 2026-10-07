// Lấy giá vàng 24K (VND/chỉ) của 4 thương hiệu cho bài TCB "Vàng 24K".
// PNJ: pnj.com.vn | DOJI: banggia.doji.vn | SJC, BTMC: webgia.com (sjc.com.vn chặn máy chủ, btmc.vn không vào được)
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia_vang.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const NGUON = {
  pnj:  { url: 'https://www.pnj.com.vn/site/gia-vang', sp: /^Nhẫn Trơn PNJ 999\.9$/i, nhan: 1000 },
  doji: { url: 'https://banggia.doji.vn/gold-price', sp: /^VÀNG MIẾNG SJC$/, nhan: 1000 },
  sjc:  { url: 'https://webgia.com/gia-vang/sjc/', sp: /^Vàng SJC 1L, 10L, 1KG$/i, nhan: 1 },
  btmc: { url: 'https://webgia.com/gia-vang/bao-tin-minh-chau/', sp: /^Nhẫn tròn trơn 999\.9 \(24k\)$/i, nhan: 1 },
};
const so = s => { const d = (s || '').replace(/\D/g, ''); return d ? parseInt(d, 10) : null; };
(async () => {
  const out = process.argv[2] || 'gia-vang.json';
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  const kq = {};
  for (const [ma, n] of Object.entries(NGUON)) {
    // DOJI trả bảng khác khi giả trình duyệt Mac -> để mặc định cho DOJI
    const pg = await b.newPage(ma === 'doji' ? {} : { userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36' });
    try {
      await pg.goto(n.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      let hit = null, text = '';
      for (let i = 0; i < 6 && !hit; i++) {
        await pg.waitForTimeout(4000);
        const rows = await pg.evaluate(() => [...document.querySelectorAll('tr')].map(tr => [...tr.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim())));
        for (const r of rows) {
          const k = r.findIndex(c => n.sp.test(c.normalize('NFC').toUpperCase()) || n.sp.test(c.normalize('NFC')));
          if (k >= 0 && so(r[k + 1]) && so(r[k + 2])) { hit = [r[k], so(r[k + 1]) * n.nhan, so(r[k + 2]) * n.nhan]; break; }
        }
        text = await pg.evaluate(() => document.body.innerText);
      }
      const m = text.match(/Cập nhật[^\n]{0,40}?(\d{1,2}:\d{2}(?::\d{2})?[^\n]{0,8}\d{1,2}\/\d{1,2}\/\d{4}|\d{1,2}\/\d{1,2}\/\d{4}[^\n]{0,4}\d{1,2}:\d{2}(?::\d{2})?)/i);
      kq[ma] = hit ? { san_pham: hit[0], mua: hit[1], ban: hit[2], cap_nhat: m ? m[1] : '?', nguon: n.url } : null;
    } catch (e) { kq[ma] = null; console.error(ma, 'LỖI', e.message.slice(0, 120)); }
    await pg.close();
  }
  await b.close();
  fs.writeFileSync(out, JSON.stringify(kq, null, 1));
  for (const [ma, v] of Object.entries(kq))
    console.log(ma.padEnd(5), v ? `${v.san_pham} | mua ${v.mua.toLocaleString('en-US')} | bán ${v.ban.toLocaleString('en-US')} | cập nhật ${v.cap_nhat}` : 'KHÔNG ĐỌC ĐƯỢC');
  if (Object.values(kq).some(v => !v)) process.exit(1);
})();

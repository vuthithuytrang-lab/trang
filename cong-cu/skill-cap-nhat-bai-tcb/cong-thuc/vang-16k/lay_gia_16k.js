// Lấy giá vàng 16K (VND/chỉ) cho bài TCB "Vàng 16K giá hôm nay".
// SJC: webgia.com (sjc.com.vn chặn máy chủ) | PNJ: pnj.com.vn | Mi Hồng: mihong.vn
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia_16k.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const NGUON = {
  sjc:    { url: 'https://webgia.com/gia-vang/sjc/', sp: /^Nữ trang 68%$/i, nhan: 1 },
  mihong: { url: 'https://www.mihong.vn/gia-vang-trong-nuoc', sp: /^680$/, nhan: 1 },
  pnj:    { url: 'https://www.pnj.com.vn/site/gia-vang', sp: /^Vàng 680 \(16\.3K\)$/i, nhan: 1000 },
};
const so = s => { const m = (s || '').match(/^[\d.,]+/); const d = m ? m[0].replace(/\D/g, '') : ''; return d ? parseInt(d, 10) : null; };
(async () => {
  const out = process.argv[2] || 'gia-16k.json';
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  const kq = {};
  for (const [ma, n] of Object.entries(NGUON)) {
    const pg = await b.newPage({ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36' });
    try {
      await pg.goto(n.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      let hit = null, text = '';
      for (let i = 0; i < 6 && !hit; i++) {
        await pg.waitForTimeout(4000);
        const rows = await pg.evaluate(() => [...document.querySelectorAll('tr')].map(tr => [...tr.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim())));
        for (const r of rows) {
          const k = r.findIndex(c => n.sp.test(c.normalize('NFC')));
          if (k < 0) continue;
          const gt = r.slice(k + 1).filter(c => !/VND\/chỉ/i.test(c));   // Mi Hồng có cột "VND/chỉ <ngày giờ>"
          if (so(gt[0]) && so(gt[1])) { hit = [r[k], so(gt[0]) * n.nhan, so(gt[1]) * n.nhan]; break; }
        }
        text = await pg.evaluate(() => document.body.innerText);
      }
      const m = (ma === 'mihong' ? text.match(/(\d{2}\/\d{2}\/\d{4} \d{1,2}:\d{2})/) && [null, text.match(/(\d{2}\/\d{2}\/\d{4} \d{1,2}:\d{2})/)[1]] : null) || text.match(/Cập nhật[^\n]{0,40}?(\d{1,2}:\d{2}(?::\d{2})?[^\n]{0,8}\d{1,2}\/\d{1,2}\/\d{4}|\d{1,2}\/\d{1,2}\/\d{4}[^\n]{0,4}\d{1,2}:\d{2}(?::\d{2})?)/i);
      kq[ma] = hit ? { san_pham: hit[0], mua: hit[1], ban: hit[2], cap_nhat: m ? m[1] : '?', nguon: n.url } : null;
    } catch (e) { kq[ma] = null; console.error(ma, 'LỖI', e.message.slice(0, 120)); }
    await pg.close();
  }
  await b.close();
  fs.writeFileSync(out, JSON.stringify(kq, null, 1));
  for (const [ma, v] of Object.entries(kq))
    console.log(ma.padEnd(9), v ? `${v.san_pham} | mua ${v.mua.toLocaleString('en-US')} | bán ${v.ban.toLocaleString('en-US')} đ/chỉ | cập nhật ${v.cap_nhat}` : 'KHÔNG ĐỌC ĐƯỢC');
  if (Object.values(kq).some(v => !v)) process.exit(1);
})();

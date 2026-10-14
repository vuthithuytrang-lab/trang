// Lấy giá vàng 610 (VND/chỉ) cho bài TCB "Vàng 610 là vàng gì?…" – 2 nguồn để giữ dạng khoảng "từ … đến …" của bài.
// PNJ: pnj.com.vn "Vàng 610 (14.6K)" (nghìn đ/chỉ) | SJC: webgia.com "Nữ trang 61%" (đ/chỉ)
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia_610.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const NGUON = {
  pnj: { url: 'https://www.pnj.com.vn/site/gia-vang', sp: /^Vàng 610 \(14\.6K\)$/i, nhan: 1000 },
  sjc: { url: 'https://webgia.com/gia-vang/sjc/', sp: /^Nữ trang 61%$/i, nhan: 1 },
};
const so = s => { const d = (s || '').replace(/\D/g, ''); return d ? parseInt(d, 10) : null; };
(async () => {
  const out = process.argv[2] || 'gia-610.json';
  const b = await chromium.launch({ args: ['--no-sandbox'], ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
  const kq = {};
  for (const [ma, n] of Object.entries(NGUON)) {
    const pg = await b.newPage({ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36' });
    // Chromium không tin chứng chỉ proxy của máy chủ → mọi lượt tải đi qua Node (vẫn kiểm tra chứng chỉ bằng CA của proxy)
    await pg.route('**/*', async r => { try { await r.fulfill({ response: await r.fetch() }); } catch (e) { await r.abort().catch(() => {}); } });
    try {
      await pg.goto(n.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      let hit = null, text = '';
      for (let i = 0; i < 6 && !hit; i++) {
        await pg.waitForTimeout(4000);
        const rows = await pg.evaluate(() => [...document.querySelectorAll('tr')].map(tr => [...tr.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim())));
        for (const r of rows) {
          const k = r.findIndex(c => n.sp.test(c.normalize('NFC')));
          if (k >= 0 && so(r[k + 1]) && so(r[k + 2])) { hit = [r[k], Math.round(so(r[k + 1]) * n.nhan), Math.round(so(r[k + 2]) * n.nhan)]; break; }
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
    console.log(ma.padEnd(9), v ? `${v.san_pham} | mua ${v.mua.toLocaleString('en-US')} | bán ${v.ban.toLocaleString('en-US')} đ/chỉ | cập nhật ${v.cap_nhat}` : 'KHÔNG ĐỌC ĐƯỢC');
  if (Object.values(kq).some(v => !v)) process.exit(1);
})();

// Lấy giá vàng 10K (VND/chỉ) của PNJ cho bài TCB "Vàng 10K là gì?…".
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia_10k.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const URL = 'https://www.pnj.com.vn/site/gia-vang';
const so = s => { const d = (s || '').replace(/\D/g, ''); return d ? parseInt(d, 10) : null; };
(async () => {
  const out = process.argv[2] || 'gia-10k.json';
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  const pg = await b.newPage({ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36' });
  let kq = null;
  try {
    await pg.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    for (let i = 0; i < 12 && !kq; i++) {
      if (i === 6) await pg.reload({ waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
      await pg.waitForTimeout(4000);
      const rows = await pg.evaluate(() => [...document.querySelectorAll('tr')].map(tr => [...tr.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim())));
      for (const r of rows) {
        const k = r.findIndex(c => /^Vàng 416 \(10K\)$/i.test(c.normalize('NFC')));
        if (k >= 0 && so(r[k + 1]) && so(r[k + 2])) {
          const text = await pg.evaluate(() => document.body.innerText);
          const m = text.match(/Cập nhật ngày:\s*([^\n]+)/i);
          kq = { pnj: { san_pham: r[k], mua: so(r[k + 1]) * 1000, ban: so(r[k + 2]) * 1000, cap_nhat: m ? m[1].trim() : '?', nguon: URL } };
          break;
        }
      }
    }
  } catch (e) { console.error('LỖI', e.message.slice(0, 120)); }
  await b.close();
  fs.writeFileSync(out, JSON.stringify(kq || { pnj: null }, null, 1));
  if (!kq) { console.log('pnj KHÔNG ĐỌC ĐƯỢC'); process.exit(1); }
  console.log(`pnj ${kq.pnj.san_pham} | mua ${kq.pnj.mua.toLocaleString('en-US')} | bán ${kq.pnj.ban.toLocaleString('en-US')} đ/chỉ | cập nhật ${kq.pnj.cap_nhat}`);
})();

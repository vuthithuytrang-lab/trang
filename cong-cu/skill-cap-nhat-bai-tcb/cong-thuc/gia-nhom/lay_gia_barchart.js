// Đọc giá chốt (settlement) từng hợp đồng trên barchart.com/futures/quotes/<MÃ>/overview
// Cách chạy: NODE_PATH=/opt/node22/lib/node_modules node barchart.js <file-ra.json> ALV26 ALX26 ...
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [out, ...syms] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--no-sandbox'], ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
  const pg = await b.newPage({ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36' });
  await pg.route('**/*', async r => { const u = r.request().url(); if (/\.(png|jpg|gif|woff2?|svg)(\?|$)/.test(u) || /doubleclick|googlesyndication|adservice/.test(u)) return r.abort().catch(()=>{}); try { await r.fulfill({ response: await r.fetch() }); } catch (e) { await r.abort().catch(() => {}); } });
  const res = { nguon: 'https://www.barchart.com/futures/quotes/<mã>/overview', lay_luc: new Date().toISOString(), hop_dong: [] };
  for (const s of syms) {
    const url = `https://www.barchart.com/futures/quotes/${s}/overview`;
    let row = { ma: s, url };
    for (let k = 0; k < 2 && !row.gia; k++) {
      try { await pg.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 }); } catch (e) { row.loi = e.message.split('\n')[0]; }
      for (let i = 0; i < 8; i++) {
        await pg.waitForTimeout(3000);
        const t = await pg.evaluate(() => document.body ? document.body.innerText : '');
        const re = new RegExp(`\\(${s}\\)\\s*\\n\\s*([0-9,]+\\.[0-9]+)(s?)\\s+([+-]?[0-9,.]+|unch)\\s+\\(([+-]?[0-9.]+%|unch)\\)\\s+([0-9/]+(?: [0-9:]+ [A-Z]+)?)`);
        const m = t.match(re);
        if (m) { const pc = t.match(/Previous Close\s*\n\s*([0-9,]+\.[0-9]+)/); Object.assign(row, { ten: (t.match(new RegExp(`(Aluminum|Copper)[^\\n]*\\(${s}\\)`))||[''])[0], gia: m[1], chot: m[2] === 's', thay_doi: m[3], phan_tram: m[4], thoi_diem: m[5], gia_truoc: pc ? pc[1] : null }); break; }
      }
    }
    console.log(JSON.stringify(row));
    res.hop_dong.push(row);
  }
  await b.close();
  fs.writeFileSync(out, JSON.stringify(res, null, 1));
})();

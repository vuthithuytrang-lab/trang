// Đọc 3 bảng hợp đồng kỳ hạn cao su trên giacaphe.com/gia-cao-su-truc-tuyen/ (TOCOM RSS3, SHFE, SGX TSR20).
// Trang vẽ số bằng JavaScript nên phải mở bằng Chromium có sẵn.
// Cách chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia_the_gioi.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const URL = 'https://giacaphe.com/gia-cao-su-truc-tuyen/';
(async () => {
  const out = process.argv[2] || 'gia-the-gioi.json';
  const b = await chromium.launch({ args: ['--no-sandbox'], ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
  const pg = await b.newPage({ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36' });
  await pg.route('**/*', async r => { try { await r.fulfill({ response: await r.fetch() }); } catch (e) { await r.abort().catch(() => {}); } });
  await pg.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
  const SAN = [['tocom', 'rubber_tocom'], ['shfe', 'shz_rubber'], ['sgx', 'str20_rubber']];
  let data = null;
  for (let i = 0; i < 12; i++) {
    await pg.waitForTimeout(5000);
    data = await pg.evaluate((SAN) => {
      const bang = {}, tieu_de = {};
      for (const [ten, ma] of SAN) {
        const t = document.querySelector(`table[data-exchange="${ma}"]`);
        if (!t) continue;
        tieu_de[ten] = [...t.querySelectorAll('thead th')].map(x => x.innerText.replace(/\s+/g, ' ').trim());
        bang[ten] = [...t.querySelectorAll('tbody tr')].map(tr => [...tr.cells].map(x => x.innerText.replace(/\s+/g, ' ').trim()))
          .filter(c => c.length > 2 && /\d/.test(c[1] || ""));
      }
      return { cap_nhat: [...document.querySelectorAll('span.tructuyen--time')].map(x => x.innerText.trim()), tieu_de, bang };
    }, SAN);
    if (SAN.every(([t]) => data.bang[t]?.length)) break;
  }
  await b.close();
  data.nguon = URL;
  data.lay_luc = new Date().toISOString();
  fs.writeFileSync(out, JSON.stringify(data, null, 1));
  console.log(JSON.stringify(data, null, 1));
  if (!SAN.every(([t]) => data.bang[t]?.length)) { console.error('KHÔNG đọc được đủ 3 bảng'); process.exit(1); }
})();

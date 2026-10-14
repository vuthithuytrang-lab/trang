// Đọc bảng giá Robusta London + Arabica New York trên giacaphe.com/gia-ca-phe-truc-tuyen/.
// Trang vẽ số bằng JavaScript nên phải mở bằng trình duyệt thật (Chromium có sẵn).
// Cách chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia_the_gioi.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const URL = 'https://giacaphe.com/gia-ca-phe-truc-tuyen/';
(async () => {
  const out = process.argv[2] || 'gia-the-gioi.json';
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  const pg = await b.newPage({ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36' });
  await pg.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
  let data = null;
  for (let i = 0; i < 12; i++) {           // chờ tối đa ~60 giây cho số hiện ra
    await pg.waitForTimeout(5000);
    data = await pg.evaluate(() => {
      const bang = {};
      for (const [ten, ma] of [['robusta', 'coffee_liffe'], ['arabica', 'coffee_ice']]) {
        const t = document.querySelector(`table[data-exchange="${ma}"]`);
        if (!t) continue;
        bang[ten] = [...t.querySelectorAll('tbody tr')].map(tr => {
          const c = [...tr.cells].map(x => x.innerText.replace(/\s+/g, ' ').trim());
          return { ky_han: c[0], gia: c[1], thay_doi: (c[2] || '').split(' ')[0], hom_truoc: c[7] };
        }).filter(r => /^\d\d\/\d\d$/.test(r.ky_han) && r.gia);
      }
      return { cap_nhat: document.querySelector('span.tructuyen--time')?.innerText || '', bang };
    });
    if (data.bang.robusta?.length && data.bang.arabica?.length) break;
  }
  await b.close();
  data.nguon = URL;
  fs.writeFileSync(out, JSON.stringify(data, null, 1));
  console.log(JSON.stringify(data, null, 1));
  if (!(data.bang.robusta?.length && data.bang.arabica?.length)) { console.error('KHÔNG đọc được bảng giá thế giới'); process.exit(1); }
})();

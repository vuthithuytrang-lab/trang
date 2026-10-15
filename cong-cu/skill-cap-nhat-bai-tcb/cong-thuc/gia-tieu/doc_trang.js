const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [url, out, wait] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--no-sandbox'], ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
  const pg = await b.newPage({ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36' });
  await pg.route('**/*', async r => { try { await r.fulfill({ response: await r.fetch() }); } catch (e) { await r.abort().catch(() => {}); } });
  await pg.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await pg.waitForTimeout(+(wait||15000));
  fs.writeFileSync(out, await pg.evaluate(() => document.body.innerText)); fs.writeFileSync(out+".html", await pg.content());
  await b.close();
})();

// Lấy toàn bộ bảng giá vàng SJC (chỉ khu vực Hồ Chí Minh = bảng niêm yết SJC) cho bài TCB "Giá vàng SJC".
// Nguồn: webgia.com/gia-vang/sjc/ (bản chép bảng giá chính thức của SJC; sjc.com.vn chặn máy chủ).
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia.js <file-ra.json>
// Ra: {"webgia": {"url","cap_nhat","dong":[{"ten","mua","ban"}]}}  (mua/bán = chuỗi số VND/lượng-chỉ đúng như nguồn, vd "13.800.000")
// Không đọc được -> "webgia": null, in "webgia KHÔNG ĐỌC ĐƯỢC", thoát mã 1.
const { chromium } = require('playwright');
const fs = require('fs');
const URL = 'https://webgia.com/gia-vang/sjc/';
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36';
const laSo = s => /^\d{1,3}(\.\d{3})+$/.test((s || '').trim());
(async () => {
  const out = process.argv[2] || 'gia.json';
  let kq = { webgia: null };
  const b = await chromium.launch({ args: ['--no-sandbox'], ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
  try {
    const pg = await b.newPage({ userAgent: UA });
    await pg.route('**/*', async r => { try { await r.fulfill({ response: await r.fetch() }); } catch (e) { await r.abort().catch(() => {}); } });
    await pg.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    let dong = [], text = '';
    for (let i = 0; i < 12 && !dong.length; i++) {
      if (i === 6) await pg.reload({ waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
      await pg.waitForTimeout(4000);
      const rows = await pg.evaluate(() => {
        const t = [...document.querySelectorAll('table')].find(t => /Loại vàng/i.test(t.innerText) && /Mua vào/i.test(t.innerText));
        return t ? [...t.querySelectorAll('tr')].map(tr => [...tr.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim())) : [];
      });
      // bảng niêm yết = khối "Hồ Chí Minh" (dòng đầu có ô khu vực, các dòng sau chỉ có 3 ô) cho tới khi gặp khu vực khác
      let trong = false;
      const tmp = [];
      for (const r of rows) {
        if (r.length === 4) { trong = /^Hồ Chí Minh$/i.test(r[0].normalize('NFC')); if (trong) r.shift(); else continue; }
        else if (!trong) continue;
        if (r.length === 3 && laSo(r[1]) && laSo(r[2])) tmp.push({ ten: r[0], mua: r[1], ban: r[2] });
        else if (r.length === 3) tmp.push({ ten: r[0], mua: null, ban: null });   // nguồn che số (webgia.com) -> không dùng
      }
      if (tmp.some(x => x.mua)) dong = tmp;
      text = await pg.evaluate(() => document.body.innerText);
    }
    const m = text.match(/Bảng giá vàng SJC hôm nay được cập nhật lúc\s*(\d{1,2}:\d{2}(?::\d{2})?\s+\d{1,2}\/\d{1,2}\/\d{4})/i)
           || text.match(/Cập nhật lúc\s*(\d{1,2}:\d{2}(?::\d{2})?\s+\d{1,2}\/\d{1,2}\/\d{4})/i);
    if (dong.length) kq.webgia = { url: URL, cap_nhat: m ? m[1] : '?', dong };
  } catch (e) { console.error('webgia LỖI', e.message.slice(0, 120)); }
  await b.close();
  fs.writeFileSync(out, JSON.stringify(kq, null, 1));
  const v = kq.webgia;
  if (!v) { console.log('webgia KHÔNG ĐỌC ĐƯỢC'); process.exit(1); }
  console.log(`webgia: ${v.dong.length} dòng, cập nhật ${v.cap_nhat}`);
  for (const d of v.dong) console.log(`  ${d.ten.padEnd(45)} mua ${d.mua || '(che)'} | bán ${d.ban || '(che)'}`);
})();

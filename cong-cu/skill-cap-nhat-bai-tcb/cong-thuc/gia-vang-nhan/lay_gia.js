// Lấy giá VÀNG NHẪN TRƠN 999.9 của 5 thương hiệu + giá vàng thế giới cho bài TCB "Giá vàng nhẫn hôm nay".
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia.js cap-nhat/gia.json
// Ra: { <mã>: {url, cap_nhat, ten_dong, mua, ban (VND/chỉ, số nguyên)} | null, thegioi: {url, cap_nhat, usd, doi_24h} | null }
// Nguồn hỏng -> in "<mã> KHÔNG ĐỌC ĐƯỢC …" và ghi null (không bao giờ đoán số).
const { chromium } = require('playwright');
const fs = require('fs');
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36';
// dòng nhẫn trơn của từng thương hiệu (khớp theo TÊN Ô, không theo thứ tự); nhan = hệ số đổi ra VND/chỉ
const NGUON = {
  sjc:    { url: 'https://webgia.com/gia-vang/sjc/', ua: UA, dong: /^Vàng nhẫn SJC 99,99% 1 chỉ, 2 chỉ, 5 chỉ$/i, nhan: 1 },
  btmc:   { url: 'https://webgia.com/gia-vang/bao-tin-minh-chau/', ua: UA, dong: /^Nhẫn tròn trơn 999\.9/i, nhan: 1 },
  phuquy: { url: 'https://phuquygroup.vn/', ua: UA, dong: /^Nhẫn tròn Phú Quý 999\.9$/i, nhan: 1 },
  doji:   { url: 'https://banggia.doji.vn/gold-price', ua: null, dong: /^NHẪN TRÒN 9999 HƯNG THỊNH VƯỢNG$/i, nhan: 1000 },   // DOJI ghi nghìn đ/chỉ
  pnj:    { url: 'https://www.pnj.com.vn/site/gia-vang', ua: UA, dong: /^Nhẫn Trơn PNJ 999\.9$/i, nhan: 1000 },                  // PNJ ghi nghìn đ/chỉ
  thegioi:{ url: 'https://giavang.org/the-gioi/', ua: UA, chu: /Giá vàng quốc tế \(XAU\) hôm nay là/i },
};
const so = s => { const d = String(s || '').replace(/\D/g, ''); return d ? parseInt(d, 10) : null; };
(async () => {
  const out = process.argv[2] || 'gia.json';
  const b = await chromium.launch({ args: ['--no-sandbox'], ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
  const kq = {};
  for (const [ma, n] of Object.entries(NGUON)) {
    const pg = await b.newPage(n.ua ? { userAgent: n.ua } : {});
    await pg.route('**/*', async r => { try { await r.fulfill({ response: await r.fetch() }); } catch (e) { await r.abort().catch(() => {}); } });
    let dong = null, text = '', loi = '';
    const tim = rows => {
      for (const r of rows) {
        const i = r.findIndex(c => n.dong.test(c.normalize('NFC')));
        if (i < 0) continue;
        const gia = r.slice(i + 1).map(so).filter(x => x);
        if (gia.length >= 2) return { ten_dong: r[i], mua: gia[0] * n.nhan, ban: gia[1] * n.nhan };
      }
      return null;
    };
    try {
      await pg.goto(n.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      for (let i = 0; i < 12; i++) {
        if (i === 6) await pg.reload({ waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
        await pg.waitForTimeout(4000);
        text = await pg.evaluate(() => document.body.innerText);
        if (n.chu) { if (n.chu.test(text)) break; continue; }
        const rows = await pg.evaluate(() => [...document.querySelectorAll('tr')].map(tr => [...tr.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim())).filter(r => r.length));
        dong = tim(rows);
        if (dong) break;
      }
    } catch (e) { loi = e.message.slice(0, 100); }
    await pg.close();
    const m = text.match(/[Cc]ập nhật[^\n]{0,40}?(\d{1,2}:\d{2}(?::\d{2})?[^\n]{0,8}\d{1,2}\/\d{1,2}\/\d{4}|\d{1,2}\/\d{1,2}\/\d{4}[^\n]{0,4}\d{1,2}:\d{2}(?::\d{2})?)/);
    const cap_nhat = m ? m[1].trim() : '?';
    if (ma === 'thegioi') {
      const u = text.match(/Giá vàng quốc tế \(XAU\) hôm nay là ([\d,]+\.?\d*) USD/);
      const d = text.match(/tương ứng với (giảm|tăng) [+-]?([\d,]+\.?\d*) USD/);
      if (u) {
        const usd = parseFloat(u[1].replace(/,/g, ''));
        const doi = d ? (d[1] === 'giảm' ? -1 : 1) * parseFloat(d[2].replace(/,/g, '')) : null;
        kq[ma] = { url: n.url, cap_nhat, usd, doi_24h: doi };
        console.log(ma.padEnd(8), `${usd} USD/ounce (${doi === null ? 'không rõ biến động' : doi}), cập nhật ${cap_nhat}`);
      } else { kq[ma] = null; console.log(`${ma} KHÔNG ĐỌC ĐƯỢC giá vàng thế giới ${loi}`); }
    } else if (dong) {
      kq[ma] = { url: n.url, cap_nhat, ...dong };
      console.log(ma.padEnd(8), `${dong.ten_dong}: mua ${dong.mua} / bán ${dong.ban} VND/chỉ, cập nhật ${cap_nhat}`);
    } else { kq[ma] = null; console.log(`${ma} KHÔNG ĐỌC ĐƯỢC dòng nhẫn trơn ${loi}`); }
  }
  await b.close();
  fs.mkdirSync(require('path').dirname(require('path').resolve(out)), { recursive: true });
  fs.writeFileSync(out, JSON.stringify(kq, null, 1));
})();

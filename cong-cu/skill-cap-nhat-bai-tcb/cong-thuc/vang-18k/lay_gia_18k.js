// Lấy giá vàng 18K (VND/chỉ) cho bài TCB "Vàng 18K là gì?…".
// PNJ: pnj.com.vn | SJC: webgia.com (sjc.com.vn chặn máy chủ) | DOJI: banggia.doji.vn (chỉ có giá mua "GIÁ NGUYÊN LIỆU 18K")
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia_18k.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36';
const NGUON = {
  pnj:  { url: 'https://www.pnj.com.vn/site/gia-vang', sp: /^Vàng 750 \(18K\)$/i, nhan: 1000, ua: UA },
  sjc:  { url: 'https://webgia.com/gia-vang/sjc/', sp: /^Nữ trang 75%$/i, nhan: 1, ua: UA },
  doji: { url: 'https://banggia.doji.vn/gold-price', sp: /NGUY.N LI.U 18K$/i, nhan: 1000, chi_mua: true },  // DOJI: để trình duyệt mặc định
};
const so = s => { const d = (s || '').replace(/\D/g, ''); return d ? parseInt(d, 10) : null; };
(async () => {
  const out = process.argv[2] || 'gia-18k.json';
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  const kq = {};
  for (const [ma, n] of Object.entries(NGUON)) {
    const pg = await b.newPage(n.ua ? { userAgent: n.ua } : {});
    try {
      await pg.goto(n.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      let hit = null, text = '';
      for (let i = 0; i < 12 && !hit; i++) {          // chờ tối đa ~48 giây, giữa chừng tải lại trang 1 lần (DOJI có lúc không hiện bảng)
        if (i === 6) await pg.reload({ waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
        await pg.waitForTimeout(4000);
        const rows = await pg.evaluate(() => [...document.querySelectorAll('tr')].map(tr => [...tr.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim())));
        for (const r of rows) {
          const k = r.findIndex(c => n.sp.test(c.normalize('NFC')));
          if (k >= 0 && so(r[k + 1]) && (n.chi_mua || so(r[k + 2]))) {
            hit = [r[k], so(r[k + 1]) * n.nhan, so(r[k + 2]) ? so(r[k + 2]) * n.nhan : null]; break;
          }
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
  const f = v => v == null ? '-' : v.toLocaleString('en-US');
  for (const [ma, v] of Object.entries(kq))
    console.log(ma.padEnd(5), v ? `${v.san_pham} | mua ${f(v.mua)} | bán ${f(v.ban)} đ/chỉ | cập nhật ${v.cap_nhat}` : 'KHÔNG ĐỌC ĐƯỢC');
  if (Object.values(kq).some(v => !v)) process.exit(1);
})();

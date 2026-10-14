// Đọc toàn bộ bảng giá của 6 trang (mỗi dòng = danh sách ô) cho bài TCB "1 chỉ vàng bao nhiêu tiền".
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_bang.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36';
const NGUON = {
  huythanh: { url: 'https://huythanhjewelry.vn/gia-vang-hom-nay', ua: UA, can: /nguyên liệu 22K/i },
  sjc:      { url: 'https://webgia.com/gia-vang/sjc/', ua: UA, can: /Vàng SJC 1L/i },
  btmc:     { url: 'https://webgia.com/gia-vang/bao-tin-minh-chau/', ua: UA, can: /Rồng Thăng Long/i },
  phuquy:   { url: 'https://phuquygroup.vn/', ua: UA, can: /Phú Quý 1 Lượng/i },
  doji:     { url: 'https://banggia.doji.vn/gold-price', ua: null, can: /NGUY.N LI.U 18K/i },   // DOJI: để trình duyệt mặc định
  pnj:      { url: 'https://www.pnj.com.vn/site/gia-vang', ua: UA, can: /Vàng 750 \(18K\)/i },
  thegioi:  { url: 'https://giavang.org/the-gioi/', ua: UA, chu: /1 cây vàng[^\n]*có giá là/i },   // lấy chữ, không lấy bảng
};
(async () => {
  const out = process.argv[2] || 'bang-nguon.json';
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  const kq = {};
  for (const [ma, n] of Object.entries(NGUON)) {
    const pg = await b.newPage(n.ua ? { userAgent: n.ua } : {});
    let rows = [], text = '';
    try {
      await pg.goto(n.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      for (let i = 0; i < 12; i++) {
        if (i === 6) await pg.reload({ waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
        await pg.waitForTimeout(4000);
        rows = await pg.evaluate(() => [...document.querySelectorAll('tr')].map(tr => [...tr.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim())).filter(r => r.length));
        if (n.chu) {
          const t = await pg.evaluate(() => document.body.innerText);
          if (n.chu.test(t)) { rows = t.split('\n').filter(l => /XAU|Ounce|cây vàng|Cập nhật lúc/i.test(l)).map(l => [l.trim()]); break; }
          continue;
        }
        if (rows.some(r => n.can.test(r.join(' ').normalize('NFC')))) break;
        rows = [];
      }
      text = await pg.evaluate(() => document.body.innerText);
    } catch (e) { console.error(ma, 'LỖI', e.message.slice(0, 120)); }
    await pg.close();
    const m = text.match(/[Cc]ập nhật[^\n]{0,40}?(\d{1,2}:\d{2}(?::\d{2})?[^\n]{0,8}\d{1,2}\/\d{1,2}\/\d{4}|\d{1,2}\/\d{1,2}\/\d{4}[^\n]{0,4}\d{1,2}:\d{2}(?::\d{2})?)/);
    kq[ma] = rows.length ? { url: n.url, cap_nhat: m ? m[1] : '?', rows } : null;
    console.log(ma.padEnd(9), rows.length ? `${rows.length} dòng, cập nhật ${kq[ma].cap_nhat}` : 'KHÔNG ĐỌC ĐƯỢC');
  }
  await b.close();
  fs.writeFileSync(out, JSON.stringify(kq, null, 1));
})();

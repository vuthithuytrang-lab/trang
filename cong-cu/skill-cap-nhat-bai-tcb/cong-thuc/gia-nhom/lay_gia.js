// Lấy giá nhôm cho bài TCB "Giá nhôm hôm nay" -> gia.json (đầu vào của tao_sua.py).
// TradingView COMEX (hợp đồng tương lai nhôm ALI…): mã, ngày đáo hạn, giá USD/tấn, % thay đổi, giờ "As of …"
// Phế Liệu Quang Phong: các dòng nhôm trong bảng giá thu mua (đ/kg) + "Cập nhật ngày …"
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36';
const TV = 'https://www.tradingview.com/symbols/COMEX-ALI1!/contracts/';
const QP = 'https://www.phelieuquangphong.com/bang-gia-thu-mua-phe-lieu/';

async function moTrang(b, url) {
  const pg = await b.newPage({ userAgent: UA });
  // Chromium không tin chứng chỉ proxy của máy chủ -> mọi lượt tải đi qua Node (vẫn kiểm tra chứng chỉ bằng CA của proxy)
  await pg.route('**/*', async r => { try { await r.fulfill({ response: await r.fetch() }); } catch (e) { await r.abort().catch(() => {}); } });
  await pg.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  return pg;
}
const hang = pg => pg.evaluate(() => [...document.querySelectorAll('tr')].map(tr => [...tr.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim())));

async function tradingview(b) {
  const pg = await moTrang(b, TV);
  try {
    let ds = [], text = '';
    for (let i = 0; i < 10; i++) {                       // chờ bảng hiện đủ (tối đa ~40 giây, giữa chừng tải lại 1 lần)
      if (i === 5) await pg.reload({ waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
      await pg.waitForTimeout(4000);
      ds = [];
      for (const r of await hang(pg)) {
        const m = (r[0] || '').match(/^(ALI[FGHJKMNQUVXZ]\d{4})\b/);
        if (!m || r.length < 4 || !/\d/.test(r[2])) continue;
        ds.push({ ma: m[1], dao_han: r[1], gia: r[2], thay_doi: r[3].replace(/−/g, '-'), tre: /\bD$/.test(r[0]) });
      }
      text = await pg.evaluate(() => document.body.innerText);
      if (ds.length >= 10 && /As of/i.test(text)) break;
    }
    if (!ds.length) return null;
    const m = text.match(/As of ([^\n]{0,40}?GMT)/i);
    return { hop_dong: ds, cap_nhat: m ? m[1] : '?', nguon: TV };
  } finally { await pg.close(); }
}

async function quangphong(b) {
  const pg = await moTrang(b, QP);
  try {
    let ds = {}, text = '';
    for (let i = 0; i < 6 && !Object.keys(ds).length; i++) {
      await pg.waitForTimeout(i ? 4000 : 1500);
      for (const r of await hang(pg)) {
        for (let k = 0; k + 1 < r.length; k++) {
          if (/nhôm/i.test(r[k]) && /\d.*đ\/kg/.test(r[k + 1])) { ds[r[k]] = r[k + 1]; break; }
        }
      }
      text = await pg.evaluate(() => document.body.innerText);
    }
    if (!Object.keys(ds).length) return null;
    const m = text.match(/Cập nhật ngày\s*(\d{1,2}\/\d{1,2}\/\d{4})/i);
    return { dong: ds, cap_nhat: m ? m[1] : '?', nguon: QP };
  } finally { await pg.close(); }
}

(async () => {
  const out = process.argv[2] || 'gia.json';
  const b = await chromium.launch({ args: ['--no-sandbox'], ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
  const kq = {};
  for (const [ma, ham] of [['tradingview', tradingview], ['quangphong', quangphong]]) {
    try { kq[ma] = await ham(b); } catch (e) { kq[ma] = null; console.error(ma, 'LỖI', e.message.slice(0, 120)); }
  }
  await b.close();
  fs.writeFileSync(out, JSON.stringify(kq, null, 1));
  const tv = kq.tradingview, qp = kq.quangphong;
  if (tv) { console.log(`tradingview: ${tv.hop_dong.length} hợp đồng, As of ${tv.cap_nhat}`);
    for (const h of tv.hop_dong.slice(0, 12)) console.log(`  ${h.ma} ${h.dao_han} ${h.gia} ${h.thay_doi}${h.tre ? ' (D)' : ''}`); }
  else console.log('tradingview KHÔNG ĐỌC ĐƯỢC');
  if (qp) { console.log(`quangphong: cập nhật ngày ${qp.cap_nhat}`);
    for (const [k, v] of Object.entries(qp.dong)) console.log(`  ${k}: ${v}`); }
  else console.log('quangphong KHÔNG ĐỌC ĐƯỢC');
  if (!tv || !qp) process.exit(1);
})();

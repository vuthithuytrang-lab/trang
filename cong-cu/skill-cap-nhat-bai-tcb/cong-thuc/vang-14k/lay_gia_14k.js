// Lấy giá vàng 14K (VND/chỉ) cho bài TCB "Vàng 14K giá hôm nay".
// SJC: webgia.com (sjc.com.vn chặn máy chủ) | PNJ: pnj.com.vn | Huy Thanh: huythanhjewelry.vn
// + lịch sử giá PNJ "Vàng 585 (14K)" (API công khai của PNJ, ngàn đồng/lượng) cho đoạn "Xu hướng" → khóa "_lich_su_pnj"
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia_14k.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const NGUON = {
  sjc:      { url: 'https://webgia.com/gia-vang/sjc/', sp: /^Nữ trang 58,3%$/i, nhan: 1 },
  pnj:      { url: 'https://www.pnj.com.vn/site/gia-vang', sp: /^Vàng 585 \(14K\)$/i, nhan: 1000 },
  huythanh: { url: 'https://huythanhjewelry.vn/gia-vang-hom-nay', sp: /^Giá nguyên liệu 14K$/i, nhan: 1 },
};
const LS_URL = 'https://edge-api.pnj.io/ecom-frontend/v1/get-gold-price-history?date=';
const LS_SP = 'Vàng 585 (14K)';
const so = s => { const d = (s || '').replace(/\D/g, ''); return d ? parseInt(d, 10) : null; };
(async () => {
  const out = process.argv[2] || 'gia-14k.json';
  const b = await chromium.launch({ args: ['--no-sandbox'], ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
  const kq = {};
  for (const [ma, n] of Object.entries(NGUON)) {
    const pg = await b.newPage({ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36' });
    // Chromium không tin chứng chỉ proxy của máy chủ → mọi lượt tải đi qua Node (vẫn kiểm tra chứng chỉ bằng CA của proxy)
    await pg.route('**/*', async r => { try { await r.fulfill({ response: await r.fetch() }); } catch (e) { await r.abort().catch(() => {}); } });
    try {
      await pg.goto(n.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      let hit = null, text = '';
      for (let i = 0; i < 6 && !hit; i++) {
        await pg.waitForTimeout(4000);
        const rows = await pg.evaluate(() => [...document.querySelectorAll('tr')].map(tr => [...tr.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim())));
        for (const r of rows) {
          const k = r.findIndex(c => n.sp.test(c.normalize('NFC')));
          if (k >= 0 && so(r[k + 1]) && so(r[k + 2])) { hit = [r[k], so(r[k + 1]) * n.nhan, so(r[k + 2]) * n.nhan]; break; }
        }
        text = await pg.evaluate(() => document.body.innerText);
      }
      const m = text.match(/Cập nhật[^\n]{0,40}?(\d{1,2}:\d{2}(?::\d{2})?[^\n]{0,8}\d{1,2}\/\d{1,2}\/\d{4}|\d{1,2}\/\d{1,2}\/\d{4}[^\n]{0,4}\d{1,2}:\d{2}(?::\d{2})?)/i);
      kq[ma] = hit ? { san_pham: hit[0], mua: hit[1], ban: hit[2], cap_nhat: m ? m[1] : '?', nguon: n.url } : null;
    } catch (e) { kq[ma] = null; console.error(ma, 'LỖI', e.message.slice(0, 120)); }
    await pg.close();
  }
  kq._lich_su_pnj = await lichSu(b).catch(e => { console.error('lịch sử PNJ LỖI', e.message.slice(0, 120)); return null; });
  await b.close();
  fs.writeFileSync(out, JSON.stringify(kq, null, 1));
  const ls = kq._lich_su_pnj;
  console.log('lịch sử PNJ', ls ? Object.entries(ls.moc).map(([k, v]) => `${k} ${v.ngay} bán ${v.ban.toLocaleString('en-US')}`).join(' | ') + ' đ/lượng' : 'KHÔNG ĐỌC ĐƯỢC');
  for (const [ma, v] of Object.entries(kq)) if (ma[0] !== '_')
    console.log(ma.padEnd(9), v ? `${v.san_pham} | mua ${v.mua.toLocaleString('en-US')} | bán ${v.ban.toLocaleString('en-US')} đ/chỉ | cập nhật ${v.cap_nhat}` : 'KHÔNG ĐỌC ĐƯỢC');
  if (Object.values(kq).some(v => !v)) process.exit(1);
})();

// Giá đóng phiên (lần cập nhật cuối trong ngày) của PNJ Vàng 585 (14K) ở các mốc: mới nhất, phiên trước, 7 ngày, 1 tháng, cùng kỳ năm trước.
// Ngày không có phiên (chủ nhật, lễ) → lùi dần tới ngày gần nhất có phiên (tối đa 10 ngày).
async function lichSu(b) {
  const ctx = await b.newContext();
  const ngay8 = d => `${d.getUTCFullYear()}${String(d.getUTCMonth() + 1).padStart(2, '0')}${String(d.getUTCDate()).padStart(2, '0')}`;
  const dmy = d => `${String(d.getUTCDate()).padStart(2, '0')}/${String(d.getUTCMonth() + 1).padStart(2, '0')}/${d.getUTCFullYear()}`;
  const cache = {};
  const phien = async d => {
    const k = ngay8(d);
    if (!(k in cache)) {
      const r = await ctx.request.get(LS_URL + k, { timeout: 30000 });
      const j = r.ok() ? await r.json() : {};
      const nhom = (j.locations || []).find(l => l.name === 'Giá vàng nữ trang');
      const sp = nhom && nhom.gold_type.find(g => g.name.normalize('NFC') === LS_SP.normalize('NFC'));
      const cuoi = sp && sp.data.length ? sp.data[sp.data.length - 1] : null;
      cache[k] = cuoi && so(cuoi.gia_ban) ? { ngay: dmy(d), ban: so(cuoi.gia_ban) * 1000, mua: so(cuoi.gia_mua) * 1000, luc: cuoi.updated_at } : null;
      if (!r.ok() && r.status() !== 422) throw new Error(`HTTP ${r.status()} ngày ${k}`);
    }
    return cache[k];
  };
  const lui = async (d, toiDa = 10) => {
    for (let i = 0; i <= toiDa; i++) {
      const x = await phien(new Date(d.getTime() - i * 864e5));
      if (x) return x;
    }
    return null;
  };
  const vn = new Date(Date.now() + 7 * 3600e3);
  const homNay = new Date(Date.UTC(vn.getUTCFullYear(), vn.getUTCMonth(), vn.getUTCDate()));
  const moi = await lui(homNay);
  if (!moi) throw new Error('không thấy phiên nào trong 10 ngày gần đây');
  const [dd, mm, yy] = moi.ngay.split('/').map(Number);
  const D = Date.UTC(yy, mm - 1, dd);
  const cung = (y, m) => new Date(Date.UTC(y, m, Math.min(dd, new Date(Date.UTC(y, m + 1, 0)).getUTCDate())));  // cùng ngày, kẹp về cuối tháng
  const moc = {
    moi_nhat: moi,
    phien_truoc: await lui(new Date(D - 864e5)),
    '7_ngay': await lui(new Date(D - 7 * 864e5)),
    '1_thang': await lui(cung(yy, mm - 2)),
    cung_ky: await lui(cung(yy - 1, mm - 1)),
  };
  await ctx.close();
  if (Object.values(moc).some(v => !v)) throw new Error('thiếu mốc: ' + Object.keys(moc).filter(k => !moc[k]).join(', '));
  return { san_pham: LS_SP, nguon: LS_URL + '<yyyymmdd>', cach_tinh: 'giá đóng phiên = lần cập nhật cuối trong ngày; ngày nghỉ lùi về phiên gần nhất', moc };
}

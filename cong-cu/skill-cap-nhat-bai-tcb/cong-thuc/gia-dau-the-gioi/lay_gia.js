// Lấy giá dầu Brent (UKOIL) + WTI (USOIL) trên TradingView cho bài TCB "Cập nhật giá dầu thế giới hôm nay".
// TradingView vẽ số bằng JavaScript nên mở bằng trình duyệt thật (Chromium của playwright).
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36';
const NGUON = {
  brent: { url: 'https://vn.tradingview.com/symbols/UKOIL/', ma: 'UKOIL' },
  wti:   { url: 'https://vn.tradingview.com/symbols/USOIL/', ma: 'USOIL' },
};
// "−2.71" (dấu trừ Unicode) / "1,234.56" / "+2.47%" -> số
const so = s => {
  const t = (s || '').replace(/[−–]/g, '-').replace(/[,%\s]/g, '').replace(/USD.*$/i, '');
  return /^[+-]?\d+(\.\d+)?$/.test(t) ? parseFloat(t) : null;
};
(async () => {
  const out = process.argv[2] || 'gia.json';
  const b = await chromium.launch({ args: ['--no-sandbox'], ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
  const kq = {};
  for (const [ten, n] of Object.entries(NGUON)) {
    const pg = await b.newPage({ userAgent: UA });
    // Chromium không tin chứng chỉ proxy của máy chủ → mọi lượt tải đi qua Node (vẫn kiểm tra chứng chỉ bằng CA của proxy)
    await pg.route('**/*', async r => { try { await r.fulfill({ response: await r.fetch() }); } catch (e) { await r.abort().catch(() => {}); } });
    try {
      await pg.goto(n.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      let d = null;
      for (let i = 0; i < 12; i++) {                      // chờ tối đa ~48 giây cho số hiện ra, giữa chừng tải lại 1 lần
        if (i === 6) await pg.reload({ waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
        await pg.waitForTimeout(4000);
        d = await pg.evaluate(() => {
          const q = s => document.querySelector(s)?.innerText?.trim() || '';
          const body = document.body.innerText;
          const m = (re) => (body.match(re) || [])[1] || '';
          return {
            last: q('.js-symbol-last'),
            doi: q('.js-symbol-change-direction').split('\n')[0],
            doi_pt: q('.js-symbol-change-pt'),
            tieu_de: document.title,
            luc: m(/(Tính đến[^\n]*)/),
            trang_thai: m(/(Thị trường (?:mở|đóng) cửa|Giao dịch (?:trước|sau) giờ[^\n]*)/),
            dong_cua_truoc: m(/Đóng cửa ngày hôm trước\s*\n\s*([\d.,]+)/),
          };
        });
        if (so(d.last) != null && so(d.doi) != null && so(d.doi_pt) != null) break;
      }
      const gia = so(d.last), doi = so(d.doi), doi_pt = so(d.doi_pt), truoc = so(d.dong_cua_truoc);
      if (gia == null || doi == null || doi_pt == null || !d.tieu_de.includes(n.ma)) throw new Error('không thấy số trên trang: ' + JSON.stringify(d).slice(0, 200));
      kq[ten] = {
        ma: n.ma, gia, doi, doi_pt, dong_cua_truoc: truoc,
        chu: { gia: d.last, doi: d.doi, doi_pt: d.doi_pt },   // đúng như TradingView hiển thị (để soát)
        cap_nhat: d.luc || '?', trang_thai: d.trang_thai || '?', lay_luc: new Date().toISOString(), nguon: n.url,
      };
      if (truoc != null && Math.abs(truoc + doi - gia) > 0.051)
        kq[ten].canh_bao = `giá ${gia} ≠ đóng cửa hôm trước ${truoc} + thay đổi ${doi}`;
    } catch (e) { kq[ten] = null; console.error(ten, 'LỖI', e.message.slice(0, 200)); }
    await pg.close();
  }
  await b.close();
  fs.writeFileSync(out, JSON.stringify(kq, null, 1));
  for (const [ten, v] of Object.entries(kq))
    console.log(ten.padEnd(5), v ? `${v.ma} ${v.gia} USD/thùng | ${v.chu.doi} (${v.chu.doi_pt}) | ${v.cap_nhat} | ${v.trang_thai}${v.canh_bao ? ' | CẢNH BÁO ' + v.canh_bao : ''}`
                                  : `${NGUON[ten].ma} KHÔNG ĐỌC ĐƯỢC`);
  if (Object.values(kq).some(v => !v)) process.exit(1);
})();

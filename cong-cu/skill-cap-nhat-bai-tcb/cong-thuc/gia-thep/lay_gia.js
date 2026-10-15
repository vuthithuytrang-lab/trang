// Lấy số cho bài "Giá thép hôm nay" (Techcombank) bằng trình duyệt Chromium có sẵn:
//  1) Barchart: hợp đồng thép HRC FOB China (mã V7, sàn LME) — mở trang overview của từng tháng, 12 tháng tính từ tháng này.
//  2) Steelonline: bảng giá thép xây dựng 10 thương hiệu (https://steelonline.vn/bang-gia-thep-xay-dung-hom-nay).
// Cách chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const MA = 'FGHJKMNQUVXZ';
const SO = 'https://steelonline.vn/bang-gia-thep-xay-dung-hom-nay';
(async () => {
  const out = process.argv[2] || 'gia.json';
  const b = await chromium.launch({ args: ['--no-sandbox'], ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
  const ctx = await b.newContext({ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36' });
  const pg = await ctx.newPage();
  // Chromium không tin chứng chỉ proxy → mọi lượt tải đi qua Node (vẫn kiểm tra chứng chỉ bằng CA của proxy); bỏ ảnh/quảng cáo cho nhanh
  await pg.route('**/*', async r => {
    const u = r.request().url();
    if (/\.(png|jpe?g|gif|webp|woff2?|svg|mp4)|doubleclick|googletag|criteo|33across|pubmatic|adnxs|facebook/.test(u)) return r.abort().catch(() => {});
    try { await r.fulfill({ response: await r.fetch() }); } catch (e) { await r.abort().catch(() => {}); }
  });
  const ra = { lay_luc: new Date().toISOString(), hrc: { nguon: 'https://www.barchart.com/futures/quotes/V7*0/futures-prices', hop_dong: [] }, trong_nuoc: {} };

  // 1) HRC
  const now = new Date(Date.now() + 7 * 3600e3);          // giờ VN
  let y = now.getUTCFullYear(), m = now.getUTCMonth();    // 0..11
  for (let i = 0; i < 12; i++, m++) {
    if (m > 11) { m = 0; y++; }
    const sym = `V7${MA[m]}${String(y).slice(2)}`;
    let rec = { ma: sym, thang: `${m + 1}/${y}`, url: `https://www.barchart.com/futures/quotes/${sym}/overview` };
    for (let lan = 0; lan < 2; lan++) {
      try {
        await pg.goto(rec.url, { waitUntil: 'domcontentloaded', timeout: 90000 });
        await pg.waitForTimeout(7000);
        const t = await pg.evaluate(() => document.body.innerText);
        const k = t.match(new RegExp(`Steel HRC FOB China [^\\n]*\\(${sym}\\)\\n([\\d,.]+)(s?)\\s+([+-]?[\\d,.]+|unch)\\s+\\(([^)]*)\\)\\s+(\\d\\d/\\d\\d/\\d\\d)`));
        if (k) { Object.assign(rec, { gia: k[1], chot_phien: k[2] === 's', thay_doi: k[3], phan_tram: k[4], ngay: k[5] }); break; }
        rec.loi = 'không thấy dòng giá';
      } catch (e) { rec.loi = String(e).slice(0, 150); }
    }
    console.log(JSON.stringify(rec));
    ra.hrc.hop_dong.push(rec);
  }

  // 2) Steelonline
  await pg.goto(SO, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await pg.waitForTimeout(10000);
  const t = await pg.evaluate(() => document.body.innerText);
  const ngay = (t.match(/NGÀY\s+(\d\d-\d\d-\d{4})/) || [])[1] || '';
  ra.trong_nuoc = { nguon: SO, ngay_tren_trang: ngay, thuong_hieu: {} };
  const khoi = t.split(/BẢNG GIÁ THÉP /).slice(1);
  for (const k of khoi) {
    const ten = k.split('\n')[0].trim();
    const vung = (k.match(/(Miền (?:Bắc|Trung|Nam)\n)+/) || [''])[0].trim().split('\n');
    const dong = [...k.matchAll(/^\d+\t(D\d+)\t([^\n]+)$/gm)].map(x => [x[1], ...x[2].split('\t')]);
    if (!dong.length) continue;
    ra.trong_nuoc.thuong_hieu[ten] = { vung_hien_thi_dau: vung[0] || '', cac_vung: vung, dong };
  }
  console.log('Steelonline', ngay, Object.keys(ra.trong_nuoc.thuong_hieu).join(', '));
  await b.close();
  fs.writeFileSync(out, JSON.stringify(ra, null, 1));
  const okHrc = ra.hrc.hop_dong.filter(x => x.gia).length, okTn = Object.keys(ra.trong_nuoc.thuong_hieu).length;
  if (!okHrc || !okTn) { console.error(`THIẾU SỐ: HRC ${okHrc} hợp đồng, Steelonline ${okTn} thương hiệu`); process.exit(1); }
})();

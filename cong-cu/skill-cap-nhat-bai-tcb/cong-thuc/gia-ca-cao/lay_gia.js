// Lấy giá cho bài TCB "Giá ca cao hôm nay…" → gia.json
//  - trong_nuoc: banggianongsan.com, bảng "Nông sản | Giá cũ | Giá mới | Chênh lệch" (chép nguyên chữ từng ô)
//  - new_york / london: trang dữ liệu chính thức của sàn ICE (ice.com, giá trễ tối thiểu 15 phút).
//    Trang ICE tự tải danh sách hợp đồng (contract-data) khi mở; script chỉ ghi lại đúng dữ liệu trang đó tải về.
//    (Barchart – nguồn Trang chọn – chặn máy chủ: 403 / "The request could not be satisfied" → không gọi nữa.)
// Nguồn nào lỗi → null + in "<nguồn> KHÔNG ĐỌC ĐƯỢC". Không bịa, không giữ số cũ.
// Chạy: NODE_PATH=/opt/node22/lib/node_modules node lay_gia.js <file-ra.json>
const { chromium } = require('playwright');
const fs = require('fs');
const BGNS = 'https://banggianongsan.com/bang-gia-cacao-hom-nay/';
const ICE = {
  new_york: 'https://www.ice.com/products/7/Cocoa-Futures/data',
  london: 'https://www.ice.com/products/37089076/London-Cocoa-Futures/data',
};
const TEN_ICE = { new_york: /Cocoa Futures/, london: /London Cocoa Futures/ };

async function moTrang(b, url, bat) {
  const pg = await b.newPage();
  // Chromium không tin chứng chỉ proxy của máy chủ → mọi lượt tải đi qua Node (vẫn kiểm tra chứng chỉ bằng CA của proxy)
  await pg.route('**/*', async r => {
    try {
      const resp = await r.fetch();
      if (bat) await bat(r.request().url(), resp);
      await r.fulfill({ response: resp });
    } catch (e) { await r.abort().catch(() => {}); }
  });
  await pg.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  return pg;
}

(async () => {
  const out = process.argv[2] || 'gia.json';
  const b = await chromium.launch({ args: ['--no-sandbox'], ...(process.env.HTTPS_PROXY ? { proxy: { server: process.env.HTTPS_PROXY } } : {}) });
  const kq = { lay_luc: new Date().toISOString(), trong_nuoc: null, new_york: null, london: null };

  // 1) banggianongsan
  try {
    const pg = await moTrang(b, BGNS);
    let bang = null, text = '';
    for (let i = 0; i < 5 && !bang; i++) {
      await pg.waitForTimeout(3000);
      const tables = await pg.evaluate(() => [...document.querySelectorAll('table')].map(t => [...t.rows].map(tr => [...tr.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim()))));
      bang = tables.find(t => t.length > 1 && /NÔNG SẢN/i.test(t[0][0] || '') && /GIÁ CŨ/i.test(t[0][1] || '') && /GIÁ MỚI/i.test(t[0][2] || ''));
      text = await pg.evaluate(() => document.body.innerText);
    }
    if (bang) {
      const dang = text.match(/Đăng bởi[\s\S]{0,80}?(\d{1,2}:\d{2}\s+\d{1,2}\/\d{1,2}\/\d{4})/);
      const tieu_de = text.match(/BẢNG GIÁ CACAO MỚI NHẤT\s*-\s*(\d{1,2}\/\d{1,2}\/\d{4})/i);
      kq.trong_nuoc = {
        nguon: BGNS, dang_luc: dang ? dang[1] : null, ngay_bang: tieu_de ? tieu_de[1] : null,
        dong: bang.slice(1).filter(r => r.length >= 4).map(r => ({ ten: r[0], gia_cu: r[1], gia_moi: r[2], chenh_lech: r[3] })),
      };
    }
    await pg.close();
  } catch (e) { console.error('banggianongsan LỖI', e.message.slice(0, 120)); }

  // 2) ICE New York + London
  for (const [ma, url] of Object.entries(ICE)) {
    try {
      let api = null, data = null;
      const pg = await moTrang(b, url, async (u, resp) => {
        if (!data && /\/marketdata\/api\/productguide\/charting\/contract-data\?/.test(u) && resp.status() === 200) {
          try { data = JSON.parse(await resp.text()); api = u; } catch (e) {}
        }
      });
      let text = '';
      for (let i = 0; i < 10 && !data; i++) await pg.waitForTimeout(2000);
      await pg.waitForTimeout(1500);
      text = await pg.evaluate(() => document.body.innerText);
      const ten = TEN_ICE[ma].test(text) && !(ma === 'new_york' && /London Cocoa Futures/.test(text));
      const asof = text.match(/As of [^\n]*?Market data delayed[^\n]*/);
      if (Array.isArray(data) && data.length && ten) {
        kq[ma] = {
          nguon: url, api, ghi_chu_trang: asof ? asof[0].trim() : null,
          hop_dong: data.map(x => ({ thang: x.marketStrip, gia: x.lastPrice, thay_doi_pct: x.change, luc: x.lastTime, khoi_luong: x.volume })),
        };
      }
      await pg.close();
    } catch (e) { console.error(ma, 'LỖI', e.message.slice(0, 120)); }
  }
  await b.close();
  fs.writeFileSync(out, JSON.stringify(kq, null, 1));

  const tn = kq.trong_nuoc;
  console.log('banggianongsan', tn ? `${tn.dong.length} dòng | đăng ${tn.dang_luc} | bảng ngày ${tn.ngay_bang}` : 'KHÔNG ĐỌC ĐƯỢC');
  for (const ma of Object.keys(ICE)) {
    const v = kq[ma];
    console.log(`ICE ${ma}`, v ? v.hop_dong.map(h => `${h.thang} ${h.gia ?? '-'}`).join(', ') + ` | ${v.ghi_chu_trang || ''}` : 'KHÔNG ĐỌC ĐƯỢC');
  }
  if (!tn || !kq.new_york || !kq.london) process.exit(1);
})();

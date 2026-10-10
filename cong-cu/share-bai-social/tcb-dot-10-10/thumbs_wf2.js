const { chromium } = require('playwright'); const fs=require('fs');
const rows=JSON.parse(fs.readFileSync('plan.json'));
const esc=s=>s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const palettes=[['#0B2545','#13315C','#8DA9C4'],['#1B3A4B','#065A60','#7FD1B9'],['#22223B','#4A4E69','#C9ADA7'],['#0F3057','#00587A','#E7E7DE']];
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const p=await b.newPage({viewport:{width:1200,height:630}});
for(const [i,r] of rows.entries()){ if(process.argv[2] && !process.argv.slice(2).includes(String(r.row))) continue;
 const m=JSON.parse(fs.readFileSync(`bai/${r.row}/meta.json`)); const [a,c,acc]=palettes[(i+2)%4];
 const kw=r.kw.charAt(0).toUpperCase()+r.kw.slice(1);
 await p.setContent(`<html><body style="margin:0;width:1200px;height:630px;font-family:Inter,sans-serif;background:linear-gradient(135deg,${a},${c});color:#fff;display:flex;flex-direction:column;justify-content:center;padding:0 90px;box-sizing:border-box;position:relative;overflow:hidden">
 <div style="position:absolute;right:-120px;top:-120px;width:460px;height:460px;border-radius:50%;border:60px solid ${acc};opacity:.18"></div>
 <div style="position:absolute;right:120px;bottom:-160px;width:300px;height:300px;border-radius:50%;background:${acc};opacity:.12"></div>
 <div style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:${acc};font-weight:600;margin-bottom:26px">Kiến thức tài chính doanh nghiệp</div>
 <div style="font-size:${kw.length>34?62:74}px;font-weight:800;line-height:1.12;max-width:960px">${esc(kw)}</div>
 <div style="width:120px;height:8px;background:${acc};border-radius:4px;margin:34px 0 26px"></div>
 <div style="font-size:28px;line-height:1.4;max-width:900px;opacity:.9">${esc((m.title_webflow||m.title_blogger))}</div></body></html>`);
 await p.screenshot({path:`thumb_wf/${r.row}.png`});}
await b.close();})();

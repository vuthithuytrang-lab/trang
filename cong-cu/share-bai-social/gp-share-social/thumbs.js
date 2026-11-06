// node thumbs.js <row> -> thumb/<row>.png
const { chromium } = require('playwright'); const fs=require('fs');
const row=process.argv[2]; const m=JSON.parse(fs.readFileSync(`bai/${row}/meta.json`));
const esc=s=>s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const P=m.platform==='wp'
 ?[['#0B2545','#13315C','#8DA9C4'],['#14213D','#1F4E79','#FCA311'],['#102A43','#243B53','#9FB3C8'],['#0F3057','#00587A','#E7E7DE']]
 :[['#1B3A4B','#065A60','#7FD1B9'],['#22223B','#4A4E69','#C9ADA7'],['#2D3142','#4F5D75','#EF8354'],['#073B4C','#118AB2','#FFD166']];
const [a,c,acc]=P[parseInt(row)%4];
const label=m.platform==='wp'?'Kiến thức tài chính cá nhân':'Cẩm nang quản lý tiền';
const kw=m.keyword.charAt(0).toUpperCase()+m.keyword.slice(1);
(async()=>{fs.mkdirSync('thumb',{recursive:true});const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const p=await b.newPage({viewport:{width:1200,height:630}});
const shape=m.platform==='wp'
 ?`<div style="position:absolute;right:-120px;top:-120px;width:460px;height:460px;border-radius:50%;border:60px solid ${acc};opacity:.18"></div><div style="position:absolute;right:120px;bottom:-160px;width:300px;height:300px;border-radius:50%;background:${acc};opacity:.12"></div>`
 :`<div style="position:absolute;right:-60px;top:60px;width:380px;height:380px;transform:rotate(18deg);border:46px solid ${acc};opacity:.16;border-radius:40px"></div><div style="position:absolute;left:0;bottom:0;width:100%;height:14px;background:${acc}"></div>`;
await p.setContent(`<html><body style="margin:0;width:1200px;height:630px;font-family:Inter,'Noto Sans',sans-serif;background:linear-gradient(135deg,${a},${c});color:#fff;display:flex;flex-direction:column;justify-content:center;padding:0 90px;box-sizing:border-box;position:relative;overflow:hidden">${shape}
<div style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:${acc};font-weight:600;margin-bottom:26px">${label}</div>
<div style="font-size:${kw.length>34?58:70}px;font-weight:800;line-height:1.12;max-width:960px">${esc(kw)}</div>
<div style="width:120px;height:8px;background:${acc};border-radius:4px;margin:34px 0 26px"></div>
<div style="font-size:28px;line-height:1.4;max-width:900px;opacity:.92">${esc(m.title)}</div></body></html>`);
await p.screenshot({path:`thumb/${row}.png`}); await b.close();})();

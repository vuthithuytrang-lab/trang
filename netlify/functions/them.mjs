// Nút "Gửi yêu cầu thêm bài" trên app công khai: nhận link bài + nguồn → bấm workflow them-bai.yml (ghi yêu cầu vào nhánh tu-dong-ket-qua).
// Dùng chung chìa GITHUB_TOKEN với hàm `chay` (quyền Actions: Read and write). Không lưu gì ở Netlify.
const CORS = {'access-control-allow-origin': '*', 'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'content-type'};
const tra = (o, status = 200) => Response.json(o, {status, headers: CORS});

export default async (req) => {
  if (req.method === 'OPTIONS') return new Response(null, {status: 204, headers: CORS});
  if (req.method !== 'POST') return tra({loi: 'Chỉ nhận POST'}, 405);
  let b;
  try { b = await req.json(); } catch { b = {}; }
  const url = String(b.url || '').trim();
  if (!/^https:\/\/techcombank\.com\/thong-tin\/blog\/[a-z0-9-]{3,120}\/?$/.test(url)) return tra({loi: 'Link phải là bài trên techcombank.com/thong-tin/blog/…'}, 400);
  const nguon = String(b.nguon || '').slice(0, 3000);
  const ghi_chu = String(b.ghi_chu || '').slice(0, 500);
  const chia = process.env.GITHUB_TOKEN;
  if (!chia) return tra({loi: 'Chưa cài chìa (GITHUB_TOKEN)'}, 503);
  const r = await fetch('https://api.github.com/repos/vuthithuytrang-lab/trang/actions/workflows/them-bai.yml/dispatches', {
    method: 'POST',
    headers: {authorization: `Bearer ${chia}`, accept: 'application/vnd.github+json', 'content-type': 'application/json', 'user-agent': 'vttt-sn', 'x-github-api-version': '2022-11-28'},
    body: JSON.stringify({ref: 'claude/ai-boss-data-replace-hn412r', inputs: {url, nguon, ghi_chu}}),
  });
  if (!r.ok) return tra({loi: `GitHub từ chối (${r.status})`}, 502);
  return tra({ok: true, url});
};

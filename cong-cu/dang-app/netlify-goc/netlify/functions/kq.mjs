// Đọc kết quả mới nhất trên nhánh tu-dong-ket-qua NGAY (raw.githubusercontent.com giữ bản cũ tới 5 phút → app thấy chậm).
// Dùng chìa GITHUB_TOKEN có sẵn trong Netlify (kho công khai, chỉ đọc). Chỉ cho đọc file tên dạng <mã>.html / .json.
const CORS = {'access-control-allow-origin': '*', 'cache-control': 'no-store'};
export default async (req) => {
  const f = new URL(req.url).searchParams.get('f') || '';
  if (!/^[a-z0-9-]{1,60}\.(json|html)$/.test(f)) return new Response('tên file không hợp lệ', {status: 400, headers: CORS});
  const chia = process.env.GITHUB_TOKEN;
  const r = await fetch(`https://api.github.com/repos/vuthithuytrang-lab/trang/contents/${f}?ref=tu-dong-ket-qua`, {
    headers: {...(chia ? {authorization: `Bearer ${chia}`} : {}), accept: 'application/vnd.github.raw+json', 'user-agent': 'vttt-sn', 'x-github-api-version': '2022-11-28'},
  });
  if (!r.ok) return new Response('không đọc được (' + r.status + ')', {status: r.status === 404 ? 404 : 502, headers: CORS});
  const loai = f.endsWith('.json') ? 'application/json; charset=utf-8' : 'text/plain; charset=utf-8';
  return new Response(await r.text(), {headers: {...CORS, 'content-type': loai}});
};

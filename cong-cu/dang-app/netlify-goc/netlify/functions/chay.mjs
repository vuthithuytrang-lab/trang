// Nút "Chạy cập nhật" trên trang công khai: nhận mã bài → bấm workflow tu-dong-cap-nhat.yml trên GitHub (chạy ngay, miễn phí).
// Chìa GITHUB_TOKEN do Trang tự dán trong Netlify (Project configuration → Environment variables), KHÔNG nằm trong mã/repo.
// Chìa chỉ cần quyền "Actions: Read and write" trên đúng kho trang.
const HOP_LE = new Set(['gia-ca-phe', 'gia-xang-dau', 'vang-24k', 'vang-14k', 'vang-18k', 'vang-10k', '1-chi-vang', 'vang-16k',
  'vang-610', 'lai-suat-1', 'lai-suat-2', 'gia-nhom', 'gia-lua-gao', 'gia-dieu', 'gia-dong', 'gia-thep', 'gia-ca-phe-dak-lak',
  'gia-ca-phe-luan-don', 'gia-gas', 'gia-dau-the-gioi', 'gia-tieu', 'gia-ca-cao']);   // gia-kim-loai: nguồn chặn máy GitHub
const CORS = {'access-control-allow-origin': '*', 'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'content-type'};
const tra = (o, status = 200) => Response.json(o, {status, headers: CORS});

export default async (req) => {
  if (req.method === 'OPTIONS') return new Response(null, {status: 204, headers: CORS});
  if (req.method !== 'POST') return tra({loi: 'Chỉ nhận POST'}, 405);
  let bai;
  try { bai = (await req.json()).bai; } catch { bai = null; }
  bai = Array.isArray(bai) ? [...new Set(bai.filter((b) => typeof b === 'string' && HOP_LE.has(b)))] : [];
  if (!bai.length) return tra({loi: 'Không có mã bài hợp lệ'}, 400);
  const chia = process.env.GITHUB_TOKEN;
  if (!chia) return tra({loi: 'Nút chạy chưa được cài chìa (GITHUB_TOKEN)'}, 503);
  const r = await fetch('https://api.github.com/repos/vuthithuytrang-lab/trang/actions/workflows/tu-dong-cap-nhat.yml/dispatches', {
    method: 'POST',
    headers: {authorization: `Bearer ${chia}`, accept: 'application/vnd.github+json', 'user-agent': 'vttt-sn', 'x-github-api-version': '2022-11-28'},
    body: JSON.stringify({ref: 'claude/ai-boss-data-replace-hn412r', inputs: {bai: bai.join(' ')}}),
  });
  if (!r.ok) return tra({loi: `GitHub từ chối (${r.status})`}, 502);
  return tra({ok: true, bai, luc: Math.floor(Date.now() / 1000)});
};

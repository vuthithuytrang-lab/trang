// Nút "Chạy cập nhật" trên trang công khai: nhận mã bài → bấm workflow tu-dong-cap-nhat.yml trên GitHub (chạy ngay, miễn phí).
// Chìa GITHUB_TOKEN do Trang tự dán trong Netlify (Project configuration → Environment variables), KHÔNG nằm trong mã/repo.
// Chìa chỉ cần quyền "Actions: Read and write" trên đúng kho trang.
const HOP_LE = new Set(['gia-ca-phe', 'gia-xang-dau', 'vang-24k', 'vang-14k', 'vang-18k', 'vang-10k', '1-chi-vang', 'vang-16k',
  'vang-610', 'lai-suat-1', 'lai-suat-2', 'gia-nhom', 'gia-lua-gao', 'gia-dieu', 'gia-dong', 'gia-thep', 'gia-ca-phe-dak-lak',
  'gia-ca-phe-luan-don', 'gia-gas', 'gia-dau-the-gioi', 'gia-tieu', 'gia-ca-cao',
  'gia-vang-sjc', 'gia-vang-nhan', 'gia-bach-kim', 'gia-niken', 'gia-kim-loai']);
const CORS = {'access-control-allow-origin': '*', 'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'content-type'};
const tra = (o, status = 200) => Response.json(o, {status, headers: CORS});

export default async (req) => {
  if (req.method === 'OPTIONS') return new Response(null, {status: 204, headers: CORS});
  if (req.method !== 'POST') return tra({loi: 'Chỉ nhận POST'}, 405);
  let bai, ngay = '', html = '', maHtml = '';
  try {
    const b = await req.json(); bai = b.bai; ngay = typeof b.ngay === 'string' ? b.ngay : '';
    html = typeof b.html === 'string' ? b.html : ''; maHtml = typeof b.ma_html === 'string' ? b.ma_html : '';
  } catch { bai = null; }
  // Ghép số vào HTML người dùng gửi (12/11/2026): HTML đã nén gzip + base64 ở trình duyệt; mỗi lần 1 bài
  if (html || maHtml) {
    if (!/^[A-Za-z0-9+/]+=*$/.test(html) || html.length > 60000) return tra({loi: 'HTML quá dài hoặc hỏng (tối đa ~400 KB)'}, 400);
    if (!/^[a-z0-9]{8,20}$/.test(maHtml)) return tra({loi: 'Mã yêu cầu không hợp lệ'}, 400);
    if (!Array.isArray(bai) || bai.length !== 1) return tra({loi: 'Mỗi lần ghép HTML chỉ chọn 1 bài'}, 400);
  }
  // ngày ghi trong bài (người bấm chọn trên app): chỉ nhận dd/mm/yyyy trong khoảng hôm qua…ngày kia (giờ VN)
  if (ngay) {
    const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(ngay);
    const vn = new Date(Date.now() + 7 * 3600e3), hn = Date.UTC(vn.getUTCFullYear(), vn.getUTCMonth(), vn.getUTCDate());
    const d = m ? Date.UTC(+m[3], +m[2] - 1, +m[1]) : NaN;
    if (!m || new Date(d).getUTCDate() !== +m[1] || d < hn - 864e5 || d > hn + 2 * 864e5) return tra({loi: 'Ngày không hợp lệ'}, 400);
  }
  bai = Array.isArray(bai) ? [...new Set(bai.filter((b) => typeof b === 'string' && HOP_LE.has(b)))] : [];
  if (!bai.length) return tra({loi: 'Không có mã bài hợp lệ'}, 400);
  const chia = process.env.GITHUB_TOKEN;
  if (!chia) return tra({loi: 'Nút chạy chưa được cài chìa (GITHUB_TOKEN)'}, 503);
  const r = await fetch('https://api.github.com/repos/vuthithuytrang-lab/trang/actions/workflows/tu-dong-cap-nhat.yml/dispatches', {
    method: 'POST',
    headers: {authorization: `Bearer ${chia}`, accept: 'application/vnd.github+json', 'content-type': 'application/json', 'user-agent': 'vttt-sn', 'x-github-api-version': '2022-11-28'},
    body: JSON.stringify({ref: 'claude/ai-boss-data-replace-hn412r', inputs: {bai: bai.join(' '), ngay, ...(html ? {html, ma_html: maHtml} : {})}}),
  });
  if (!r.ok) return tra({loi: `GitHub từ chối (${r.status})`}, 502);
  return tra({ok: true, bai, ngay, luc: Math.floor(Date.now() / 1000)});
};

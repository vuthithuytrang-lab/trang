// Một lượt đăng: mỗi tài khoản tối đa 1 bài, giữ nhịp an toàn. Gọi từ lịch 10 phút/lần hoặc nút "Chạy ngay".
import { settings, conns, saveConns, listItems, saveItem, log, vnHour, vnDay, fmtVN } from './store.js';
import { PLATFORMS, siteAlive, writeBack } from './platforms.js';

export async function runOnce({ force = false, maxPublish = 2 } = {}) {
  const t0 = Date.now(), S = await settings(), out = [];
  if (!S.tu_dong && !force) return ['Tự động đang tắt'];
  const h = vnHour();
  if (h < +S.gio_bat_dau || h >= +S.gio_ket_thuc) return [`Ngoài khung giờ ${S.gio_bat_dau}h–${S.gio_ket_thuc}h`];
  const C = await conns(), items = await listItems(), now = Date.now(), today = vnDay();
  const last = {}, count = {};
  for (const it of items) for (const j of it.jobs || []) if (j.status === 'da_dang' && j.when) {
    const t = Date.parse(j.when); if (!last[j.conn] || t > last[j.conn]) last[j.conn] = t;
    if (vnDay(t) === today) count[j.conn] = (count[j.conn] || 0) + 1;
  }
  let published = 0;
  for (const c of Object.values(C)) {
    if (published >= maxPublish || Date.now() - t0 > 18000) break;
    if (c.paused) continue;
    if (last[c.id] && (now - last[c.id]) / 60000 < +S.cach_nhau_phut) continue;
    if ((count[c.id] || 0) >= +S.toi_da_moi_ngay) continue;
    let pick = null;
    for (const it of items) for (const j of it.jobs || []) {
      if (j.conn !== c.id || j.status !== 'cho' || Date.parse(j.at) > now) continue;
      if (!pick || Date.parse(j.at) < Date.parse(pick.j.at)) pick = { it, j };
    }
    if (!pick) continue;
    if (!(await siteAlive(c))) {
      c.paused = true; c.pause_reason = 'Trang bị khóa (410/404/451) — tự dừng ' + fmtVN();
      await saveConns(C); await log('DỪNG ' + c.name, c.pause_reason); out.push(c.pause_reason); continue;
    }
    const { it, j } = pick;
    j.status = 'dang'; j.try_at = new Date().toISOString(); await saveItem(it);
    try {
      const res = await PLATFORMS[c.type].publish(c, it, () => saveConns(C));
      Object.assign(j, { status: 'da_dang', url: res.url, when: new Date().toISOString(), err: '' });
      published++;
      await log('ĐĂNG ' + c.name, `${it.title} → ${res.url}`);
      out.push(`Đã đăng ${c.name}: ${res.url}`);
      if (S.sheet.id && S.sheet.conn && C[S.sheet.conn]) {
        try { j.sheet = await writeBack(C[S.sheet.conn], S.sheet, j, it, res.url, fmtVN(j.when)); }
        catch (e) { j.sheet = 'Lỗi ghi sheet: ' + e.message; }
      }
    } catch (e) {
      Object.assign(j, { status: 'loi', err: e.message });
      await log('LỖI ' + c.name, `${it.title}: ${e.message}`);
      out.push(`Lỗi ${c.name}: ${e.message}`);
    }
    await saveItem(it);
  }
  if (!out.length) out.push('Chưa có bài nào đến giờ (hoặc đang chờ đủ khoảng cách an toàn)');
  return out;
}

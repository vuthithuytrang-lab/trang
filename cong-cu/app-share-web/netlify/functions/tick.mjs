// Lịch tự chạy của Netlify: 10 phút/lần, kể cả khi tắt máy. Không dùng AI.
import { runOnce } from './lib/runner.mjs';
import { log } from './lib/store.mjs';

export default async () => {
  try { await runOnce(); } catch (e) { await log('LỖI lượt tự động', e.message); }
  return new Response('ok');
};
export const config = { schedule: '*/10 * * * *' };

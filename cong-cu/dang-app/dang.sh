#!/usr/bin/env bash
# Đăng 1 app (thư mục có index.html) lên web công khai GitHub Pages của Trang.
#   bash cong-cu/dang-app/dang.sh <thư mục app> <tên đường dẫn>
#   vd: bash cong-cu/dang-app/dang.sh cong-cu/app-rank rank  →  https://vuthithuytrang-lab.github.io/trang/rank/
# Tên "." = gốc trang (đang là app Cập nhật bài TCB — đừng ghi đè nếu không chủ ý).
set -euo pipefail
NGUON=${1:?thiếu thư mục app}; TEN=${2:?thiếu tên đường dẫn}
[[ $TEN == . || $TEN =~ ^[a-z0-9-]{2,40}$ ]] || { echo "Tên đường dẫn chỉ gồm chữ thường không dấu, số, gạch ngang"; exit 1; }
[ -f "$NGUON/index.html" ] || { echo "Thiếu $NGUON/index.html"; exit 1; }
GOC=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
WEB=https://vuthithuytrang-lab.github.io/trang/$([ "$TEN" = . ] || echo "$TEN/")

# 1. Soát rò rỉ — repo công khai: không email, không chìa khóa
if grep -rInE '[A-Za-z0-9._%+-]+@(gmail|seongon|yahoo|outlook)\.|ghp_[A-Za-z0-9]{20}|github_pat_|sk-[A-Za-z0-9]{20}|AIza[0-9A-Za-z_-]{30}|Bearer [A-Za-z0-9._-]{20}' "$NGUON"; then
  echo "DỪNG: có email/chìa khóa trong app (dòng ở trên)"; exit 1; fi

# 2. Chép vào nhánh gh-pages
TAM=$(mktemp -d); trap 'git -C "$GOC" worktree remove --force "$TAM" 2>/dev/null || true' EXIT
git -C "$GOC" fetch -q origin gh-pages
git -C "$GOC" worktree add -q --detach "$TAM" origin/gh-pages
DICH=$TAM/$TEN; mkdir -p "$DICH"; cp -r "$NGUON"/. "$DICH"/
PB=$(TZ=Asia/Ho_Chi_Minh date +%Y%m%d%H%M)
grep -q 'phien-ban:' "$DICH/index.html" && sed -i "s/phien-ban: [0-9a-z-]*/phien-ban: $PB/" "$DICH/index.html" \
  || sed -i "0,/<head>/s//<head>\n<!-- phien-ban: $PB -->/" "$DICH/index.html"
cd "$TAM"; git add -A
git diff --cached --quiet && { echo "Không có gì thay đổi. $WEB"; exit 0; }
git commit -qm "Đăng app $TEN (phiên bản $PB)"
git push -q origin HEAD:gh-pages
# Netlify (vttt-sn.netlify.app) đăng từ nhánh netlify = bản sao gh-pages, chỉ đẩy khi đăng app
# (số liệu đổi hằng ngày chỉ vào gh-pages → Netlify không phải đăng lại, đỡ tốn lượt miễn phí)
cp -r "$GOC/cong-cu/dang-app/netlify-goc/." .     # + cấu hình & hàm nút chạy, chỉ ở nhánh netlify
git add -A && git commit -qm "Cấu hình Netlify (nút chạy)" && git push -qf origin HEAD:refs/heads/netlify

# 3. Chờ web thật lên đúng phiên bản
for i in $(seq 1 12); do
  curl -s "$WEB?t=$RANDOM" | grep -q "phien-ban: $PB" && { echo "ĐÃ LÊN: $WEB (phiên bản $PB)"; exit 0; }
  sleep 15; done
echo "Đã đẩy nhưng sau 3 phút web chưa hiện bản $PB — kiểm tra lại: $WEB"; exit 1

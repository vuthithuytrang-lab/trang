#!/usr/bin/env bash
# Chạy sau chay.sh trên máy GitHub (12/11/2026): ghép số vào HTML người dùng gửi.
#  - HTML gửi kèm lệnh chạy (biến HTML_B64 + MA_HTML, đường hàm Netlify bản mới), và/hoặc
#  - HTML đang chờ trong "hộp thư" Apps Script (DongBoDocs.gs, ?hop=<mã bài>) – đường miễn phí khi Netlify hết lượt.
# Dùng: bash sau_chay.sh <mã bài>   (thư mục hiện tại có ket-qua/)
MA=$1; TD=$(cd "$(dirname "$0")" && pwd)
giai(){ head -c 200000 | base64 -d 2>/dev/null | gunzip 2>/dev/null | head -c 3000000; }
if [ -n "${HTML_B64:-}" ] && [[ ${MA_HTML:-} =~ ^[a-z0-9]{8,20}$ ]]; then
  printf '%s' "$HTML_B64" | giai > dau-vao.html || true
  python3 -I "$TD/ghep_yeu_cau.py" "$MA" "$MA_HTML" dau-vao.html
fi
URL=$(tr -d ' \n\r' < "$TD/dong-bo-url.txt" 2>/dev/null)
[[ $URL =~ ^https://script\.google\.com/macros/s/[A-Za-z0-9_-]+/exec$ ]] || exit 0
curl -sfL -m 30 "$URL?hop=$MA" -o hop.json || exit 0
python3 -I - "$MA" <<'PY' > hop.ds
import json, re, sys
try:
    d = json.load(open('hop.json'))
except Exception:
    d = {}
for x in (d.get('ds') or [])[:20]:
    if isinstance(x, dict) and re.fullmatch(r'[a-z0-9]{8,20}', str(x.get('id', ''))) and re.fullmatch(r'[A-Za-z0-9+/]+=*', str(x.get('html', ''))):
        open('hop-' + x['id'] + '.b64', 'w').write(x['html']); print(x['id'])
PY
while read -r ID; do
  giai < "hop-$ID.b64" > "hop-$ID.html" || true
  python3 -I "$TD/ghep_yeu_cau.py" "$MA" "$ID" "hop-$ID.html"
done < hop.ds
exit 0

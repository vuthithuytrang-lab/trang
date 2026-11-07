#!/bin/bash
# Vòng đăng chạy nền tối đa ~115 phút: mỗi phút thử 1 lượt Wix + 1 lượt GG (các script tự giữ giờ/khoảng cách).
cd "$(dirname "$0")"
end=$(( $(date +%s) + 6900 ))
while [ "$(date +%s)" -lt "$end" ]; do
  h=$(TZ=Asia/Ho_Chi_Minh date +%H)
  if [ "$h" -ge 7 ] && [ "$h" -lt 23 ]; then
    code=$(curl -s -o /dev/null -w '%{http_code}' -L -m 40 https://trangjena3.wixsite.com/techcombankvietnam)
    if [ "$code" = "410" ] || [ "$code" = "404" ] || [ "$code" = "451" ]; then echo "$(date +%H:%M) WIX_BLOCKED $code" >> loop.log; else
      timeout 600 python3 step.py 2>&1 | grep -E "^PUBLISHED|ERR" | sed "s/^/$(TZ=Asia/Ho_Chi_Minh date +%H:%M) WIX /" >> loop.log; fi
    python3 gg_tick.py 2>&1 | grep -E "GG_PUBLISHED|GG_LOI|GG_HET|GG_BO_QUA|GG_CHO_BAI" | sed "s/^/$(TZ=Asia/Ho_Chi_Minh date +%H:%M) /" >> loop.log
    grep -q GG_HET loop.log && [ "$(python3 -c "import json;print(json.load(open('state.json'))['wix'][:4])")" = "2099" ] && break
  fi
  sleep 60
done
echo "$(date +%H:%M) LOOP_END" >> loop.log

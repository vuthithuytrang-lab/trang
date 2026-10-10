#!/bin/bash
# Giữ cả 3 công cụ đăng bài Tuấn (Blogger/Wix/Webflow) luôn chạy: mỗi phút kiểm tra, cái nào chết mà chưa xong 40 bài thì bật lại.
S=/tmp/claude-0/-home-user-trang/6eab5a25-c14a-599d-8b8f-5e47d95ef1af/scratchpad
B=$(cd "$(dirname "$0")" && pwd)
xong() { [ -f "$B/$1/da-dang.jsonl" ] && [ "$(wc -l < "$B/$1/da-dang.jsonl")" -ge 40 ]; }
while true; do
  con=0
  if ! xong tcb-tuan-blogger; then con=1; pgrep -f "^python3 dang_blogger.py" >/dev/null || (cd $B/tcb-tuan-blogger && setsid python3 dang_blogger.py >> $S/blogger.log 2>&1 &); fi
  if ! xong tcb-tuan-wix; then con=1; pgrep -f "^python3 dang_wix.py" >/dev/null || (cd $B/tcb-tuan-wix && GIAN_MIN=420 GIAN_MAX=600 setsid python3 dang_wix.py run >> $S/wix.log 2>&1 &); fi
  if ! xong tcb-tuan-webflow; then con=1; pgrep -f "^python3 dang_webflow.py" >/dev/null || (cd $B/tcb-tuan-webflow && setsid python3 dang_webflow.py run >> $S/webflow.log 2>&1 &); fi
  [ $con = 0 ] && exit 0
  sleep 60
done

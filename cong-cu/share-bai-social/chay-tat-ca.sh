#!/bin/bash
# Chạy cả 3 công cụ đăng bài Tuấn (Blogger/Wix/Webflow), chờ tới khi xong. Bỏ qua cái nào đang chạy rồi.
S=/tmp/claude-0/-home-user-trang/6eab5a25-c14a-599d-8b8f-5e47d95ef1af/scratchpad
B=$(cd "$(dirname "$0")" && pwd)
pgrep -f "^python3 dang_blogger.py" >/dev/null || (cd $B/tcb-tuan-blogger && python3 dang_blogger.py >> $S/blogger.log 2>&1 &)
pgrep -f "^python3 dang_wix.py" >/dev/null || (cd $B/tcb-tuan-wix && GIAN_MIN=420 GIAN_MAX=600 python3 dang_wix.py run >> $S/wix.log 2>&1 &)
pgrep -f "^python3 dang_webflow.py" >/dev/null || (cd $B/tcb-tuan-webflow && python3 dang_webflow.py run >> $S/webflow.log 2>&1 &)
while pgrep -f "^python3 dang_" >/dev/null; do sleep 60; done

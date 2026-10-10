#!/bin/bash
# Tạo lần lượt các bài Blogger theo lich-blogger.json, mỗi lần gọi cách nhau 20 phút. Chạy lại được (bỏ qua row đã đăng).
cd "$(dirname "$0")"
for r in $(python3 -c "import json;[print(x['row']) for x in json.load(open('lich-blogger.json'))]"); do
  [ -f da-dang-blogger.jsonl ] && grep -q "\"row\": $r," da-dang-blogger.jsonl && continue
  W=$(python3 -c "import json;print([x['when'] for x in json.load(open('lich-blogger.json')) if x['row']==$r][0])")
  echo "$(date -u +%FT%TZ) row $r -> $W"
  python3 post-blogger.py $r $W; rc=$?
  [ $rc -eq 3 ] && { echo "DUNG: bi gioi han"; exit 3; }
  sleep 1200
done
echo XONG

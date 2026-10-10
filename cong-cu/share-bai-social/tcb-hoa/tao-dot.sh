#!/bin/bash
# Tạo tối đa N bài Blogger kế tiếp (mặc định 3), cách nhau 4 phút. Dùng cho mỗi lần check-in (tiến trình nền không sống qua lúc máy chủ khởi động lại).
cd "$(dirname "$0")"; N=${1:-3}; n=0
for r in $(python3 -c "import json;[print(x['row']) for x in json.load(open('lich-blogger.json'))]"); do
  [ -f da-dang-blogger.jsonl ] && grep -q "\"row\": $r," da-dang-blogger.jsonl && continue
  [ $n -ge $N ] && break
  [ $n -gt 0 ] && sleep 240
  W=$(python3 -c "import json;print([x['when'] for x in json.load(open('lich-blogger.json')) if x['row']==$r][0])")
  echo "$(date -u +%FT%TZ) row $r -> $W"
  python3 post-blogger.py $r $W; rc=$?
  [ $rc -eq 3 ] && { echo "DUNG: bi gioi han"; exit 3; }
  n=$((n+1))
done
echo "XONG DOT ($n bai)"

#!/bin/bash
# Đăng/hẹn giờ các row truyền vào theo lich-dang.json (bỏ qua row đã đăng)
cd "$(dirname "$0")"
for r in "$@"; do
  grep -q "\"row\": $r," da-dang.jsonl && { echo "$r da dang"; continue; }
  W=$(python3 -c "import json;print([x['when'] for x in json.load(open('lich-dang.json')) if x['row']==$r][0])")
  python3 post-hoa.py $r $W | tail -1
done

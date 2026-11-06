#!/bin/bash
cd "$(dirname "$0")"
for r in $(python3 -c "import json;d={json.loads(l)['row'] for l in open('da-dang.jsonl')};print(' '.join(str(x['row']) for x in json.load(open('plan.json')) if x['row'] not in d))"); do
  python3 dang_wix.py post $r 2>&1 | tail -c 300; echo
  sleep 25
done
echo XONG

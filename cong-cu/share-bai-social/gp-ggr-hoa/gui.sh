#!/bin/bash
# Gửi 1 bài GG Group - Hoa. Usage: gui.sh <row>. Ghi kết quả vào da-gui.jsonl. Không in token.
set -e
cd "$(dirname "$0")"; G=/home/user/trang/.claude/skills/share-bai-ggr; K=techcombankvn@googlegroups.com; R=$1
grep -q "\"row\": $R," da-gui.jsonl 2>/dev/null && { echo "row $R da gui"; exit 0; }
TITLE=$(python3 -c "import json;print([x['title'] for x in json.load(open('lich.json')) if x['row']==$R][0])")
A="$G/ggr-accounts.local.json"; T=$(mktemp -d)
CID=$(node $G/scripts/ggr-json.js get-account-field $A $K client_id); CS=$(node $G/scripts/ggr-json.js get-account-field $A $K client_secret); RT=$(node $G/scripts/ggr-json.js get-account-field $A $K refresh_token)
bash $G/scripts/ggr-http.sh refresh-token "$CID" "$CS" "$RT" $T/tok.json >/dev/null
node $G/scripts/ggr-json.js save-refreshed-access-token $A $K $T/tok.json >/dev/null
AT=$(node $G/scripts/ggr-json.js get-account-field $A $K access_token)
node $G/scripts/ggr-json.js build-mime-message $R.html "$TITLE" $K $T/payload.json $R.jpg image/jpeg >/dev/null
bash $G/scripts/ggr-http.sh gmail-send "$AT" $T/payload.json $T/send.json >/dev/null
MID=$(python3 -c "import json;print(json.load(open('$T/send.json'))['id'])")
bash $G/scripts/ggr-http.sh gmail-get-message "$AT" "$MID" $T/msg.json >/dev/null
RMID=$(node $G/scripts/ggr-json.js extract-message-id $T/msg.json | tail -1)
LINK=$(node $G/scripts/ggr-json.js build-permalink $K "$RMID" | tail -1)
NOW=$(TZ=Asia/Ho_Chi_Minh date '+%H:%M %d/%m/%Y')
echo "{\"row\": $R, \"gmail_id\": \"$MID\", \"link\": \"$LINK\", \"luc\": \"$NOW\"}" | tee -a da-gui.jsonl
rm -rf $T

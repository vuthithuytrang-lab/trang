#!/bin/zsh
# gsc.sh — điều khiển 1 tab Google Search Console qua AppleScript (mọi trình duyệt nhân Chrome, mọi profile)
#   gsc.sh find <domain|chuỗi trong URL>   tìm tab GSC đang mở cho domain đó, lưu vào state
#   gsc.sh nav <url>                       điều hướng tab đã lưu
#   gsc.sh js '<code>'                     chạy JS trong tab đã lưu, in kết quả
# State: $GSC_STATE (mặc định ~/.cache/gsc-indexing/current) chứa tab.env (APP, WID, TID, RID)
STATE=${GSC_STATE:-$HOME/.cache/gsc-indexing/current}; mkdir -p $STATE
APPS=(${(s:,:)${GSC_APPS:-Google Chrome,Google Chrome Beta,Google Chrome Dev,Google Chrome Canary,Chromium,Brave Browser,Microsoft Edge,Arc,Vivaldi}})
case $1 in
find)
  D=$2; found=""
  for A in $APPS; do
    [[ $(osascript -e "application \"$A\" is running" 2>/dev/null) == true ]] || continue
    res=$(osascript 2>/dev/null <<AS
using terms from application "Google Chrome"
set r to ""
tell application "$A"
  repeat with w in windows
    try
      repeat with t in (get tabs of w)
        try
          set u to URL of t
          if u contains "search.google.com/search-console" and u contains "$D" then set r to r & (id of w) & "|" & (id of t) & "|" & u & linefeed
        end try
      end repeat
    end try
  end repeat
end tell
return r
end using terms from
AS
)
    [[ -n $res ]] && { found="$A|${res%%$'\n'*}"; break; }
  done
  [[ -z $found ]] && { echo "NOT_FOUND: không thấy tab Search Console nào chứa '$D'. Hãy mở GSC của property đó trong trình duyệt (profile có quyền)."; exit 1; }
  A=${found%%|*}; rest=${found#*|}; W=${rest%%|*}; rest=${rest#*|}; T=${rest%%|*}; U=${rest#*|}
  RID=$(print -r -- $U | sed -nE 's/.*[?&]resource_id=([^&#]*).*/\1/p')
  [[ -z $RID ]] && { echo "NO_RESOURCE: tab $U không có resource_id — mở một trang bất kỳ của property (Overview/Performance) rồi chạy lại."; exit 1; }
  print -r -- "APP='$A'; WID=$W; TID=$T; RID='$RID'" > $STATE/tab.env
  echo "FOUND\t$A\twindow=$W tab=$T\tresource_id=$RID"
  ok=$($0 js '1+1' 2>&1)
  [[ $ok == 2 ]] && echo "JS_OK" || echo "JS_BLOCKED: bật View → Developer → Allow JavaScript from Apple Events trong $A (lỗi: $ok)"
  ;;
nav|js)
  [[ -f $STATE/tab.env ]] || { echo "Chưa có tab — chạy: gsc.sh find <domain>"; exit 1; }
  source $STATE/tab.env
  if [[ $1 == nav ]]; then
    osascript -e "using terms from application \"Google Chrome\"" -e "tell application \"$APP\" to set URL of (tab id $TID of window id $WID) to \"$2\"" -e "end using terms from"
  else
    osascript - "$2" <<AS
on run argv
using terms from application "Google Chrome"
tell application "$APP" to return execute (tab id $TID of window id $WID) javascript (item 1 of argv)
end using terms from
end run
AS
  fi ;;
*) sed -n 2,6p $0; exit 1 ;;
esac

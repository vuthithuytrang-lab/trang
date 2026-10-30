#!/bin/zsh
# run.sh <domain> <file_urls> [log]
# Submit lần lượt từng URL: thử lại tối đa $GSC_MAX_RETRY (mặc định 20) lần/URL, rồi kiểm tra Last crawl.
# Gặp "Quota exceeded" sau khi đã hết số lần thử → dừng các URL còn lại (ghi SKIP).
D=${0:h}; DOM=$1; LIST=$2; OUT=${3:-${LIST:r}_gsc.log}; MAX=${GSC_MAX_RETRY:-20}
[[ -z $DOM || ! -f $LIST ]] && { echo "usage: run.sh <domain> <file_urls> [log]"; exit 1; }
export GSC_STATE=${GSC_STATE:-$HOME/.cache/gsc-indexing/${DOM//[^A-Za-z0-9.-]/_}}
$D/gsc.sh find "$DOM" | tee -a $OUT | grep -q JS_OK || { echo "STOP: không điều khiển được tab GSC" >> $OUT; echo DONE >> $OUT; exit 1; }
rm -f $GSC_STATE/last_fail
grep -Eo 'https?://[^[:space:]]+' $LIST > $GSC_STATE/urls.txt
while read u; do
  if [[ -n $QSTOP ]]; then print -r -- "$u\tSKIP (hết quota)" >> $OUT; continue; fi
  res=$($D/request.sh "$u" | tail -1); n=0
  while [[ $res != *OK* && $res != *SKIP* && $n -lt $MAX ]]; do
    n=$((n+1)); print -r -- "  retry $n/$MAX ($res): $u" >> $OUT
    res=$($D/request.sh "$u" | tail -1)
  done
  print -r -- "$u\t$res\t(thử lại $n)" >> $OUT
  [[ $res == *Quota* ]] && { echo "STOP: hết quota sau $MAX lần thử lại" >> $OUT; QSTOP=1; }
done < $GSC_STATE/urls.txt
echo "=== LAST CRAWL" >> $OUT
while read u; do $D/inspect.sh "$u" >> $OUT; done < $GSC_STATE/urls.txt
echo DONE >> $OUT

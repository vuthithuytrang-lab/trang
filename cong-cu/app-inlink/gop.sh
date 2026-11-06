#!/bin/bash
# Gộp mọi file .gs thành 1 file để dán vào Apps Script: bash gop.sh
cd "$(dirname "$0")"
{ echo "// ===== App Inlink — bản gộp tự động từ cong-cu/app-inlink/*.gs. Sửa file gốc rồi chạy gop.sh ====="
  for f in CauHinh.gs Core.gs Sheet.gs TaoFile.gs Gemini.gs GopY.gs Main.gs; do echo; echo "// ----- $f -----"; sed '/^if (typeof module/,/^}/d' "$f"; done; } > Inlink-gop.gs
cp Inlink-gop.gs /tmp/kiem-tra-gop.js && node --check /tmp/kiem-tra-gop.js && echo "Gộp xong, cú pháp OK ($(wc -l < Inlink-gop.gs) dòng)"

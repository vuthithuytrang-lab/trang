#!/bin/zsh
# request.sh <url> : Request indexing cho 1 URL. Chỉ tính thành công khi thấy bước "Testing if live URL"
# rồi hộp thoại "Indexing requested" MỚI. In 1 dòng "RESULT: ...".
D=${0:h}; S=$D/gsc.sh; U=$1
STATE=${GSC_STATE:-$HOME/.cache/gsc-indexing/current}; source $STATE/tab.env; LF=$STATE/last_fail
# lần thử lại cùng URL: bị "rejected" chờ 15s, lỗi khác chờ 60s
[[ -f $LF && "$(cat $LF)" == "$U|rejected" ]] && sleep ${GSC_WAIT_REJECTED:-15}
[[ -f $LF && "$(cat $LF)" == "$U" ]] && sleep ${GSC_WAIT_RETRY:-60}
CLICK='(lbl)=>{const bs=[...document.querySelectorAll("[role=button]")].filter(e=>lbl.test((e.innerText||"").trim())&&e.offsetParent);bs.forEach(b=>{const r=b.getBoundingClientRect(),o={bubbles:true,cancelable:true,view:window,clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0};["pointerdown","mousedown","pointerup","mouseup","click"].forEach(t=>b.dispatchEvent(new (t.startsWith("pointer")?PointerEvent:MouseEvent)(t,o)))});return bs.length}'
DISMISS='(()=>{const bs=[...document.querySelectorAll("button")].filter(b=>/^Dismiss$/i.test((b.innerText||"").trim())&&b.offsetParent);bs.forEach(b=>b.click());return bs.length})()'
VIS='(()=>[...document.querySelectorAll("*")].filter(e=>e.children.length===0&&/Indexing requested/.test(e.textContent)&&e.offsetParent).length)()'
INSPECT="(()=>{const i=[...document.querySelectorAll('input')].find(x=>/Inspect any URL/.test(x.getAttribute('aria-label')||''));if(!i)return 0;i.focus();i.value='$U';i.dispatchEvent(new Event('input',{bubbles:true}));const o={key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true};['keydown','keypress','keyup'].forEach(t=>i.dispatchEvent(new KeyboardEvent(t,o)));return 1})()"
# 0. tải lại trang sạch (giao diện tiếng Anh)
$S nav "https://search.google.com/search-console?resource_id=$RID&hl=en"; sleep 7
# 1. inspect URL
st=""
for k in 1 2 3; do
  $S js "($CLICK)(/^(Dismiss|GOT IT)\$/i)" >/dev/null; sleep 1
  $S js "$INSPECT" >/dev/null
  for i in {1..15}; do sleep 3
    st=$($S js "(()=>{const t=document.body.innerText;if(/not in (the current )?property/i.test(t))return 'NOTPROP';if(!location.pathname.includes('inspect')||!t.includes('$U')||/Retrieving data/i.test(t))return 'loading';return /REQUEST INDEXING/i.test(t)?'READY':'loading'})()")
    [[ $st == READY || $st == NOTPROP ]] && break; done
  [[ $st == READY || $st == NOTPROP ]] && break
done
[[ $st == NOTPROP ]] && { rm -f $LF; echo "RESULT: SKIP (URL không thuộc property này)"; exit 2; }
[[ $st != READY ]] && { echo "$U" > $LF; echo "RESULT: FAIL (không mở được trang inspect)"; exit 1; }
# 2. đảm bảo không còn hộp thoại cũ
$S js "($CLICK)(/^(Dismiss|GOT IT)\$/i)" >/dev/null; sleep 1
[[ $($S js "$VIS") != 0 ]] && { echo "$U" > $LF; echo "RESULT: FAIL (hộp thoại cũ chưa đóng)"; exit 1; }
# 3. bấm Request indexing, chờ màn hình phản hồi (tối đa 10 phút)
$S js "($CLICK)(/^REQUEST INDEXING\$/i)" >/dev/null
seen=0; r=none
for i in {1..200}; do sleep 3
  r=$($S js "(()=>{const t=document.body.innerText;if(/Indexing request rejected/i.test(t))return 'rejected';const m=t.match(/Quota exceeded|Something went wrong|not a robot|recaptcha/i);if(m)return m[0];if($VIS>0&&/added to a priority crawl queue/i.test(t))return 'requested';return /Testing if live URL/i.test(t)?'testing':'none'})()")
  [[ $r == testing ]] && seen=1
  [[ $r != none && $r != testing ]] && break
done
if [[ $r == requested && $seen == 1 ]]; then rm -f $LF; echo "RESULT: OK (Indexing requested)"
elif [[ $r == rejected ]]; then $S js "$DISMISS" >/dev/null; echo "$U|rejected" > $LF; echo "RESULT: FAIL (rejected, testing_seen=$seen)"
else echo "$U" > $LF; echo "RESULT: FAIL ($r, testing_seen=$seen)"; fi
$S js "($CLICK)(/^(Dismiss|GOT IT)\$/i)" >/dev/null

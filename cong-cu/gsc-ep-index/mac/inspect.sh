#!/bin/zsh
# inspect.sh <url> : đọc trạng thái + Last crawl của URL. In: url \t trạng thái \t số khối \t Last crawl \t link inspect
S=${0:h}/gsc.sh; U=$1
STATE=${GSC_STATE:-$HOME/.cache/gsc-indexing/current}; source $STATE/tab.env
READ="(()=>{const t=document.body.innerText;if(!location.pathname.includes('inspect')||!t.includes('$U')||/Retrieving data/i.test(t)||!/URL is (not )?on Google|unknown to Google|not in (the current )?property/i.test(t))return 'loading';const m=[...document.querySelectorAll('*')].filter(e=>e.children.length===0&&e.textContent.trim()==='Last crawl');const lc=m.map(x=>x.parentElement.parentElement.textContent.replace('Last crawl','').replace(/Crawled as.*/,'').trim()).join(' || ');const st=(t.match(/URL is (not )?on Google|URL is unknown to Google|not in (the current )?property/i)||[''])[0];return 'OK\t'+st+'\t'+m.length+'\t'+lc+'\t'+location.href})()"
INSPECT="(()=>{const i=[...document.querySelectorAll('input')].find(x=>/Inspect any URL/.test(x.getAttribute('aria-label')||''));if(!i)return 0;i.focus();i.value='$U';i.dispatchEvent(new Event('input',{bubbles:true}));const o={key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true};['keydown','keypress','keyup'].forEach(t=>i.dispatchEvent(new KeyboardEvent(t,o)));return 1})()"
$S nav "https://search.google.com/search-console?resource_id=$RID&hl=en"; sleep 6
for k in 1 2 3; do
  $S js "$INSPECT" >/dev/null
  r=""; for i in {1..15}; do sleep 3; r=$($S js "$READ"); [[ $r == OK* ]] && break; done
  [[ $r == OK* ]] && break; sleep 3
done
[[ $r != OK* ]] && { echo "$U\tTIMEOUT"; exit 1; }
# tải lại đúng trang kết quả cho DOM sạch rồi đọc lại
href=${r##*	}; $S nav "$href"; sleep 5
for i in {1..20}; do r=$($S js "$READ"); [[ $r == OK* ]] && break; sleep 3; done
echo "$U\t${r#OK	}"

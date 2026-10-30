# ep-index.ps1 — Bản Windows của skill gsc-request-indexing.
# Điều khiển tab Google Search Console trong cửa sổ Chrome mở bằng 1-MO-CHROME-GSC.bat
# (Chrome bật cổng điều khiển 9222, hồ sơ riêng %LOCALAPPDATA%\GSC-Chrome).
#
# Quy trình:
#   1. Đọc Last crawl của từng URL.
#      - Google đã đọc SAU mốc giờ  → DA-DOC, không ép.
#      - Đọc TRƯỚC mốc / chưa có    → đưa vào danh sách cần ép.
#   2. Ép từng URL, thử lại đến khi OK (không giới hạn số lần).
#      Hết quota → chờ 30 phút, đọc lại Last crawl (Google đọc rồi thì thôi), rồi ép tiếp.
#   3. Ghi ket-qua.tsv (URL, DA-DOC/OK/SKIP, thời điểm) để tích bảng theo dõi.
# Chuẩn OK giữ nguyên skill gốc: phải thấy "Testing if live URL" rồi hộp thoại "Indexing requested" MỚI.
param(
  [string]$Domain = 'techcombank.com',
  [string]$UrlFile,
  [string]$Moc,                       # "yyyy-MM-dd HH:mm", giờ trên máy
  [int]$Port = 9222,
  [int]$WaitRetry = 60,
  [int]$WaitRejected = 15,
  [int]$WaitQuota = 1800
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $UrlFile) { $UrlFile = Join-Path $Here 'danh-sach-url.txt' }
$Log = Join-Path $Here 'nhat-ky.log'
$Out = Join-Path $Here 'ket-qua.tsv'
$Inv = [Globalization.CultureInfo]::InvariantCulture

function Say($s) {
  $line = '[{0}] {1}' -f (Get-Date -Format 'dd/MM HH:mm:ss'), $s
  Write-Host $line
  Add-Content -Path $Log -Value $line -Encoding UTF8
}
function Add-Result($u, $kq, $note) {
  Add-Content -Path $Out -Value "$u`t$kq`t$note" -Encoding UTF8
}

# ---------- Điều khiển Chrome qua DevTools Protocol ----------
$script:ws = $null; $script:cid = 0; $script:RID = ''

function Connect-Tab {
  try { $tabs = Invoke-RestMethod "http://127.0.0.1:$Port/json/list" -TimeoutSec 10 }
  catch { throw "Không thấy cửa sổ Chrome GSC. Hãy mở bằng file 1-MO-CHROME-GSC.bat." }
  $tab = $tabs | Where-Object { $_.type -eq 'page' -and $_.url -like '*search.google.com/search-console*' -and $_.url -like "*$Domain*" } | Select-Object -First 1
  if (-not $tab) { throw "Chưa có tab Search Console của $Domain. Hãy mở trang Tổng quan (Overview) của $Domain trong cửa sổ Chrome GSC." }
  $m = [regex]::Match($tab.url, '[?&]resource_id=([^&#]*)')
  if (-not $m.Success) { throw "Tab GSC chưa chọn website. Hãy mở trang Tổng quan (Overview) của $Domain." }
  $script:RID = $m.Groups[1].Value
  if ($script:ws) { try { $script:ws.Dispose() } catch {} }
  $script:ws = New-Object System.Net.WebSockets.ClientWebSocket
  $script:ws.Options.KeepAliveInterval = [TimeSpan]::FromSeconds(20)
  $script:ws.ConnectAsync([Uri]$tab.webSocketDebuggerUrl, [Threading.CancellationToken]::None).Wait()
  [void](Cdp-Raw 'Page.bringToFront' @{})
}

function Cdp-Raw($method, $params) {
  $script:cid++
  $id = $script:cid
  $msg = @{ id = $id; method = $method; params = $params } | ConvertTo-Json -Depth 10 -Compress
  $bytes = [Text.Encoding]::UTF8.GetBytes($msg)
  $seg = New-Object 'ArraySegment[byte]' -ArgumentList @(, $bytes)
  if (-not $script:ws.SendAsync($seg, 'Text', $true, [Threading.CancellationToken]::None).Wait(30000)) { throw 'CDP send timeout' }
  $buf = New-Object byte[] 65536
  while ($true) {
    $ms = New-Object IO.MemoryStream
    do {
      $rseg = New-Object 'ArraySegment[byte]' -ArgumentList @(, $buf)
      $t = $script:ws.ReceiveAsync($rseg, [Threading.CancellationToken]::None)
      if (-not $t.Wait(60000)) { throw 'CDP receive timeout' }
      $ms.Write($buf, 0, $t.Result.Count)
    } while (-not $t.Result.EndOfMessage)
    $o = [Text.Encoding]::UTF8.GetString($ms.ToArray()) | ConvertFrom-Json
    if ($o.id -eq $id) { return $o }
  }
}

# Gọi CDP; mất kết nối (Chrome ngủ, tab tải lại...) thì nối lại và thử 1 lần nữa
function Cdp($method, $params) {
  try { return Cdp-Raw $method $params }
  catch { Start-Sleep 3; Connect-Tab; return Cdp-Raw $method $params }
}
function Js($code) {
  $r = Cdp 'Runtime.evaluate' @{ expression = $code; returnByValue = $true; userGesture = $true }
  if ($r.result.exceptionDetails) { return 'jserr' }
  return "$($r.result.result.value)"
}
function Nav($url) { [void](Cdp 'Page.navigate' @{ url = $url }) }
function Home { Nav "https://search.google.com/search-console?resource_id=$($script:RID)&hl=en" }

# ---------- JS dùng chung (giữ nguyên logic skill gốc) ----------
$CLICK = @'
(lbl)=>{const bs=[...document.querySelectorAll("[role=button]")].filter(e=>lbl.test((e.innerText||"").trim())&&e.offsetParent);bs.forEach(b=>{const r=b.getBoundingClientRect(),o={bubbles:true,cancelable:true,view:window,clientX:r.x+r.width/2,clientY:r.y+r.height/2,button:0};["pointerdown","mousedown","pointerup","mouseup","click"].forEach(t=>b.dispatchEvent(new (t.startsWith("pointer")?PointerEvent:MouseEvent)(t,o)))});return bs.length}
'@
$CLOSE_DIALOG = "($CLICK)(/^(Dismiss|GOT IT)`$/i)"
$DISMISS = '(()=>{const bs=[...document.querySelectorAll("button")].filter(b=>/^Dismiss$/i.test((b.innerText||"").trim())&&b.offsetParent);bs.forEach(b=>b.click());return bs.length})()'
$VIS = '(()=>[...document.querySelectorAll("*")].filter(e=>e.children.length===0&&/Indexing requested/.test(e.textContent)&&e.offsetParent).length)()'
$INSPECT = @'
(()=>{const i=[...document.querySelectorAll('input')].find(x=>/Inspect any URL/.test(x.getAttribute('aria-label')||''));if(!i)return 0;i.focus();i.value='__URL__';i.dispatchEvent(new Event('input',{bubbles:true}));const o={key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true};['keydown','keypress','keyup'].forEach(t=>i.dispatchEvent(new KeyboardEvent(t,o)));return 1})()
'@
$READ = @'
(()=>{const t=document.body.innerText;if(!location.pathname.includes('inspect')||!t.includes('__URL__')||/Retrieving data/i.test(t)||!/URL is (not )?on Google|unknown to Google|not in (the current )?property/i.test(t))return 'loading';const m=[...document.querySelectorAll('*')].filter(e=>e.children.length===0&&e.textContent.trim()==='Last crawl');const lc=m.map(x=>x.parentElement.parentElement.textContent.replace('Last crawl','').replace(/Crawled as.*/,'').trim()).join(' || ');const st=(t.match(/URL is (not )?on Google|URL is unknown to Google|not in (the current )?property/i)||[''])[0];return 'OK\t'+st+'\t'+m.length+'\t'+lc+'\t'+location.href})()
'@
$READY = @'
(()=>{const t=document.body.innerText;if(/not in (the current )?property/i.test(t))return 'NOTPROP';if(!location.pathname.includes('inspect')||!t.includes('__URL__')||/Retrieving data/i.test(t))return 'loading';return /REQUEST INDEXING/i.test(t)?'READY':'loading'})()
'@
$WATCH = @'
(()=>{const t=document.body.innerText;if(/Indexing request rejected/i.test(t))return 'rejected';const m=t.match(/Quota exceeded|Something went wrong|not a robot|recaptcha/i);if(m)return m[0];if(__VIS__>0&&/added to a priority crawl queue/i.test(t))return 'requested';return /Testing if live URL/i.test(t)?'testing':'none'})()
'@
function Fill($js, $u) { return $js.Replace('__URL__', $u) }

# ---------- Đọc Last crawl (như inspect.sh) ----------
function Inspect-Url($u) {
  Home; Start-Sleep 6
  $r = ''
  for ($k = 0; $k -lt 3; $k++) {
    [void](Js (Fill $INSPECT $u))
    for ($i = 0; $i -lt 15; $i++) { Start-Sleep 3; $r = Js (Fill $READ $u); if ($r -like 'OK*') { break } }
    if ($r -like 'OK*') { break }
    Start-Sleep 3
  }
  if ($r -notlike 'OK*') { return $null }
  # tải lại đúng trang kết quả cho sạch rồi đọc lại
  Nav (($r -split "`t")[-1]); Start-Sleep 5
  for ($i = 0; $i -lt 20; $i++) { $r = Js (Fill $READ $u); if ($r -like 'OK*') { break }; Start-Sleep 3 }
  if ($r -notlike 'OK*') { return $null }
  $p = $r -split "`t"
  return [pscustomobject]@{ Status = $p[1]; LastCrawl = $p[3] }
}

# "Oct 30, 2026, 9:15:23 PM" → DateTime; không đọc được → $null (coi như chưa đọc)
function Parse-Crawl($s) {
  if (-not $s) { return $null }
  $s = (($s -split ' \|\| ')[0] -replace '[  ]', ' ').Trim()
  foreach ($f in 'MMM d, yyyy, h:mm:ss tt', 'MMM d, yyyy, h:mm tt') {
    try { return [datetime]::ParseExact($s, $f, $Inv) } catch {}
  }
  return $null
}

# ---------- Một lần Request indexing (như request.sh) ----------
# Trả về: OK | SKIP | REJECTED | QUOTA | ROBOT | FAIL:<lý do>
function Request-Url($u) {
  Home; Start-Sleep 7
  $st = ''
  for ($k = 0; $k -lt 3; $k++) {
    [void](Js $CLOSE_DIALOG); Start-Sleep 1
    [void](Js (Fill $INSPECT $u))
    for ($i = 0; $i -lt 15; $i++) { Start-Sleep 3; $st = Js (Fill $READY $u); if ($st -eq 'READY' -or $st -eq 'NOTPROP') { break } }
    if ($st -eq 'READY' -or $st -eq 'NOTPROP') { break }
  }
  if ($st -eq 'NOTPROP') { return 'SKIP' }
  if ($st -ne 'READY') { return 'FAIL:không mở được trang inspect' }
  [void](Js $CLOSE_DIALOG); Start-Sleep 1
  if ((Js $VIS) -ne '0') { return 'FAIL:hộp thoại cũ chưa đóng' }
  [void](Js "($CLICK)(/^REQUEST INDEXING`$/i)")
  $seen = $false; $r = 'none'
  for ($i = 0; $i -lt 200; $i++) {
    Start-Sleep 3
    $r = Js ($WATCH.Replace('__VIS__', $VIS))
    if ($r -eq 'testing') { $seen = $true }
    if ($r -ne 'none' -and $r -ne 'testing') { break }
  }
  if ($r -eq 'requested' -and $seen) { $res = 'OK' }
  elseif ($r -eq 'rejected') { [void](Js $DISMISS); $res = 'REJECTED' }
  elseif ($r -match 'Quota') { $res = 'QUOTA' }
  elseif ($r -match 'robot|recaptcha') { $res = 'ROBOT' }
  else { $res = "FAIL:$r (testing_seen=$seen)" }
  [void](Js $CLOSE_DIALOG)
  return $res
}

# ---------- Chạy ----------
try { $cut = [datetime]::ParseExact($Moc, 'yyyy-MM-dd HH:mm', $Inv) }
catch { Say "Mốc giờ sai định dạng: '$Moc' (cần dạng 2026-10-30 21:00)"; exit 1 }
$urls = @(Get-Content $UrlFile -Encoding UTF8 | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^https?://' } | Select-Object -Unique)
try { Connect-Tab } catch { Say "DỪNG: $($_.Exception.Message)"; exit 1 }
Set-Content -Path $Out -Value "URL`tKết quả`tGhi chú" -Encoding UTF8
Say "Bắt đầu: $($urls.Count) URL, mốc giờ $($cut.ToString('dd/MM/yyyy HH:mm'))"

# Đã được Google đọc sau mốc chưa? Trả về chữ ngày đọc nếu rồi, $null nếu chưa.
function Fresh-Since($u) {
  $i = Inspect-Url $u
  if (-not $i) { return $null }
  if ($i.Status -match 'not in') { return 'NOTPROP' }
  $d = Parse-Crawl $i.LastCrawl
  if ($d -and $d -ge $cut) { return $d.ToString('dd/MM/yyyy HH:mm') }
  Say "  Last crawl: $($i.LastCrawl)"
  return $null
}

Say '=== BƯỚC 1: KIỂM TRA GOOGLE ĐÃ ĐỌC CHƯA'
$todo = @()
$n = 0
foreach ($u in $urls) {
  $n++
  $f = Fresh-Since $u
  if ($f -eq 'NOTPROP') { Add-Result $u 'SKIP' 'không thuộc property'; Say "[$n] SKIP (không thuộc property): $u" }
  elseif ($f) { Add-Result $u 'DA-DOC' "Google đọc lúc $f"; Say "[$n] ĐÃ ĐỌC lúc $f — bỏ qua: $u" }
  else { $todo += $u; Say "[$n] CẦN ÉP: $u" }
}

Say "=== BƯỚC 2: ÉP $($todo.Count) URL"
$n = 0
foreach ($u in $todo) {
  $n++; $try = 0
  while ($true) {
    $try++
    $r = Request-Url $u
    if ($r -eq 'OK') { Add-Result $u 'OK' "ép lúc $(Get-Date -Format 'dd/MM/yyyy HH:mm')"; Say "[$n/$($todo.Count)] OK sau $try lần: $u"; break }
    if ($r -eq 'SKIP') { Add-Result $u 'SKIP' 'không thuộc property'; Say "[$n/$($todo.Count)] SKIP: $u"; break }
    if ($r -eq 'ROBOT') { Say 'DỪNG: Google hiện ô "Tôi không phải robot" — cần bạn tự bấm, rồi chạy lại file 2.'; exit 1 }
    Say "  lần $try chưa được ($r): $u"
    if ($r -eq 'QUOTA') {
      Say "  Hết lượt ép trong ngày của Google — chờ $([int]($WaitQuota/60)) phút rồi thử lại"
      Start-Sleep $WaitQuota
      $f = Fresh-Since $u
      if ($f -and $f -ne 'NOTPROP') { Add-Result $u 'DA-DOC' "Google đọc lúc $f"; Say "  Google đã tự đọc lúc $f — thôi ép: $u"; break }
    }
    elseif ($r -eq 'REJECTED') { Start-Sleep $WaitRejected }
    else { Start-Sleep $WaitRetry }
  }
}
Say "=== XONG. Kết quả ở file: $Out"

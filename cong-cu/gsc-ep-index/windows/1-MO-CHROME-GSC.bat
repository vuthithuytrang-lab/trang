@echo off
rem Mo cua so Chrome rieng cho GSC, bat cong dieu khien 9222 de file 2 dieu khien duoc.
rem Lan dau: dang nhap Google bang tai khoan co quyen GSC. Cac lan sau Chrome nho dang nhap.
set "CH=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not exist "%CH%" set "CH=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not exist "%CH%" set "CH=%LocalAppData%\Google\Chrome\Application\chrome.exe"
if not exist "%CH%" (
  echo Khong tim thay Google Chrome tren may. Hay cai Chrome roi chay lai.
  pause
  exit /b 1
)
start "" "%CH%" --remote-debugging-port=9222 --user-data-dir="%LocalAppData%\GSC-Chrome" --no-first-run "https://search.google.com/search-console?hl=en"

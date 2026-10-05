@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo ============================================
echo   CAI DAT THEO DOI PUBLISH TECHCOMBANK
echo ============================================
echo.
echo [1/4] Kiem tra Python...
call _tim-python.bat
if not defined PY (
    echo Chua co Python. Dang cai Python 3.12, vui long cho...
    winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
    echo.
    echo Da cai xong Python. Hay DONG cua so nay roi bam dup CAI-DAT.bat them 1 lan nua.
    pause
    exit /b
)
%PY% --version

echo.
echo [2/4] Cai thu vien can thiet...
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 ( echo LOI: khong cai duoc thu vien. Chup man hinh gui Agent. & pause & exit /b 1 )

echo.
echo [3/4] Kiem tra chia khoa...
if not exist "bi-mat\service-account.json" echo   THIEU: bi-mat\service-account.json
if exist "bi-mat\service-account.json" echo   Co file service-account.json

echo.
echo [4/4] Bat lich tu dong 08:00 va 20:00...
for /f "delims=" %%i in ('%PY% -c "import sys;print(sys.executable)"') do set "PYEXE=%%i"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0cai-lich.ps1" -PythonExe "%PYEXE%"
if errorlevel 1 ( echo LOI: khong bat duoc lich. Chup man hinh gui Agent. & pause & exit /b 1 )

echo.
echo XONG! Nhat ky moi lan chay nam trong thu muc logs\
pause

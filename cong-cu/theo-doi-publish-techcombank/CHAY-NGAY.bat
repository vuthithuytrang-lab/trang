@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
call _tim-python.bat
if not defined PY ( echo Chua co Python - hay chay CAI-DAT.bat truoc. & pause & exit /b 1 )
echo Dang kiem tra tat ca URL (mat khoang 2-3 phut)...
%PY% theo_doi.py %*
pause

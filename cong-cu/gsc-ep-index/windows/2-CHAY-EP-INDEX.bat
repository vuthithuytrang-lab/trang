@echo off
chcp 65001 >nul
echo ============================================
echo   EP INDEX GOOGLE SEARCH CONSOLE
echo ============================================
echo Danh sach link lay tu file danh-sach-url.txt (cung thu muc).
echo.
echo Nhap GIO PUBLISH theo dang: nam-thang-ngay gio:phut
echo Vi du: 2026-10-30 21:00
echo Link nao Google da doc SAU gio nay se duoc bo qua.
echo.
set /p MOC=Gio publish: 
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ep-index.ps1" -Domain techcombank.com -UrlFile "%~dp0danh-sach-url.txt" -Moc "%MOC%"
echo.
echo Xong. Hay gui file ket-qua.tsv trong thu muc nay vao khung chat cho Claude.
pause

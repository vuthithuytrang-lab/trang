@rem Tim Python tren may, dat vao bien PY. Dung chung cho cac file .bat khac.
set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY python --version >nul 2>nul && set "PY=python"

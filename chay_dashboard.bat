@echo off
rem Buong lai Quy — mo dashboard Streamlit tai http://medici-ptdttc (cong 80, chi nghe 127.0.0.1).
rem Lan dau: uv venv .venv --python 3.12 ^&^& uv pip install --python .venv\Scripts\python.exe -r requirements.txt pytest
rem Ten mien medici-ptdttc = dong "127.0.0.1 medici-ptdttc" trong file hosts; thieu thi tu them (hoi quyen admin 1 lan).
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if not exist ".venv\Scripts\streamlit.exe" (
  echo Chua co .venv — chay lenh cai dat o dong 3 cua file nay truoc.
  pause
  exit /b 1
)
set HOSTS=%SystemRoot%\System32\drivers\etc\hosts
findstr /r /c:"^127\.0\.0\.1[ 	][ 	]*medici-ptdttc$" "%HOSTS%" >nul 2>&1
if errorlevel 1 (
  echo Them ten mien medici-ptdttc vao file hosts — bam Yes o hop thoai quyen admin.
  powershell -NoProfile -Command "Start-Process cmd -Verb RunAs -Wait -ArgumentList '/c (echo.&echo 127.0.0.1 medici-ptdttc)>>%HOSTS%&ipconfig /flushdns'"
)
".venv\Scripts\streamlit.exe" run dashboard\app.py --server.address 127.0.0.1 --server.port 80 --browser.serverAddress medici-ptdttc --browser.serverPort 80 --browser.gatherUsageStats false

@echo off
rem Buong lai Quy — mo dashboard Streamlit tai http://localhost:8501 (chi nghe localhost).
rem Lan dau: uv venv .venv --python 3.12 ^&^& uv pip install --python .venv\Scripts\python.exe -r requirements.txt pytest
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if not exist ".venv\Scripts\streamlit.exe" (
  echo Chua co .venv — chay lenh cai dat o dong 3 cua file nay truoc.
  pause
  exit /b 1
)
".venv\Scripts\streamlit.exe" run dashboard\app.py --server.address localhost --server.port 8501 --browser.gatherUsageStats false

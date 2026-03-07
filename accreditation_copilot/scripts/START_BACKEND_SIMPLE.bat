@echo off
cd /d "%~dp0"
echo Starting Backend API...
echo.
call ..\venv\Scripts\activate.bat
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
pause

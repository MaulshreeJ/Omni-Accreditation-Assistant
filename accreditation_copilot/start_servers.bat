@echo off
echo Starting Omni Accreditation Copilot...
echo.

REM Start backend API in a new window (with venv activation)
start "Backend API" cmd /k "cd /d %~dp0 && call ..\venv\Scripts\activate.bat && uvicorn api.main:app --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
start "Frontend UI" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Both servers are starting in separate windows...
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
echo.
echo Press any key to exit this window (servers will keep running)
pause >nul

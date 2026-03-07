@echo off
cd /d "%~dp0"
echo ========================================
echo  Restarting Backend API with Updates
echo ========================================
echo.
echo Activating virtual environment...
call ..\venv\Scripts\activate.bat
echo.
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

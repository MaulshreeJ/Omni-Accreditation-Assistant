# Start Omni Accreditation Copilot Servers
Write-Host "Starting Omni Accreditation Copilot..." -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start backend API in a new window with venv
Write-Host "Starting Backend API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir'; ..\venv\Scripts\Activate.ps1; uvicorn api.main:app --host 0.0.0.0 --port 8000"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend in a new window
Write-Host "Starting Frontend UI..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\frontend'; npm run dev"

Write-Host ""
Write-Host "Both servers are starting in separate windows..." -ForegroundColor Green
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend UI: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this window (servers will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

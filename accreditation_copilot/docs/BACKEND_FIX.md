# Backend Ingestion Fix

## Problem Identified
The backend server was running without the virtual environment activated, causing the `pdfplumber` and `PyMuPDF` imports to fail during ingestion.

## Root Cause
The startup scripts (`start_servers.bat` and `start_servers.ps1`) were not activating the Python virtual environment before starting the backend server.

## Fix Applied
Updated both startup scripts to activate the venv before starting uvicorn:

### start_servers.bat
```batch
start "Backend API" cmd /k "cd /d %~dp0 && call ..\venv\Scripts\activate.bat && uvicorn api.main:app --host 0.0.0.0 --port 8000"
```

### start_servers.ps1
```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir'; ..\venv\Scripts\Activate.ps1; uvicorn api.main:app --host 0.0.0.0 --port 8000"
```

## How to Fix Right Now

### Option 1: Restart Using Fixed Batch File
1. Close all existing server windows
2. Run: `accreditation_copilot\start_servers.bat`
3. This will start both backend and frontend with proper venv activation

### Option 2: Manual Restart
1. Close the existing backend server window
2. Open a new terminal in the project root
3. Run:
```bash
cd accreditation_copilot
..\venv\Scripts\activate
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Option 3: Kill and Restart
1. Find the backend process:
```powershell
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
```

2. Kill it:
```powershell
Stop-Process -Id <PID> -Force
```

3. Start with venv:
```bash
cd accreditation_copilot
..\venv\Scripts\activate
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Verification
After restarting, test the ingestion endpoint:
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/upload/ingest" -Method POST
```

You should see a successful response instead of "No module named 'pdfplumber'".

## What This Fixes
- File ingestion will now work properly
- The "check the backend logs" error will be resolved
- Evidence will display with real content from uploaded PDFs
- All Python dependencies will be available to the backend

## Next Steps
1. Restart the backend using one of the options above
2. Refresh the frontend page
3. Click "Ingest Files" button
4. Wait for ingestion to complete
5. Run an audit query to see real evidence

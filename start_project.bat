@echo off
echo ============================================================
echo  CRICKET STRATEGY AI - STARTING ALL SERVICES
echo ============================================================
echo.
echo Starting FastAPI backend on port 8000...
start "FastAPI Backend" cmd /k "cd C:\Users\vishal\Desktop\cricket_statergy_ai && C:\Users\vishal\Desktop\cricket_statergy_ai\venv311\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting React frontend on port 5173...
start "React Frontend" cmd /k "cd C:\Users\vishal\Desktop\cricket_statergy_ai\frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo Opening browser...
start "" "http://localhost:5173"

echo.
echo ============================================================
echo  ALL SERVICES STARTED!
echo  React App  : http://localhost:5173
echo  API Docs   : http://localhost:8000/docs
echo ============================================================
pause

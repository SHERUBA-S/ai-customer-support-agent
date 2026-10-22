@echo off
title AI Customer Support Agent - Launcher
echo ===================================================
echo   Starting AI Customer Support RAG System
echo ===================================================
echo.

cd /d "%~dp0"

echo [1/3] Starting Backend Server (FastAPI on Port 8000)...
start "AI Agent Backend (FastAPI)" cmd /k "cd /d %~dp0 && set PYTHONUTF8=1 && set PYTHONPATH=backend && .\venv\Scripts\python.exe backend\run_backend.py"

timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend Server (Vite on Port 5173)...
start "AI Agent Frontend (Vite)" cmd /k "cd /d %~dp0\frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo [3/3] Opening Browser...
start http://localhost:5173/

echo.
echo ===================================================
echo   System is running!
echo   - Frontend: http://localhost:5173
echo   - Backend Docs: http://127.0.0.1:8000/docs
echo   - Admin User: admin
echo   - Admin Pass: admin123
echo ===================================================
pause

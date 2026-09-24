@echo off
title Loan Master - Starting...
color 0A
echo ========================================
echo   LOAN MASTER - Starting System
echo ========================================
echo.

echo [1/4] Starting XAMPP Services...
start "" "C:\xampp\xampp-control.exe"
timeout /t 3 >nul

echo [2/4] Activating Virtual Environment...
call venv\Scripts\activate

echo [3/4] Starting Flask Application...
echo.
echo ========================================
echo   SYSTEM RUNNING
echo   Open browser: http://localhost:5000
echo ========================================
echo.
echo Press CTRL+C to stop the server
echo.

python main.py
pause
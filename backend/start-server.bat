@echo off
REM NexQA Backend Server Startup Script for Windows
REM This script ensures clean server startup and proper process cleanup

echo Starting NexQA Backend Server...
echo.

REM Kill any existing Python processes running server.py
echo Checking for existing server processes...
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr /I "PID"') do (
    wmic process where "ProcessId=%%a and CommandLine like '%%server.py%%'" delete 2>nul
)

REM Wait a moment for cleanup
timeout /t 2 /nobreak >nul

REM Navigate to backend directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Start the server
echo.
echo Starting Flask server on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python server.py

REM If server exits, pause to show any error messages
if errorlevel 1 (
    echo.
    echo Server exited with an error!
    pause
)

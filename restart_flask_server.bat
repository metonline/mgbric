@echo off
REM Kill all Python processes
TASKKILL /F /IM python.exe /T

REM Wait a moment to ensure all are killed
TIMEOUT /T 2 /NOBREAK >nul

REM Activate virtual environment
CALL .venv\Scripts\activate.bat

REM Start the Flask server
start "Flask Server" .venv\Scripts\python.exe scheduled_server.py

echo Server started. Press any key to exit this window.
pause

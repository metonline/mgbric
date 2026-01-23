@echo off
REM BRIC Complete Database Update Script
REM Runs daily via Windows Task Scheduler
REM Updates: tournament results, hands, board results, player rankings

cd /d "C:\Users\metin\Desktop\BRIC"

echo [%date% %time%] Starting BRIC Complete Update >> complete_update_log.txt

REM Run the complete update pipeline
"C:\Users\metin\Desktop\BRIC\.venv\Scripts\python.exe" complete_update.py >> complete_update_log.txt 2>&1

echo [%date% %time%] Update completed >> complete_update_log.txt
echo. >> complete_update_log.txt

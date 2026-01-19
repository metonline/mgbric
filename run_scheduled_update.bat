@echo off
REM BRIC Database Update Script
REM This script is called by Windows Task Scheduler to automatically update the database

cd /d "C:\Users\metin\Desktop\BRIC"
"C:\Users\metin\Desktop\BRIC\.venv\Scripts\python.exe" scheduled_update.py >> update_log.txt 2>&1

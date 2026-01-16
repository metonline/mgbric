# Automatic Tournament Data Fetching

This document explains how to set up automatic fetching of tournament data from Vugraph.

## Quick Start

### One-Time Fetch (Manual)
```bash
python auto_fetch_tournaments.py
```
This checks for new dates and fetches any missing tournament data.

### Check What's New
```bash
python auto_fetch_tournaments.py --check
```
Shows how many new dates are available without fetching.

### List All Dates
```bash
python auto_fetch_tournaments.py --list
```
Lists all available dates and their status (in database or missing).

---

## Automation Options

### Option 1: Windows Task Scheduler (Recommended)

**Automatic Setup:**
```bash
python setup_auto_fetch.py
```
Then choose option 1 to create a scheduled task.

**Manual Setup:**
1. Press `Win+R`, type `tasksched.msc`, press Enter
2. Click "Create Basic Task"
3. Name: `BRIC Auto-Fetch Tournaments`
4. Trigger: Daily at preferred time (e.g., 12:00 AM)
5. Action:
   - Program: `C:\Path\To\python.exe`
   - Arguments: `auto_fetch_tournaments.py`
   - Start in: `C:\Users\metin\Desktop\BRIC`
6. Click Finish

**Pro:** Windows handles scheduling, runs even when user isn't logged in, can be configured with detailed rules

### Option 2: Batch File + Task Scheduler

**Automatic Setup:**
```bash
python setup_auto_fetch.py
```
Then choose option 2 to create a batch file.

**Manual Setup:**
Create `fetch_tournaments_scheduled.bat`:
```batch
@echo off
cd /d "C:\Users\metin\Desktop\BRIC"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python auto_fetch_tournaments.py
```

Then use Windows Task Scheduler to run this batch file on a schedule.

**Pro:** Easier to debug, shows output, can be run manually anytime

### Option 3: Background Python Scheduler

**Install dependency:**
```bash
pip install schedule
```

**Run in background:**
```bash
python background_fetch_scheduler.py
```

Or with custom time:
```bash
python background_fetch_scheduler.py 18:00 6
```
This runs daily at 6:00 PM and every 6 hours.

**Pro:** Cross-platform, flexible scheduling, runs while Python is open

### Option 4: Windows Startup Script

Add to your startup folder to run fetcher when you log in:

Create `auto_fetch_on_startup.vbs`:
```vbscript
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd /c cd C:\Users\metin\Desktop\BRIC && python auto_fetch_tournaments.py", 0
```

Place in `C:\Users\metin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

**Pro:** Runs automatically when you start your computer

---

## How It Works

The automatic fetcher does this:

1. **Scans Vugraph Calendar** (`https://clubs.vugraph.com/hosgoru/calendar.php`)
   - Extracts all dates that have tournament events

2. **Checks Database** 
   - Sees which dates are already in `database.json`

3. **Identifies New Dates**
   - Compares available dates with database dates

4. **Fetches Missing Data**
   - For each new date, runs the vugraph_fetcher with correct date-event mapping
   - Properly handles both NS (Kuzey-Güney) and EW (Doğu-Batı) sections

5. **Updates Database**
   - Adds new tournament records
   - Removes old records for that date (prevents duplicates)

## Example Output

```
======================================================================
AUTOMATIC TOURNAMENT DATA FETCHER
======================================================================

1. Scanning Vugraph calendar for events...
   Found 31 dates with events

2. Checking database...
   Database has 29 unique dates

3. Identifying new dates to fetch...
   Found 2 new date(s) to fetch: ['30.12.2025', '31.12.2025']

4. Fetching tournament data for 2 date(s)...

   [1/2] Fetching 30.12.2025...
   
   ============================================================
   Fetching data for: 30.12.2025
   ============================================================
   
   1. Fetching Vugraph calendar...
   2. Parsing calendar events...
      Found 1 total events
   
   3. Fetching tournament data...
      Found 1 event(s) for 30.12.2025
   
      Event 404057: Salı
      ✓ Parsed 50 records (NS: 27, EW: 23)
   
   4. Updating database...
      Removed 0 old records for 30.12.2025
      Added 50 new records
      Total database now: 55352 records
   
       ✓ Database saved successfully
   
   5. Verification:
      30.12.2025: 50 total records
      NS pairs: 27
      EW pairs: 23
   
      Tournaments for 30.12.2025:
      • Salı Turnuvası Sonuçları (30.12.2025 14:00): 50 records
   
   ✓ Data for 30.12.2025 successfully updated!
       ✓ Successfully added 30.12.2025
   
   [2/2] Fetching 31.12.2025...
   ... (similar output)

======================================================================
SUMMARY
======================================================================
Successfully fetched: 2 date(s)
Failed: 0 date(s)
Total records in database: 55402
======================================================================
```

## Features

✅ **Automatic Date Detection** - Knows exactly which dates have events  
✅ **No Duplicates** - Removes old records before adding new ones  
✅ **Correct Parsing** - Properly handles both NS and EW sections  
✅ **Error Handling** - Continues even if one date fails  
✅ **Logging** - Shows detailed progress  
✅ **Database Integrity** - Validates JSON before/after updates  

## Troubleshooting

### "ModuleNotFoundError: No module named 'schedule'"
```bash
pip install schedule
```

### "Connection timeout" errors
- Check your internet connection
- Vugraph might be temporarily unavailable
- Wait a few minutes and try again

### Task Scheduler not running the task
- Make sure Python.exe path is correct
- Verify the working directory is set
- Check Task Scheduler logs for errors
- Run Task Scheduler as Administrator

### Want to see what's happening?
```bash
python auto_fetch_tournaments.py --check
python auto_fetch_tournaments.py --list
```

## Using with Existing Database

✅ The automatic fetcher **safely updates** existing data:
- Only fetches dates that aren't in the database
- Removes old records for a date before adding new ones
- Preserves all other data
- Validates database integrity

## Scheduling Examples

### Daily at Midnight
```bash
python setup_auto_fetch.py
# Choose option 1, use default time (12:00 = midnight)
```

### Every 6 Hours
```bash
python background_fetch_scheduler.py 00:00 6
# Runs at midnight, 6am, noon, 6pm every day
```

### Only on Weekdays at 1:00 AM
Use Windows Task Scheduler with custom trigger settings.

## Advanced: Manual Date Fetching

If you need to fetch a specific date:
```bash
python vugraph_fetcher.py 25.12.2025
```

This directly fetches data for Christmas 2025.

---

## Performance Notes

- **Calendar scan:** ~1-2 seconds
- **Per date fetch:** ~3-5 seconds (depends on event count)
- **Full month fetch:** ~30-60 seconds
- **Database update:** <1 second

Fetching 30 dates takes roughly 2-3 minutes total.

## Data Quality

The automated system ensures:
- ✅ Correct date-to-event mapping (verified from calendar grid)
- ✅ Both NS and EW sections parsed correctly
- ✅ Duplicate removal before adding new data
- ✅ Tournament names consistent with source
- ✅ Pair rankings and scores accurate

---

Need help? Check the main README.md or examine the scripts' code comments.

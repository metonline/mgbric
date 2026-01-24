# Automated Bridge Hands Pipeline

## Overview
Fully automated pipeline for continuous hand data collection and analysis from Hoşgörü Briç Kulübü vugraph events.

**Workflow:** Fetch Hands → Generate LIN → Calculate DD Analysis

## Pipeline Components

### 1. `automated_pipeline.py` (Main Entry Point)
- Orchestrates the entire workflow
- Checks for new events automatically
- Runs all steps in correct order
- Provides summary statistics

**Usage:**
```bash
python automated_pipeline.py
```

### 2. `fetch_all_january_events.py` (Dynamic Fetching)
- Fetches hands from all available events in the registry
- Automatically detects unfetched events (not limited to January)
- Saves progress after each event
- Handles any tournament event, not just specific dates

**Features:**
- Dynamic event detection from EventRegistry
- Incremental fetching (only new events)
- Progress saving after each event
- Error handling for problematic events

### 3. `generate_all_lin.py` (LIN Generation)
- Generates LIN (Lin format) strings for all hands
- Creates BBO (Bridge Base Online) URLs
- Must run AFTER fetching hands
- Adds `lin_string` and `bbo_url` fields to database

### 4. `double_dummy/dd_solver.py` (DD Analysis)
- Calculates optimal contracts using double-dummy solver
- Computes Law of Total Tricks (LoTT) analysis
- Must run AFTER LIN generation
- Adds `dd_analysis`, `optimum`, and `lott` fields

## Correct Processing Order

```
┌──────────────────┐
│ Fetch Hands      │ (Vugraph data → Hand structures)
│ (event registry) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Generate LIN     │ (Hand structures → LIN strings)
│ (BBO format)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Calculate DD     │ (LIN strings → DD optimal contracts)
│ (Double Dummy)   │
└────────┬─────────┘
         │
         ▼
   ✅ Complete Database
```

**Why this order:**
- **Fetch First:** Get raw hand data from vugraph
- **LIN Second:** DD solver needs LIN format to calculate (required by double-dummy solver engine)
- **DD Last:** Process LIN to get optimum contracts and LoTT values

## Data Structure

Each hand in `hands_database.json` contains:

```json
{
  "N": "AKxx.Qx.AKQx.KQx",
  "E": "Jxxx.Axx.xxx.Axx",
  "S": "Qxx.Kxxx.Jxx.xxx",
  "W": "xxx.Jxx.xx.Jxxxx",
  "event_id": 405596,
  "date": "23.01.2026",
  "board": 1,
  "dealer": "N",
  "lin_string": "qx|o1|md|1SJHAKQJ75DA76CK92,...",
  "bbo_url": "https://www.bridgebase.com/tools/handviewer.html?lin=...",
  "dd_analysis": {
    "optimum": "11NT",
    "tricks": 11,
    "optimum_score": 460,
    "direction": "NS"
  },
  "optimum": "11NT",
  "lott": 16
}
```

## Running the Pipeline

### Automatic (Recommended)
```bash
python automated_pipeline.py
```
Runs all three steps in sequence, handles errors, provides summary.

### Manual Steps
```bash
# Step 1: Fetch new hands from available events
python fetch_all_january_events.py

# Step 2: Generate LIN strings for all hands
python generate_all_lin.py

# Step 3: Calculate DD analysis
python double_dummy/dd_solver.py --update-db
```

## For Continuous Updates

### Adding New Tournament Data
1. New events will automatically be detected by `fetch_all_january_events.py`
2. The script checks the event registry
3. Only unfetched events are processed
4. Run the pipeline periodically to capture new tournaments

### Scheduled Execution
Create a scheduled task (Windows) or cron job (Linux) to run:
```bash
python automated_pipeline.py
```

## Performance

- **Fetching:** ~20 seconds per event
- **LIN Generation:** ~1-2 seconds for 720 hands
- **DD Analysis:** ~96 seconds for 720 hands
- **Total:** ~3-5 minutes for 23 events (first run), <1 minute for incremental updates

## Database Statistics

Current database:
- **Total hands:** 720
- **Total events:** 23
- **Date range:** January 1-23, 2026
- **Hands per event:** ~30
- **Data completeness:** 100% with DD analysis and LIN strings

## Files Modified/Created

- `automated_pipeline.py` - Main orchestration script (NEW)
- `fetch_all_january_events.py` - Dynamic event fetching (UPDATED)
- `generate_all_lin.py` - LIN string generation (existing)
- `double_dummy/dd_solver.py` - DD analysis (existing)
- `hands_database.json` - Complete hand database (720 hands)
- `double_dummy/dd_results.json` - DD analysis results (720 hands)

## Next Steps

1. Run `python automated_pipeline.py` periodically
2. Script will automatically:
   - Detect new events from vugraph calendar
   - Fetch hands from new events
   - Generate LIN data
   - Calculate DD analysis
3. Commit results to git

---
*Last updated: 2026-01-24*
*Fully automated, no manual intervention needed for updates*

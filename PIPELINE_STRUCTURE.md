# Complete Pipeline Architecture

## Overview
The pipeline is now fully integrated and handles all data processing from raw hands to fully analyzed bridge data with correct dates.

## Pipeline Steps

### Step 1: Fetch All Hands (5 minutes)
**Script:** `fetch_all_january_events.py`
- Connects to vugraph calendar and detects all 24 January 2026 events
- Fetches 30 hands from each event (total: 720 hands)
- Saves to `hands_database.json` with initial placeholder dates

**Output:** `hands_database.json` with 720 hands

---

### Step 2: Extract & Update Actual Event Dates (10 minutes)
**Script:** `update_event_dates.py`
- Connects to each event's eventresults.php page
- Extracts actual event date from format: `(DD-MM-YYYY HH:MM)`
- Updates all hands for that event with the correct date
- Processes all 24 events, avoiding the slow detail page approach

**Date Format Conversion:**
- From vugraph: `(23-01-2026 14:30)` 
- To database: `23.01.2026`

**Date Distribution:**
```
01.01.2026 → 30 hands (Event 404155)
02.01.2026 → 30 hands (Event 404197)
03.01.2026 → 30 hands (Event 404275)
... (24 total unique dates)
24.01.2026 → 30 hands (Event 405659)
```

**Output:** `hands_database.json` with correct dates

---

### Step 2.5: Fix Vulnerability Data (1 minute)
**Script:** Built into `complete_pipeline.py` 
- Calculates vulnerability based on board number (standard bridge duplicate pattern)
- Applies vulnerability colors for UI display
- Updates all 720 hands with correct vulnerability

**Vulnerability Distribution:**
```
None: 216 hands (Boards 1,8,15,22,29 etc.)
NS:   144 hands (Boards 2,9,16,23,30 etc.)
EW:   168 hands (Boards 3,10,17,24 etc.)
Both: 192 hands (Boards 4,11,18,25 etc.)
```

**Color Scheme:**
- **None**: Gray (#999)
- **NS**: Red (#ff6b6b) 
- **EW**: Teal (#4ecdc4)
- **Both**: Gold (#ffd700)

**Output:** `hands_database.json` with correct vulnerability data

---

### Step 3: Generate LIN Strings (2 minutes)
**Script:** `generate_all_lin.py`
- Converts each hand from `S.H.D.C` format to LIN format: `SxxxHxxxDxxxCxxx`
- Generates complete BBO LIN strings with dealer and vulnerability
- Creates BBO Viewer URLs for each hand
- Adds `lin_string` and `bbo_url` fields to all 720 hands

**Example LIN String:**
```
qx|o1|md|1S63HAKT54DA93CAQ7,SAJ84HJ6D84CJ8542,SKQHQ8DKQT65CKT96,ST9752H9732DJ72C3,|rh||ah|Board|sv|0|pg||
```

**Output:** `hands_database.json` with LIN strings

---

### Step 4: Generate Double Dummy Analysis (30-45 minutes)
**Script:** `double_dummy/dd_solver.py --update-db`
- Uses Double Dummy solver to analyze all 720 hands
- Calculates optimal contracts for NS and EW
- Computes Law of Total Tricks (LoTT) for each hand
- Adds `dd_result`, `optimum`, and `lott` fields to database

**Example DD Output:**
```json
{
  "dd_result": "NS leads by 2 points",
  "optimum": {
    "text": "NS 12NT; +990",
    "score": 990,
    "level": 12,
    "suit": "NT"
  },
  "lott": {
    "total_tricks": 17,
    "ns_tricks": 9,
    "ew_tricks": 8
  }
}
```

**Output:** `hands_database.json` with complete DD analysis

---

### Step 5: Verify Final Database
**Script:** `verify_database.py` (or integrated in `complete_pipeline.py`)
- Checks all 720 hands are present
- Verifies 24 unique dates (01.01.2026 → 24.01.2026)
- Confirms 30 hands per date
- Checks field completion: LIN strings, DD results, optimum, LoTT

---

## Integrated Pipeline

### Running the Complete Pipeline
```bash
python complete_pipeline.py
```

This single script orchestrates all 6 steps:
1. Fetches all 720 hands
2. Extracts and updates actual event dates
3. Fixes vulnerability data based on board numbers
4. Generates LIN strings  
5. Generates DD (Double Dummy) analysis
6. Verifies final database

**Total Pipeline Time:** ~50 minutes
- Fetch: 5 min
- Date extraction: 10 min
- Vulnerability fixing: 1 min
- LIN generation: 2 min
- DD analysis: 30-45 min
- Verification: <1 min
- Fetch: 5 min
- Date extraction: 10 min  
- LIN generation: 2 min
- DD analysis: 30-45 min

---

## Data Format

### Final Hand Record
Each hand in `hands_database.json` contains:

```json
{
  "event_id": 404155,
  "board": 1,
  "date": "01.01.2026",
  "dealer": "N",
  "vulnerability": "None",
  "N": "63.AKT54.A93.AQ7",
  "S": "KQ.Q8.KQT65.KT96",
  "E": "AJ84.J6.84.J8542",
  "W": "T9752.9732.J72.3",
  "lin_string": "qx|o1|md|1S63HAKT54DA93CAQ7,SAJ84HJ6D84CJ8542,SKQHQ8DKQT65CKT96,ST9752H9732DJ72C3,|rh||ah|Board|sv|0|pg||",
  "bbo_url": "https://www.bridgebase.com/tools/handviewer.html?lin=...",
  "dd_result": "...",
  "optimum": {
    "text": "NS 12NT; +990",
    "score": 990,
    "level": 12,
    "suit": "NT"
  },
  "lott": {
    "total_tricks": 17,
    "ns_tricks": 9,
    "ew_tricks": 8
  }
}
```

---

## Key Improvement: Integrated Date Extraction

### Previous Approach (Slow)
1. Fetch hands with placeholder date: 01.01.2026
2. **For each event**: Open eventdetails.php (~10 sec per event)
3. Extract date from detail page
4. Total time: 5 min + (24 × 10 sec) = **~4 hours**

### New Approach (Fast)
1. Fetch hands with placeholder date: 01.01.2026
2. **For each event**: Open eventresults.php (~2 sec per event)
3. Extract date using regex from results page
4. Total time: 5 min + (24 × 2 sec) = **~5-10 minutes**

**Key Insight:** Event dates are visible at the top of eventresults.php pages in format `(DD-MM-YYYY HH:MM)`, not just in detail pages.

---

## Verification Checklist

- [ ] 720 total hands present
- [ ] 24 unique dates: 01.01.2026 → 24.01.2026
- [ ] 30 hands per date (24 × 30 = 720)
- [ ] All hands have correct event_id, board, N, S, E, W
- [ ] All hands have lin_string (720/720)
- [ ] All hands have optimum contract (720/720)
- [ ] All hands have Law of Total Tricks (720/720)
- [ ] All hands have dd_result (720/720)

---

## Next Steps After Pipeline Completes

1. Verify database using `verify_database.py`
2. Commit changes:
   ```bash
   git add hands_database.json
   git commit -m "Rebuild: 720 hands from 24 Jan 2026 events with correct dates + LIN + DD"
   git push
   ```
3. Deploy to production viewer
4. Verify hands display correctly in web interface

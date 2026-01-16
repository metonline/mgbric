# DD Values Extraction Guide

## Overview

You have **30 bridge tournament boards**. Board 1 has real DD (Double Dummy) values, but Boards 2-30 currently have placeholder values. This guide explains how to populate them with real DD analysis from BBO.

---

## Quick Start

### Option A: Automated (Recommended if you have Chrome installed)

```bash
pip install selenium
python extract_dd_auto.py
```

**Time**: ~5-10 minutes ⏱️

### Option B: Manual (Web Form)

1. Ensure server is running:
```bash
cd app\www
python server_with_api.py
```

2. Open form:
```
http://localhost:8000/dd_input.html
```

3. Fill in values for each board (look them up in BBO)

**Time**: ~5 minutes per board × 29 boards = 2-3 hours ⏰

---

## Detailed Instructions

### Method A: Automated Extraction

#### Requirements:
- Google Chrome or Chromium browser installed
- Python 3.6+
- Selenium library

#### Setup:

1. **Install Selenium**:
   ```bash
   pip install selenium
   ```

2. **Run the extractor**:
   ```bash
   python extract_dd_auto.py
   ```

#### What It Does:

The script will:
1. Load all 30 boards from the database
2. For each board 2-30:
   - Generate the hand data in BBO's LIN format
   - Open BBO's hand viewer in a headless (invisible) browser
   - Wait for the DD table to load
   - Extract trick values for all 20 suit/player combinations (5 suits × 4 players)
   - Save to database
3. Skip Board 1 (already has real values)
4. Report success/failure for each board

#### Output:

```
======================================================================
BBO DD VALUES EXTRACTOR - AUTOMATED
======================================================================

Loading database...
Found 30 boards

Processing...
----------------------------------------------------------------------
  Board 2: Opening BBO...
  Board 2: Looking for DD table...
  Board 2: ✓ Extracted all 20 values
  Board 3: Opening BBO...
  ...
  Board 30: ✓ Extracted all 20 values
----------------------------------------------------------------------

RESULTS
======================================================================
✓ Successfully extracted: 29/29 boards
🎉 All boards successfully updated!
======================================================================
```

#### Troubleshooting:

**Issue**: "Chrome not found"
```
Solution: Make sure Google Chrome is installed
          https://google.com/chrome
```

**Issue**: "Selenium module not found"
```
Solution: pip install selenium
```

**Issue**: Some boards fail to extract
```
Solution: Note the failed board numbers
          Manually fill them in using dd_input.html
```

---

### Method B: Manual Input Form

#### Requirements:
- Python HTTP server running
- Web browser
- BBO (to look up DD values)

#### Setup:

1. **Start the server** (if not already running):
   ```bash
   cd c:\Users\metin\Desktop\BRIC\app\www
   python server_with_api.py
   ```

2. **Open the input form**:
   ```
   http://localhost:8000/dd_input.html
   ```

#### How to Use:

**For Each Board (2-30):**

1. **Click the board number button** (starts with board 2)
   
2. **Look up the board on BBO**:
   - Open BBO in another tab
   - Or use the BBO viewer already open

3. **Read the DD table**:
   - Look at the "Double Dummy" analysis table
   - Find tricks values for each suit and direction
   - Example format:
     ```
     NT: N=6, S=6, E=9, W=9
     S:  N=6, S=6, E=10, W=10
     H:  N=8, S=8, E=7, W=7
     D:  N=7, S=7, E=6, W=6
     C:  N=9, S=9, E=5, W=5
     ```

4. **Enter the values** in the form:
   - 5 rows (one for each suit: NT, S, H, D, C)
   - 4 columns (one for each direction: N, S, E, W)
   - Values must be 6-13 (representing tricks available)

5. **Click "Save Board"**:
   - Button turns green ✓
   - Board number button turns green and shows ✓

6. **Click "Next Board"** or select next board number:
   - Form clears for next board
   - Continue from step 1

**Example Fill-in:**

For Board 2 with values:
- NT: N=6, S=6, E=9, W=9
- S: N=6, S=6, E=10, W=10
- H: N=8, S=8, E=7, W=7
- D: N=7, S=7, E=6, W=6
- C: N=9, S=9, E=5, W=5

Fill in grid:
```
      N    S    E    W
NT    6    6    9    9
S     6    6   10   10
H     8    8    7    7
D     7    7    6    6
C     9    9    5    5
```

#### Progress Tracking:

- **Gray buttons**: Not started
- **Blue button** (selected): Currently editing
- **Green buttons with ✓**: Completed

The form shows "X/29 Boards Completed" at the top.

#### Advantages:

✓ No dependencies (besides Python server)
✓ Can verify each value as you enter
✓ Full control over data entry
✓ Can go back and edit any board

#### Time Estimate:

- ~3 minutes reading/entering per board
- 29 boards = ~1.5-2 hours total
- Can work in sessions (save progress as you go)

---

## Understanding DD Values

### What is DD (Double Dummy)?

DD Analysis shows how many tricks are available for each player in each suit, assuming optimal play by both sides and all hands revealed.

### Format Used:

```json
{
  "NTN": 6,   // NT (No Trump) - North can make 6 tricks
  "NTS": 6,   // NT - South can make 6 tricks
  "NTE": 9,   // NT - East can make 9 tricks
  "NTW": 9,   // NT - West can make 9 tricks
  "SN": 6,    // Spades - North can make 6 tricks
  "SS": 6,    // Spades - South can make 6 tricks
  "SE": 10,   // Spades - East can make 10 tricks
  "SW": 10,   // Spades - West can make 10 tricks
  ...
}
```

### Key Points:

- **6 tricks**: Pass (no contract makeable)
- **7 tricks**: 1-level contract possible
- **8 tricks**: 2-level contract possible
- **9 tricks**: 3-level contract possible
- **13 tricks**: Grand slam possible (all tricks)

### Valid Range:

Always between **6 and 13** tricks.

---

## Verification

After completing either method, verify the values were saved:

```bash
# Check a sample of boards
python -c "import json; f=open('app/www/hands_database.json'); d=json.load(f); boards=d['events']['hosgoru_04_01_2026']['boards']; print('Board 1:', dict(list(boards['1']['dd_analysis'].items())[:5])); print('Board 2:', dict(list(boards['2']['dd_analysis'].items())[:5])); print('Board 30:', dict(list(boards['30']['dd_analysis'].items())[:5]))"
```

Expected output:
```
Board 1: {'NTN': 6, 'NTS': 6, 'NTE': 9, 'NTW': 9, 'SN': 6}
Board 2: {'NTN': ..., 'NTS': ..., ...}  # Different values
Board 30: {'NTN': ..., 'NTS': ..., ...} # Different values
```

---

## API Reference

If you need to save DD values programmatically:

### Endpoint
```
POST /api/save_dd
```

### Request Format
```json
{
  "board_num": 2,
  "dd_analysis": {
    "NTN": 6,
    "NTS": 6,
    "NTE": 9,
    "NTW": 9,
    "SN": 6,
    "SS": 6,
    "SE": 10,
    "SW": 10,
    "HN": 8,
    "HS": 8,
    "HE": 7,
    "HW": 7,
    "DN": 7,
    "DS": 7,
    "DE": 6,
    "DW": 6,
    "CN": 9,
    "CS": 9,
    "CE": 5,
    "CW": 5
  }
}
```

### Response
```json
{
  "success": true,
  "message": "Board 2 DD values saved"
}
```

---

## Recommended Workflow

### For Quick Completion (Automated):

```bash
# 1. Install dependencies
pip install selenium

# 2. Run automated extraction
python extract_dd_auto.py

# 3. (Optional) Check results
python check_database.py

# 4. Open viewer to verify
# http://localhost:8000/hands_viewer.html
```

**Time: ~10 minutes**

### For Careful/Manual Process:

```bash
# 1. Ensure server running
cd app\www && python server_with_api.py

# 2. Open manual input form
# http://localhost:8000/dd_input.html

# 3. Work through boards 2-30
# (Can do in multiple sessions)

# 4. Verify in viewer
# http://localhost:8000/hands_viewer.html
```

**Time: 2-3 hours (can split into sessions)**

### For Hybrid Approach:

```bash
# 1. Try automated extraction
python extract_dd_auto.py

# 2. If some boards fail, use manual form for those
# http://localhost:8000/dd_input.html

# 3. Fill in only the failed boards
# (Much faster than doing all manually)
```

**Time: ~15-30 minutes**

---

## Questions?

### Where do I find DD values for a board?

**Option 1**: Use BBO directly
- Go to https://bridgebase.com
- Use hand viewer (Hands menu → View Hands)
- Look for "Double Dummy" table

**Option 2**: Use online bridge solver
- https://www.dealmaster.com (advanced)
- Enter all four hands
- Run solver

**Option 3**: Use local bridge software
- GIB (GUI Bridge Interface)
- Dealer software
- Other bridge analysis tools

### Can I edit values after saving?

**Manual form**: Yes, just click the board again and update values

**Automated extraction**: Yes, manually edit with the form

Both methods preserve existing values - you can update incrementally.

### What if I stop halfway through?

Progress is saved automatically. Just open the form again and continue from where you left off. Green ✓ buttons show completed boards.

### How do I check my server is running?

```bash
# Should return JSON data
curl http://localhost:8000/hands_database.json

# Or open in browser
http://localhost:8000/hands_viewer.html
```

---

## Next Steps

1. **Choose your method** (Automated or Manual)
2. **Follow the instructions** for your chosen method
3. **Verify the results** in the hands viewer
4. **Deploy or share** the final application

**Happy bridging!** 🌉

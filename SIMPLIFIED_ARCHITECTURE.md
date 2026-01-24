# Simplified Pipeline Architecture

## Key Insight: Vulnerability is PRESET Information

**Vulnerability is NOT a variable property** - it's completely deterministic based on board number.

- **Boards 1, 5, 9, 13, 17, 21, 25, 29...**: None (Gray)
- **Boards 2, 6, 10, 14, 18, 22, 26, 30...**: NS (Red)
- **Boards 3, 7, 11, 15, 19, 23, 27, 31...**: EW (Teal)
- **Boards 4, 8, 12, 16, 20, 24, 28, 32...**: Both (Gold)

*Pattern repeats every 32 boards*

---

## Pipeline: 4 Simple Steps (No Vulnerability Update Needed)

```
STEP 1: FETCH (5 min)
  └─ Get 720 hands from 24 events
  └─ Save to hands_database.json with placeholder dates

STEP 2: DATES (10 min)
  └─ Extract actual event dates from eventresults.php
  └─ Update all hands with correct dates

STEP 3: LIN STRINGS (2 min)
  └─ Generate BBO LIN format for each hand
  └─ Calculate vulnerability on-the-fly from board number
  └─ Create viewer URLs

STEP 4: DOUBLE DUMMY ANALYSIS (30-45 min)
  └─ Run DD solver on all hands
  └─ Add optimum contracts and LoTT data
```

---

## Code Architecture

### `vulnerability.py` - Utility Module
```python
def get_vulnerability_by_board(board_num):
    """Preset mapping - always returns same vulnerability for board"""
    return {'1':'None', '2':'NS', '3':'EW', '4':'Both', ...}

def get_vulnerability_color(vulnerability):
    """Return CSS color for display"""
    return {'None':'#999', 'NS':'#ff6b6b', 'EW':'#4ecdc4', 'Both':'#ffd700'}
```

**Used by:**
- `complete_pipeline.py` - Calculate when generating LIN strings
- `card_placement.js` - Calculate when rendering hand diagrams

### `complete_pipeline.py` - Main Pipeline
- Imports `get_vulnerability_by_board` from `vulnerability.py`
- In `generate_lin_strings()`: 
  ```python
  vuln = get_vulnerability_by_board(board_num)  # Calculate fresh
  ```

### `card_placement.js` - Display Layer
- Includes `getVulnerabilityByBoard()` function (JavaScript port)
- In `renderHandDiagram()`:
  ```javascript
  const vul = getVulnerabilityByBoard(boardNum);  // Calculate fresh
  const vulColor = getVulnerabilityColor(vul);
  ```

### `hands_database.json` - Database
- **Does NOT store vulnerability field** (unnecessary redundancy)
- Only stores: event_id, board, date, N/S/E/W, dealer, lin_string, bbo_url, dd_result, optimum, lott
- Vulnerability calculated on-demand when needed

---

## Advantages of This Approach

✅ **No redundant data** - Vulnerability never changes, why store it?  
✅ **Single source of truth** - `get_vulnerability_by_board()` function  
✅ **Faster operations** - Skip the intermediate "fix" step  
✅ **Smaller database** - Fewer fields = smaller JSON  
✅ **Consistent** - Every hand always gets correct vulnerability (no update bugs)  
✅ **Future-proof** - If adding new hands, vulnerability is automatic  

---

## Command to Run Pipeline

```bash
python complete_pipeline.py
```

This will:
1. Fetch all hands from calendar
2. Extract and update event dates
3. Generate LIN (with vulnerability calculated from board)
4. Run DD analysis
5. Verify database

**Total Time:** ~50 minutes

---

## Example: How Vulnerability Works

### When Generating LIN (Step 3)
```python
for hand in hands:
    board_num = hand['board']
    vuln = get_vulnerability_by_board(board_num)  # Returns 'None', 'NS', 'EW', or 'Both'
    lin = generate_bbo_lin(hand, dealer, vuln)    # Use it
```

### When Rendering Display
```javascript
function renderHandDiagram(handData, boardNum, ...) {
    const vul = getVulnerabilityByBoard(boardNum);  // Calculate fresh
    const color = getVulnerabilityColor(vul);       // Get display color
    // Display vulnerability with correct color
}
```

### When Viewing Grid
Navigate to: `http://localhost:5000/hands_in_grid.html?date=24.01.2026`

Each hand shows:
- Board number (determines vulnerability)
- Vulnerability color (calculated from board)
- All 4 hands, dealer position
- LIN viewer link
- DD analysis (if available)

---

## Key Files

| File | Purpose | Stored Vulnerability? |
|------|---------|----------------------|
| `vulnerability.py` | Utility module with preset mapping | N/A (code, not data) |
| `complete_pipeline.py` | Main pipeline orchestration | Calculates on Step 3 |
| `card_placement.js` | Display rendering | Calculates on render |
| `hands_database.json` | Hand data persistence | **NO** (not needed) |

---

## Migration From Old System

**Old:** Store vulnerability in database + Step 2.5 to "fix" it  
**New:** Calculate vulnerability on-demand from board number

**Existing data:** Already has vulnerability field, safe to ignore  
**New hands:** Will not have vulnerability field, but it's calculated anyway

---

## Future Updates

When running `python complete_pipeline.py` again:
- New hands will be fetched with placeholder dates
- Dates will be extracted and updated
- LIN will be generated with correct vulnerability (calculated fresh)
- DD analysis will run
- No separate "fix" step needed

**Vulnerability is always correct automatically.**


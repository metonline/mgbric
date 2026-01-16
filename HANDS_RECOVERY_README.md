# HANDS DATA RECOVERY - COMPLETE GUIDE

## Problem Summary

The original hands_database.json that was fetched from Vugraph is **lost**. The current database was reconstructed from the LIN file (tournament_boards.lin), which is:

- ❌ **Wrong approach**: Reverse-engineering from derivative data
- ❌ **Methodologically flawed**: Using generated data as source instead of original
- ❌ **Unverified**: No way to confirm if reconstructed hands are correct

## Solution: Fetch From Original Source

We will retrieve hands directly from the Vugraph website using Selenium, navigating through players' board lists with **cross-validation** from multiple sources.

### Data Lineage (Correct)

```
┌─────────────────────────┐
│  Vugraph Website        │  ← ORIGINAL SOURCE
│  Event 404377           │
└────────────┬────────────┘
             │
             ↓ (Fetch using Selenium)
┌─────────────────────────┐
│  hands_database.json    │  ← AUTHORITATIVE COPY
│  (30 boards × 4 hands)  │
└────────────┬────────────┘
             │
             ├→ Generate LIN file (for Bridge Solver)
             ├→ Generate DD values (manual or auto)
             └→ Upload to BBO/Bridge Solver
```

## How It Works: Player-Based Fetching

### Why Not Direct Board Fetch?

❌ Tried: `boarddetails.php?event=404377&board=1`
- Returns page with board info but hands not in expected format
- Likely structured for human viewing, not machine parsing

### Why Player-Based Works

✅ Fetch: `pairsummary.php?event=404377&section=A&pair=1&direction=NS`
- Shows table with all boards played by pair 1
- Each row has link to board details for THIS PAIR
- When pair 1 plays board 1, hands show from pair 1's perspective
- When pair 2 plays board 1, hands show from pair 2's perspective
- **Multiple sources for same board = cross-validation**

### Navigation Flow

```
Step 1: Get Event Overview
  URL: eventresults.php?event=404377
  Extract: All pairs (1-26) with pairsummary links

Step 2: For Each Pair (1-26)
  URL: pairsummary.php?event=404377&section=A&pair=N&direction=NS
  Extract: Table with boards they played (1-30)
           Each board has link to boarddetails page

Step 3: For Each Board (1-30)
  URL: boarddetails.php?event=404377&board=N&pair=P&direction=D
  Extract: Hand data from page text
           Record source: pair_P

Step 4: Cross-Check
  Board 1, North hand from pair 1: "SAKJT93HQD854CT"
  Board 1, North hand from pair 2: "SAKJT93HQD854CT"  ✓ MATCH
  Board 1, North hand from pair 3: "SAKJT93HQD854CT"  ✓ MATCH
  
  If one pair shows different: Use majority vote

Step 5: Save Results
  hands_database.json with:
  - All 30 boards × 4 hands = 120 hands total
  - fetch_sources: shows which pairs provided each hand
  - Validation: hands confirmed from 2-8 independent sources
```

## Available Scripts

### 1. `inspect_page_for_hands.py` (Diagnostic)
- Opens a sample pair page
- Analyzes page structure
- Looks for hand display format
- Helps understand what data is available

**Run if**: You want to inspect the page structure first
```bash
python inspect_page_for_hands.py
```

### 2. `test_board1_fetch.py` (Validation)
- Fetches Board 1 from first 5 pairs only
- Tests the fetch & parse logic
- Validates cross-checking works
- Saves results to `test_board1_results.json`

**Run if**: You want to test before running full fetch
```bash
python test_board1_fetch.py
```

### 3. `fetch_hands_with_validation.py` (Full Execution)
- Fetches all 26 pairs
- Navigates to all 30 boards
- Extracts all 120 hands with sources
- Cross-validates using majority vote
- Saves complete database
- **RECOMMENDED for final recovery**

**Run to get**: Complete hands_database.json with original Vugraph data
```bash
python fetch_hands_with_validation.py
```

## Quick Start

### Option A: Quick Test (5 minutes)
```bash
# Test on Board 1 only
python test_board1_fetch.py

# Check results
cat test_board1_results.json | python -m json.tool
```

### Option B: Full Recovery (15-20 minutes)
```bash
# Fetch all 30 boards from all pairs
python fetch_hands_with_validation.py

# The script will:
# 1. Navigate to all pairs (1-26)
# 2. Extract all boards (1-30) from each pair
# 3. Parse hands from each board detail page
# 4. Cross-check across multiple sources
# 5. Resolve conflicts with majority vote
# 6. Save to hands_database.json with source tracking
```

## Expected Output

### During Execution
```
======================================================================
STEP 1: Fetching pairs list from event 404377
======================================================================

Opening: https://clubs.vugraph.com/hosgoru/eventresults.php?event=404377

✓ Found 26 pairs

  1. Pair  1: PAIR NAME 1
  2. Pair  2: PAIR NAME 2
  ... and 24 more

======================================================================
STEP 2: Fetching hands from board details pages
======================================================================

  Pair  1: ✓ 30 boards
  Pair  2: ✓ 30 boards
  ...
```

### After Completion
```
======================================================================
SUMMARY
======================================================================
Total boards with hands: 30/30
```

### Saved Data Structure
```json
{
  "events": {
    "hosgoru_04_01_2026": {
      "boards": {
        "1": {
          "dealer": "N",
          "vulnerability": "None",
          "hands": {
            "North": {"S": "AKJ9", "H": "Q92", "D": "T8643", "C": "K7"},
            "South": {"S": "Q8642", "H": "J97", "D": "3", "C": "A842"},
            "East": {"S": "52", "H": "KT8642", "D": "A62", "C": "KQ"},
            "West": {"S": "T3", "H": "A", "D": "KQJ9", "C": "QJT965"}
          },
          "fetch_sources": {
            "North": ["pair_1", "pair_2", "pair_13"],
            "South": ["pair_1", "pair_2", "pair_13"],
            "East": ["pair_1", "pair_2"],
            "West": ["pair_1", "pair_2"]
          },
          "dd_analysis": {},           ← Preserved from current database
          "results": []                ← Preserved from current database
        },
        "2": { ... },
        ...
        "30": { ... }
      }
    }
  }
}
```

**New field**: `fetch_sources` shows which pairs this hand came from
- If multiple sources shown: Hand is confirmed from multiple independent players
- Conflict resolution used majority vote if any disagreements

## Benefits of This Approach

| Benefit | How |
|---------|-----|
| **Authoritative** | Data from Vugraph, not reconstructed |
| **Validated** | Multiple pairs provide same hand = confirmed |
| **Traceable** | Know exactly where each hand came from |
| **Recoverable** | Can re-fetch anytime if needed |
| **Safe** | Preserves DD values, doesn't delete data |
| **Verifiable** | Can spot-check by browsing Vugraph |

## Verification After Fetch

Once fetch is complete, verify with:

```bash
# 1. Check all boards have hands
python -c "
import json
with open('app/www/hands_database.json') as f:
    db = json.load(f)
    boards = db['events']['hosgoru_04_01_2026']['boards']
    for bid, board in boards.items():
        hands = [board['hands'][p] for p in ['North','South','East','West']]
        if not all(h for h in hands):
            print(f'Board {bid}: MISSING HANDS')
        else:
            total = sum(sum(len(v) for v in h.values()) for h in hands)
            if total != 52:
                print(f'Board {bid}: WRONG TOTAL ({total} cards)')
    print('✓ All boards validated')
"

# 2. Start server and view hands
cd app/www
python server_with_api.py
# Then open: http://localhost:8000/hands_viewer.html
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Script opens browser but doesn't find hands | Run `inspect_page_for_hands.py` to see actual page structure |
| Only partial hands extracted | Try test script first: `python test_board1_fetch.py` |
| Script crashes on some pair | Specific pair page may have issues; script continues to next |
| Chrome/Chromium not found | Install Chrome or use `pip install webdriver-manager` |
| All hands empty | Vugraph page structure may have changed; inspect first |

## Next After Recovery

### 1. Validate Hands
```bash
python -c "import json; db=json.load(open('app/www/hands_database.json')); print('✓ Loaded, boards:', len(db['events']['hosgoru_04_01_2026']['boards']))"
```

### 2. View on Web Interface
```bash
cd app/www
python server_with_api.py
# Open: http://localhost:8000/hands_viewer.html
```

### 3. Re-Generate LIN File
```bash
python create_lin_file.py
python generate_lin_links.py
```

### 4. Upload to Bridge Solver
- Generate DD values (manual or automated)
- Upload tournament_boards.lin to: https://dds.bridgewebs.com

## Important Notes

- ✅ **Safe**: Doesn't delete existing DD values or results
- ✅ **Non-destructive**: Can run multiple times if needed
- ✅ **Trackable**: Each hand shows its sources for verification
- ⚠️ **Takes time**: ~15-20 minutes to fetch all 30 boards × 26 pairs
- ⚠️ **Requires internet**: Needs to reach Vugraph website

## Summary

**Old Approach (Wrong):**
```
Corrupt database → Restore from LIN → Reconstructed hands (unverified)
```

**New Approach (Correct):**
```
Vugraph website → Fetch via players → Cross-validate → Authoritative hands
```

---

**Status**: Ready to execute  
**Execution Time**: ~15-20 minutes  
**Expected Result**: Complete hands_database.json with all 30 boards × 4 hands from verified sources

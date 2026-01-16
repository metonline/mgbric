# Hands Data Recovery: Player-Based Fetching Strategy

## Overview

You identified a critical issue: the current database was reconstructed from the LIN file (which is derivative), rather than from the original Vugraph-fetched hands data. The LIN file was created FROM the original hands, not the other way around.

**Data Lineage:**
```
Original Source:     Vugraph Website
                           ↓
Phase 1 (Working):   hands_database.json (original - NOW LOST)
                           ↓
Phase 2 (Working):   tournament_boards.lin (created from hands)
                           ↓
Phase 3 (Wrong):     hands_database.json (reverse-engineered from LIN - CURRENT)
```

## The Solution: Fetch From Original Source

Instead of trying to reconstruct from LIN, we go back to the Vugraph website and fetch hands directly using Selenium, walking through the players' data.

### Why This Works Better

1. **Authoritative Source**: Data comes directly from Vugraph, not reverse-engineered
2. **Cross-Validation**: Multiple pairs played the same boards → multiple sources for same hand
3. **Source Tracking**: We know exactly where each hand came from
4. **Conflict Resolution**: If sources disagree, use majority vote

### Key Strategy: Navigate Through Players

Instead of trying to fetch from board summary pages (which don't expose hands), we:

1. **Get Players List** → Navigate to event overview
2. **For Each Player** → Get their pair summary (shows which boards they played)
3. **For Each Board They Played** → Navigate to board details page
4. **Extract Hands** → Parse from displayed text
5. **Cross-Check** → Same player's hand should be identical when fetched from different pairs

### Example Navigation

```
1. Fetch: eventresults.php?event=404377
   ↓ Extract pair links
   
2. Fetch: pairsummary.php?event=404377&section=A&pair=1&direction=NS
   ↓ Shows table: [Board 1] [Opponent] [Result] [Score]
   ↓ Extract board links
   
3. Fetch: boarddetails.php?event=404377&board=1&pair=1&direction=NS
   ↓ Parse hands from page text
   ↓ North hand from this pair's perspective
   
4. Cross-check: Fetch same board from another pair that played it
   Fetch: boarddetails.php?event=404377&board=1&pair=2&direction=NS
   ↓ Should show same North hand
   ↓ If different, flag as conflict
```

## Implementation: `fetch_hands_with_validation.py`

This script implements the full strategy:

### Step 1: Get Pairs List
- Opens event overview page
- Extracts all pairsummary links
- Identifies unique pairs (1-26)

### Step 2: Fetch Hands for Each Pair
- For each pair → gets their pair summary page
- Extracts all boards they played
- For each board → navigates to board details
- Extracts hands from page text
- Records source attribution

### Step 3: Cross-Check & Resolve
- Groups hands by value
- Detects conflicts (multiple different hands for same player)
- Uses majority vote to resolve
- Marks data with source provenance

### Step 4: Save Results
- Updates `hands_database.json` with fetched hands
- Includes `fetch_sources` field showing where each hand came from
- Preserves existing DD values and other data

## Running the Script

```bash
cd "c:\Users\metin\Desktop\BRIC"
python fetch_hands_with_validation.py
```

**What to Expect:**

```
======================================================================
STEP 1: Fetching pairs list from event 404377
======================================================================

Opening: https://clubs.vugraph.com/hosgoru/eventresults.php?event=404377

✓ Found 26 pairs

  1. Pair  1: PAIR NAME
  2. Pair  2: PAIR NAME
  ... and 24 more

======================================================================
STEP 2: Fetching hands from board details pages
======================================================================

  Pair  1: ✓ 30 boards
  Pair  2: ✓ 30 boards
  ...

======================================================================
STEP 3: Resolving conflicts via cross-check
======================================================================

Board  1 N: 3 variants from 8 sources
✓ Resolved: 95
⚠ Conflicts: 5

======================================================================
STEP 4: Saving to hands_database.json
======================================================================

✓ Updated 30 boards
✓ Saved to app/www/hands_database.json

======================================================================
SUMMARY
======================================================================
Total boards with hands: 30/30
```

## Data Structure After Fetch

```json
{
  "events": {
    "hosgoru_04_01_2026": {
      "boards": {
        "1": {
          "dealer": "N",
          "vulnerability": "None",
          "hands": {
            "North": {
              "S": "AKJ9",
              "H": "Q92",
              "D": "T8643",
              "C": "K7"
            },
            "South": {...},
            "East": {...},
            "West": {...}
          },
          "fetch_sources": {
            "North": ["pair_1", "pair_2", "pair_13"],
            "South": ["pair_1", "pair_2"],
            "East": ["pair_1"],
            "West": ["pair_1"]
          },
          "dd_analysis": {...},  ← Preserved from before
          "results": {...}        ← Preserved from before
        }
      }
    }
  }
}
```

## Advantages

1. ✅ **Original Source**: From Vugraph, not reverse-engineered
2. ✅ **Validated**: Multiple sources per hand confirm accuracy
3. ✅ **Tracked**: Know exactly where data came from
4. ✅ **Recoverable**: Can re-run at any time if needed
5. ✅ **Cross-Checkable**: Hands from different pairs should match
6. ✅ **Preserves**: DD values and results stay intact

## Potential Issues & Solutions

| Issue | Solution |
|-------|----------|
| Hand format varies on page | Multiple parsing strategies (text nodes, tables, script data) |
| Some pairs didn't play all boards | Only extract from pairs that played that board |
| Hand display might be in different language/format | Use suit symbols and card patterns |
| Website structure changed | Selenium can find elements dynamically |
| Script times out | Runs per-board, can be restarted from any point |

## Validation Checklist

After running the script:

- [ ] 30 boards have hands extracted
- [ ] Each hand has 13 cards (4 suits, sum to 13)
- [ ] No hand has duplicate cards
- [ ] Total 52 cards per board
- [ ] fetch_sources shows where each hand came from
- [ ] Hands match between different source pairs
- [ ] DD values still present and unchanged
- [ ] Can run web interface and see hands displayed

## Next Steps

1. **Run the fetcher**: `python fetch_hands_with_validation.py`
2. **Verify output**: Check that all 30 boards have hands
3. **Validate data**: Run validation script to confirm card totals
4. **Test UI**: Start server and view hands on web interface
5. **Generate LIN**: Create new LIN file from validated hands
6. **Upload to Bridge Solver**: Use verified data for DD analysis

---

**Created**: 2025-01-06  
**Purpose**: Recover original hand data from Vugraph via player-based navigation  
**Method**: Selenium-based scraping with cross-validation  
**Status**: Ready to execute

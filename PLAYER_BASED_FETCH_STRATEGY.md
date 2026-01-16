# Player-Based Hand Fetching Strategy

## The Problem
- Board summary pages (boarddetails.php) may not contain direct hand data
- Selenium needs to navigate through multiple pages to correlate data
- Not all players played all boards (need to filter by participants)
- Data must be cross-checked across multiple sources

## The Solution: Player-Based Approach

### Step 1: Get Players List
- URL: `eventresults.php?event=404377`
- Extract all pairs: `pairsummary.php?event=404377&section=A&pair=X&direction=NS/EW`

### Step 2: For Each Player Pair
- Navigate to: `pairsummary.php?event=404377&section=A&pair=1&direction=NS`
- Extract table with columns: `Bord` | `Rakip` | `Sonuç` | `Skor`
- This gives: Board Number | Opponent | Result | Score
- Get link to board: `boarddetails.php?event=404377&board=X&pair=1&direction=NS`

### Step 3: For Each Board
- Navigate to: `boarddetails.php?event=404377&board=X&pair=1&direction=NS`
- Find hand display (may be in different formats):
  - Format A: Text nodes with "North: S:AK H:Q..." etc
  - Format B: HTML table with hand columns
  - Format C: JavaScript data with card strings

### Step 4: Cross-Check
- For Board 1, North should be:
  - Seen from Pair 1 NS page as their N
  - Seen from Pair 2 NS page as their N (if they played it)
  - Seen from Pair 13 EW page as their W  (since they sit opposite)
  - All sources should show identical cards

### Step 5: Resolve & Save
- Use majority vote if conflicts
- Mark sources for each hand
- Save with provenance data

## Implementation Steps

1. Create `fetch_hands_with_validation.py`
   - Navigate pairs → boards → hands
   - Store with source tracking
   - Cross-reference validation
   - Save with multi-source confirmation

2. For each board, expect to see:
   - Dealer position (N/E/S/W)
   - Vulnerability status
   - Four hands (N/S/E/W)
   - One or more pairs that played it

3. Validation rules:
   - All sources for same player must match
   - Hands must sum to 52 cards total
   - Each suit has exactly 13 cards per hand
   - East + West = North + South complements

## Database Structure After Fetch

```json
{
  "board": 1,
  "dealer": "N",
  "vulnerability": "None",
  "hands": {
    "North": {"S": "AK", "H": "Q", "D": "T8643", "C": "K7"},
    "South": {"S": "Q864", "H": "J97", "D": "3", "C": "A842"}
  },
  "sources": {
    "North": ["Pair_1_NS", "Pair_2_NS", "Pair_13_EW"],
    "South": ["Pair_1_NS", "Pair_2_NS", "Pair_13_EW"]
  }
}
```

## Challenges & Solutions

**Challenge 1: Some pairs didn't play all boards**
- Solution: Only extract hands from pairs that played that board
- Result: Multiple sources per hand (cross-check)

**Challenge 2: Hand display format may vary**
- Solution: Try multiple selectors/parsers
- Look for: suit symbols (S:, ♠), card values, position names

**Challenge 3: Need to validate data integrity**
- Solution: Check card totals, verify no duplicates
- Cross-check against multiple sources

**Challenge 4: Dealer and vulnerability not always shown**
- Solution: Extract from deal string or use known defaults
- Store as metadata with source

## Key URLs Pattern

```
Event overview:     eventresults.php?event=404377
Pair summary:       pairsummary.php?event=404377&section=A&pair=N&direction=NS/EW
Board results:      boarddetails.php?event=404377&board=N&pair=P&direction=D
```

## Data Lineage

```
Vugraph Website
    ↓
Fetch Players List (all pairs in event)
    ↓
For each pair → Fetch their board list
    ↓
For each board → Extract hands (multiple sources)
    ↓
Cross-check & validate
    ↓
Build hands_database.json with source tracking
```

## Next Steps

1. **Test on Sample Board**: Run fetch for Board 1 only
   - Try multiple pairs to see what hands they show
   - Compare results
   - Validate card totals

2. **Implement Validation**: Add card verification
   - 13 cards per hand
   - 4 cards per suit
   - Total 52 per board

3. **Scale to All Boards**: Loop 1-30
   - Track progress
   - Log sources
   - Save incrementally

4. **Verify Database**: Compare with known good data
   - Count boards with complete hands
   - Validate all 30 boards have all 4 hands
   - Check no duplicates/missing cards


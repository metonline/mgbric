# HANDS DATA RECOVERY - QUICK REFERENCE

## The Problem
You correctly identified that restoring hands from the LIN file is **wrong approach** because:
- LIN file is **derivative** (created FROM hands_database.json)
- Original hands_database.json from Vugraph is **LOST**
- Current database is reverse-engineered, unverified

## The Solution
Fetch hands **directly from Vugraph website** using Selenium, navigating through **players' board lists** with **cross-validation** across multiple sources.

---

## 📖 DOCUMENTATION (Read These)

### For Users - Start Here
| Document | Purpose | Time |
|-----------|---------|------|
| **HANDS_RECOVERY_README.md** | Complete user guide with examples | 10 min |
| **HANDS_RECOVERY_SUMMARY.txt** | What was created and why | 5 min |
| **PLAYER_BASED_FETCH_STRATEGY.md** | Architecture and flow diagrams | 5 min |

### For Reference
| Document | Purpose |
|-----------|---------|
| HANDS_RECOVERY_STRATEGY.md | Technical deep-dive on strategy |
| This file | Quick reference and command guide |

---

## 🎯 SCRIPTS (Run These)

### Phase 1: Quick Test (5 minutes)
```bash
python test_board1_fetch.py
```
- Fetches Board 1 from first 5 pairs only
- Validates the approach works
- Saves results to: `test_board1_results.json`
- **Result**: Confirms if we can extract hands

### Phase 2: Full Recovery (15-20 minutes)
```bash
python fetch_hands_with_validation.py
```
- Fetches all 26 pairs
- Navigates to all 30 boards
- Extracts all 120 hands
- Cross-validates across sources
- Updates: `app/www/hands_database.json`
- **Result**: Complete recovered database with verified hands

### Phase 3: Diagnostic (If needed)
```bash
python inspect_page_for_hands.py
```
- Analyzes Vugraph page structure
- Shows what data is available
- Helps debug if fetch isn't working
- **When to use**: If fetch script fails

---

## 🚀 QUICK START (Choose One)

### Option A: Test First (Safe)
```bash
# 1. Read the strategy
cat HANDS_RECOVERY_README.md

# 2. Test Board 1 only
python test_board1_fetch.py

# 3. If successful, run full fetch
python fetch_hands_with_validation.py

# 4. Verify
python -c "import json; d=json.load(open('app/www/hands_database.json')); b=d['events']['hosgoru_04_01_2026']['boards']; print(f'Complete: {sum(1 for x in b.values() if all(x[\"hands\"][p] for p in [\"North\",\"South\",\"East\",\"West\"]))}/{len(b)}')"
```

### Option B: Direct Fetch (Faster)
```bash
# 1. Read the guide
cat HANDS_RECOVERY_README.md

# 2. Go directly to full fetch
python fetch_hands_with_validation.py

# 3. Check results in web interface
cd app/www && python server_with_api.py
# Open: http://localhost:8000/hands_viewer.html
```

---

## 📊 EXPECTED OUTPUT

### Test Script Output
```
✓ Found 5 pairs
✓ Extracted from 5 pairs
  N: "SAKJT93HQD854CT" (from pair_1, pair_2, pair_3)
  S: "SQ864HJ97DT3CA842" (from pair_1, pair_2)
  E: "S52HKT8642DA62CKQ" (from pair_1)
  W: ... (from pair_1, pair_2, pair_13)
```

### Full Fetch Output
```
======================================================================
STEP 1: Fetching pairs list from event 404377
======================================================================
✓ Found 26 pairs

======================================================================
STEP 2: Fetching hands from board details pages
======================================================================
  Pair  1: ✓ 30 boards
  Pair  2: ✓ 30 boards
  ...
  Pair 26: ✓ 30 boards

======================================================================
STEP 3: Resolving conflicts via cross-check
======================================================================
✓ Resolved: 120
⚠ Conflicts: 0

======================================================================
STEP 4: Saving to hands_database.json
======================================================================
✓ Updated 30 boards

======================================================================
SUMMARY
======================================================================
Total boards with hands: 30/30
```

---

## 🔍 VERIFY AFTER RECOVERY

```bash
# Check all boards have hands
python -c "
import json
with open('app/www/hands_database.json') as f:
    db = json.load(f)
    boards = db['events']['hosgoru_04_01_2026']['boards']
    
    # Count complete boards
    complete = 0
    for bid, board in boards.items():
        hands = [board['hands'][p] for p in ['North','South','East','West']]
        if all(h and any(h.values()) for h in hands):
            complete += 1
    
    print(f'✓ Complete boards: {complete}/{len(boards)}')
    print(f'✓ Hands recovered: {complete * 4} / 120')
"

# View hands on web
cd app/www
python server_with_api.py
# → Open: http://localhost:8000/hands_viewer.html
```

---

## 📱 NEXT STEPS (After Recovery)

Once hands are recovered and verified:

1. **View Data**
   ```bash
   cd app/www && python server_with_api.py
   ```

2. **Re-Generate LIN**
   ```bash
   python create_lin_file.py      # Create LIN from verified hands
   python generate_lin_links.py   # Generate BridgeBase links
   ```

3. **Add DD Values**
   - Manual entry via web form: http://localhost:8000/dd_input.html
   - Auto-fetch from BBO: `python extract_dd_from_bbo.py`

4. **Upload to Bridge Solver**
   - Site: https://dds.bridgewebs.com
   - File: `app/www/tournament_boards.lin`
   - Include DD values for all 30 boards

---

## ⚙️ HOW IT WORKS

### Data Flow
```
Vugraph Website (Event 404377)
    ↓
[1] Get pairs list (eventresults.php)
    ↓
[2] For each pair → Get their board list (pairsummary.php)
    ↓
[3] For each board → Get hands (boarddetails.php)
    ↓
[4] Cross-check: Same player's hand should match across pairs
    ↓
[5] Save with source attribution
    ↓
hands_database.json (complete with metadata)
```

### Why Multiple Sources Work
- **Board 1** is played by 26 pairs (NS and EW directions)
- **Pair 1 NS** sees Board 1 from their position
- **Pair 2 NS** sees Board 1 from their position (same hands)
- **Pair 13 EW** sees Board 1 from their position (East=West, North=North)
- If all sources show same hands → Confirmed valid
- If sources disagree → Use majority vote

---

## 🛠️ TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| Test script finds no hands | Run `python inspect_page_for_hands.py` to diagnose page structure |
| Fetch script crashes | Check Chrome/Chromium installed: `pip install webdriver-manager` |
| Partial hands extracted | Continue anyway, some pairs may not have played all boards |
| Low confidence in hands | Cross-check sources: open Vugraph directly and compare |
| Need to re-run fetch | Just run again - script won't duplicate, will overwrite |

---

## 📋 CHECKLIST

- [ ] Read HANDS_RECOVERY_README.md
- [ ] Run test_board1_fetch.py and check results
- [ ] Run fetch_hands_with_validation.py (wait 15-20 minutes)
- [ ] Verify: All 30 boards have hands
- [ ] Verify: Each hand has 13 cards
- [ ] View on web: http://localhost:8000/hands_viewer.html
- [ ] Regenerate LIN: python create_lin_file.py
- [ ] Add DD values to all boards
- [ ] Upload to Bridge Solver

---

## 📞 KEY COMMANDS

```bash
# Read guides
cat HANDS_RECOVERY_README.md
cat HANDS_RECOVERY_SUMMARY.txt

# Test
python test_board1_fetch.py

# Full recovery
python fetch_hands_with_validation.py

# Verify
python check_database.py

# View
cd app/www && python server_with_api.py

# Regenerate
python create_lin_file.py
python generate_lin_links.py

# Upload
# → Go to: https://dds.bridgewebs.com
# → Upload: tournament_boards.lin
```

---

## ✅ SUCCESS INDICATORS

You're done when:
- ✅ All 30 boards have 4 hands (120 total)
- ✅ fetch_sources shows 2+ pairs per hand
- ✅ Web interface displays all hands correctly
- ✅ LIN file regenerates successfully
- ✅ Hands match Vugraph website when spot-checked

---

## 📌 IMPORTANT NOTES

- **Safe**: Doesn't delete DD values or existing data
- **Time**: 15-20 minutes for full recovery
- **Internet**: Requires connection to Vugraph website
- **Repeatable**: Can run multiple times if needed
- **Verifiable**: Source tracking shows where each hand came from
- **Authoritative**: Original data from Vugraph, not reconstructed

---

**Status**: ✅ Ready to execute

**Time Estimate**: 5-20 minutes depending on which approach you choose

**Expected Result**: Complete hands_database.json with all 30 boards × 4 hands from verified Vugraph sources

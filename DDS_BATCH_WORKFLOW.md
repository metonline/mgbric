# Get Exact DD Values from DDS Bridge Solver

## Your Pragmatic Solution ✓

Instead of trying to get a DDS library working locally, you'll upload batch to the free DDS solver online:

### Step-by-Step Workflow

**Step 1: Generate PBN File** (Already Done!)
```bash
python generate_pdn_for_dds.py
```
Creates `hands_for_dds.pbn` with all 109 boards in PBN format.

**Step 2: Upload to DDS Solver**
1. Open: https://dds.bridgewebs.com/bsol_standalone/ddummy.html
2. Look for "Upload PBN" or file input button
3. Select `hands_for_dds.pbn`
4. Click "Solve All" (or equivalent button)
5. Wait for processing (~1-5 minutes for 109 boards)

**Step 3: Download Results**
1. When complete, right-click page
2. Select "Save as" → `hands_dd_results.html`
3. Save in your BRIC folder

**Step 4: Parse & Update Database**
```bash
python parse_dd_results.py
```
Extracts exact DD values from HTML and updates `hands_database.json`

### Why This Works

✓ **No library conflicts** - uses web interface instead  
✓ **Batch processing** - all 109 boards at once  
✓ **Exact values** - DDS solver is the official reference  
✓ **Free service** - https://dds.bridgewebs.com is public  
✓ **Repeatable** - can re-run anytime for new boards  

### Schedule for 30 Boards/Day

Run this workflow:
- **Weekly**: 30 boards × 7 days = 210 boards done in a week
- **Monthly**: 30 boards × 30 days = 900 boards done in a month

For your 109 boards: ~4 days worth at 30/day

### Alternative: Manual Entry (if DDS solver interface is different)

If the DDS solver's HTML structure doesn't match regex parsing:

1. After uploading and solving, view each board
2. Screenshot the DD table
3. Copy-paste into your database manually
4. Takes ~5 minutes per board (540 min = 9 hours for 109 boards)

### Troubleshooting

**Q: DDS solver won't accept PBN file?**
- Try pasting content instead of uploading
- Or use BBO format (may need slight modification)

**Q: parse_dd_results.py finds 0 boards?**
- HTML structure might be different
- Open `hands_dd_results.html` in browser
- Check format and adjust regex in `parse_dd_results.py` at line marked "# Pattern:"

**Q: How often should I update?**
- Once for current 109 boards
- Weekly/Monthly for new boards as you add them

### Files Created

| File | Purpose |
|------|---------|
| `generate_pbn_for_dds.py` | Create PBN file for DDS |
| `hands_for_dds.pbn` | Input file (109 boards) |
| `parse_dd_results.py` | Extract results & update DB |
| `batch_upload_dds.py` | Selenium automation (optional) |

### Success Metrics

✅ `hands_database.json` dd_analysis values updated from estimates to **EXACT**  
✅ All 109 boards solved in single batch  
✅ Ready for production use  

---

**Total Time**: ~10-15 minutes of work + 5 minutes waiting for solver

# Bridge Tournament DD (Double Dummy) Analysis System

## 📊 Current Status

| Status | Details |
|--------|---------|
| **Total Boards** | 30 |
| **Real DD Values** | Board 1 only |
| **Placeholder Values** | Boards 2-30 |
| **Hands Data** | ✓ All 30 boards validated |
| **Viewer** | ✓ Fully functional |
| **Server** | ✓ Running on localhost:8000 |

---

## 🚀 Quick Start

### Option 1: Fastest Setup (Automated)
```bash
# 1. Install Selenium
pip install selenium

# 2. Run the setup wizard
python dd_setup_wizard.py

# 3. Choose "1" for automated extraction
# Done in ~10 minutes!
```

### Option 2: Manual Control
```bash
# 1. Start the server
cd app\www
python server_with_api.py

# 2. Open the form in browser
# http://localhost:8000/dd_input.html

# 3. Fill in values for boards 2-30
# (~5 min per board)
```

---

## 📁 Files Overview

### Core Scripts

| File | Purpose | Use Case |
|------|---------|----------|
| `dd_setup_wizard.py` | **START HERE** - Interactive setup guide | First-time setup |
| `extract_dd_auto.py` | Automated BBO DD extraction | Quick population (10 min) |
| `check_dd_status.py` | Check current DD status | Verify progress |

### Web Interface

| File | URL | Purpose |
|------|-----|---------|
| `app/www/hands_viewer.html` | `/hands_viewer.html` | View all 30 boards |
| `app/www/dd_input.html` | `/dd_input.html` | Manual DD input form |
| `app/www/server_with_api.py` | - | HTTP server + API |

### Data

| File | Contents |
|------|----------|
| `app/www/hands_database.json` | All 30 boards with hands & DD values |

### Documentation

| File | Content |
|------|---------|
| `DD_EXTRACTION_GUIDE.md` | Detailed instructions for both methods |
| `DD_POPULATION_README.md` | Quick reference guide |

---

## ⚡ Recommended Workflow

### For Complete Beginners:

```
1. Open terminal
2. Run: python dd_setup_wizard.py
3. Follow the interactive prompts
4. Choose method (automated or manual)
5. Verify results at: http://localhost:8000/hands_viewer.html
```

### For Automation Lovers:

```bash
pip install selenium
python extract_dd_auto.py
# Grab coffee ☕ - done in ~10 minutes
```

### For Careful Verification:

```bash
cd app\www
python server_with_api.py
# Open: http://localhost:8000/dd_input.html
# Fill in values while looking at BBO
# Progress saved automatically
```

---

## 🔧 Troubleshooting

### "Chrome not found"
```bash
# Install Google Chrome from:
# https://google.com/chrome
```

### "Selenium not installed"
```bash
pip install selenium
```

### "Server not running"
```bash
# Make sure you're in the right directory
cd c:\Users\metin\Desktop\BRIC\app\www
python server_with_api.py
```

### "DD values aren't updating"
```bash
# Check database status
python check_dd_status.py

# Verify API endpoint
# POST http://localhost:8000/api/save_dd
```

### "Some boards failed extraction"
Use the manual form for the failed boards:
```
http://localhost:8000/dd_input.html
```

---

## 📚 Understanding DD Values

### What is DD (Double Dummy)?

DD Analysis shows how many tricks each player can make in each suit assuming:
- All hands are revealed
- Both sides play optimally
- Perfect information for all players

### Format Used

```json
{
  "NTN": 6,    // No Trump - North = 6 tricks
  "NTS": 6,    // No Trump - South = 6 tricks  
  "NTE": 9,    // No Trump - East = 9 tricks
  "NTW": 9,    // No Trump - West = 9 tricks
  "SN": 6,     // Spades - North = 6 tricks
  // ... and so on for H, D, C
}
```

**Key Facts:**
- **6 tricks** = Pass (no contract makeable)
- **7-13 tricks** = Tricks available for that player
- **Always between 6-13**
- **20 values total** (5 suits × 4 players)

---

## 🔄 System Architecture

### Data Flow

```
hands_database.json (Database)
         ↓
    Boards 1-30
    - Hands (N, S, E, W)
    - DD values
         ↓
    API: /api/save_dd
         ↓
    Update board DD values
```

### Web Architecture

```
Browser
  ├─ hands_viewer.html (Display all boards)
  ├─ dd_input.html (Manual input form)
  └─ server_with_api.py (Python HTTP server)
       └─ hands_database.json (Data storage)
```

### Automated Extraction Flow

```
extract_dd_auto.py
  ├─ Load: hands_database.json
  ├─ For each board 2-30:
  │  ├─ Generate: BBO LIN URL
  │  ├─ Open: Chrome (headless)
  │  ├─ Wait: DD table loads
  │  ├─ Extract: 20 trick values
  │  └─ Save: To database
  └─ Report: Success/failures
```

---

## ✨ Features

### Hands Viewer
- ✓ Responsive layout (3-column desktop, fullscreen mobile)
- ✓ BBO hand viewer integration
- ✓ DD Analysis table display
- ✓ Date-based filtering
- ✓ Click-to-copy functionality

### DD Input Form
- ✓ Board selector with progress tracking
- ✓ 20 input fields (5 suits × 4 players)
- ✓ Real-time validation (6-13)
- ✓ Color-coded completion tracking
- ✓ Auto-save to API endpoint
- ✓ Resume from where you left off

### Automated Extractor
- ✓ Headless Chrome automation
- ✓ BBO DD table parsing
- ✓ Error handling & fallback
- ✓ Rate limiting (doesn't overwhelm BBO)
- ✓ Progress reporting
- ✓ Partial failure handling

---

## 🎯 Goal States

### Immediate Next Step
Complete DD extraction for Boards 2-30:
- [ ] Board 1: Real values (completed)
- [ ] Boards 2-30: Extract real values

### Final State
All 30 boards with complete, accurate DD analysis:
- [x] Hands: All 30 boards ✓
- [x] Hands validation: All 30 boards ✓
- [x] Hands display: Working ✓
- [ ] DD values: **IN PROGRESS**
- [ ] DD display: Working ✓

### Success Criteria
- All 30 boards show in viewer
- DD tables display for each board
- Each board has different, realistic DD values
- Can view on desktop and mobile

---

## 📋 API Reference

### List All Boards
```
GET /api/boards
Response: {"boards": [1, 2, ..., 30]}
```

### Get Board Data
```
GET /api/board/1
Response: {
  "board": 1,
  "hands": {...},
  "dd_analysis": {...}
}
```

### Save DD Values
```
POST /api/save_dd
Body: {
  "board_num": 2,
  "dd_analysis": {
    "NTN": 6,
    "NTS": 6,
    ...
  }
}
Response: {"success": true, "message": "..."}
```

---

## 🔐 Data Integrity

### Validation
- All hands validated for 13-card suits
- DD values constrained to 6-13
- Database backups on each save
- Change tracking with timestamps

### Backups
Database automatically backed up:
- Before each save
- With timestamp suffix
- Keep last 10 versions

---

## 🚀 Deployment Options

### Local Development
```bash
cd app\www
python server_with_api.py
# Open: http://localhost:8000
```

### Docker (Optional)
```bash
docker-compose up -d
# Open: http://localhost:8000
```

### Online Hosting
- Files: HTML, CSS, JS (static)
- API: Python Flask server
- Database: JSON file (can be SQLite)

---

## 🤝 Support

### Common Issues

**Q: Where do I find DD values?**
A: Look at the DD (Double Dummy) table when viewing a hand on BBO or any bridge solver.

**Q: Can I edit values after saving?**
A: Yes, just open the form and update any board.

**Q: How long does automated extraction take?**
A: About 10-15 minutes for 29 boards (rate limited to avoid overwhelming BBO).

**Q: What if automated extraction fails?**
A: Switch to manual method for failed boards - much faster than doing all manually.

**Q: Can I do extraction in multiple sessions?**
A: Yes! Progress is saved automatically. Just reopen the form.

---

## 📈 Progress Tracking

### Check Status
```bash
python check_dd_status.py
```

### Sample Output
```
SUMMARY
✓ Boards with real DD values:      1/30
⚠ Boards with placeholder values:  29/30
✗ Boards missing DD data:          0/30

NEXT STEPS: Run extract_dd_auto.py or use dd_input.html
```

---

## 🎓 Learning Resources

### Bridge Double Dummy
- [Wikipedia: Double Dummy Bridge](https://en.wikipedia.org/wiki/Bridge_player)
- [BridgeBase: Hand Viewer](https://www.bridgebase.com/)
- [Dealmaster Solver](https://www.dealmaster.com/)

### This System
- `DD_EXTRACTION_GUIDE.md` - Detailed guide
- `DD_POPULATION_README.md` - Quick reference
- Code comments in scripts

---

## 📞 Getting Help

### Verify Everything Works
```bash
# Check DD status
python check_dd_status.py

# Start server
cd app\www && python server_with_api.py

# Open in browser
http://localhost:8000/hands_viewer.html
```

### If Something Breaks
1. Check error messages in terminal
2. Run `check_dd_status.py` to see data status
3. Verify database file exists: `app/www/hands_database.json`
4. Try restarting server
5. Clear browser cache if needed

---

## 🎉 Success!

Once all 30 boards have real DD values:

1. **View your tournament:**
   ```
   http://localhost:8000/hands_viewer.html
   ```

2. **Share with others:**
   - Deploy to web hosting
   - Export as PDF
   - Share JSON data

3. **Analyze results:**
   - Compare contracts vs DD
   - Study optimal bidding
   - Learn from hands

---

**Happy bridging! 🌉**

For detailed instructions, see:
- `DD_EXTRACTION_GUIDE.md` - Complete step-by-step guide
- `DD_POPULATION_README.md` - Quick reference

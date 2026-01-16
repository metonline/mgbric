# 🌉 BRIDGE TOURNAMENT DD EXTRACTION SYSTEM

## START HERE 👇

### If you have 2 minutes:
Read: **[QUICK_START_DD.txt](QUICK_START_DD.txt)**

### If you have 5 minutes:
Read: **[VISUAL_GUIDE_DD.md](VISUAL_GUIDE_DD.md)**

### If you want to get started NOW:
Run: **`python dd_setup_wizard.py`**

---

## 📋 COMPLETE FILE GUIDE

### 🚀 EXECUTABLE SCRIPTS (Run These)

| File | What It Does | Run With | Time |
|------|-------------|----------|------|
| **dd_setup_wizard.py** | Interactive setup guide (RECOMMENDED) | `python dd_setup_wizard.py` | 15 min |
| **extract_dd_auto.py** | Automated extraction from BBO | `python extract_dd_auto.py` | 10 min |
| **check_dd_status.py** | Check current DD status | `python check_dd_status.py` | 2 min |

---

### 📖 DOCUMENTATION (Read These)

#### Quick References
| File | Best For | Read Time |
|------|----------|-----------|
| **[QUICK_START_DD.txt](QUICK_START_DD.txt)** | Fast overview, paths A/B/C | 2 min |
| **[VISUAL_GUIDE_DD.md](VISUAL_GUIDE_DD.md)** | Flowcharts, diagrams, examples | 5 min |
| **[FILES_CREATED.md](FILES_CREATED.md)** | What was created, quick start | 3 min |

#### Detailed Guides
| File | Best For | Read Time |
|------|----------|-----------|
| **[DD_EXTRACTION_GUIDE.md](DD_EXTRACTION_GUIDE.md)** | Step-by-step instructions | 10 min |
| **[DD_POPULATION_README.md](DD_POPULATION_README.md)** | Method comparison | 5 min |
| **[README_DD_SYSTEM.md](README_DD_SYSTEM.md)** | Complete reference | 15 min |

---

### 🌐 WEB INTERFACE (Open in Browser)

| File | URL | Purpose |
|------|-----|---------|
| **dd_input.html** | `http://localhost:8000/dd_input.html` | Manual DD value input form |
| **hands_viewer.html** | `http://localhost:8000/hands_viewer.html` | View all 30 boards |

---

### 📊 DATA

| File | Purpose |
|------|---------|
| **hands_database.json** | Database with all 30 boards (in `app/www/`) |

---

## 🎯 THREE WAYS TO EXTRACT DD VALUES

### PATH A: FULLY AUTOMATED ⚡ (10 minutes)
```bash
pip install selenium
python extract_dd_auto.py
```
✓ Fastest | ✓ No manual work | ⚠ Needs Chrome

### PATH B: MANUAL WEB FORM 🔧 (2-3 hours)
```bash
cd app\www
python server_with_api.py
# Open: http://localhost:8000/dd_input.html
```
✓ Full control | ✓ Can verify | ⚠ Time consuming

### PATH C: INTERACTIVE WIZARD 🧙 (15 minutes)
```bash
python dd_setup_wizard.py
```
✓ Guided setup | ✓ Checks requirements | ✓ Best for beginners

---

## 📊 CURRENT STATUS

```
✓ Board 1:      Real DD values (done)
⚠ Boards 2-30:  Placeholder values (need extraction)

Next: Run one of the scripts above
```

---

## 🎓 WHAT IS DD?

**DD = Double Dummy Analysis**

Shows how many tricks each player can make in each suit, assuming:
- All hands are known
- Both sides play perfectly
- Perfect information

**Format for each board:**
```
5 suits (NT, S, H, D, C) × 4 players (N, S, E, W) = 20 values
Each value is 6-13 (tricks available)
```

---

## ✅ SUCCESS CHECKLIST

After running extraction, you should have:

- [x] All 30 boards load in viewer
- [x] Board 1 shows real DD values
- [x] Each board 2-30 shows different DD values
- [x] Values are realistic (6-13 tricks)
- [x] Can view on desktop and mobile
- [x] BBO hand viewer works

---

## 📞 QUICK ANSWERS

**Q: Which method should I use?**
A: Start with `python dd_setup_wizard.py` - it will guide you

**Q: How long will it take?**
A: 10 minutes (automated) to 3 hours (manual)

**Q: Do I need anything special?**
A: Just Python (you already have it)

**Q: Can I pause and resume?**
A: Manual method yes, automated method no (but it runs once)

**Q: What if it fails?**
A: Use manual form as fallback for failed boards

**Q: Where do I find DD values?**
A: They're shown in BBO hand viewer - look for "Double Dummy" table

---

## 🚀 QUICK START FLOWCHART

```
You are here ↓
    │
    ├─ Have 2 min? ──→ Read QUICK_START_DD.txt
    │
    ├─ Have 5 min? ──→ Read VISUAL_GUIDE_DD.md
    │
    ├─ Ready now? ───→ python dd_setup_wizard.py
    │
    ├─ Want auto? ───→ pip install selenium
    │                 python extract_dd_auto.py
    │
    └─ Want manual? ─→ cd app\www
                      python server_with_api.py
                      Open dd_input.html in browser
```

---

## 📈 PROGRESS TRACKING

### Check Status Anytime
```bash
python check_dd_status.py
```

### View Results
```
http://localhost:8000/hands_viewer.html
```

### Verify Database
```bash
python -c "import json; f=open('app/www/hands_database.json'); d=json.load(f); b=d['events']['hosgoru_04_01_2026']['boards']; print(f'Board 1: {list(b[\"1\"][\"dd_analysis\"].values())[:5]}'); print(f'Board 2: {list(b[\"2\"][\"dd_analysis\"].values())[:5]}')"
```

---

## 🎨 SYSTEM OVERVIEW

```
                     TOURNAMENT DATA
                     (30 Boards)
                            │
            ┌───────────────┼───────────────┐
            │               │               │
        Hands Data      DD Values        Status
         (DONE)         (YOUR TASK)     (RUNNING)
            │               │               │
            └───────────────┼───────────────┘
                            │
                    ┌─────────────────┐
                    │  Database       │
                    │ (hands_database │
                    │   .json)        │
                    └─────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
        API Endpoint    Web Forms    Hand Viewer
       (/api/save_dd)   Input HTML   Display HTML
```

---

## 🔧 SYSTEM REQUIREMENTS

### For Automated Method
- [x] Python 3.6+ (you have this)
- [x] Google Chrome or Chromium
- [ ] Selenium (install with: `pip install selenium`)
- [x] Internet connection

### For Manual Method
- [x] Python 3.6+ (you have this)
- [x] Web browser (Chrome, Firefox, Safari, Edge)
- [x] Internet connection
- [x] BBO account (free)

### For Wizard
- [x] Python 3.6+ (you have this)
- [x] That's it!

---

## 💾 DATA STRUCTURE

Each board in the database looks like:

```json
{
  "1": {
    "hands": {
      "north": {"S": "K986", "H": "AK75", "D": "A963", "C": "K2"},
      "south": {"S": "QJ7", "H": "8643", "D": "KQ8", "C": "653"},
      "east": {"S": "A5432", "H": "J92", "D": "J7", "C": "QJ7"},
      "west": {"S": "T", "H": "QT", "D": "T542", "C": "AT9864"}
    },
    "dd_analysis": {
      "NTN": 6, "NTS": 6, "NTE": 9, "NTW": 9,
      "SN": 6, "SS": 6, "SE": 10, "SW": 10,
      "HN": 8, "HS": 8, "HE": 7, "HW": 7,
      "DN": 7, "DS": 7, "DE": 6, "DW": 6,
      "CN": 9, "CS": 9, "CE": 5, "CW": 5
    }
  },
  ... (boards 2-30)
}
```

---

## 🎯 YOUR NEXT STEP

### RECOMMENDED:
```bash
python dd_setup_wizard.py
```

This will:
1. Check your system
2. Show you the options
3. Install what you need
4. Run the extraction
5. Show results

**No configuration needed - just run it!**

---

## 📚 FULL DOCUMENTATION INDEX

### Getting Started
1. [QUICK_START_DD.txt](QUICK_START_DD.txt) - 2 min read
2. [VISUAL_GUIDE_DD.md](VISUAL_GUIDE_DD.md) - 5 min read
3. Run: `python dd_setup_wizard.py`

### Methods & Guides
1. [DD_EXTRACTION_GUIDE.md](DD_EXTRACTION_GUIDE.md) - Detailed instructions
2. [DD_POPULATION_README.md](DD_POPULATION_README.md) - Method comparison
3. [README_DD_SYSTEM.md](README_DD_SYSTEM.md) - Full reference

### System Info
1. [FILES_CREATED.md](FILES_CREATED.md) - What was created
2. This file - Master index

---

## 🆘 TROUBLESHOOTING

### "Command not found"
```bash
# Make sure you're in the right directory
cd c:\Users\metin\Desktop\BRIC
python dd_setup_wizard.py
```

### "Chrome not found"
```bash
# Install from: https://google.com/chrome
# Or use manual method instead
```

### "Server not starting"
```bash
# Make sure you're in the right directory
cd c:\Users\metin\Desktop\BRIC\app\www
python server_with_api.py
```

### More troubleshooting
See [DD_EXTRACTION_GUIDE.md](DD_EXTRACTION_GUIDE.md) for detailed help

---

## ✨ YOU ARE ALL SET!

Everything you need is ready:

✓ Scripts created
✓ Documentation written
✓ Database prepared
✓ Web interface ready
✓ Server configured

**Just run one command and follow the prompts!**

```bash
python dd_setup_wizard.py
```

---

## 🎉 WHAT'S NEXT

After extraction:

1. **View Results**
   ```
   http://localhost:8000/hands_viewer.html
   ```

2. **Verify Status**
   ```bash
   python check_dd_status.py
   ```

3. **Deploy or Share**
   - Upload to web server
   - Share JSON file
   - Export to PDF

---

**You've got this! 🌉**

**Questions?** Check one of the guides above
**Ready to go?** Run `python dd_setup_wizard.py`

# DD Values Population - Two Methods

## Method 1: Automated Extraction from BBO (Recommended)

**Script**: `extract_dd_from_bbo.py`

This script automatically opens BBO's hand viewer for each board, extracts the DD table values, and saves them to the database.

### Setup:
```bash
pip install selenium
# Also need Chrome/Chromium browser installed
```

### Usage:
```bash
python extract_dd_from_bbo.py
```

The script will:
1. Load all 30 boards from the database
2. For each board, generate the BBO LIN URL
3. Open BBO in a headless browser
4. Wait for DD table to load
5. Extract tricks values for all 20 suit/player combinations
6. Save to database
7. Move to next board

**Advantages:**
- Fully automated
- Gets real DD values from BBO
- Completes all 30 boards in one run

**Time required:** ~1-2 minutes (rate-limited to avoid overwhelming BBO)

---

## Method 2: Manual Web Interface

**URL**: `http://localhost:8000/dd_input.html`

A web form where you can manually input DD values for each board.

### Steps:

1. Start the server:
```bash
cd c:\Users\metin\Desktop\BRIC\app\www
python server_with_api.py
```

2. Open the form:
Navigate to `http://localhost:8000/dd_input.html`

3. For each board:
   - Open BBO hand viewer in another tab
   - Read the DD table
   - Input the tricks values (6-13) in the form
   - Click "Save Board"
   - Click "Next Board"

4. The interface shows progress and highlights completed boards

**Advantages:**
- Works without additional dependencies
- Can verify DD values manually
- No automation required

**Time required:** ~5 minutes per board × 30 boards = ~2-3 hours

---

## Which Method to Use?

### Choose **Method 1 (Automated)** if:
- You want to populate all boards quickly
- You have Chrome/Chromium installed
- You can install Selenium

### Choose **Method 2 (Manual)** if:
- You want to verify DD values as you go
- You prefer to stay in control
- Automation doesn't work on your system

---

## Current Status

- **Board 1**: Has real DD values (calculated manually)
- **Boards 2-30**: Have diverse placeholder values (different numbers to show they're distinct)

Once you run either method above, boards 2-30 will be updated with real DD values from BBO.

---

## Troubleshooting

### Method 1 Issues:

**"Selenium not installed"**
```bash
pip install selenium
```

**"Chrome not found"**
Make sure Google Chrome or Chromium is installed on your system.

**"Could not extract complete DD table"**
BBO's page structure may have changed. This can happen if BBO updates their interface. Try Method 2 as fallback.

### Method 2 Issues:

**API endpoint not working**
Make sure the server is running:
```bash
python server_with_api.py
```

**Can't see DD table in BBO**
Scroll down in the hand viewer - the DD table appears below the hand layout.

---

## Verifying Results

After running either method, verify the DD values were saved:

```bash
python -c "import json; f=open('app/www/hands_database.json'); d=json.load(f); boards=d['events']['hosgoru_04_01_2026']['boards']; print('Board 1:', list(boards['1']['dd_analysis'].values())[:5]); print('Board 2:', list(boards['2']['dd_analysis'].values())[:5])"
```

You should see different values for each board.

---

## API Reference

### Save DD Values
**Endpoint**: `POST /api/save_dd`

**Request**:
```json
{
  "board_num": 1,
  "dd_analysis": {
    "NTN": 6,
    "NTS": 6,
    "NTE": 9,
    "NTW": 9,
    ...
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Board 1 DD values saved"
}
```

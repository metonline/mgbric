# 📊 Adding Tournament Hands to Database

Your hands database is currently at: `app/www/hands_database.json`
Currently contains: **30 boards** (from Event 404377)

## Database Structure

Each board is stored as:
```json
{
  "1": {
    "N": {"S": "AK9", "H": "QJ8", "D": "K87", "C": "AQJ"},
    "E": {"S": "QT8", "H": "A765", "D": "J92", "C": "K65"},
    "S": {"S": "J765", "H": "K942", "D": "AQT", "C": "87"},
    "W": {"S": "432", "H": "T3", "D": "643", "C": "T9432"}
  },
  "2": { ... }
}
```

## Methods to Add Hands

### Method 1: From Vugraph Website (Automatic)
```bash
python fetch_vugraph_hands.py
# Fetches from event ID (e.g., 404377)
```

### Method 2: From JSON File (Interactive)
```bash
python manage_hands_database.py
# Choose option 1: "Add hands from JSON file"
# Provide path to your JSON file
```

### Method 3: Find Available Tournaments
```bash
python find_tournaments.py
# Lists tournaments available from 01.01.2026 onwards
```

### Method 4: Manual Addition (Python)
```python
import json

# Load database
with open('app/www/hands_database.json', 'r') as f:
    db = json.load(f)

# Add new boards
highest_board = max([int(k) for k in db.keys()])
highest_board += 1

new_board = {
    "N": {"S": "...", "H": "...", "D": "...", "C": "..."},
    "E": {"S": "...", "H": "...", "D": "...", "C": "..."},
    "S": {"S": "...", "H": "...", "D": "...", "C": "..."},
    "W": {"S": "...", "H": "...", "D": "...", "C": "..."}
}

db[str(highest_board)] = new_board

# Save database
with open('app/www/hands_database.json', 'w') as f:
    json.dump(db, f, indent=2)
```

## Vugraph Tournaments Since 01.01.2026

Known tournaments:
- **Event 404377**: PAZAR SİMULTANE (04-01-2026) - *Already in database*

To find more tournaments:
1. Visit: https://clubs.vugraph.com/hosgoru/
2. Look for tournaments by date
3. Note the event ID (shown in URLs)
4. Use fetch_vugraph_hands.py with that event ID

## Card Notation

Format: `"S": "AK9"` means Spades: Ace, King, Nine

Supported ranks: A, K, Q, J, T (10), 2-9

Example: `"H": "KJT5432"` = Hearts: King, Jack, Ten, 5, 4, 3, 2

## Automation Script

After adding hands, your tournament_hands.html page will automatically:
1. Show new boards in the grid
2. Allow filtering by date
3. Generate LIN links for BBO
4. Display DD tables

No additional configuration needed!

---

**Current Status**: 30 boards
**Last Updated**: 2026-01-07
**Format**: Standard tournament bridge (N/S vs E/W)

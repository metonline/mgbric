# Bridge Hands Viewer - Features

## ✅ Dual Solver Support

The hands viewer now supports **2 alternative bridge solvers** with seamless switching:

### 1. **BBO (BridgeBase Online) Viewer** 🌐
- Official BridgeBase online hand viewer
- Fast, responsive interface
- Real-time hand display
- Tab: Click "🌐 BBO Viewer"
- URL: https://www.bridgebase.com/tools/handviewer.html

### 2. **Bridge Solver (BridgeWebs)** 🔧
- Advanced DD (Double Dummy) analysis tool
- More detailed contract analysis
- Professional solver interface
- Tab: Click "🔧 Bridge Solver"
- URL: https://dds.bridgewebs.com/bsol_standalone/ddummy.html

## Usage

### Viewing Hands
1. Open: http://localhost:8000/app/www/hands_viewer.html
2. Navigate through the hands grid (100 boards total)
3. Each hand card displays:
   - **Board Number** (1-100)
   - **Dealer** (North, East, South, West)
   - **Zone Status** (Vulnerability)
   - **Solver Tabs** to switch between BBO and Bridge Solver
   - **Double Dummy Analysis Table** (tricks for each denomination × seat)

### Switching Solvers
Each hand has 2 tabs at the top:
- **BBO Viewer Tab**: Fast, simple hand display
- **Bridge Solver Tab**: Professional analysis with additional DD data

Click either tab to instantly switch between solvers without reloading.

## Data Flow

```
hands_database.json (100 hands)
    ↓
handToLIN() - Converts to LIN format
    ↓
Tab Selection
    ├→ BBO Viewer: https://www.bridgebase.com/tools/handviewer.html?lin=...
    └→ Bridge Solver: https://dds.bridgewebs.com/bsol_standalone/ddummy.html?lin=...
    ↓
Display in iframe
    ↓
DD Analysis Table (below)
```

## DD (Double Dummy) Analysis

The **Double Dummy Analysis Table** shows contract makability:

- **Denominations**: NT (No Trump), ♠ (Spades), ♥ (Hearts), ♦ (Diamonds), ♣ (Clubs)
- **Seats**: N (North), S (South), E (East), W (West)
- **Values**: Number of tricks makable by each seat in each denomination

Example:
```
     NT  ♠  ♥  ♦  ♣
N    9   10 8  9  8
S    8   9  8  8  7
E    4   3  5  4  5
W    4   3  5  4  5
```

## Technical Details

### Hand Format (Flat JSON)
```json
{
  "1": {
    "N": {"S": "AKQ2", "H": "J98", "D": "AK3", "C": "Q76"},
    "S": {"S": "984", "H": "T632", "D": "Q76", "C": "K95"},
    "E": {"S": "J76", "H": "KQ5", "D": "J952", "C": "A42"},
    "W": {"S": "53", "H": "A74", "D": "T84", "C": "JT832"},
    "dealer": "N",
    "vulnerability": "None",
    "dd_analysis": {"NTS": 9, "NTN": 8, ...}  // Optional DD data
  }
}
```

### LIN Format
The system converts hands to BBO LIN format automatically:
```
h|N:AKQ2JJ98AK3KQ76|984T632Q76K95|J76KQ5J952A42|53A74T84CJT832|N|0|0|0|0|0|0|0|
```

## Tested Solvers

- ✅ **BBO**: Fully functional, official interface
- ✅ **Bridge Solver**: Professional DD solver with advanced analysis
- ✅ **Tab Switching**: Instant switching without page reload
- ✅ **LIN Format**: Compatible with both solvers
- ✅ **DD Tables**: Display with both solvers

## Next Steps

### Enhance DD Analysis
- Fetch actual DD values from solver (if API available)
- Display recommended contracts
- Show par contracts

### Additional Solvers
- Add more bridge solver interfaces if needed
- Create custom solver adapter

### Database Enrichment
- Calculate DD values for all 100 hands
- Add tournament context
- Link to official vugraph if available

## Files Modified
- `app/www/hands_viewer.html` - Added solver tabs and dual iframe support
- Added CSS for `.solver-tabs` and `.solver-tab` styling
- Added JavaScript for tab switching functionality
- Added `openBridgeSolverNewTab()` function for external links

## Commit History
```
Add: Dual solver support - BBO and Bridge Solver with tab switching
```

---

**Last Updated**: January 17, 2026
**Status**: ✅ Fully Functional

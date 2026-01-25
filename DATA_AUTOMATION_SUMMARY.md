# DATA FETCHING & AUTOMATION OVERVIEW

## 🎯 CURRENT STATUS (as of Jan 25, 2026)

### Pipeline Health
- **Last Run**: Jan 24, 2026 05:27:36
- **Total Runs**: 32 times
- **Total Boards Fetched**: 90
- **Success Rate**: ~97% (1 error in recent history)
- **Registry Loaded**: 1579 dates, 1595 events

---

## 📊 SYSTEM ARCHITECTURE

### 1. **Core Data Fetching** (`unified_fetch.py`)
**Purpose**: Centralized data collection system

**Capabilities**:
- Auto-detect new tournaments from Vugraph
- Fetch hand data (el verileri)
- Fetch board rankings (sıralama)
- Validate event ID consistency
- Multi-threaded fetching (5 workers)
- Data deduplication and caching

**Usage Options**:
```bash
# Fetch all missing data
python unified_fetch.py

# Hands only
python unified_fetch.py --hands-only

# Rankings only  
python unified_fetch.py --rankings-only

# Specific date
python unified_fetch.py --date 21.01.2026

# Daemon mode (30 min intervals)
python unified_fetch.py --daemon

# Data validation
python unified_fetch.py --validate
```

**Input Sources**:
- `EVENT_REGISTRY.py` - 1595 events with dates
- Vugraph website - Live hand/ranking data
- Local database cache - Quick lookup

**Output Files**:
- `database.json` - Event metadata
- `hands_database.json` - Actual hand data (500KB+)
- `board_results.json` - Board scores & rankings

---

### 2. **Scheduled Pipeline** (`scheduled_pipeline.py`)
**Purpose**: Automated periodic updates

**Workflow**:
1. Data integrity check
2. Event ID consistency fixes
3. Missing rankings fetch
4. Result logging & status update

**Usage Options**:
```bash
# Full update
python scheduled_pipeline.py

# Quick update (missing data only)
python scheduled_pipeline.py --quick

# Rankings only
python scheduled_pipeline.py --rankings

# Daemon mode (30 min, auto-repeat)
python scheduled_pipeline.py --daemon --interval 30

# Check status
python scheduled_pipeline.py --status
```

**Available VS Code Tasks**:
- ✅ **Pipeline: Quick Update** - Fetch missing data only (~2 min)
- ✅ **Pipeline: Full Update** - Complete refresh (~5-10 min)
- ✅ **Pipeline: Daemon Mode (30 min)** - Background auto-update
- ✅ **Pipeline: Status** - Check last run details
- ✅ **Validate Data Integrity** - Run consistency checks

---

### 3. **Data Validation** (`unified_fetch.py --validate`)
**Purpose**: Ensure data consistency and completeness

**Checks**:
- Event ID consistency
- Duplicate hand records
- Missing rankings data
- Board numbering continuity
- Database file integrity

**Output**:
- `validation_results.txt` - Detailed report

---

## 🔧 ADVANCED AUTOMATION SCRIPTS

### Tournament Fetching
| Script | Purpose |
|--------|---------|
| `auto_fetch_tournaments.py` | Auto-discover new tournaments |
| `fetch_all_2026_boards.py` | Bulk fetch 2026 boards |
| `fetch_all_board_results.py` | Get all board scores |
| `fetch_missing_rankings.py` | Find incomplete rankings |
| `fetch_missing_pair_data.py` | Get pair statistics |

### Specialized Fetchers
| Script | Purpose |
|--------|---------|
| `fetch_dd_from_bridgewebs.py` | Double dummy from external source |
| `vugraph_fetcher.py` | Direct Vugraph crawler |
| `calendar_crawler.py` | Event calendar parser |
| `click_events_crawler.py` | Navigate calendar events |

### Data Transformation
| Script | Purpose |
|--------|---------|
| `populate_hands_from_lin.py` | LIN → Hand database |
| `generate_all_lin.py` | Hand database → LIN format |
| `normalize_hands.py` | Standardize hand format |

### Quality Assurance
| Script | Purpose |
|--------|---------|
| `verify_database.py` | Check database integrity |
| `check_duplicates.py` | Find duplicate records |
| `check_missing_events.py` | Identify gaps |
| `final_database_check.py` | Comprehensive validation |

---

## 📈 DATA FLOW DIAGRAM

```
Vugraph Website
      ↓
unified_fetch.py (DataFetcher class)
      ↓
  ┌───┴────┬──────────┐
  ↓        ↓          ↓
Hands   Rankings   Events
Database Database  Registry
  ↓        ↓          ↓
  └────┬────┴──────┬──┘
       ↓           ↓
hands_database.json  database.json
       ↓           ↓
  ┌────┴───────────┘
  ↓
scheduled_pipeline.py (validation & updates)
  ↓
pipeline_status.json (tracking)
  ↓
Web UI (hands_in_grid.html)
```

---

## 🚀 QUICK START COMMANDS

### Run Now (Interactive)
```bash
# Full data refresh
python scheduled_pipeline.py

# Quick (missing only)
python scheduled_pipeline.py --quick

# Check what's wrong
python unified_fetch.py --validate

# Check status
python scheduled_pipeline.py --status
```

### Via VS Code Tasks
1. Press `Ctrl+Shift+B` (or Cmd+Shift+B)
2. Select:
   - **"Pipeline: Quick Update"** - 2-3 minutes
   - **"Pipeline: Full Update"** - 5-10 minutes
   - **"Validate Data Integrity"** - 1 minute
   - **"Pipeline: Status"** - Instant

### Background Automation
```bash
# Start 30-min auto-update daemon
python scheduled_pipeline.py --daemon --interval 30
```

---

## ⚙️ CONFIGURATION

### Event Registry
- **File**: `event_registry.py`
- **Tracks**: 1595 events across 2024-2026
- **Updated**: Automatically during fetch
- **Format**: 
  ```python
  {
    "event_id": "405376",
    "date": "24.01.2026",
    "club": "Hoşgörü BK"
  }
  ```

### Database Structure
```json
{
  "version": "2.0",
  "events": {
    "405376": {
      "date": "24.01.2026",
      "event_type": "Teams",
      "boards": 30,
      "pairs": 24,
      "hands_count": 30,
      "rankings_count": 24
    }
  }
}
```

### Status Tracking
```json
{
  "last_run": "2026-01-24T05:27:36.648109",
  "last_success": "2026-01-24T05:27:36.648109",
  "total_runs": 32,
  "total_boards_fetched": 90,
  "errors": []
}
```

---

## ✅ WHAT'S WORKING

✅ Hands data fetching (el verileri)
✅ Board results collection  
✅ Rankings/pair scores
✅ Event date tracking
✅ Duplicate detection
✅ Retry mechanism (3 attempts)
✅ Concurrent fetching (5 threads)
✅ JSON caching
✅ Status logging
✅ Error tracking

---

## ⚠️ KNOWN ISSUES

### Current (Jan 24, 2026)
1. **30 boards unable to fetch** (last attempt: Jan 24)
   - Likely network/source timeouts
   - Auto-retry on next run
   - Status: Monitored

2. **Missing data gaps**
   - Some older events (2024) may have incomplete data
   - Newer events (2026) being filled progressively

### Potential Issues to Watch
- Vugraph website structure changes
- Network timeouts on large fetches
- Database file size growth (currently ~500KB hands)

---

## 🎯 RECOMMENDATIONS

### Immediate Actions
1. **Run validation**: `python unified_fetch.py --validate`
2. **Check status**: `python scheduled_pipeline.py --status`
3. **Quick update**: Use "Pipeline: Quick Update" task

### Weekly Maintenance
- Check `pipeline.log` for errors
- Verify `pipeline_status.json` shows recent runs
- Run full validation monthly

### Performance
- **Daemon mode**: Keeps data fresh without manual runs
- **Quick mode**: 2-3 min, ideal for frequent updates
- **Full mode**: 5-10 min, comprehensive refresh

---

## 📚 RELATED FILES

### Configuration
- `event_registry.py` - Event tracking
- `unified_fetch.py` - Main fetcher
- `scheduled_pipeline.py` - Scheduler

### Logs & Status
- `pipeline.log` - Detailed operation log
- `pipeline_status.json` - Last run metrics
- `validation_results.txt` - Data check report

### Data
- `database.json` - Event metadata (1595 events)
- `hands_database.json` - Hand details (~90 boards, 30 hands each)
- `board_results.json` - Rankings & scores

---

## 🔄 NEXT STEPS

**What would you like to do?**

1. **Run data validation** - Check for issues
2. **Schedule daemon mode** - 24/7 auto-updates
3. **Improve missing data fetch** - Get those 30 boards
4. **Add new data source** - Integrate different tournament site
5. **Enhance database** - Add more metadata/statistics

Choose your priority and I'll implement it!

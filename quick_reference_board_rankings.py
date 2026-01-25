#!/usr/bin/env python3
"""
Quick reference: Accessing board rankings in different ways
"""

import json
from pathlib import Path

print("=" * 70)
print("BOARD RANKINGS - QUICK ACCESS GUIDE")
print("=" * 70)

# Load board_results.json
board_results_path = Path('board_results.json')
if not board_results_path.exists():
    print("❌ board_results.json not found - run: python generate_board_rankings.py")
    exit(1)

with open('board_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. List all events
print("\n1. ALL EVENTS AVAILABLE:")
print("-" * 70)
events = sorted(data['events'].keys())
print(f"Total: {len(events)} events")
for event_id in events[:10]:
    board_count = sum(1 for k in data['boards'].keys() if k.startswith(f"{event_id}_"))
    print(f"  • {event_id}: {board_count} boards")
if len(events) > 10:
    print(f"  • ... and {len(events) - 10} more")

# 2. Sample board structure
print("\n2. SAMPLE BOARD (404155_1):")
print("-" * 70)
sample_key = "404155_1"
if sample_key in data['boards']:
    sample_board = data['boards'][sample_key]
    results = sample_board.get('results', [])
    print(f"Board: {sample_key}")
    print(f"Rankings: {len(results)} pairs\n")
    print(f"{'Rank':<6} {'Pair Names':<35} {'Dir':<4} {'Contract':<10} {'Score':<8} {'Percent':<8}")
    print("-" * 70)
    for r in results[:5]:
        pair_name = r['pair_names'][:32]
        print(f"{r['rank']:<6} {pair_name:<35} {r['direction']:<4} {r['contract']:<10} {r['score']:<8} {r['percent']:<8}%")
    if len(results) > 5:
        print(f"  ... and {len(results) - 5} more")

# 3. How to access programmatically
print("\n3. HOW TO ACCESS IN YOUR CODE:")
print("-" * 70)
print("""
# Load rankings
with open('board_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get specific board results
event_id = '404155'
board_num = '1'
board_key = f"{event_id}_{board_num}"
results = data['boards'][board_key]['results']

# Iterate through rankings
for ranking in results:
    print(f"{ranking['rank']}. {ranking['pair_names']} ({ranking['direction']})")
    print(f"   {ranking['contract']} by {ranking['lead']} = {ranking['score']} ({ranking['percent']}%)")
""")

# 4. API endpoint
print("\n4. HOW TO ACCESS VIA API:")
print("-" * 70)
print("""
# Start Flask server:
python app.py

# Then request:
curl http://localhost:5000/api/board-results?event=404155&board=1

# Response format:
{
  "event": "404155",
  "board": 1,
  "results": [
    {
      "rank": 1,
      "pair_names": "...",
      "direction": "NS|EW",
      "contract": "...",
      "lead": "...",
      "result": "...",
      "score": 1362,
      "percent": 100.0
    }
  ]
}
""")

# 5. Integration with pipeline
print("\n5. HOW TO REGENERATE (in pipeline):")
print("-" * 70)
print("""
# Option 1: Manual run
python generate_board_rankings.py

# Option 2: With pipeline
python scheduled_pipeline.py --quick
python scheduled_pipeline.py --full
python scheduled_pipeline.py --daemon --interval 30

# Option 3: In code
from generate_board_rankings import BoardRankingsGenerator
generator = BoardRankingsGenerator()
generator.generate_all()  # Returns True/False
""")

# 6. Statistics
print("\n6. CURRENT STATISTICS:")
print("-" * 70)
total_results = sum(len(board.get('results', [])) for board in data['boards'].values())
print(f"Total Events:  {len(data['events'])}")
print(f"Total Boards:  {len(data['boards'])}")
print(f"Total Results: {total_results}")
print(f"Avg Results/Board: {total_results / len(data['boards']):.1f}")
print(f"Updated: {data.get('updated_at', 'N/A')}")

print("\n" + "=" * 70)
print("For more info: see BOARD_RANKINGS_AUTOMATION.md")
print("=" * 70)

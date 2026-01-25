#!/usr/bin/env python3
"""
Test board rankings integration
Verify: 1) Generator works, 2) File is created, 3) API can load it
"""

import json
import sys
from pathlib import Path
from generate_board_rankings import BoardRankingsGenerator

print("=" * 60)
print("BOARD RANKINGS INTEGRATION TEST")
print("=" * 60)

# 1. Test generator
print("\n1️⃣  Testing BoardRankingsGenerator...")
try:
    generator = BoardRankingsGenerator()
    success = generator.generate_all()
    if not success:
        print("❌ Generator failed")
        sys.exit(1)
    print("✅ Generator completed successfully")
except Exception as e:
    print(f"❌ Generator error: {e}")
    sys.exit(1)

# 2. Verify file created
print("\n2️⃣  Verifying board_results.json...")
board_results_path = Path('board_results.json')
if not board_results_path.exists():
    print("❌ board_results.json not found")
    sys.exit(1)

file_size = board_results_path.stat().st_size
print(f"✅ File exists ({file_size:,} bytes)")

# 3. Verify structure
print("\n3️⃣  Verifying JSON structure...")
try:
    with open('board_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    events = len(data.get('events', {}))
    boards = len(data.get('boards', {}))
    updated_at = data.get('updated_at')
    
    print(f"✅ Valid JSON structure")
    print(f"   - Events: {events}")
    print(f"   - Boards: {boards}")
    print(f"   - Updated: {updated_at}")
    
    if events == 0 or boards == 0:
        print("❌ No data generated")
        sys.exit(1)
        
except json.JSONDecodeError as e:
    print(f"❌ Invalid JSON: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error reading file: {e}")
    sys.exit(1)

# 4. Verify sample board structure
print("\n4️⃣  Verifying sample board structure...")
try:
    # Find a board with results
    sample_board_key = None
    for board_key, board_data in data.get('boards', {}).items():
        if board_data.get('results'):
            sample_board_key = board_key
            break
    
    if not sample_board_key:
        print("⚠️  No boards with results found (may be empty)")
    else:
        board_data = data['boards'][sample_board_key]
        results = board_data.get('results', [])
        
        print(f"✅ Sample board: {sample_board_key}")
        print(f"   - Results count: {len(results)}")
        
        if results:
            first_result = results[0]
            required_fields = ['rank', 'pair_names', 'direction', 'contract', 'score', 'percent']
            missing = [f for f in required_fields if f not in first_result]
            
            if missing:
                print(f"❌ Missing fields: {missing}")
                sys.exit(1)
            
            print(f"   - All required fields present")
            print(f"   - Sample: {first_result['pair_names']} ({first_result['direction']}) #{first_result['rank']}")

except Exception as e:
    print(f"❌ Structure validation error: {e}")
    sys.exit(1)

# 5. Test API-like loading
print("\n5️⃣  Testing API-like data access...")
try:
    # Simulate API endpoint behavior
    test_event = list(data.get('events', {}).keys())[0] if data.get('events') else None
    test_board = None
    
    if test_event:
        # Find a board for this event
        for board_key in data.get('boards', {}).keys():
            if board_key.startswith(f"{test_event}_"):
                test_board = board_key.split('_')[1]
                break
    
    if test_event and test_board:
        board_key = f"{test_event}_{test_board}"
        board_data = data.get('boards', {}).get(board_key)
        
        if board_data:
            results = board_data.get('results', [])
            print(f"✅ API simulation successful")
            print(f"   - Event: {test_event}, Board: {test_board}")
            print(f"   - Results available: {len(results)}")
        else:
            print(f"⚠️  No data for {board_key}")
    else:
        print("⚠️  No test event/board found")

except Exception as e:
    print(f"❌ API simulation error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - Integration Ready")
print("=" * 60)
print("\nReady to:")
print("  • Serve via Flask /api/board-results endpoint")
print("  • Use in board_ranking.html UI")
print("  • Run in scheduled_pipeline.py automation")
print()

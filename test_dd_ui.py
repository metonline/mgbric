#!/usr/bin/env python3
"""
Quick test to verify DD solver UI integration
Checks if all files are in place and valid JSON
"""

import json
from pathlib import Path

def test_dd_integration():
    """Test DD solver integration"""
    workspace = Path(__file__).parent
    
    print("\n" + "="*60)
    print("DD SOLVER UI INTEGRATION TEST")
    print("="*60 + "\n")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: DD results file exists
    tests_total += 1
    dd_file = workspace / "double_dummy" / "dd_results.json"
    if dd_file.exists():
        with open(dd_file) as f:
            dd_data = json.load(f)
        boards_count = len(dd_data.get('boards', {}))
        print(f"✓ DD Results File: {dd_file.name}")
        print(f"  - Total boards: {boards_count}")
        print(f"  - Generated: {dd_data.get('generated', 'N/A')}")
        tests_passed += 1
    else:
        print(f"✗ DD Results File not found: {dd_file}")
    
    # Test 2: Hands database exists
    tests_total += 1
    hands_file = workspace / "hands_database.json"
    if hands_file.exists():
        with open(hands_file) as f:
            hands_data = json.load(f)
        hands_count = len(hands_data) if isinstance(hands_data, list) else len(hands_data.get('hands', {}))
        print(f"\n✓ Hands Database: {hands_file.name}")
        print(f"  - Total hands: {hands_count}")
        tests_passed += 1
    else:
        print(f"\n✗ Hands Database not found: {hands_file}")
    
    # Test 3: UI JavaScript files exist
    tests_total += 1
    js_file = workspace / "dd-solver-ui.js"
    if js_file.exists():
        print(f"\n✓ UI JavaScript: {js_file.name}")
        print(f"  - Size: {js_file.stat().st_size} bytes")
        tests_passed += 1
    else:
        print(f"\n✗ UI JavaScript not found: {js_file}")
    
    # Test 4: UI CSS file exists
    tests_total += 1
    css_file = workspace / "dd-solver-ui.css"
    if css_file.exists():
        print(f"\n✓ UI Stylesheet: {css_file.name}")
        print(f"  - Size: {css_file.stat().st_size} bytes")
        tests_passed += 1
    else:
        print(f"\n✗ UI Stylesheet not found: {css_file}")
    
    # Test 5: Hand diagram HTML file exists
    tests_total += 1
    html_file = workspace / "hands_with_dd.html"
    if html_file.exists():
        print(f"\n✓ Hand Display Page: {html_file.name}")
        print(f"  - Size: {html_file.stat().st_size} bytes")
        print(f"  - Open at: http://localhost:5000/hands_with_dd.html")
        tests_passed += 1
    else:
        print(f"\n✗ Hand Display Page not found: {html_file}")
    
    # Test 6: Sample board data verification
    tests_total += 1
    board_results = workspace / "board_results.json"
    if board_results.exists():
        with open(board_results, encoding='utf-8-sig') as f:
            boards = json.load(f)
        total_boards = len(boards.get('boards', {}))
        print(f"\n✓ Board Results: {board_results.name}")
        print(f"  - Total boards: {total_boards}")
        tests_passed += 1
    else:
        print(f"\n✗ Board Results not found: {board_results}")
    
    # Summary
    print("\n" + "="*60)
    print(f"TESTS PASSED: {tests_passed}/{tests_total}")
    print("="*60 + "\n")
    
    if tests_passed == tests_total:
        print("✓ All tests passed! DD Solver UI is ready to use.\n")
        print("To view hand diagrams with DD analysis:")
        print("  1. Start the server: python dev_server.py")
        print("  2. Open: http://localhost:5000/hands_with_dd.html\n")
        return True
    else:
        print(f"✗ {tests_total - tests_passed} test(s) failed.\n")
        return False

if __name__ == '__main__':
    import sys
    success = test_dd_integration()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Merge corrected Board 1 data into the main database.
"""

import json

# Load the corrected results
with open("board1_correct_scores.json", "r", encoding="utf-8") as f:
    corrected_results = json.load(f)

# Load the main database
with open("app/www/hands_database.json", "r", encoding="utf-8") as f:
    database = json.load(f)

# Update Board 1 results with corrected data
board1_data = database["events"]["hosgoru_04_01_2026"]["boards"]["1"]
board1_data["results"] = corrected_results

# Save updated database
with open("app/www/hands_database.json", "w", encoding="utf-8") as f:
    json.dump(database, f, indent=2, ensure_ascii=False)

print(f"✓ Updated Board 1 with {len(corrected_results)} pairs")
print("✓ Individual board scores are now correct")
print("✓ Database saved to app/www/hands_database.json")

# Show summary
print("\nBoard 1 Results Summary:")
ns_results = [r for r in corrected_results if r['direction'] == 'N-S']
ew_results = [r for r in corrected_results if r['direction'] == 'E-W']

print(f"\nN-S Pairs: {len(ns_results)}")
for r in ns_results[:3]:
    print(f"  {r['pair_names'][:40]:40} {r['contract']:5} {r['result']:5} {r['score']:6.2f}%")

print(f"\nE-W Pairs: {len(ew_results)}")
for r in ew_results[:3]:
    print(f"  {r['pair_names'][:40]:40} {r['contract']:5} {r['result']:5} {r['score']:6.2f}%")

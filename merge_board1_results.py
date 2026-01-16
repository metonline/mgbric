#!/usr/bin/env python3
"""
Merge scraped Board 1 results into the main database.
"""

import json

# Load the scraped results
with open("board1_all_pairs.json", "r", encoding="utf-8") as f:
    scraped_results = json.load(f)

# Load the main database
with open("app/www/hands_database.json", "r", encoding="utf-8") as f:
    database = json.load(f)

# Update Board 1 results
board1_data = database["events"]["hosgoru_04_01_2026"]["boards"]["1"]

# Clear old results and add new ones
board1_data["results"] = []

# Convert scraped results to database format
for result in scraped_results:
    # Convert result points to contract notation if possible
    # For now, just store the raw result points
    result_text = result["result"]
    
    # Try to interpret the result as tricks over/under contract
    # Positive numbers = tricks over, negative = tricks under
    # But we need the contract first - we'll add this separately
    
    db_result = {
        "pair_names": result["pair_names"],
        "pair_num": result["pair_num"],
        "direction": result["direction"],
        "contract": "",  # Will be filled from boarddetails if available
        "result": result_text,  # This is the points, not the contract result
        "score": result["score"]
    }
    
    board1_data["results"].append(db_result)

# Save updated database
with open("app/www/hands_database.json", "w", encoding="utf-8") as f:
    json.dump(database, f, indent=2, ensure_ascii=False)

print(f"Updated Board 1 with {len(board1_data['results'])} pair results")
print("Database saved to hands_database.json")

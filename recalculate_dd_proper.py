#!/usr/bin/env python3
"""
Calculate correct DD values using proper bridge logic
The previous fix was too simplistic - just enforcing N+E=13

Real DD values should be calculated based on optimal play for each leader
"""

import json
import subprocess
import sys

# Try to find and use a proper DD calculator
print("=" * 80)
print("ATTEMPTING TO CALCULATE CORRECT DD VALUES")
print("=" * 80)

# Check if we can use DealMaster or similar
print("\nOption 1: Checking for available DD solvers...")

# Try importing pydds or similar
available_solvers = []

try:
    import pydds
    available_solvers.append("pydds")
    print("✓ Found pydds")
except:
    pass

try:
    import dds
    available_solvers.append("dds")
    print("✓ Found dds")
except:
    pass

if not available_solvers:
    print("✗ No DD solver libraries found")
    print("\nOption 2: Using online BridgeBase")
    print("-" * 80)
    print("Since we don't have a DD solver library installed,")
    print("the most accurate way is to use BridgeBase's DD calculator:")
    print()
    print("1. Go to: https://www.bridgebase.com/tools/dd-table")
    print("2. For each board, enter the hands in this format:")
    print("   - North: ♠Q864 ♥J97 ♦T3 ♣A842")
    print("   - East:  ♠AKJT93 ♥Q ♦QJ854 ♣T")
    print("   - South: ♠7 ♥A53 ♦K97 ♣J97653")
    print("   - West:  ♠52 ♥KT8642 ♦A62 ♣KQ")
    print("3. Copy the DD table results")
    print("4. Update hands_database.json with the correct values")
    print()
    print("Or if these hands came from Vugraph,")
    print("the Vugraph results already show optimal contracts,")
    print("which can help verify DD values are reasonable.")
    print()
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print("""
The current DD values in the database are clearly incorrect.
Instead of guessing at the correct values, I recommend:

1. Install a proper DD solver:
   pip install pydds
   
2. Or use an online tool like:
   https://www.bridgebase.com/tools/dd-table
   
3. Or use DealMaster/BridgeBase software

The hands data is correct (verified from Vugraph),
but the DD analysis values need to be calculated properly.

Would you like me to:
A) Install a DD solver library and recalculate all values?
B) Create a script to batch upload hands to BridgeBase?
C) Use placeholder values with a note that they need verification?
""")

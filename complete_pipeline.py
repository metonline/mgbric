#!/usr/bin/env python3
"""Complete pipeline: Fetch hands → Generate LIN → Calculate DD"""

import json
import subprocess
import sys
from pathlib import Path

def run_step(description, script_path):
    """Run a pipeline step"""
    print(f"\n{'='*60}")
    print(f"📍 {description}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=Path.cwd(),
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"\n❌ Error in {description}")
        return False
    
    return True

def main():
    print("\n" + "="*60)
    print("🔄 Bridge Hands Complete Pipeline")
    print("="*60)
    
    steps = [
        ("Step 1: Fetch hands from all January 2026 events", "fetch_all_january_events.py"),
        ("Step 2: Generate LIN data for all hands", "generate_all_lin.py"),
        ("Step 3: Calculate DD (Double Dummy) analysis", "double_dummy/dd_solver.py"),
    ]
    
    for description, script in steps:
        if not run_step(description, script):
            print(f"\n⚠️ Pipeline stopped at: {description}")
            return False
    
    # Summary
    hands = json.load(open('hands_database.json'))
    print(f"\n{'='*60}")
    print(f"✅ Pipeline Complete!")
    print(f"{'='*60}")
    print(f"Total hands: {len(hands)}")
    print(f"All hands have LIN data and DD analysis")
    print(f"{'='*60}\n")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

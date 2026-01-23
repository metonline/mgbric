#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPLETE BRIDGE HANDS AUTOMATION SYSTEM
========================================
Fully automated pipeline for:
1. Building hands database (with actual hands + estimates)
2. Processing DD (Double Dummy) tables
3. Generating complete tournament analysis
4. Can be scheduled via cron/Task Scheduler

Usage:
    python auto_dd_pipeline.py                # Run once
    python auto_dd_pipeline.py --schedule     # Run periodically
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import argparse

class BridgeAutomationPipeline:
    """Full automation pipeline for bridge tournament data"""
    
    def __init__(self, workspace_dir=None):
        self.workspace = Path(workspace_dir or Path(__file__).parent)
        self.board_results = self.workspace / "board_results.json"
        self.hands_db = self.workspace / "hands_database.json"
        self.dd_results = self.workspace / "double_dummy" / "dd_results.json"
        self.log_file = self.workspace / "automation_log.txt"
    
    def log(self, message):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + "\n")
    
    def step_1_build_hands_database(self):
        """Step 1: Build comprehensive hands database"""
        self.log("\n" + "="*60)
        self.log("STEP 1: Building Hands Database")
        self.log("="*60)
        
        script = self.workspace / "build_hands_database.py"
        if not script.exists():
            self.log("✗ build_hands_database.py not found!")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.log("✓ Hands database built successfully")
                # Show summary
                for line in result.stdout.split('\n'):
                    if '✓' in line or 'Saved' in line:
                        self.log(f"  {line.strip()}")
                return True
            else:
                self.log(f"✗ Failed to build hands database")
                if result.stderr:
                    self.log(f"  Error: {result.stderr[:200]}")
                return False
        except subprocess.TimeoutExpired:
            self.log("✗ Hands database building timed out")
            return False
        except Exception as e:
            self.log(f"✗ Error: {e}")
            return False
    
    def step_2_process_dd_tables(self):
        """Step 2: Process DD tables for all boards"""
        self.log("\n" + "="*60)
        self.log("STEP 2: Processing DD Tables")
        self.log("="*60)
        
        script = self.workspace / "full_dd_automation.py"
        if not script.exists():
            self.log("✗ full_dd_automation.py not found!")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                self.log("✓ DD processing completed")
                
                # Extract summary
                for line in result.stdout.split('\n'):
                    if 'Success rate' in line or 'Successful' in line or 'Failed' in line or 'Total boards' in line:
                        self.log(f"  {line.strip()}")
                return True
            else:
                self.log(f"✗ DD processing failed")
                if result.stderr:
                    self.log(f"  Error: {result.stderr[:200]}")
                return False
        except subprocess.TimeoutExpired:
            self.log("✗ DD processing timed out")
            return False
        except Exception as e:
            self.log(f"✗ Error: {e}")
            return False
    
    def step_3_verify_output(self):
        """Step 3: Verify output files"""
        self.log("\n" + "="*60)
        self.log("STEP 3: Verifying Output")
        self.log("="*60)
        
        success = True
        
        # Check hands database
        if self.hands_db.exists():
            with open(self.hands_db, 'r') as f:
                hands = json.load(f)
            self.log(f"✓ Hands database: {len(hands)} hands")
        else:
            self.log("✗ Hands database file not found!")
            success = False
        
        # Check DD results
        if self.dd_results.exists():
            with open(self.dd_results, 'r') as f:
                dd = json.load(f)
            boards_count = len(dd.get('boards', {}))
            self.log(f"✓ DD results: {boards_count} boards processed")
            
            # Get success rate
            total = dd.get('total_boards', 0)
            if total > 0:
                rate = 100 * boards_count / total
                self.log(f"  Success rate: {rate:.1f}%")
        else:
            self.log("✗ DD results file not found!")
            success = False
        
        return success
    
    def run_full_pipeline(self):
        """Run complete automation pipeline"""
        self.log("\n" + "#"*60)
        self.log("BRIDGE HANDS AUTOMATION PIPELINE")
        self.log(f"Started: {datetime.now()}")
        self.log("#"*60)
        
        # Run steps
        step1_ok = self.step_1_build_hands_database()
        if not step1_ok:
            self.log("\n✗ Pipeline failed at Step 1")
            return False
        
        step2_ok = self.step_2_process_dd_tables()
        if not step2_ok:
            self.log("\n✗ Pipeline failed at Step 2")
            return False
        
        step3_ok = self.step_3_verify_output()
        
        # Final summary
        self.log("\n" + "#"*60)
        if step1_ok and step2_ok and step3_ok:
            self.log("✓ PIPELINE COMPLETED SUCCESSFULLY")
        else:
            self.log("✗ PIPELINE COMPLETED WITH ERRORS")
        self.log(f"Finished: {datetime.now()}")
        self.log("#"*60 + "\n")
        
        return step1_ok and step2_ok and step3_ok

def main():
    parser = argparse.ArgumentParser(description="Bridge Hands Automation Pipeline")
    parser.add_argument('--schedule', action='store_true', help='Schedule for periodic execution')
    parser.add_argument('--workspace', type=str, default=None, help='Workspace directory')
    
    args = parser.parse_args()
    
    pipeline = BridgeAutomationPipeline(args.workspace)
    
    if args.schedule:
        print("Scheduling not yet implemented")
        print("Manual runs: python auto_dd_pipeline.py")
        sys.exit(1)
    else:
        # Run once
        success = pipeline.run_full_pipeline()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

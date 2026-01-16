#!/usr/bin/env python3
"""
Interactive DD Extraction Setup Wizard
Helps users choose between automated and manual extraction methods.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")

def check_chrome():
    """Check if Chrome is installed."""
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Chromium\Application\chrome.exe",
    ]
    
    for path in chrome_paths:
        if Path(path).exists():
            return True
    
    return False

def check_selenium():
    """Check if Selenium is installed."""
    try:
        import selenium
        return True
    except ImportError:
        return False

def install_selenium():
    """Install Selenium package."""
    print("\nInstalling Selenium...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "selenium"], 
                          capture_output=True, text=True)
    return result.returncode == 0

def main():
    print_header("DD EXTRACTION SETUP WIZARD")
    
    # Check current status
    db_path = Path('app/www/hands_database.json')
    if not db_path.exists():
        print("ERROR: hands_database.json not found!")
        sys.exit(1)
    
    print("Current Status: Board 1 has real DD values, Boards 2-30 have placeholders")
    print("\nTwo methods available to populate real DD values:\n")
    
    print("┌─────────────────────────────────────────────────────────────┐")
    print("│ METHOD 1: AUTOMATED (Fastest - ~10 minutes)                 │")
    print("├─────────────────────────────────────────────────────────────┤")
    print("│ • Script runs and extracts DD values automatically          │")
    print("│ • Requires: Chrome/Chromium + Selenium                      │")
    print("│ • Best for: Quick, hands-off completion                     │")
    print("│ • Setup time: ~2 minutes                                    │")
    print("│ • Run time: ~10 minutes                                     │")
    print("└─────────────────────────────────────────────────────────────┘\n")
    
    print("┌─────────────────────────────────────────────────────────────┐")
    print("│ METHOD 2: MANUAL WEB FORM (Most control - 2-3 hours)        │")
    print("├─────────────────────────────────────────────────────────────┤")
    print("│ • Fill in DD values through web form                        │")
    print("│ • Requires: Web browser only                                │")
    print("│ • Best for: Verification, learning, slow internet           │")
    print("│ • Setup time: 1 minute                                      │")
    print("│ • Work time: 5 min/board × 29 boards                        │")
    print("└─────────────────────────────────────────────────────────────┘\n")
    
    while True:
        choice = input("Choose method (1=Automated, 2=Manual, Q=Quit): ").strip().upper()
        
        if choice == 'Q':
            print("\nAborted.")
            sys.exit(0)
        
        if choice == '1':
            handle_automated()
            break
        elif choice == '2':
            handle_manual()
            break
        else:
            print("Invalid choice. Enter 1, 2, or Q.\n")

def handle_automated():
    """Handle automated extraction setup."""
    print_header("AUTOMATED EXTRACTION SETUP")
    
    # Check prerequisites
    has_chrome = check_chrome()
    has_selenium = check_selenium()
    
    print("Checking requirements...\n")
    print(f"✓ Chrome installed:    {has_chrome}")
    print(f"✓ Selenium installed:  {has_selenium}")
    
    if not has_chrome:
        print("\n⚠ Chrome not found!")
        print("   Please install Google Chrome from: https://google.com/chrome")
        print("   Then run this script again.")
        return
    
    if not has_selenium:
        print("\nInstalling Selenium...")
        if install_selenium():
            print("✓ Selenium installed successfully")
        else:
            print("✗ Failed to install Selenium")
            print("  Try manually: pip install selenium")
            return
    
    print("\n" + "=" * 70)
    print("READY TO RUN AUTOMATED EXTRACTION")
    print("=" * 70)
    print("\nThis will:")
    print("1. Load database (30 boards)")
    print("2. For each board 2-30:")
    print("   - Open BBO in headless browser")
    print("   - Extract DD table")
    print("   - Save to database")
    print("3. Show results (success/failures)")
    print("\nTime estimate: ~10 minutes\n")
    
    confirm = input("Run automated extraction now? (Y/N): ").strip().upper()
    
    if confirm == 'Y':
        print("\n" + "=" * 70)
        print("Starting extraction...")
        print("=" * 70 + "\n")
        
        result = subprocess.run([sys.executable, "extract_dd_auto.py"], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✓ Extraction completed successfully!")
            print("\nNext step: View results")
            print("  http://localhost:8000/hands_viewer.html")
        else:
            print("\n✗ Extraction failed or had errors")
            print("   Try manual method instead: python dd_setup_wizard.py")

def handle_manual():
    """Handle manual extraction setup."""
    print_header("MANUAL EXTRACTION SETUP")
    
    print("For manual DD input, you'll need:\n")
    print("1. Python HTTP server running")
    print("2. Web browser")
    print("3. BBO (to look up DD values)")
    print("\n" + "=" * 70)
    print("STARTING SERVER")
    print("=" * 70 + "\n")
    
    # Change to www directory
    os.chdir('app/www')
    
    print("Starting server on http://localhost:8000...")
    print("\nServer is running. Open a new terminal or browser window and visit:")
    print("\n  ► Input form:   http://localhost:8000/dd_input.html")
    print("  ► Hand viewer:  http://localhost:8000/hands_viewer.html")
    print("  ► Server logs:  Below\n")
    print("=" * 70)
    print("Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")
    
    try:
        subprocess.run([sys.executable, "server_with_api.py"], 
                      capture_output=False, text=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted.")
        sys.exit(0)

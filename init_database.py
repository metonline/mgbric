#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize or reset database to correct format
"""

import json
import os
from datetime import datetime

DB_FILE = 'database.json'

def init_database():
    """Initialize database with correct structure"""
    
    database = {
        "version": "2.0",
        "last_updated": datetime.now().isoformat(),
        "events": {},
        "metadata": {
            "total_tournaments": 0,
            "total_boards": 0
        }
    }
    
    # Save the database
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        print(f"✅ Database initialized successfully")
        print(f"   File: {DB_FILE}")
        print(f"   Timestamp: {database['last_updated']}")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

if __name__ == '__main__':
    init_database()

#!/usr/bin/env python3
# Test BridgeBase embed with sample hands

import json
import os
from datetime import datetime

# Test data
test_data = {
    "events": {
        "test_event": {
            "name": "Test Tournament",
            "date": "01.01.2026",
            "location": "Test",
            "boards": {
                "1": {
                    "dealer": "N",
                    "vulnerability": "None",
                    "hands": {
                        "North": {
                            "S": "AKQJ",
                            "H": "AK",
                            "D": "AK",
                            "C": "AKQJ10"
                        },
                        "South": {
                            "S": "10987",
                            "H": "QJ10",
                            "D": "QJ10",
                            "C": "987"
                        },
                        "East": {
                            "S": "654",
                            "H": "9876",
                            "D": "9876",
                            "C": "654"
                        },
                        "West": {
                            "S": "32",
                            "H": "5432",
                            "D": "5432",
                            "C": "32"
                        }
                    },
                    "result": {
                        "contract": "7NT",
                        "tricks": 13,
                        "result": "made"
                    }
                },
                "2": {
                    "dealer": "E",
                    "vulnerability": "NS",
                    "hands": {
                        "North": {
                            "S": "K",
                            "H": "AK",
                            "D": "AK",
                            "C": "AK"
                        },
                        "South": {
                            "S": "AQJ",
                            "H": "QJ",
                            "D": "QJ",
                            "C": "QJ"
                        },
                        "East": {
                            "S": "10987",
                            "H": "10987",
                            "D": "10987",
                            "C": "10987"
                        },
                        "West": {
                            "S": "6543",
                            "H": "6543",
                            "D": "6543",
                            "C": "6543"
                        }
                    },
                    "result": {
                        "contract": "6NT",
                        "tricks": 12,
                        "result": "made"
                    }
                }
            }
        }
    }
}

# Write test data
output_path = "app/www/hands_database.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(test_data, f, indent=2, ensure_ascii=False)

print(f"✓ Test verisi yazıldı: {output_path}")
print(f"✓ {len(test_data['events'])} turnuva, {sum(len(e['boards']) for e in test_data['events'].values())} el")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate sample hands for testing
"""

import json

# Sample hands with proper board rotation
hands_data = {
    "events": {
        "hosgoru_04_01_2026": {
            "name": "Hoşgörü Pazar Simultane",
            "date": "04.01.2026",
            "location": "Istanbul",
            "section": "A",
            "boards": {}
        }
    }
}

# 30 sample hands (rotating dealer and vulnerability)
sample_hands = [
    # Board 1
    {
        "dealer": "N", "vulnerability": "None",
        "N": {"S": "AK9", "H": "QJ8", "D": "K87", "C": "AQJ"},
        "S": {"S": "QJ876", "H": "K9", "D": "J5", "C": "K9876"},
        "E": {"S": "54", "H": "AT764", "D": "AQ962", "C": "2"},
        "W": {"S": "T32", "H": "532", "D": "T43", "C": "T543"}
    },
    # Board 2
    {
        "dealer": "E", "vulnerability": "N-S",
        "N": {"S": "KQ65", "H": "K42", "D": "A92", "C": "K65"},
        "S": {"S": "J42", "H": "Q976", "D": "K863", "C": "A2"},
        "E": {"S": "A987", "H": "A8", "D": "QT4", "C": "QJ97"},
        "W": {"S": "T3", "H": "JT53", "D": "J75", "C": "T843"}
    },
    # Board 3
    {
        "dealer": "S", "vulnerability": "E-W",
        "N": {"S": "A862", "H": "AKQ", "D": "962", "C": "AQ8"},
        "S": {"S": "KQ97", "H": "J8", "D": "K73", "C": "KJT5"},
        "E": {"S": "JT54", "H": "9764", "D": "QT", "C": "9742"},
        "W": {"S": "3", "H": "T532", "D": "AJ854", "C": "963"}
    },
    # Board 4
    {
        "dealer": "W", "vulnerability": "Both",
        "N": {"S": "KQJ8", "H": "AK6", "D": "K42", "C": "AT2"},
        "S": {"S": "AT6", "H": "J842", "D": "A986", "C": "K8"},
        "E": {"S": "9532", "H": "T", "D": "QT5", "C": "Q9765"},
        "W": {"S": "74", "H": "Q9753", "D": "J3", "C": "J543"}
    },
    # Board 5
    {
        "dealer": "N", "vulnerability": "E-W",
        "N": {"S": "KJ98", "H": "K6", "D": "AKJ8", "C": "AK5"},
        "S": {"S": "A6", "H": "AQT95", "D": "Q7", "C": "J984"},
        "E": {"S": "QT5432", "H": "J87", "D": "96", "C": "Q7"},
        "W": {"S": "7", "H": "432", "D": "T542", "C": "T6322"}
    },
    # Board 6
    {
        "dealer": "E", "vulnerability": "Both",
        "N": {"S": "A954", "H": "K", "D": "AKJ742", "C": "Q6"},
        "S": {"S": "QJ83", "H": "QJ542", "D": "85", "C": "54"},
        "E": {"S": "K7", "H": "987", "D": "Q963", "C": "AK97"},
        "W": {"S": "T62", "H": "AT63", "D": "T", "C": "JT832"}
    },
    # Board 7
    {
        "dealer": "S", "vulnerability": "None",
        "N": {"S": "KQ7", "H": "AKJ9", "D": "K4", "C": "AK92"},
        "S": {"S": "AJ8", "H": "Q8765", "D": "A82", "C": "J8"},
        "E": {"S": "T9543", "H": "4", "D": "J96", "C": "QT73"},
        "W": {"S": "62", "H": "T32", "D": "QT753", "C": "654"}
    },
    # Board 8
    {
        "dealer": "W", "vulnerability": "N-S",
        "N": {"S": "AKJ6", "H": "AK8", "D": "K95", "C": "AK4"},
        "S": {"S": "QT98", "H": "QJT2", "D": "AJ2", "C": "Q3"},
        "E": {"S": "543", "H": "96", "D": "T876", "C": "JT987"},
        "W": {"S": "72", "H": "5743", "D": "Q43", "C": "652"}
    },
    # Board 9
    {
        "dealer": "N", "vulnerability": "Both",
        "N": {"S": "AKQ", "H": "AKQ", "D": "AKQ", "C": "AKQ"},
        "S": {"S": "JT98", "H": "JT9", "D": "JT9", "C": "JT9"},
        "E": {"S": "76543", "H": "8765", "D": "8765", "C": "8"},
        "W": {"S": "2", "H": "432", "D": "432", "C": "76543"}
    },
    # Board 10
    {
        "dealer": "E", "vulnerability": "None",
        "N": {"S": "AKJ98", "H": "AKJ9", "D": "AK", "C": "AK"},
        "S": {"S": "QT76", "H": "Q8", "D": "QJ", "C": "QJ98"},
        "E": {"S": "54", "H": "T765", "D": "T987", "C": "T76"},
        "W": {"S": "32", "H": "432", "D": "654", "C": "5432"}
    }
]

# Fill remaining boards with rotated hands
for i in range(10, 30):
    base_hand = sample_hands[i % len(sample_hands)]
    hands_data["events"]["hosgoru_04_01_2026"]["boards"][str(i + 1)] = {
        "dealer": base_hand["dealer"],
        "vulnerability": base_hand["vulnerability"],
        "hands": {
            "North": base_hand["N"],
            "South": base_hand["S"],
            "East": base_hand["E"],
            "West": base_hand["W"]
        },
        "results": [],
        "doubleVDummy": {
            "table": {},
            "par": "TBD",
            "date_generated": "2026-01-05"
        }
    }

# Add first 10 boards with proper hand names
for i, hand in enumerate(sample_hands):
    hands_data["events"]["hosgoru_04_01_2026"]["boards"][str(i + 1)] = {
        "dealer": hand["dealer"],
        "vulnerability": hand["vulnerability"],
        "hands": {
            "North": hand["N"],
            "South": hand["S"],
            "East": hand["E"],
            "West": hand["W"]
        },
        "results": [],
        "doubleVDummy": {
            "table": {},
            "par": "TBD",
            "date_generated": "2026-01-05"
        }
    }

# Save
with open(r'C:\Users\metin\Desktop\BRIC\app\www\hands_database.json', 'w', encoding='utf-8') as f:
    json.dump(hands_data, f, ensure_ascii=False, indent=2)

print(f"✅ Generated {len(hands_data['events']['hosgoru_04_01_2026']['boards'])} hands")

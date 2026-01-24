#!/usr/bin/env python3
"""
Regenerate hands display HTML files from current database
Uses correct N/W/E/S mapping
"""

import json
from datetime import datetime

def generate_hands_preview():
    """Generate preview HTML from hands database"""
    
    # Load hands
    hands = json.load(open('hands_database.json'))
    
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hands Preview - Regenerated</title>
    <style>
        body { font-family: Arial; background: #1a1a2e; color: #fff; padding: 20px; margin: 0; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #00d9ff; text-align: center; }
        .info-bar { text-align: center; color: #aaa; margin-bottom: 20px; }
        .board { background: #16213e; border: 2px solid #0f3460; margin: 15px 0; padding: 20px; border-radius: 8px; }
        .board-header { display: flex; justify-content: space-between; margin-bottom: 15px; }
        .board-title { font-size: 1.2em; color: #00d9ff; font-weight: bold; }
        .board-meta { color: #aaa; font-size: 0.9em; }
        .hands { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 15px 0; }
        .hand { background: #0f3460; padding: 15px; border-radius: 5px; border-left: 4px solid #00d9ff; }
        .position { font-weight: bold; color: #00d9ff; margin-bottom: 8px; font-size: 1.1em; }
        .cards { font-family: 'Courier New'; background: #1a1a2e; padding: 10px; border-radius: 3px; color: #fff; }
        .dd-info { margin-top: 10px; padding: 10px; background: #0f3460; border-radius: 3px; color: #00ff00; font-weight: bold; }
        .error { color: #ff0000; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Bridge Hands Database Preview</h1>
        <div class="info-bar">
            <p>Generated: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
            <p>Total Hands: ''' + str(len(hands)) + '''</p>
        </div>
'''
    
    for hand in hands[:15]:  # First 15 hands
        board = hand.get('board', 'N/A')
        date = hand.get('date', 'N/A')
        event = hand.get('event_id', 'N/A')
        dealer = hand.get('dealer', 'N/A')
        vuln = hand.get('vulnerability', 'None')
        dd_result = hand.get('dd_analysis', {})
        optimum = dd_result.get('optimum', {}).get('text', 'Pending')
        
        html += f'''        <div class="board">
            <div class="board-header">
                <div class="board-title">Board {board}</div>
                <div class="board-meta">{date} | Event {event}</div>
            </div>
            <div class="board-meta">Dealer: <strong>{dealer}</strong> | Vuln: <strong>{vuln}</strong></div>
            <div class="hands">
                <div class="hand">
                    <div class="position">N (North)</div>
                    <div class="cards">{hand.get('N', 'ERROR')}</div>
                </div>
                <div class="hand">
                    <div class="position">E (East)</div>
                    <div class="cards">{hand.get('E', 'ERROR')}</div>
                </div>
                <div class="hand">
                    <div class="position">S (South)</div>
                    <div class="cards">{hand.get('S', 'ERROR')}</div>
                </div>
                <div class="hand">
                    <div class="position">W (West)</div>
                    <div class="cards">{hand.get('W', 'ERROR')}</div>
                </div>
            </div>
            <div class="dd-info">DD Result: {optimum}</div>
        </div>
'''
    
    html += '''    </div>
</body>
</html>
'''
    
    with open('hands_preview_regenerated.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'✅ Generated: hands_preview_regenerated.html ({len(hands)} hands)')

if __name__ == '__main__':
    generate_hands_preview()

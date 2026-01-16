#!/usr/bin/env python3
"""
Generate BridgeBase LIN format links for all tournament boards.
Uses the correct LIN format that BridgeBase hand viewer expects.
"""

import json
import urllib.parse

def dealer_to_position(dealer):
    """Convert dealer letter (N, E, S, W) to position (1, 2, 3, 4)"""
    dealer_map = {'N': 1, 'E': 2, 'S': 3, 'W': 4}
    return dealer_map.get(dealer, 1)

def hands_to_lin_format(hands, dealer):
    """
    Convert hand dict to LIN format.
    Format: West,North,East (South is implicit)
    Suits in order: S, H, D, C
    """
    def format_hand(hand_dict):
        """Format a single hand as suit+cards string"""
        result = ""
        for suit in ['S', 'H', 'D', 'C']:
            cards = hand_dict.get(suit, '')
            if cards:
                result += suit + cards
            else:
                result += suit  # Empty suit still needs the letter
        return result
    
    # Order for LIN: West, North, East
    west_lin = format_hand(hands['West'])
    north_lin = format_hand(hands['North'])
    east_lin = format_hand(hands['East'])
    
    return f"{west_lin},{north_lin},{east_lin}"

def vulnerability_to_code(vuln):
    """Convert vulnerability text to code"""
    vuln_map = {
        'None': '0',
        'N-S': '1',
        'E-W': '2',
        'Both': '3'
    }
    return vuln_map.get(vuln, '0')

def generate_lin_url(board_num, hands, dealer, vuln):
    """Generate full BridgeBase LIN URL"""
    dealer_pos = dealer_to_position(dealer)
    hands_str = hands_to_lin_format(hands, dealer)
    vuln_code = vulnerability_to_code(vuln)
    
    # LIN format: md|<dealer_pos><hands>
    lin_string = f"qx|o1|md|{dealer_pos}{hands_str}|rh||ah|Board%20{board_num}|sv|{vuln_code}|pg||"
    
    url = f"https://www.bridgebase.com/tools/handviewer.html?lin={lin_string}"
    return url, lin_string

def main():
    # Load database
    with open('app/www/hands_database.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    event = db['events']['hosgoru_04_01_2026']
    boards = event['boards']
    
    print("\n" + "="*80)
    print("BRIDGEBASE LIN FORMAT LINKS - ALL 30 BOARDS".center(80))
    print("="*80)
    
    results = []
    
    for board_num in range(1, 31):
        board_key = str(board_num)
        if board_key not in boards:
            continue
        
        board = boards[board_key]
        hands = board['hands']
        dealer = board['dealer']
        vuln = board['vulnerability']
        
        url, lin_str = generate_lin_url(board_num, hands, dealer, vuln)
        
        results.append({
            'board': board_num,
            'dealer': dealer,
            'vulnerability': vuln,
            'lin_string': lin_str,
            'url': url
        })
        
        print(f"\n📋 Board {board_num}")
        print(f"   Dealer: {dealer} | Vulnerability: {vuln}")
        print(f"   LIN: {lin_str}")
        print(f"   URL: {url}")
    
    # Save results to JSON
    with open('app/www/lin_links.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print(f"✅ Generated LIN links for {len(results)} boards")
    print("📁 Saved to: app/www/lin_links.json")
    print("="*80)
    
    # Create HTML page with clickable links
    generate_html_viewer(results)
    
    return results

def generate_html_viewer(results):
    """Generate an HTML page with clickable LIN links"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BridgeBase LIN Links - All Boards</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .boards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .board-card {
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        .board-card:hover {
            border-color: #667eea;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
            transform: translateY(-2px);
        }
        .board-header {
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .board-info {
            font-size: 12px;
            color: #666;
            margin-bottom: 15px;
            line-height: 1.6;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
        }
        .info-label {
            font-weight: 600;
            color: #555;
        }
        .lin-string {
            background: #f0f0f0;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            margin: 10px 0;
            word-break: break-all;
            max-height: 60px;
            overflow-y: auto;
            color: #333;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        .btn {
            flex: 1;
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-align: center;
            text-decoration: none;
            display: inline-block;
        }
        .btn-view {
            background: #667eea;
            color: white;
        }
        .btn-view:hover {
            background: #5568d3;
            transform: scale(1.02);
        }
        .btn-copy {
            background: #e0e0e0;
            color: #333;
        }
        .btn-copy:hover {
            background: #d0d0d0;
        }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }
        .badge-dealer {
            background: #fff3cd;
            color: #856404;
        }
        .badge-vuln {
            background: #d1ecf1;
            color: #0c5460;
        }
        .stats {
            background: #f0f0f0;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
        }
        .stat-item {
            display: inline-block;
            margin: 0 20px;
        }
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: #333;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 8px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
            white-space: normal;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        .footer {
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌉 BridgeBase Hand Viewer Links</h1>
        <p class="subtitle">Click any board to view hands in BridgeBase Hand Viewer</p>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">30</div>
                <div class="stat-label">Total Boards</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">✓</div>
                <div class="stat-label">LIN Format Ready</div>
            </div>
        </div>
        
        <div class="boards-grid">
"""
    
    for result in results:
        board_num = result['board']
        dealer = result['dealer']
        vuln = result['vulnerability']
        url = result['url']
        lin = result['lin_string']
        
        # Determine badge colors for vulnerability
        vuln_short = {
            'None': 'None',
            'N-S': 'N-S',
            'E-W': 'E-W',
            'Both': 'Both'
        }.get(vuln, vuln)
        
        html += f"""
            <div class="board-card">
                <div class="board-header">
                    <span>Board {board_num}</span>
                    <span style="font-size: 16px;">♠</span>
                </div>
                <div class="board-info">
                    <div class="info-row">
                        <span class="info-label">Dealer:</span>
                        <span class="badge badge-dealer">{dealer}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Vulnerability:</span>
                        <span class="badge badge-vuln">{vuln_short}</span>
                    </div>
                </div>
                <div class="lin-string" title="LIN Format String">{lin}</div>
                <div class="button-group">
                    <a href="{url}" target="_blank" class="btn btn-view">📂 View Hands</a>
                    <button class="btn btn-copy" onclick="copyToClipboard('{lin}', this)">📋 Copy LIN</button>
                </div>
            </div>
"""
    
    html += """
        </div>
        
        <div class="footer">
            <p>💡 <strong>Tip:</strong> Copy LIN format to use with automated DD solvers or other bridge analysis tools.</p>
            <p>Generated on: """ + str(json.dumps(results[0]))[:10] + """</p>
        </div>
    </div>
    
    <script>
        function copyToClipboard(text, button) {
            navigator.clipboard.writeText(text).then(() => {
                const originalText = button.textContent;
                button.textContent = '✓ Copied!';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000);
            });
        }
    </script>
</body>
</html>
"""
    
    with open('app/www/lin_links.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("\n📄 Also created: app/www/lin_links.html (view in browser)")

if __name__ == '__main__':
    main()

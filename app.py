import os
import json
import subprocess
import threading
from flask import Flask, send_file, jsonify, request
from pathlib import Path

app = Flask(__name__, static_folder='.', static_url_path='')

# Secret key for webhook authentication (set in Railway environment)
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'bric-update-secret-2026')

def safe_send_file(filename):
    """Safely send a file, return index.html if not found"""
    try:
        filepath = Path(filename)
        if filepath.exists():
            return send_file(filename)
    except Exception as e:
        print(f"Error serving {filename}: {e}")
    
    # Fallback to index.html
    try:
        return send_file('index.html')
    except:
        return "Not found", 404


def run_update_async(update_type='all'):
    """Run the full update pipeline asynchronously
    
    Pipeline steps:
    1. scores   - Fetch tournament scores from Vugraph
    2. hands    - Fetch board hands from Vugraph
    3. dd       - Calculate Double Dummy analysis
    4. analysis - Update site statistics
    """
    try:
        # Use full_update_pipeline.py for complete workflow
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'full_update_pipeline.py')
        
        if update_type == 'scores':
            cmd = ['python', script_path, '--step', 'scores']
        elif update_type == 'hands':
            cmd = ['python', script_path, '--step', 'hands']
        elif update_type == 'dd':
            cmd = ['python', script_path, '--step', 'dd']
        elif update_type == 'analysis':
            cmd = ['python', script_path, '--step', 'analysis']
        else:
            # Run full pipeline: scores → hands → dd → analysis
            cmd = ['python', script_path]
        
        print(f"[PIPELINE] Starting: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)  # 20 min timeout
        print(f"[PIPELINE] Completed with return code: {result.returncode}")
        if result.stdout:
            # Log last 1000 chars of output
            print(f"[PIPELINE] Output:\n{result.stdout[-1000:]}")
        if result.stderr:
            print(f"[PIPELINE] Errors:\n{result.stderr[-500:]}")
    except subprocess.TimeoutExpired:
        print(f"[PIPELINE] Timeout after 1200 seconds")
    except Exception as e:
        print(f"[PIPELINE] Error running update: {e}")

@app.route('/')
def index():
    return safe_send_file('index.html')

@app.route('/style.css')
def style():
    return safe_send_file('style.css')

@app.route('/script.js')
def script():
    return safe_send_file('script.js')

@app.route('/tr.json')
def tr():
    return safe_send_file('tr.json')

@app.route('/en.json')
def en():
    return safe_send_file('en.json')

@app.route('/api/data')
def api_data():
    return safe_send_file('database.json')

@app.route('/database.json')
def database():
    return safe_send_file('database.json')

@app.route('/api/hands')
def api_hands():
    return safe_send_file('hands_database.json')

@app.route('/hands_database.json')
def hands():
    return safe_send_file('hands_database.json')

@app.route('/dd_viewer')
@app.route('/dd_viewer.html')
def dd_viewer():
    return safe_send_file('double_dummy/dd_viewer.html')

@app.route('/double_dummy/<path:filename>')
def dd_files(filename):
    return safe_send_file(f'double_dummy/{filename}')

@app.route('/api/calculate_all_dd', methods=['POST'])
def calculate_all_dd():
    """Placeholder for DD calculation - returns success"""
    return jsonify({'success': True, 'message': 'DD calculation queued'})


# ============== WEBHOOK ENDPOINTS FOR RAILWAY ==============

@app.route('/api/webhook/update', methods=['POST'])
def webhook_update():
    """
    Webhook endpoint to trigger database updates from Railway or external schedulers
    
    Usage:
        POST /api/webhook/update
        Headers: X-Webhook-Secret: <secret>
        Body (optional): {"type": "all" | "scores" | "hands" | "dd" | "analysis"}
    
    Pipeline (type=all):
        1. scores   - Fetch tournament scores from Vugraph calendar
        2. hands    - Fetch board hands from Vugraph boarddetails
        3. dd       - Calculate Double Dummy analysis (endplay)
        4. analysis - Update site statistics and reports
    """
    # Verify secret
    provided_secret = request.headers.get('X-Webhook-Secret', '')
    if provided_secret != WEBHOOK_SECRET:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get update type from request body
    data = request.get_json(silent=True) or {}
    update_type = data.get('type', 'all')
    
    if update_type not in ['all', 'scores', 'hands', 'dd', 'analysis']:
        return jsonify({'error': 'Invalid type. Use: all, scores, hands, dd, or analysis'}), 400
    
    # Run update in background thread
    thread = threading.Thread(target=run_update_async, args=(update_type,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': f'Pipeline triggered ({update_type})',
        'pipeline_steps': ['scores', 'hands', 'dd', 'analysis'] if update_type == 'all' else [update_type],
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })


@app.route('/api/webhook/status', methods=['GET'])
def webhook_status():
    """Check the last update status and database info including DD analysis"""
    try:
        # Get database stats
        with open('database.json', 'r', encoding='utf-8') as f:
            db_data = json.load(f)
        
        with open('hands_database.json', 'r', encoding='utf-8') as f:
            hands_data = json.load(f)
        
        # Count records
        if isinstance(db_data, dict):
            score_count = len(db_data.get('legacy_records', []))
            last_updated = db_data.get('last_updated', 'Unknown')
            metadata = db_data.get('metadata', {})
        else:
            score_count = len(db_data)
            last_updated = 'Unknown'
            metadata = {}
        
        hands_count = len(hands_data)
        
        # Count hands with DD analysis
        hands_with_dd = len([h for h in hands_data if h.get('dd_analysis')])
        hands_with_optimum = len([h for h in hands_data if h.get('optimum')])
        hands_with_lott = len([h for h in hands_data if h.get('lott')])
        
        # Get latest dates (properly sorted by date)
        def parse_date(d):
            try:
                parts = d.split('.')
                return (int(parts[2]), int(parts[1]), int(parts[0]))
            except:
                return (0, 0, 0)
        
        if isinstance(db_data, dict) and 'legacy_records' in db_data:
            dates = [r.get('Tarih', '') for r in db_data['legacy_records'] if r.get('Tarih')]
        elif isinstance(db_data, list):
            dates = [r.get('Tarih', '') for r in db_data if isinstance(r, dict) and r.get('Tarih')]
        else:
            dates = []
        
        # Get hands dates (check both formats)
        hands_dates = []
        for h in hands_data:
            d = h.get('date') or h.get('Tarih', '')
            if d:
                hands_dates.append(d)
        
        latest_score = max(dates, key=parse_date) if dates else None
        latest_hands = max(hands_dates, key=parse_date) if hands_dates else None
        
        # Unique tournament dates
        unique_dates = set(hands_dates)
        
        return jsonify({
            'status': 'ok',
            'database': {
                'scores': score_count,
                'hands': hands_count,
                'hands_with_dd': hands_with_dd,
                'hands_with_optimum': hands_with_optimum,
                'hands_with_lott': hands_with_lott,
                'unique_tournament_dates': len(unique_dates),
                'last_updated': last_updated,
                'latest_score_date': latest_score,
                'latest_hands_date': latest_hands
            },
            'metadata': metadata,
            'pipeline': {
                'steps': ['scores', 'hands', 'dd', 'analysis'],
                'description': 'Full pipeline: Vugraph scores → Vugraph hands → DD analysis → Site stats'
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/cron/update', methods=['GET', 'POST'])
def cron_update():
    """
    Cron endpoint for Railway scheduled jobs
    Can be called with GET (for simple cron) or POST
    
    Add to Railway cron: curl https://your-app.railway.app/api/cron/update?secret=<secret>
    """
    # Verify secret (from query param or header)
    provided_secret = request.args.get('secret', '') or request.headers.get('X-Webhook-Secret', '')
    if provided_secret != WEBHOOK_SECRET:
        return jsonify({'error': 'Unauthorized'}), 401
    
    update_type = request.args.get('type', 'all')
    
    # Run update in background
    thread = threading.Thread(target=run_update_async, args=(update_type,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': f'Cron update triggered ({update_type})',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })


# ============== PAIR SUMMARY ENDPOINT ==============

@app.route('/api/pair-summary', methods=['GET'])
def api_pair_summary():
    """
    Fetch pair summary from Vugraph boarddetails for a specific event, pair, and direction
    
    Query params:
        event: Event ID (e.g., 405278)
        pair: Pair number (e.g., 12)
        direction: NS or EW
        section: Section letter (default: A)
    
    Returns board-by-board results with:
        - contract (e.g., 4♥)
        - declarer (N, S, E, W)
        - result (=, +1, -1, etc.)
        - lead (e.g., ♦6)
        - score_ns, score_ew
        - percent_ns, percent_ew
    """
    import requests
    from bs4 import BeautifulSoup
    
    event_id = request.args.get('event')
    pair_num = request.args.get('pair')
    direction = request.args.get('direction', 'NS')
    section = request.args.get('section', 'A')
    
    if not event_id or not pair_num:
        return jsonify({'error': 'Missing event or pair parameter'}), 400
    
    try:
        results = []
        
        # Fetch each board's details (boards 1-30)
        for board_num in range(1, 31):
            url = f"https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section={section}&pair={pair_num}&direction={direction}&board={board_num}"
            
            try:
                response = requests.get(url, timeout=10)
                response.encoding = 'iso-8859-9'  # Turkish encoding
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find the highlighted row (class="fantastic" for the requesting pair's result)
                fantastic_row = soup.find('td', class_='fantastic')
                
                if fantastic_row:
                    row = fantastic_row.find_parent('tr')
                    cells = row.find_all('td', class_='fantastic')
                    
                    if len(cells) >= 8:
                        # Parse contract (e.g., "4<img>H")
                        contract_cell = cells[0]
                        contract = parse_contract_cell(contract_cell)
                        
                        # Declarer
                        declarer = cells[1].get_text(strip=True)
                        
                        # Result (=, +1, -1, -2, etc.)
                        result = cells[2].get_text(strip=True)
                        
                        # Lead (e.g., "D6" -> ♦6)
                        lead_cell = cells[3]
                        lead = parse_lead_cell(lead_cell)
                        
                        # Scores - cells[4] is NS, cells[5] is EW
                        score_ns = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
                        score_ew = cells[5].get_text(strip=True) if not cells[5].find('img') else ''
                        
                        # Percentages - cells[6] is NS%, cells[7] is EW%
                        pct_ns = cells[6].get_text(strip=True) if not cells[6].find('img') else ''
                        pct_ew = cells[7].get_text(strip=True) if not cells[7].find('img') else ''
                        
                        results.append({
                            'board': board_num,
                            'contract': contract,
                            'declarer': declarer,
                            'result': result,
                            'lead': lead,
                            'score_ns': score_ns,
                            'score_ew': score_ew,
                            'percent_ns': pct_ns,
                            'percent_ew': pct_ew
                        })
                else:
                    # Try finding in results class (non-highlighted)
                    results_rows = soup.find_all('tr')
                    for rrow in results_rows:
                        cells = rrow.find_all('td', class_='results')
                        if len(cells) >= 8:
                            # This is a valid result row
                            contract = parse_contract_cell(cells[0])
                            declarer = cells[1].get_text(strip=True)
                            result = cells[2].get_text(strip=True)
                            lead = parse_lead_cell(cells[3])
                            
                            score_ns = cells[4].get_text(strip=True) if not cells[4].find('img') else ''
                            score_ew = cells[5].get_text(strip=True) if not cells[5].find('img') else ''
                            pct_ns = cells[6].get_text(strip=True) if not cells[6].find('img') else ''
                            pct_ew = cells[7].get_text(strip=True) if not cells[7].find('img') else ''
                            
                            results.append({
                                'board': board_num,
                                'contract': contract,
                                'declarer': declarer,
                                'result': result,
                                'lead': lead,
                                'score_ns': score_ns,
                                'score_ew': score_ew,
                                'percent_ns': pct_ns,
                                'percent_ew': pct_ew
                            })
                            break  # Only first row for this pair
                            
            except Exception as e:
                # Skip boards that fail to load
                continue
        
        # Get pair names and tournament date from first board page
        pair_names = ""
        tournament_date = ""
        try:
            url = f"https://clubs.vugraph.com/hosgoru/boarddetails.php?event={event_id}&section={section}&pair={pair_num}&direction={direction}&board=1"
            response = requests.get(url, timeout=10)
            response.encoding = 'iso-8859-9'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get pair names from h3
            h3 = soup.find('h3')
            if h3:
                text = h3.get_text(strip=True)
                # Extract names: "... ZÜLKÜF TEOMAN HAZNECI - HIKMET ALBAYRAK ... Bord 1"
                if '...' in text:
                    parts = text.split('...')
                    if len(parts) >= 2:
                        pair_names = parts[1].strip()
                        if 'Bord' in pair_names:
                            pair_names = pair_names.split('Bord')[0].strip()
            
            # Get tournament date from h2 (format: "Çiftler Cuma Turnuvası - 17.01.2026")
            h2 = soup.find('h2')
            if h2:
                h2_text = h2.get_text(strip=True)
                # Extract date
                import re
                date_match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', h2_text)
                if date_match:
                    day, month, year = date_match.groups()
                    # Format: "17 Ocak 2026 Cuma"
                    from datetime import datetime
                    try:
                        dt = datetime(int(year), int(month), int(day))
                        # Turkish day names
                        day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
                        month_names = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 
                                      'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
                        day_name = day_names[dt.weekday()]
                        month_name = month_names[int(month)]
                        tournament_date = f"{int(day)} {month_name} {year} {day_name}"
                    except:
                        tournament_date = f"{day}.{month}.{year}"
        except:
            pass
        
        return jsonify({
            'success': True,
            'pair_names': pair_names,
            'tournament_date': tournament_date,
            'direction': direction,
            'event_id': event_id,
            'pair_num': pair_num,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def parse_contract_cell(cell):
    """Parse contract cell with suit image (e.g., '4<img src="h.gif">') -> '4♥'"""
    text = cell.get_text(strip=True)
    img = cell.find('img')
    if img:
        alt = img.get('alt', '').upper()
        src = img.get('src', '').lower()
        suit = ''
        if 's' in alt or 's.gif' in src:
            suit = '♠'
        elif 'h' in alt or 'h.gif' in src:
            suit = '♥'
        elif 'd' in alt or 'd.gif' in src:
            suit = '♦'
        elif 'c' in alt or 'c.gif' in src:
            suit = '♣'
        return text + suit
    return text


def parse_lead_cell(cell):
    """Parse lead cell (e.g., 'D6') -> '♦6'"""
    text = cell.get_text(strip=True)
    if len(text) >= 2:
        suit_char = text[0].upper()
        card = text[1:]
        suit_map = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'}
        if suit_char in suit_map:
            return suit_map[suit_char] + card
    return text


# ============================================================

@app.route('/<path:filename>')
def serve_file(filename):
    return safe_send_file(filename)

@app.errorhandler(404)
def not_found(e):
    return safe_send_file('index.html')

@app.errorhandler(500)
def server_error(e):
    print(f"Server error: {e}")
    return "Internal server error", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[OK] Starting Flask server on port {port}")
    print(f"[OK] Open http://localhost:{port}/hands_bbo_view.html")
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except OSError as e:
        print(f"[ERROR] {e}")
        print(f"  Port {port} may already be in use. Try PORT=5001 python app.py")

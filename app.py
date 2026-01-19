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
    Fetch pair summary from Vugraph for a specific event, pair, and direction
    
    Query params:
        event: Event ID (e.g., 405278)
        pair: Pair number (e.g., 12)
        direction: NS or EW
        section: Section letter (default: A)
    
    Returns board-by-board results with contract info calculated from score
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
        # Fetch pair summary from Vugraph
        url = f"https://clubs.vugraph.com/hosgoru/pairsummary.php?event={event_id}&section={section}&pair={pair_num}&direction={direction}"
        
        response = requests.get(url, timeout=30)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get pair names from page title (h4)
        pair_names = ""
        h4 = soup.find('h4')
        if h4:
            text = h4.get_text(strip=True)
            if 'Çift Özeti' in text:
                pair_names = text.replace('Çift Özeti', '').strip()
        
        # Find the main results table
        tables = soup.find_all('table')
        results = []
        
        if len(tables) >= 2:
            main_table = tables[1]  # Second table has the data
            rows = main_table.find_all('tr')
            
            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 4:
                    board = cells[0].get_text(strip=True)
                    opponent = cells[1].get_text(strip=True)
                    result_score = cells[2].get_text(strip=True)
                    mp_score = cells[3].get_text(strip=True)
                    
                    # Parse result score to int
                    try:
                        result_int = int(result_score)
                    except:
                        result_int = 0
                    
                    # Estimate contract from score (simplified)
                    contract_info = estimate_contract_from_score(result_int, direction)
                    
                    results.append({
                        'board': board,
                        'opponent': opponent,
                        'result': result_score,
                        'score': mp_score,
                        'contract': contract_info.get('contract', '?'),
                        'declarer': contract_info.get('declarer', '?'),
                        'contract_display': contract_info.get('display', '?')
                    })
        
        return jsonify({
            'success': True,
            'pair_names': pair_names,
            'direction': direction,
            'event_id': event_id,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def estimate_contract_from_score(score, pair_direction):
    """
    Estimate the likely contract and declarer from the result score.
    This is a heuristic based on common bridge scoring.
    
    Score patterns:
    - Positive for NS: NS made contract or set EW
    - Negative for NS: EW made contract or NS went down
    
    Common scores:
    - 420: 4♠/4♥ made, not vul
    - 620: 4♠/4♥ made, vul
    - 430: 3NT+1, not vul
    - 400: 3NT made, not vul
    - 600: 3NT made, vul
    - 110/140: Partial in major
    - 90/110/130: Partial in minor
    - 50/100: 1 down
    """
    
    # Determine who likely declared based on score sign and pair direction
    if pair_direction == 'NS':
        if score > 0:
            # NS positive: NS made or EW went down
            declarer = 'NS'
        else:
            # NS negative: EW made or NS went down
            declarer = 'EW'
    else:  # EW
        if score > 0:
            declarer = 'EW'
        else:
            declarer = 'NS'
    
    abs_score = abs(score)
    contract = '?'
    
    # Major game scores
    if abs_score in [420, 450, 480, 510]:
        contract = '4♠/♥'
    elif abs_score in [620, 650, 680, 710]:
        contract = '4♠/♥'
    # NT game scores
    elif abs_score in [400, 430, 460, 490]:
        contract = '3NT'
    elif abs_score in [600, 630, 660, 690]:
        contract = '3NT'
    # Minor game scores
    elif abs_score in [400, 920, 1370, 1390]:
        contract = '5♣/♦'
    # Slam scores
    elif abs_score >= 980 and abs_score <= 1020:
        contract = '6♠/♥'
    elif abs_score >= 1430 and abs_score <= 1470:
        contract = '6♠/♥'
    elif abs_score >= 990 and abs_score <= 1020:
        contract = '6NT'
    elif abs_score >= 1500:
        contract = '7x'
    # Partial scores - majors
    elif abs_score in [110, 140, 170, 200]:
        contract = '2♠/♥'
    elif abs_score in [80, 50]:
        contract = '1♠/♥'
    # Partial scores - minors
    elif abs_score in [90, 110, 130]:
        contract = '2♣/♦'
    # Down scores
    elif abs_score in [50, 100, 150, 200, 250, 300]:
        contract = 'Down'
    elif abs_score in [100, 200, 300, 500, 800, 1100]:
        contract = 'Down (Vul)'
    # Common partials
    elif abs_score in [120, 150, 180]:
        contract = '2-3♠/♥'
    
    display = f"{contract} ({declarer})" if contract != '?' else '?'
    
    return {
        'contract': contract,
        'declarer': declarer,
        'display': display
    }


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

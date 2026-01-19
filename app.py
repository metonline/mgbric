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
    """Run the scheduled update script asynchronously"""
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scheduled_update.py')
        
        if update_type == 'scores':
            cmd = ['python', script_path, '--scores-only']
        elif update_type == 'hands':
            cmd = ['python', script_path, '--hands-only']
        else:
            cmd = ['python', script_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        print(f"[UPDATE] Completed with return code: {result.returncode}")
        if result.stdout:
            print(f"[UPDATE] Output: {result.stdout[-500:]}")
        if result.stderr:
            print(f"[UPDATE] Errors: {result.stderr[-500:]}")
    except Exception as e:
        print(f"[UPDATE] Error running update: {e}")

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
        Body (optional): {"type": "all" | "scores" | "hands"}
    """
    # Verify secret
    provided_secret = request.headers.get('X-Webhook-Secret', '')
    if provided_secret != WEBHOOK_SECRET:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get update type from request body
    data = request.get_json(silent=True) or {}
    update_type = data.get('type', 'all')
    
    if update_type not in ['all', 'scores', 'hands']:
        return jsonify({'error': 'Invalid type. Use: all, scores, or hands'}), 400
    
    # Run update in background thread
    thread = threading.Thread(target=run_update_async, args=(update_type,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': f'Update triggered ({update_type})',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })


@app.route('/api/webhook/status', methods=['GET'])
def webhook_status():
    """Check the last update status and database info"""
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
        else:
            score_count = len(db_data)
            last_updated = 'Unknown'
        
        hands_count = len(hands_data)
        
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
        
        hands_dates = [h.get('Tarih', '') for h in hands_data if h.get('Tarih')]
        
        latest_score = max(dates, key=parse_date) if dates else None
        latest_hands = max(hands_dates, key=parse_date) if hands_dates else None
        
        return jsonify({
            'status': 'ok',
            'database': {
                'scores': score_count,
                'hands': hands_count,
                'last_updated': last_updated,
                'latest_score_date': latest_score,
                'latest_hands_date': latest_hands
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

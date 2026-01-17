import os
import json
from flask import Flask, send_file, jsonify
from pathlib import Path

app = Flask(__name__, static_folder='.', static_url_path='')

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

@app.route('/api/calculate_all_dd', methods=['POST'])
def calculate_all_dd():
    """Placeholder for DD calculation - returns success"""
    return jsonify({'success': True, 'message': 'DD calculation queued'})

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

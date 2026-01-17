from flask import Flask, send_file, jsonify
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html', mimetype='text/html')

@app.route('/style.css')
def style():
    return send_file('style.css', mimetype='text/css')

@app.route('/script.js')
def script():
    return send_file('script.js', mimetype='text/javascript')

@app.route('/tr.json')
def tr_trans():
    return send_file('tr.json', mimetype='application/json')

@app.route('/en.json')
def en_trans():
    return send_file('en.json', mimetype='application/json')

@app.route('/api/data')
def api_data():
    """Serve database as JSON API"""
    return send_file('database.json', mimetype='application/json')

@app.route('/database.json')
def database():
    return send_file('database.json', mimetype='application/json')

@app.route('/<path:filename>')
def serve_file(filename):
    try:
        return send_file(filename)
    except:
        return send_file('index.html', mimetype='text/html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Flask on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

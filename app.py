import os
from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/style.css')
def style():
    return send_file('style.css')

@app.route('/script.js')
def script():
    return send_file('script.js')

@app.route('/tr.json')
def tr():
    return send_file('tr.json')

@app.route('/en.json')
def en():
    return send_file('en.json')

@app.route('/api/data')
def api_data():
    return send_file('database.json')

@app.route('/database.json')
def database():
    return send_file('database.json')

@app.route('/api/hands')
def api_hands():
    try:
        return send_file('hands_database.json')
    except:
        return send_file('hands_database.json')

@app.route('/hands_database.json')
def hands():
    return send_file('hands_database.json')

@app.route('/<path:filename>')
def serve_file(filename):
    try:
        return send_file(filename)
    except:
        return send_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

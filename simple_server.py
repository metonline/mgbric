#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Add venv packages to path
venv_path = os.path.join(os.path.dirname(__file__), '.venv', 'Lib', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

from flask import Flask, send_from_directory, jsonify, Response
import json

app = Flask(__name__, static_folder=os.path.dirname(os.path.abspath(__file__)), static_url_path='')

# Cache kontrol
@app.after_request
def set_cache_control(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def home():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

# Serve database.json as JSON
@app.route('/get_database')
def get_database():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')
    try:
        with open(db_path, encoding='utf-8') as f:
            data = json.load(f)
        # Return raw JSON without Flask's additional wrapping
        return Response(json.dumps(data, ensure_ascii=False, indent=None), mimetype='application/json')
    except Exception as e:
        print(f"❌ Database load error: {e}")
        return Response(json.dumps([]), mimetype='application/json'), 404

# Serve database_temp.json as JSON
@app.route('/get_database_temp')
def get_database_temp():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database_temp.json')
    try:
        with open(db_path, encoding='utf-8') as f:
            data = json.load(f)
        return Response(json.dumps(data, ensure_ascii=False, indent=None), mimetype='application/json')
    except Exception as e:
        print(f"❌ Temp database load error: {e}")
        return Response(json.dumps([]), mimetype='application/json'), 404

@app.route('/<filename>')
def serve_static(filename):
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), filename)

if __name__ == '__main__':
    print("✓ Web sunucusu başladı: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

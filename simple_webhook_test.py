#!/usr/bin/env python3
"""
Simple webhook test server
"""
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/webhook', methods=['POST'])
def webhook():
    print(f"[WEBHOOK] Received push event")
    print(f"[WEBHOOK] Headers: {dict(request.headers)}")
    print(f"[WEBHOOK] Body: {request.get_json()}")
    return jsonify({'status': 'ok', 'message': 'Webhook received'})

if __name__ == '__main__':
    print("Starting simple test server...")
    app.run(host='127.0.0.1', port=5000, debug=False)

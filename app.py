from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return jsonify({
        'message': 'Hello from Flask backend!',
        'status': 'success',
        'timestamp': '2026-10-13 12:01:00'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Flask Backend',
        'port': 3000
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        'data': 'This is a test endpoint',
        'items': [1, 2, 3, 4, 5]
    })

@app.route('/api/echo/<message>', methods=['GET'])
def echo_message(message):
    return jsonify({
        'received': message,
        'echo': f'You said: {message}'
    })

if __name__ == '__main__':
    print("Starting Flask server on port 3000...")
    app.run(host='0.0.0.0', port=3000, debug=True, use_reloader=False)
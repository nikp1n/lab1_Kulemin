from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return f"🚀 CI/CD demo active — build timestamp: {datetime.utcnow().isoformat()}Z"

@app.route('/health')
def health():
    return jsonify(status="ready", service="lab1_Kulemin", time=datetime.utcnow().isoformat() + "Z")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

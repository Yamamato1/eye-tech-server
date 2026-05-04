from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

latest_data = {}

@app.route('/data', methods=['POST'])
def receive_data():
    global latest_data
    latest_data = request.json
    print("Received:", latest_data)
    return jsonify({"status": "OK"}), 200

@app.route('/latest', methods=['GET'])
def get_latest():
    return jsonify(latest_data)

@app.route('/')
def home():
    return "Server is running!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

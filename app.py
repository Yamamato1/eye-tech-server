from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

latest_data = {}

# 🔥 AI Insights function
def generate_insights(data):
    insights = []
    power = data.get("power", 0)

    if power > 1000:
        insights.append("⚠️ High power usage detected")
    elif power < 150:
        insights.append("💡 Low consumption - efficient usage")

    monthly_bill = power * 24 * 30 / 1000 * 0.1
    insights.append(f"📊 Estimated monthly bill: ${monthly_bill:.2f}")

    return insights


@app.route('/data', methods=['POST'])
def receive_data():
    global latest_data
    latest_data = request.json
    return jsonify({"status": "OK"}), 200


@app.route('/latest', methods=['GET'])
def get_latest():
    data = latest_data.copy()
    data["insights"] = generate_insights(data)
    return jsonify(data)


@app.route('/')
def home():
    return "Server running 🚀"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

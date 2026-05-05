from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🧠 Store data per user
user_data = {}

# 🔥 AI Insights
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


# 🧾 SAVE SURVEY (ONE TIME)
@app.route('/survey', methods=['POST'])
def save_survey():
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    user_data[user_id] = {
        "survey": data,
        "latest": {}
    }

    print(f"Survey saved for {user_id}: {data}")
    return jsonify({"status": "survey saved"})


# 📡 RECEIVE ESP32 DATA
@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    if user_id not in user_data:
        return jsonify({"error": "User not found. Submit survey first."}), 404

    user_data[user_id]["latest"] = data
    return jsonify({"status": "OK"})


# 📊 GET USER DATA
@app.route('/latest/<user_id>', methods=['GET'])
def get_latest(user_id):
    if user_id not in user_data:
        return jsonify({"error": "User not found"}), 404

    data = user_data[user_id]["latest"].copy()
    data["insights"] = generate_insights(data)

    return jsonify(data)


# 🏠 HOME
@app.route('/')
def home():
    return "Server running 🚀"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🧠 In-memory database
user_data = {}


# 🔥 ENERGY ESTIMATION (based on survey)
def estimate_usage(survey):
    total_kwh = 0

    total_kwh += survey.get("lights_count", 5) * 10 * 5 / 1000
    total_kwh += survey.get("tv_hours", 2) * 100 / 1000
    total_kwh += survey.get("washing_per_week", 1) * 500 / (7 * 1000)

    if "fridge" in survey.get("devices", []):
        total_kwh += 150 * 24 / 1000

    return total_kwh


# 🔌 DEVICE BREAKDOWN
def device_breakdown(survey, usage_flags):
    breakdown = {}

    lights = survey.get("lights_count", 5)
    breakdown["lights"] = lights * 10 if usage_flags.get("lights", True) else 0

    breakdown["tv"] = 100 if usage_flags.get("tv", False) else 0

    breakdown["washing_machine"] = 500 if usage_flags.get("washing_machine", False) else 0

    breakdown["fridge"] = 150  # always on

    return breakdown


# 🧠 AI INSIGHTS
def generate_insights(data):
    insights = []

    daily_kwh = data.get("estimated_daily_kwh", 0)

    if daily_kwh > 10:
        insights.append("⚠️ High daily consumption detected")

    if daily_kwh < 3:
        insights.append("💡 Very efficient energy usage")

    insights.append(f"📊 Monthly estimate: {round(daily_kwh*30,1)} kWh")

    return insights


# 🧾 SAVE SURVEY
@app.route('/survey', methods=['POST'])
def save_survey():
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    user_data[user_id] = {
        "survey": data,
        "latest": {},
        "factor": 1,
        "usage_flags": {}
    }

    return jsonify({"status": "saved"})


# 📡 RECEIVE DATA FROM ESP32
@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    user_id = data.get("user_id")

    if not user_id or user_id not in user_data:
        return jsonify({"error": "User not found"}), 404

    user_data[user_id]["latest"] = data
    return jsonify({"status": "ok"})


# 🔌 UPDATE DEVICE USAGE (toggles)
@app.route('/usage', methods=['POST'])
def update_usage():
    data = request.json
    user_id = data.get("user_id")

    if user_id not in user_data:
        return jsonify({"error": "User not found"}), 404

    user_data[user_id]["usage_flags"] = data.get("usage_flags", {})

    return jsonify({"status": "updated"})


# 🔁 FEEDBACK (self-learning)
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    user_id = data.get("user_id")
    real_kwh = data.get("real_kwh")

    if user_id not in user_data:
        return jsonify({"error": "User not found"}), 404

    survey = user_data[user_id]["survey"]
    predicted = estimate_usage(survey)

    factor = real_kwh / predicted if predicted > 0 else 1

    user_data[user_id]["factor"] = factor

    return jsonify({
        "status": "updated",
        "factor": round(factor, 2)
    })


# 📊 MAIN DATA ENDPOINT
@app.route('/latest/<user_id>', methods=['GET'])
def get_latest(user_id):

    if user_id not in user_data:
        return jsonify({"error": "User not found"}), 404

    user = user_data[user_id]
    survey = user["survey"]
    factor = user.get("factor", 1)
    usage_flags = user.get("usage_flags", {})

    breakdown = device_breakdown(survey, usage_flags)
    total_power = sum(breakdown.values())

    # 🔥 Convert to kWh
    daily_kwh = (total_power * 5) / 1000  # assume 5h usage
    corrected_kwh = daily_kwh * factor

    price = survey.get("price_per_kwh", 0.1)

    daily_cost = corrected_kwh * price
    monthly_cost = daily_cost * 30

    data = user["latest"].copy()

    data["power"] = total_power
    data["breakdown"] = breakdown
    data["estimated_daily_kwh"] = round(corrected_kwh, 2)
    data["estimated_monthly_kwh"] = round(corrected_kwh * 30, 2)
    data["daily_cost"] = round(daily_cost, 2)
    data["monthly_cost"] = round(monthly_cost, 2)

    data["insights"] = generate_insights(data)

    return jsonify(data)


# 🏠 HEALTH CHECK
@app.route('/')
def home():
    return "EyeTech Backend Running 🚀"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

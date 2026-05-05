from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

user_data = {}

DEVICE_POWER = {
    "lights": 10,
    "tv": 100,
    "washing_machine": 500,
    "fridge": 150
}

# 🧾 SURVEY
@app.route('/survey', methods=['POST'])
def save_survey():
    data = request.json
    user_id = data.get("user_id")

    user_data[user_id] = {
        "survey": data,
        "usage_flags": {},
        "active_devices": {},
        "history": [],
        "factor": 1
    }

    return jsonify({"status": "saved"})


# 🔌 DEVICE STATE
@app.route('/usage', methods=['POST'])
def update_usage():
    data = request.json
    user_id = data.get("user_id")

    if user_id not in user_data:
        return jsonify({"error": "User not found"}), 404

    user_data[user_id]["usage_flags"] = data.get("usage_flags", {})
    return jsonify({"status": "updated"})


# ⏱️ TRACK USAGE
@app.route('/track', methods=['POST'])
def track_usage():
    data = request.json
    user_id = data.get("user_id")
    device = data.get("device")
    action = data.get("action")

    if user_id not in user_data:
        return jsonify({"error": "User not found"}), 404

    now = datetime.now()
    user = user_data[user_id]

    if action == "on":
        user["active_devices"][device] = now

    elif action == "off":
        start_time = user["active_devices"].get(device)

        if start_time:
            duration = (now - start_time).total_seconds() / 3600

            record = {
                "device": device,
                "duration_hours": round(duration, 2),
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "date": start_time.strftime("%Y-%m-%d"),
                "day": start_time.strftime("%A")
            }

            user["history"].append(record)
            del user["active_devices"][device]

    return jsonify({"status": "tracked"})


# ⚡ ENERGY CALCULATION
def calculate_energy(user):
    survey = user["survey"]
    history = user["history"]

    total_kwh = 0

    for record in history:
        device = record["device"]
        duration = record["duration_hours"]

        if device == "lights":
            count = survey.get("lights_count", 5)
            power = count * DEVICE_POWER["lights"]
        else:
            power = DEVICE_POWER.get(device, 0)

        energy = (power * duration) / 1000
        total_kwh += energy

    return total_kwh


# 🧠 HABIT ANALYSIS
def analyze_habits(history):

    habits = {}

    for record in history:
        device = record["device"]
        day = record["day"]
        hour = int(record["start_time"].split(" ")[1].split(":")[0])

        if device not in habits:
            habits[device] = {
                "days": {},
                "hours": {}
            }

        habits[device]["days"][day] = habits[device]["days"].get(day, 0) + 1
        habits[device]["hours"][hour] = habits[device]["hours"].get(hour, 0) + 1

    return habits


# 🧠 SMART INSIGHTS (UPDATED)
def generate_insights(user):

    insights = []

    kwh = calculate_energy(user)
    history = user.get("history", [])
    habits = analyze_habits(history)

    # Basic
    if kwh > 10:
        insights.append("⚠️ High energy usage")

    if kwh < 3:
        insights.append("💡 Very efficient usage")

    # 🔥 HABITS
    for device, data in habits.items():

        if data["days"]:
            common_day = max(data["days"], key=data["days"].get)

            if data["days"][common_day] >= 2:
                insights.append(f"📅 You often use {device} on {common_day}")

        if data["hours"]:
            peak_hour = max(data["hours"], key=data["hours"].get)
            insights.append(f"⏰ {device} mostly used around {peak_hour}:00")

    insights.append(f"📊 Monthly estimate: {round(kwh*30,1)} kWh")

    return insights


# 📊 DASHBOARD
@app.route('/latest/<user_id>', methods=['GET'])
def get_latest(user_id):

    if user_id not in user_data:
        return jsonify({"error": "User not found"}), 404

    user = user_data[user_id]
    survey = user["survey"]

    kwh = calculate_energy(user) * user.get("factor", 1)
    price = survey.get("price_per_kwh", 0.1)

    return jsonify({
        "daily_kwh": round(kwh, 2),
        "monthly_kwh": round(kwh * 30, 2),
        "monthly_cost": round(kwh * 30 * price, 2),
        "insights": generate_insights(user)
    })


# 📜 HISTORY
@app.route('/history/<user_id>', methods=['GET'])
def history(user_id):
    return jsonify(user_data[user_id].get("history", []))


# 🔁 FEEDBACK
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    user_id = data.get("user_id")
    real_kwh = data.get("real_kwh")

    user = user_data[user_id]
    predicted = calculate_energy(user)

    factor = real_kwh / predicted if predicted > 0 else 1
    user["factor"] = factor

    return jsonify({"factor": round(factor, 2)})


@app.route('/')
def home():
    return "EyeTech Running 🚀"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

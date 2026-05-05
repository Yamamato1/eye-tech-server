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

# ---------------- SURVEY ----------------
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


# ---------------- USAGE ----------------
@app.route('/usage', methods=['POST'])
def update_usage():
    data = request.json
    user_id = data.get("user_id")

    user_data[user_id]["usage_flags"] = data.get("usage_flags", {})
    return jsonify({"status": "updated"})


# ---------------- TRACK ----------------
@app.route('/track', methods=['POST'])
def track_usage():
    data = request.json
    user_id = data.get("user_id")
    device = data.get("device")
    action = data.get("action")

    user = user_data[user_id]
    now = datetime.now()

    if action == "on":
        user["active_devices"][device] = now

    elif action == "off":
        start = user["active_devices"].get(device)

        if start:
            duration = (now - start).total_seconds() / 3600

            user["history"].append({
                "device": device,
                "duration_hours": round(duration, 2),
                "start_time": start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "date": start.strftime("%Y-%m-%d"),
                "day": start.strftime("%A")
            })

            del user["active_devices"][device]

    return jsonify({"status": "tracked"})


# ---------------- ENERGY ----------------
def calculate_energy(user):
    survey = user["survey"]
    total = 0

    for r in user["history"]:
        d = r["device"]
        dur = r["duration_hours"]

        if d == "lights":
            power = survey.get("lights_count", 5) * 10
        else:
            power = DEVICE_POWER.get(d, 0)

        total += (power * dur) / 1000

    return total


# ---------------- HABITS ----------------
def analyze_habits(history):
    habits = {}

    for r in history:
        d = r["device"]
        day = r["day"]
        hour = int(r["start_time"].split(" ")[1].split(":")[0])

        habits.setdefault(d, {"days": {}, "hours": {}})

        habits[d]["days"][day] = habits[d]["days"].get(day, 0) + 1
        habits[d]["hours"][hour] = habits[d]["hours"].get(hour, 0) + 1

    return habits


# ---------------- PEAK ----------------
def calculate_peak_hour(user):
    hourly = {}

    for r in user["history"]:
        hour = int(r["start_time"].split(" ")[1].split(":")[0])
        dur = r["duration_hours"]
        power = DEVICE_POWER.get(r["device"], 0)

        hourly[hour] = hourly.get(hour, 0) + (power * dur) / 1000

    if not hourly:
        return None

    return max(hourly, key=hourly.get)


# ---------------- WEEKLY ----------------
def weekly_report(user):
    daily = {}

    for r in user["history"]:
        date = r["date"]
        power = DEVICE_POWER.get(r["device"], 0)
        energy = (power * r["duration_hours"]) / 1000

        daily[date] = daily.get(date, 0) + energy

    return daily


# ---------------- COMPARE ----------------
def compare_users():
    vals = [calculate_energy(u) for u in user_data.values()]
    return sum(vals)/len(vals) if vals else 0


# ---------------- INSIGHTS ----------------
def generate_insights(user):

    kwh = calculate_energy(user)
    habits = analyze_habits(user["history"])

    insights = []

    if kwh > 10:
        insights.append("⚠️ High usage")
    elif kwh < 3:
        insights.append("💡 Efficient usage")

    for d, data in habits.items():
        if data["days"]:
            day = max(data["days"], key=data["days"].get)
            insights.append(f"📅 {d} often used on {day}")

        if data["hours"]:
            hr = max(data["hours"], key=data["hours"].get)
            insights.append(f"⏰ {d} used around {hr}:00")

    insights.append(f"📊 Monthly estimate: {round(kwh*30,1)} kWh")

    return insights


# ---------------- MAIN ----------------
@app.route('/latest/<user_id>')
def latest(user_id):

    user = user_data[user_id]
    kwh = calculate_energy(user) * user["factor"]
    price = user["survey"].get("price_per_kwh", 0.1)

    avg = compare_users()
    comp = "average"

    if kwh > avg:
        comp = "above average ⚠️"
    elif kwh < avg:
        comp = "below average 💡"

    return jsonify({
        "daily_kwh": round(kwh,2),
        "monthly_kwh": round(kwh*30,2),
        "monthly_cost": round(kwh*30*price,2),
        "peak_hour": calculate_peak_hour(user),
        "weekly": weekly_report(user),
        "comparison": comp,
        "insights": generate_insights(user)
    })


# ---------------- HISTORY ----------------
@app.route('/history/<user_id>')
def history(user_id):
    return jsonify(user_data[user_id]["history"])


# ---------------- FEEDBACK ----------------
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    user = user_data[data["user_id"]]

    pred = calculate_energy(user)
    real = data["real_kwh"]

    user["factor"] = real/pred if pred else 1

    return jsonify({"status":"updated"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

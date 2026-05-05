from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

user_data = {}

DEVICE_POWER = {
    "lights": 10,
    "tv": 100,
    "washing_machine": 500,
    "fridge": 150,
    "oven": 2000,
    "ac": 1500
}

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template("index.html")

# ---------------- SURVEY ----------------
@app.route('/survey', methods=['POST'])
def save_survey():
    data = request.json
    user_id = data.get("user_id")

    user_data[user_id] = {
        "survey": data,
        "active_devices": {},
        "history": [],
        "factor": 1
    }

    return jsonify({"status": "saved"})

# ---------------- TRACK ----------------
@app.route('/track', methods=['POST'])
def track():
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
                "date": start.strftime("%Y-%m-%d"),
                "day": start.strftime("%A")
            })

            del user["active_devices"][device]

    return jsonify({"status": "tracked"})

# ---------------- ENERGY ----------------
def calculate_energy(user):
    s = user["survey"]
    total = 0

    total += (s.get("lights_count",5)*10*5)/1000
    total += (s.get("tv_hours",2)*100)/1000
    total += (s.get("fridge_count",1)*150*24)/1000
    total += (s.get("washing_per_week",1)*500)/1000/7
    total += (s.get("oven_hours",1)*2000)/1000
    total += (s.get("ac_hours",2)*1500)/1000

    return total

# ---------------- HABITS ----------------
def analyze_habits(history):
    habits = {}

    for r in history:
        d = r["device"]
        hour = int(r["start_time"].split(" ")[1].split(":")[0])

        habits.setdefault(d, {"hours": {}})
        habits[d]["hours"][hour] = habits[d]["hours"].get(hour, 0) + 1

    return habits

# ---------------- PEAK ----------------
def calculate_peak(user):
    hourly = {}

    for r in user["history"]:
        hour = int(r["start_time"].split(" ")[1].split(":")[0])
        power = DEVICE_POWER.get(r["device"],0)
        energy = power * r["duration_hours"] / 1000

        hourly[hour] = hourly.get(hour,0) + energy

    return max(hourly, key=hourly.get) if hourly else None

# ---------------- WEEKLY ----------------
def weekly(user):
    d = {}

    for r in user["history"]:
        date = r["date"]
        power = DEVICE_POWER.get(r["device"],0)
        energy = power * r["duration_hours"] / 1000

        d[date] = d.get(date,0) + energy

    return d

# ---------------- SAVINGS ----------------
def calculate_savings(user):
    s = user["survey"]
    price = s.get("price_per_kwh", 0.1)

    current = calculate_energy(user)
    optimized = current

    if s.get("ac_hours",0) > 0:
        optimized -= 1.5

    if s.get("oven_hours",0) > 0:
        optimized -= 1

    return round((current-optimized)*30*price,2)

# ---------------- INSIGHTS ----------------
def insights(user):
    kwh = calculate_energy(user)
    ins = []

    if kwh > 10:
        ins.append("⚠️ High usage detected")
    else:
        ins.append("💡 Efficient usage")

    ins.append(f"📊 Monthly: {round(kwh*30,1)} kWh")

    return ins

# ---------------- MAIN ----------------
# ---------------- LIVE DATA ----------------
@app.route('/live/<user_id>')
def live(user_id):
    user = user_data.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    total_power = 0

    for d in user["active_devices"]:
        power = DEVICE_POWER.get(d, 0)
        total_power += power

    voltage = 230
    current = total_power / voltage if voltage > 0 else 0

    return jsonify({
        "voltage": round(voltage, 2),
        "current": round(current, 2),
        "power": round(total_power, 2)
    })
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

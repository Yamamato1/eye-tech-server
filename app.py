from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# =========================================
# MEMORY STORAGE
# =========================================
user_data = {}

# =========================================
# DEVICE DATABASE (Watts)
# =========================================
DEVICE_POWER = {
    "lights": 60,
    "tv": 120,
    "washing_machine": 800,
    "fridge": 150,
    "oven": 2000,
    "ac": 1500
}

# =========================================
# HOME
# =========================================
@app.route('/')
def home():
    return render_template("index.html")

# =========================================
# SAVE SURVEY
# =========================================
@app.route('/survey', methods=['POST'])
def save_survey():

    data = request.json

    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    user_data[user_id] = {
        "survey": data,
        "active_devices": {},
        "history": [],
        "factor": 1
    }

    return jsonify({
        "status": "saved",
        "user_id": user_id
    })

# =========================================
# TRACK DEVICES
# =========================================
@app.route('/track', methods=['POST'])
def track():

    data = request.json

    user_id = data.get("user_id")
    device = data.get("device")
    action = data.get("action")

    user = user_data.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    now = datetime.now()

    # TURN ON
    if action == "on":
        user["active_devices"][device] = now

    # TURN OFF
    elif action == "off":

        start = user["active_devices"].get(device)

        if start:

            duration = (now - start).total_seconds() / 3600

            user["history"].append({
                "device": device,
                "duration": duration,
                "start": start.strftime("%Y-%m-%d %H:%M:%S"),
                "end": now.strftime("%Y-%m-%d %H:%M:%S")
            })

            del user["active_devices"][device]

    return jsonify({
        "status": "tracked"
    })

# =========================================
# CALCULATE ENERGY
# =========================================
def calculate_energy(user):

    total_kwh = 0

    for record in user["history"]:

        device = record["device"]
        duration = record["duration"]

        power = DEVICE_POWER.get(device, 0)

        energy = (power * duration) / 1000

        total_kwh += energy

    return total_kwh * user.get("factor", 1)

# =========================================
# PEAK HOUR
# =========================================
def calculate_peak(user):

    hours = {}

    for record in user["history"]:

        hour = int(record["start"].split(" ")[1].split(":")[0])

        hours[hour] = hours.get(hour, 0) + 1

    if not hours:
        return None

    return max(hours, key=hours.get)

# =========================================
# WEEKLY HISTORY
# =========================================
def weekly(user):

    data = {}

    for record in user["history"]:

        date = record["start"].split(" ")[0]

        device = record["device"]

        power = DEVICE_POWER.get(device, 0)

        energy = (power * record["duration"]) / 1000

        data[date] = round(data.get(date, 0) + energy, 2)

    return data

# =========================================
# SAVINGS ESTIMATION
# =========================================
def calculate_savings(user):

    current = calculate_energy(user)

    optimized = current * 0.85

    price = user["survey"].get("price_per_kwh", 0.1)

    return round((current - optimized) * 30 * price, 2)

# =========================================
# AI INSIGHTS
# =========================================
def insights(user):

    kwh = calculate_energy(user)

    ins = []

    if kwh > 10:
        ins.append("⚠️ High energy usage detected")
    else:
        ins.append("💡 Efficient energy usage")

    ins.append(f"📊 Estimated monthly usage: {round(kwh * 30, 1)} kWh")

    return ins

# =========================================
# LIVE DATA
# =========================================
@app.route('/live/<user_id>')
def live(user_id):

    user = user_data.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    total_power = 0

    for device in user["active_devices"]:

        power = DEVICE_POWER.get(device, 0)

        total_power += power

    voltage = 230

    current = total_power / voltage if voltage > 0 else 0

    return jsonify({
        "voltage": round(voltage, 2),
        "current": round(current, 2),
        "power": round(total_power, 2)
    })

# =========================================
# MAIN DASHBOARD
# =========================================
@app.route('/latest/<user_id>')
def latest(user_id):

    user = user_data.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    kwh = calculate_energy(user)

    price = user["survey"].get("price_per_kwh", 0.1)

    return jsonify({
        "daily_kwh": round(kwh, 2),
        "monthly_kwh": round(kwh * 30, 2),
        "monthly_cost": round(kwh * 30 * price, 2),
        "peak_hour": calculate_peak(user),
        "weekly": weekly(user),
        "savings": calculate_savings(user),
        "insights": insights(user)
    })

# =========================================
# FEEDBACK / LEARNING
# =========================================
@app.route('/feedback', methods=['POST'])
def feedback():

    data = request.json

    user_id = data.get("user_id")
    real_kwh = data.get("real_kwh")

    user = user_data.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    predicted = calculate_energy(user)

    if predicted > 0:
        user["factor"] = real_kwh / predicted

    return jsonify({
        "factor": round(user["factor"], 2)
    })

# =========================================
# AI CHAT ASSISTANT
# =========================================
@app.route('/ai-chat', methods=['POST'])
def ai_chat():

    data = request.json

    message = data.get("message")

    reply = f"""
EyeTech AI Analysis:

Based on your appliance behavior and estimated energy profile,
reducing AC usage during afternoon peak hours may reduce your bill.

Your estimated household energy usage is currently within a normal range.
"""

    return jsonify({
        "reply": reply
    })

# =========================================
# APPLIANCE PHOTO ANALYSIS
# =========================================
@app.route('/upload-appliance', methods=['POST'])
def upload_appliance():

    return jsonify({
        "appliance": "Air Conditioner",
        "estimated_wattage": "1200W",
        "efficiency": "Medium",
        "confidence": "87%"
    })

# =========================================
# START SERVER
# =========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

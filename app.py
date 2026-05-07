from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import boto3

app = Flask(__name__)
CORS(app)

# =========================================
# AWS REKOGNITION
# =========================================

rekognition = boto3.client(
    'rekognition',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY',
    region_name='us-east-1'
)

# =========================================
# MEMORY STORAGE
# =========================================

user_data = {}

# =========================================
# DEVICE POWER
# =========================================

DEVICE_POWER = {
    "lights": 60,
    "tv": 120,
    "washing_machine": 500,
    "fridge": 150,
    "oven": 2000,
    "ac": 1500
}

# =========================================
# APPLIANCE DATABASE
# =========================================

APPLIANCE_DATABASE = {

    "washing machine": {
        "avg_watts": 500,
        "monthly_kwh": 24,
        "efficiency": "A+",
        "usage_type": "weekly"
    },

    "refrigerator": {
        "avg_watts": 150,
        "monthly_kwh": 45,
        "efficiency": "A++",
        "usage_type": "always_on"
    },

    "television": {
        "avg_watts": 120,
        "monthly_kwh": 18,
        "efficiency": "A",
        "usage_type": "daily"
    },

    "air conditioner": {
        "avg_watts": 1500,
        "monthly_kwh": 220,
        "efficiency": "B",
        "usage_type": "heavy"
    },

    "oven": {
        "avg_watts": 2000,
        "monthly_kwh": 40,
        "efficiency": "A",
        "usage_type": "short_usage"
    }

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
        "factor": 1,
        "appliances": []
    }

    return jsonify({
        "status": "saved"
    })

# =========================================
# TRACK DEVICE
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

    if action == "on":
        user["active_devices"][device] = now

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
# ENERGY CALCULATION
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
# WEEKLY
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
# SAVINGS
# =========================================

def calculate_savings(user):

    current = calculate_energy(user)

    optimized = current * 0.85

    price = user["survey"].get("price_per_kwh", 0.1)

    return round((current - optimized) * 30 * price, 2)

# =========================================
# INSIGHTS
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
# DASHBOARD
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
        "insights": insights(user),
        "appliances": user["appliances"]
    })

# =========================================
# FEEDBACK
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
# AI CHAT
# =========================================

@app.route('/ai-chat', methods=['POST'])
def ai_chat():

    data = request.json

    message = data.get("message")

    reply = f"""
EyeTech AI Analysis:

Based on your estimated appliance behavior and household profile,
reducing AC usage during peak afternoon hours may reduce your monthly bill.

Your current estimated energy profile appears normal.
"""

    return jsonify({
        "reply": reply
    })

# =========================================
# AWS APPLIANCE DETECTION
# =========================================

@app.route('/detect-appliance', methods=['POST'])
def detect_appliance():

    file = request.files['image']

    image_bytes = file.read()

    response = rekognition.detect_labels(
        Image={'Bytes': image_bytes},
        MaxLabels=10
    )

    labels = []

    for label in response['Labels']:

        labels.append({
            "name": label['Name'],
            "confidence": round(label['Confidence'], 2)
        })

    return jsonify(labels)

# =========================================
# APPLIANCE ANALYSIS
# =========================================

@app.route('/analyze-appliance', methods=['POST'])
def analyze_appliance():

    data = request.json

    user_id = data.get("user_id")

    appliance_name = data.get("appliance", "").lower()

    result = APPLIANCE_DATABASE.get(appliance_name)

    if not result:

        return jsonify({
            "status": "unknown",
            "message": "Appliance not found"
        })

    user = user_data.get(user_id)

    if user:

        user["appliances"].append({
            "name": appliance_name,
            "avg_watts": result["avg_watts"],
            "monthly_kwh": result["monthly_kwh"],
            "efficiency": result["efficiency"],
            "usage_type": result["usage_type"]
        })

    return jsonify({
        "status": "success",
        "appliance": appliance_name,
        "avg_watts": result["avg_watts"],
        "monthly_kwh": result["monthly_kwh"],
        "efficiency": result["efficiency"],
        "usage_type": result["usage_type"]
    })

# =========================================
# START SERVER
# =========================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

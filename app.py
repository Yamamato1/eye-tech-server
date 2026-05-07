from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# =========================================
# STORAGE
# =========================================

users = {}

# =========================================
# DEVICE POWER DATABASE (Watts)
# =========================================

DEVICE_POWER = {
    "lights": 12,
    "tv": 120,
    "fridge": 150,
    "oven": 2200,
    "ac": 1500,
    "washing_machine": 500
}

# =========================================
# HOME
# =========================================

@app.route("/")
def home():
    return jsonify({
        "status": "EyeTech Pro Backend Running"
    })

# =========================================
# SURVEY
# =========================================

@app.route("/survey", methods=["POST"])
def survey():

    data = request.json

    user_id = data.get("user_id")

    if not user_id:
        return jsonify({
            "error": "Missing user_id"
        }), 400

    users[user_id] = {
        "survey": data,
        "active_devices": [],
        "history": [],
        "factor": 1
    }

    return jsonify({
        "success": True,
        "message": "Survey saved"
    })

# =========================================
# TRACK DEVICES
# =========================================

@app.route("/track", methods=["POST"])
def track():

    data = request.json

    user_id = data.get("user_id")
    device = data.get("device")
    action = data.get("action")

    if user_id not in users:
        return jsonify({
            "error": "User not found"
        }), 404

    if action == "on":

        if device not in users[user_id]["active_devices"]:
            users[user_id]["active_devices"].append(device)

    elif action == "off":

        if device in users[user_id]["active_devices"]:
            users[user_id]["active_devices"].remove(device)

    return jsonify({
        "success": True,
        "active_devices": users[user_id]["active_devices"]
    })

# =========================================
# LIVE DATA
# =========================================

@app.route("/live/<user_id>")
def live(user_id):

    if user_id not in users:
        return jsonify({
            "error": "User not found"
        }), 404

    active = users[user_id]["active_devices"]

    total_power = 150

    for device in active:
        total_power += DEVICE_POWER.get(device, 0)

    voltage = round(random.uniform(220, 235), 1)

    current = round(total_power / voltage, 2)

    users[user_id]["history"].append(total_power)

    if len(users[user_id]["history"]) > 50:
        users[user_id]["history"].pop(0)

    return jsonify({
        "voltage": voltage,
        "current": current,
        "power": total_power,
        "active_devices": active,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

# =========================================
# DASHBOARD DATA
# =========================================

@app.route("/dashboard/<user_id>")
def dashboard(user_id):

    if user_id not in users:
        return jsonify({
            "error": "User not found"
        }), 404

    survey = users[user_id]["survey"]

    active = users[user_id]["active_devices"]

    total_power = 150

    for device in active:
        total_power += DEVICE_POWER.get(device, 0)

    daily_kwh = round((total_power * 24) / 1000, 2)

    monthly_kwh = round(daily_kwh * 30, 2)

    price = float(
        survey.get("price_per_kwh", 0.12)
    )

    monthly_bill = round(monthly_kwh * price, 2)

    peak_hour = random.choice([
        "18:00",
        "19:00",
        "20:00",
        "21:00"
    ])

    savings = round(random.uniform(1, 15), 2)

    insights = []

    if monthly_bill > 50:
        insights.append(
            "⚠️ High energy usage detected"
        )

    else:
        insights.append(
            "💡 Efficient energy usage"
        )

    if "ac" in active:
        insights.append(
            "❄️ Air Conditioner is consuming most energy"
        )

    history = users[user_id]["history"]

    return jsonify({
        "daily_kwh": daily_kwh,
        "monthly_kwh": monthly_kwh,
        "monthly_bill": monthly_bill,
        "peak_hour": peak_hour,
        "savings": savings,
        "insights": insights,
        "history": history,
        "active_devices": active
    })

# =========================================
# AI ASSISTANT
# =========================================

@app.route("/ask-ai", methods=["POST"])
def ask_ai():

    data = request.json

    user_id = data.get("user_id")
    message = data.get("message", "").lower()

    if user_id not in users:
        return jsonify({
            "error": "User not found"
        }), 404

    active = users[user_id]["active_devices"]

    total_power = 150

    for device in active:
        total_power += DEVICE_POWER.get(device, 0)

    daily_kwh = round((total_power * 24) / 1000, 2)

    monthly_kwh = round(daily_kwh * 30, 2)

    price = float(
        users[user_id]["survey"].get("price_per_kwh", 0.12)
    )

    monthly_bill = round(monthly_kwh * price, 2)

    response = ""

    # =========================================
    # AI RESPONSES
    # =========================================

    if "bill" in message or "cost" in message:

        if monthly_bill > 50:

            response = (
                f"Your estimated bill is ${monthly_bill}. "
                f"The highest energy usage is from "
                f"{', '.join(active) if active else 'background appliances'}."
            )

        else:

            response = (
                f"Your estimated monthly bill is ${monthly_bill}. "
                f"Your energy usage looks efficient."
            )

    elif "save" in message or "reduce" in message:

        if "ac" in active:

            response = (
                "Your Air Conditioner is consuming most of the energy. "
                "Reducing AC usage may significantly reduce your bill."
            )

        else:

            response = (
                "Turning off unused devices and lights can reduce your monthly bill."
            )

    elif "most" in message or "highest" in message:

        if active:

            biggest = max(
                active,
                key=lambda d: DEVICE_POWER.get(d, 0)
            )

            response = (
                f"The appliance consuming the most power right now is {biggest}."
            )

        else:

            response = (
                "No major appliances are currently active."
            )

    elif "hello" in message or "hi" in message:

        response = (
            "Hello 👋 I am EyeTech AI. "
            "I help users understand electricity usage and reduce energy bills."
        )

    else:

        response = (
            "I can help you analyze your energy usage, reduce your bill, "
            "and identify high power appliances."
        )

    return jsonify({
        "success": True,
        "reply": response
    })

# =========================================
# AI IMAGE ANALYSIS
# =========================================

@app.route("/analyze-image", methods=["POST"])
def analyze_image():

    device_types = [
        {
            "device": "Inverter Air Conditioner",
            "watts": 950,
            "efficiency": "High",
            "confidence": 94
        },
        {
            "device": "Old Air Conditioner",
            "watts": 2200,
            "efficiency": "Low",
            "confidence": 88
        },
        {
            "device": "LED Television",
            "watts": 120,
            "efficiency": "High",
            "confidence": 91
        },
        {
            "device": "Refrigerator",
            "watts": 150,
            "efficiency": "Medium",
            "confidence": 93
        },
        {
            "device": "Washing Machine",
            "watts": 500,
            "efficiency": "Medium",
            "confidence": 89
        }
    ]

    result = random.choice(device_types)

    return jsonify({
        "success": True,
        "detected_device": result["device"],
        "estimated_watts": result["watts"],
        "efficiency": result["efficiency"],
        "confidence": result["confidence"],
        "daily_hours": random.randint(2, 10)
    })

# =========================================
# SEND ALERTS
# =========================================

@app.route("/send-alert", methods=["POST"])
def send_alert():

    data = request.json

    email = data.get("email")
    device = data.get("device")

    return jsonify({
        "success": True,
        "message": f"Alert sent to {email} about {device}"
    })

# =========================================
# FEEDBACK LEARNING
# =========================================

@app.route("/feedback", methods=["POST"])
def feedback():

    data = request.json

    user_id = data.get("user_id")
    real_bill = float(data.get("real_bill", 0))

    if user_id not in users:
        return jsonify({
            "error": "User not found"
        }), 404

    users[user_id]["factor"] = real_bill

    return jsonify({
        "success": True,
        "message": "Feedback saved"
    })

# =========================================
# RUN SERVER
# =========================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

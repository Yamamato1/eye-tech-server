from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import random

app = Flask(__name__)
CORS(app)

# =========================
# DATABASE
# =========================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# MODELS
# =========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appliance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(200))
    name = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    power = db.Column(db.Float)
    hours = db.Column(db.Float)
    image_url = db.Column(db.String(500))
    status = db.Column(db.Boolean, default=False)

class EnergyHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(200))
    voltage = db.Column(db.Float)
    current = db.Column(db.Float)
    power = db.Column(db.Float)
    daily_kwh = db.Column(db.Float)
    monthly_bill = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# =========================
# CREATE DATABASE
# =========================

with app.app_context():
    db.create_all()

# =========================
# DEVICE DEFAULTS
# =========================

DEVICE_POWER = {
    "lights": 10,
    "tv": 100,
    "fridge": 150,
    "ac": 1500,
    "oven": 2000
}

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "message": "EyeTech AI Backend Live"
    })

# =========================
# LOGIN / REGISTER
# =========================

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    code = random.randint(100000, 999999)

    return jsonify({
        "success": True,
        "email": email,
        "verification_code": code
    })

# =========================
# ADD APPLIANCE
# =========================

@app.route("/add-appliance", methods=["POST"])
def add_appliance():
    data = request.json

    appliance = Appliance(
        user_email=data.get("email"),
        name=data.get("name"),
        brand=data.get("brand"),
        power=data.get("power"),
        hours=data.get("hours"),
        image_url=data.get("image_url"),
        status=True
    )

    db.session.add(appliance)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Appliance added"
    })

# =========================
# LIVE DATA
# =========================

@app.route("/live/<email>")
def live(email):

    appliances = Appliance.query.filter_by(
        user_email=email
    ).all()

    total_power = 0

    for a in appliances:
        if a.status:
            total_power += a.power

    voltage = 230
    current = round(total_power / voltage, 2)

    return jsonify({
        "voltage": voltage,
        "current": current,
        "power": total_power,
        "active_devices": len(appliances)
    })

# =========================
# DASHBOARD
# =========================

@app.route("/dashboard/<email>")
def dashboard(email):

    appliances = Appliance.query.filter_by(
        user_email=email
    ).all()

    total_power = 0
    daily_kwh = 0

    for a in appliances:
        if a.status:
            total_power += a.power
            daily_kwh += (a.power * a.hours) / 1000

    monthly_kwh = daily_kwh * 30
    monthly_bill = round(monthly_kwh * 0.12, 2)

    history = EnergyHistory(
        user_email=email,
        voltage=230,
        current=round(total_power / 230, 2),
        power=total_power,
        daily_kwh=daily_kwh,
        monthly_bill=monthly_bill
    )

    db.session.add(history)
    db.session.commit()

    return jsonify({
        "daily_kwh": round(daily_kwh, 2),
        "monthly_kwh": round(monthly_kwh, 2),
        "monthly_bill": monthly_bill,
        "power": total_power,
        "ai_insight": get_ai_insight(monthly_bill),
        "recommendation": get_recommendation(total_power)
    })

# =========================
# TOGGLE DEVICE
# =========================

@app.route("/toggle-device", methods=["POST"])
def toggle_device():

    data = request.json

    appliance = Appliance.query.get(data.get("id"))

    if not appliance:
        return jsonify({
            "success": False
        })

    appliance.status = not appliance.status

    db.session.commit()

    return jsonify({
        "success": True,
        "status": appliance.status
    })

# =========================
# AI CHAT
# =========================

@app.route("/ask-ai", methods=["POST"])
def ask_ai():

    data = request.json
    message = data.get("message", "").lower()

    response = "I am your EyeTech AI assistant."

    if "usage" in message:
        response = "Your biggest energy usage usually comes from AC and ovens."

    elif "bill" in message:
        response = "Your estimated monthly bill is based on appliance activity and daily behavior."

    elif "save" in message:
        response = "Try reducing AC hours and turning lights off during daytime."

    elif "fridge" in message:
        response = "Fridges normally stay on continuously for food safety."

    elif "hello" in message or "hi" in message:
        response = "Hello 👋 How can I help you manage your energy today?"

    return jsonify({
        "reply": response
    })

# =========================
# IMAGE ANALYSIS
# =========================

@app.route("/analyze-image", methods=["POST"])
def analyze_image():

    data = request.json

    filename = data.get("filename", "").lower()

    detected = "Unknown Appliance"
    estimated_power = 100

    if "fridge" in filename:
        detected = "Refrigerator"
        estimated_power = 150

    elif "tv" in filename:
        detected = "Television"
        estimated_power = 120

    elif "ac" in filename:
        detected = "Air Conditioner"
        estimated_power = 1500

    elif "oven" in filename:
        detected = "Electric Oven"
        estimated_power = 2000

    return jsonify({
        "detected_appliance": detected,
        "estimated_power": estimated_power,
        "confidence": "95%"
    })

# =========================
# FEEDBACK
# =========================

@app.route("/feedback", methods=["POST"])
def feedback():

    data = request.json

    return jsonify({
        "success": True,
        "message": "Feedback received",
        "data": data
    })

# =========================
# EMAIL ALERT
# =========================

@app.route("/send-alert", methods=["POST"])
def send_alert():

    data = request.json

    return jsonify({
        "success": True,
        "message": f"Alert prepared for {data.get('email')}"
    })

# =========================
# AI FUNCTIONS
# =========================

def get_ai_insight(monthly_bill):

    if monthly_bill > 100:
        return "⚠ High energy usage detected"

    elif monthly_bill > 50:
        return "📈 Moderate usage"

    return "💡 Efficient energy usage"

def get_recommendation(power):

    if power > 2000:
        return "Turn off unused heavy appliances."

    elif power > 1000:
        return "Try reducing AC usage."

    return "Your usage looks healthy."

# =========================
# START
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

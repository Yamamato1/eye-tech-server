from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from openai import OpenAI
from datetime import datetime
import os
import base64
import uuid

# =========================================
# FLASK SETUP
# =========================================

app = Flask(__name__)
CORS(app)

# =========================================
# DATABASE
# =========================================

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================================
# OPENAI
# =========================================

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =========================================
# MODELS
# =========================================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(120), unique=True)

    password = db.Column(db.String(200))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Device(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    name = db.Column(db.String(100))

    brand = db.Column(db.String(100))

    model = db.Column(db.String(100))

    category = db.Column(db.String(100))

    watts = db.Column(db.Float)

    efficiency = db.Column(db.String(50))

    monthly_kwh = db.Column(db.Float)

    monthly_cost = db.Column(db.Float)

    image_url = db.Column(db.Text)

    status = db.Column(db.String(20), default="off")

    total_hours = db.Column(db.Float, default=0)

    started_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UsageHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    device_id = db.Column(db.Integer)

    started_at = db.Column(db.DateTime)

    ended_at = db.Column(db.DateTime)

    duration_hours = db.Column(db.Float)

    energy_kwh = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# =========================================
# CREATE DATABASE
# =========================================

with app.app_context():
    db.create_all()

# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return jsonify({
        "message": "EyeTech Pro Backend Running"
    })

# =========================================
# SIGNUP
# =========================================

@app.route("/signup", methods=["POST"])
def signup():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    existing = User.query.filter_by(email=email).first()

    if existing:
        return jsonify({
            "error": "Email already exists"
        }), 400

    hashed = generate_password_hash(password)

    user = User(
        name=name,
        email=email,
        password=hashed
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": f"{name}, account created successfully"
    })

# =========================================
# LOGIN
# =========================================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    if not check_password_hash(user.password, password):

        return jsonify({
            "error": "Incorrect password"
        }), 401

    return jsonify({
        "message": f"{user.name}, soo dhawoow 👋",
        "user_id": user.id,
        "name": user.name
    })

# =========================================
# AI CHAT
# =========================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        user_id = data.get("user_id")

        message = data.get("message")

        user = User.query.get(user_id)

        devices = Device.query.filter_by(user_id=user_id).all()

        device_text = ""

        for d in devices:

            device_text += f"""
            Device: {d.name}
            Brand: {d.brand}
            Watts: {d.watts}
            Efficiency: {d.efficiency}
            """

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {
                    "role": "system",
                    "content": f"""
                    You are EyeTech Pro AI assistant.

                    User Name:
                    {user.name}

                    User Devices:
                    {device_text}

                    Speak naturally.
                    Use Somali greetings when appropriate.
                    Give energy-saving advice.
                    """
                },

                {
                    "role": "user",
                    "content": message
                }

            ]

        )

        reply = response.choices[0].message.content

        return jsonify({
            "reply": reply
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# =========================================
# PHOTO ANALYSIS
# =========================================

@app.route("/analyze-photo", methods=["POST"])
def analyze_photo():

    try:

        user_id = request.form.get("user_id")

        image = request.files["image"]

        image_bytes = image.read()

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {
                    "role": "system",
                    "content": """
                    Analyze this appliance image.

                    Detect:
                    - appliance type
                    - brand
                    - possible model
                    - estimated wattage
                    - efficiency
                    - estimated monthly kWh
                    - estimated monthly electricity cost
                    - optimization tips
                    - confidence score
                    """
                },

                {
                    "role": "user",
                    "content": [

                        {
                            "type": "text",
                            "text": "Analyze this appliance"
                        },

                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }

                    ]
                }

            ]

        )

        result = response.choices[0].message.content

        device = Device(
            user_id=user_id,
            name="Detected Appliance",
            brand="AI Detected",
            model="Estimated",
            category="General",
            watts=500,
            efficiency="A",
            monthly_kwh=35,
            monthly_cost=12
        )

        db.session.add(device)
        db.session.commit()

        return jsonify({
            "result": result,
            "device_id": device.id
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# =========================================
# TURN DEVICE ON/OFF
# =========================================

@app.route("/device-toggle", methods=["POST"])
def device_toggle():

    data = request.get_json()

    device_id = data.get("device_id")

    status = data.get("status")

    device = Device.query.get(device_id)

    if not device:

        return jsonify({
            "error": "Device not found"
        }), 404

    if status == "on":

        device.status = "on"

        device.started_at = datetime.utcnow()

    else:

        if device.started_at:

            duration = (
                datetime.utcnow() - device.started_at
            ).total_seconds() / 3600

            device.total_hours += duration

            energy = (device.watts * duration) / 1000

            history = UsageHistory(
                user_id=device.user_id,
                device_id=device.id,
                started_at=device.started_at,
                ended_at=datetime.utcnow(),
                duration_hours=duration,
                energy_kwh=energy
            )

            db.session.add(history)

        device.status = "off"

        device.started_at = None

    db.session.commit()

    return jsonify({
        "message": "Device updated",
        "status": device.status
    })

# =========================================
# DASHBOARD
# =========================================

@app.route("/dashboard/<int:user_id>")
def dashboard(user_id):

    devices = Device.query.filter_by(user_id=user_id).all()

    total_power = 0
    total_kwh = 0
    total_cost = 0

    active_devices = 0

    for d in devices:

        total_power += d.watts

        total_kwh += d.monthly_kwh

        total_cost += d.monthly_cost

        if d.status == "on":
            active_devices += 1

    return jsonify({

        "total_devices": len(devices),

        "active_devices": active_devices,

        "monthly_kwh": round(total_kwh, 2),

        "estimated_bill": round(total_cost, 2),

        "total_power": round(total_power, 2),

        "efficiency_score": 88

    })

# =========================================
# USER DEVICES
# =========================================

@app.route("/devices/<int:user_id>")
def devices(user_id):

    devices = Device.query.filter_by(user_id=user_id).all()

    results = []

    for d in devices:

        results.append({

            "id": d.id,

            "name": d.name,

            "brand": d.brand,

            "model": d.model,

            "category": d.category,

            "watts": d.watts,

            "efficiency": d.efficiency,

            "monthly_kwh": d.monthly_kwh,

            "monthly_cost": d.monthly_cost,

            "status": d.status,

            "total_hours": round(d.total_hours, 2)

        })

    return jsonify(results)

# =========================================
# DELETE DEVICE
# =========================================

@app.route("/delete-device/<int:device_id>", methods=["DELETE"])
def delete_device(device_id):

    device = Device.query.get(device_id)

    if not device:

        return jsonify({
            "error": "Device not found"
        }), 404

    db.session.delete(device)
    db.session.commit()

    return jsonify({
        "message": "Device deleted"
    })

# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )

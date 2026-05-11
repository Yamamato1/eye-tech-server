from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# Health Check
@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "project": "EyeTech Pro",
        "message": "EyeTech Pro server is running"
    })

# Waitlist API
@app.route("/api/waitlist", methods=["POST"])
def waitlist():
    try:
        data = request.get_json()

        name = data.get("name")
        phone = data.get("phone")
        feedback = data.get("feedback")

        print("NEW WAITLIST USER")
        print(name)
        print(phone)
        print(feedback)

        return jsonify({
            "success": True,
            "message": f"Mahadsanid {name}! Waan ku helnay."
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Energy Calculator API
@app.route("/api/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()

        appliance = data.get("appliance")
        wattage = float(data.get("wattage", 0))
        hours = float(data.get("hours", 0))

        price_per_kwh = 0.25

        daily_kwh = (wattage * hours) / 1000
        monthly_kwh = daily_kwh * 30
        estimated_bill = monthly_kwh * price_per_kwh

        return jsonify({
            "success": True,
            "appliance": appliance,
            "daily_kwh": round(daily_kwh, 2),
            "monthly_kwh": round(monthly_kwh, 2),
            "estimated_bill": round(estimated_bill, 2),
            "currency": "USD",
            "message": f"{appliance} wuxuu isticmaali doonaa qiyaastii ${round(estimated_bill,2)} bishii."
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Run Server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

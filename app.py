from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import resend
import os
import base64
import json

# =====================================================
# APP CONFIG
# =====================================================

app = Flask(__name__)
CORS(app)

# =====================================================
# OPENAI CONFIG
# =====================================================

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =====================================================
# RESEND CONFIG
# =====================================================

resend.api_key = os.getenv("RESEND_API_KEY")

COMPANY_EMAIL = "Eyetech.engineering2026@gmail.com"

# =====================================================
# HOME PAGE
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")

# =====================================================
# HEALTH CHECK
# =====================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "online",
        "project": "EyeTech Pro",
        "message": "AI backend operational"
    })

# =====================================================
# WAITLIST SYSTEM
# =====================================================

@app.route("/api/waitlist", methods=["POST"])
def waitlist():

    try:

        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        whatsapp = data.get("whatsapp")
        feedback = data.get("feedback")

        # =================================================
        # EMAIL TO COMPANY
        # =================================================

        resend.Emails.send({

            "from": "EyeTech Pro <onboarding@resend.dev>",

            "to": COMPANY_EMAIL,

            "subject": "New EyeTech Pro Waitlist User",

            "html": f"""

            <div style="font-family:Arial;padding:20px;">

                <h2>New Waitlist User</h2>

                <p><strong>Name:</strong> {name}</p>

                <p><strong>Email:</strong> {email}</p>

                <p><strong>WhatsApp:</strong> {whatsapp}</p>

                <p><strong>Feedback:</strong></p>

                <p>{feedback}</p>

            </div>

            """

        })

        # =================================================
        # EMAIL TO USER
        # =================================================

        resend.Emails.send({

            "from": "EyeTech Pro <onboarding@resend.dev>",

            "to": email,

            "subject": "Welcome To EyeTech Pro",

            "html": f"""

            <div style="font-family:Arial;padding:30px;background:#0a0f1e;color:white;">

                <h1 style="color:#22d3ee;">
                    Mahadsanid {name}
                </h1>

                <p>
                    Waad ku mahadsan tahay inaad ku biirtay EyeTech Pro.
                </p>

                <p>
                    Waxaan kuu soo diri doonaa updates-ka mashruuca.
                </p>

                <p>
                    Soomaaliya AI mustaqbalkeeda waan dhisaynaa 🇸🇴
                </p>

            </div>

            """

        })

        return jsonify({
            "success": True,
            "message": "Waitlist success"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =====================================================
# AI ASSISTANT
# =====================================================

@app.route("/api/assistant", methods=["POST"])
def assistant():

    try:

        data = request.get_json()

        user_message = data.get("message")

        response = client.chat.completions.create(

            model="gpt-4o",

            messages=[

                {
                    "role": "system",
                    "content": """
You are EyeTech Pro AI Assistant.

You help Somali users understand:
- electricity bills
- appliance electricity usage
- energy saving
- Somali home electricity systems
- watt calculations
- electricity cost reduction

Always answer in Somali language.
Always be smart and detailed.
"""
                },

                {
                    "role": "user",
                    "content": user_message
                }

            ],

            max_tokens=500

        )

        ai_response = response.choices[0].message.content

        return jsonify({
            "success": True,
            "response": ai_response
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =====================================================
# AI IMAGE ANALYSIS
# =====================================================

@app.route("/api/analyze-image", methods=["POST"])
def analyze_image():

    try:

        # =================================================
        # CHECK IMAGE
        # =================================================

        if "image" not in request.files:

            return jsonify({
                "success": False,
                "error": "No image uploaded"
            }), 400

        # =================================================
        # GET IMAGE
        # =================================================

        file = request.files["image"]

        image_bytes = file.read()

        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        # =================================================
        # USER HOURS
        # =================================================

        hours = request.form.get("hours")

        if not hours:
            hours = 8

        hours = float(hours)

        # =================================================
        # SOMALIA ELECTRICITY PRICE
        # =================================================

        price_per_kwh = 0.35

        # =================================================
        # OPENAI ANALYSIS
        # =================================================

        response = client.chat.completions.create(

            model="gpt-4o",

            messages=[

                {
                    "role": "system",
                    "content": f"""
You are an expert AI appliance analyzer.

TASKS:
1. Identify appliance from image.
2. Detect brand/model if visible.
3. Estimate REALISTIC watt usage using internet-level appliance knowledge.
4. Calculate electricity costs.

Electricity Price:
{price_per_kwh}$ per kWh

Usage:
{hours} hours/day

Return ONLY JSON.

FORMAT:

{{
  "appliance":"string",
  "model":"string",
  "wattage":100,
  "daily_cost":1,
  "monthly_cost":10,
  "yearly_cost":100,
  "efficiency":"A+",
  "somali_tip":"string"
}}

IMPORTANT:
- Return ONLY JSON
- No markdown
- No explanations
"""
                },

                {
                    "role": "user",
                    "content": [

                        {
                            "type": "text",
                            "text": "Analyze this appliance image carefully."
                        },

                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }

                    ]
                }

            ],

            max_tokens=500

        )

        # =================================================
        # AI RESPONSE
        # =================================================

        result = response.choices[0].message.content

        # =================================================
        # CLEAN JSON
        # =================================================

        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

        parsed = json.loads(result)

        # =================================================
        # RETURN DATA
        # =================================================

        return jsonify({

            "success": True,

            "appliance": parsed.get("appliance"),

            "model": parsed.get("model"),

            "wattage": parsed.get("wattage"),

            "daily_cost": parsed.get("daily_cost"),

            "monthly_cost": parsed.get("monthly_cost"),

            "yearly_cost": parsed.get("yearly_cost"),

            "efficiency": parsed.get("efficiency"),

            "somali_tip": parsed.get("somali_tip")

        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =====================================================
# ENERGY CALCULATOR
# =====================================================

@app.route("/api/calculate", methods=["POST"])
def calculate():

    try:

        data = request.get_json()

        wattage = float(data.get("wattage"))

        hours = float(data.get("hours"))

        # Somalia electricity rate
        price_per_kwh = 0.35

        # =================================================
        # CALCULATIONS
        # =================================================

        daily_kwh = (wattage * hours) / 1000

        daily_cost = daily_kwh * price_per_kwh

        monthly_cost = daily_cost * 30

        yearly_cost = daily_cost * 365

        # =================================================
        # RETURN
        # =================================================

        return jsonify({

            "success": True,

            "daily": round(daily_cost, 2),

            "monthly": round(monthly_cost, 2),

            "yearly": round(yearly_cost, 2)

        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =====================================================
# 404
# =====================================================

@app.errorhandler(404)
def not_found(e):

    return jsonify({
        "success": False,
        "error": "Route not found"
    }), 404

# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )

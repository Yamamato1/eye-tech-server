# =========================
# app.py
# FULL READY FLASK SERVER
# =========================

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import resend
import base64
import json

app = Flask(__name__)
CORS(app)

# ======================================
# ENV VARIABLES
# ======================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL")

# ======================================
# OPENAI
# ======================================

client = OpenAI(
    api_key=OPENAI_API_KEY
)

# ======================================
# RESEND
# ======================================

resend.api_key = RESEND_API_KEY

# ======================================
# HOME
# ======================================

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "company": "EyeTech Pro",
        "message": "AI Server Running"
    })

# ======================================
# WAITLIST
# ======================================

@app.route("/api/waitlist", methods=["POST"])
def waitlist():

    try:

        data = request.json

        name = data.get("name")
        email = data.get("email")
        whatsapp = data.get("whatsapp")
        feedback = data.get("feedback")

        # SEND TO COMPANY

        resend.Emails.send({
            "from": "EyeTech Pro <onboarding@resend.dev>",
            "to": COMPANY_EMAIL,
            "subject": f"New Waitlist User - {name}",
            "html": f"""
            <div style="font-family:Arial;padding:20px;background:#0a0f1e;color:white;">
                <h1 style="color:#22d3ee;">New EyeTech User</h1>

                <p><strong>Name:</strong> {name}</p>

                <p><strong>Email:</strong> {email}</p>

                <p><strong>WhatsApp:</strong> {whatsapp}</p>

                <p><strong>Feedback:</strong></p>

                <p>{feedback}</p>
            </div>
            """
        })

        # SEND TO USER

        resend.Emails.send({
            "from": "EyeTech Pro <onboarding@resend.dev>",
            "to": email,
            "subject": "Welcome to EyeTech Pro",
            "html": f"""
            <div style="font-family:Arial;padding:20px;background:#0a0f1e;color:white;">
                <h1 style="color:#22d3ee;">Waad ku mahadsantahay!</h1>

                <p>Salaan {name}</p>

                <p>
                Waxaad si rasmi ah ugu biirtay EyeTech Pro.
                </p>

                <p>
                Waxaan kuu soo diri doonaa updates iyo warar cusub.
                </p>

                <br>

                <p style="color:#22d3ee;">
                EyeTech Pro Team
                </p>
            </div>
            """
        })

        return jsonify({
            "success": True
        })

    except Exception as e:

        print("WAITLIST ERROR:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ======================================
# AI CHAT
# ======================================

@app.route("/api/assistant", methods=["POST"])
def assistant():

    try:

        data = request.json

        user_message = data.get("message")

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are EyeTech AI Assistant.

                    You help Somali users reduce electricity bills.

                    Always answer in Somali language.

                    Give real practical advice.
                    """
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        response = completion.choices[0].message.content

        return jsonify({
            "response": response
        })

    except Exception as e:

        print("CHAT ERROR:", str(e))

        return jsonify({
            "response": str(e)
        }), 500

# ======================================
# CALCULATOR
# ======================================

@app.route("/api/calculate", methods=["POST"])
def calculate():

    try:

        data = request.json

        wattage = float(data.get("wattage"))
        hours = float(data.get("hours"))

        somali_rate = 0.35

        daily = ((wattage * hours) / 1000) * somali_rate
        monthly = daily * 30
        yearly = daily * 365

        return jsonify({
            "daily": daily,
            "monthly": monthly,
            "yearly": yearly
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# ======================================
# IMAGE ANALYSIS
# ======================================

@app.route("/api/analyze-image", methods=["POST"])
def analyze_image():

    try:

        image = request.files["image"]

        image_bytes = image.read()

        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
                            Analyze this appliance image.

                            Return ONLY JSON:

                            {
                                "appliance":"",
                                "wattage":"",
                                "monthly_cost":0,
                                "efficiency":"",
                                "somali_tip":""
                            }
                            """
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )

        raw = completion.choices[0].message.content

        clean = raw.replace("```json", "").replace("```", "")

        result = json.loads(clean)

        return jsonify(result)

    except Exception as e:

        print("VISION ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500

# ======================================
# START
# ======================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

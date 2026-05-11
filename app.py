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

COMPANY_EMAIL = os.getenv("COMPANY_EMAIL")

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

        # ============================================
        # SEND EMAIL TO COMPANY
        # ============================================

        resend.Emails.send({

            "from": "EyeTech Pro <onboarding@resend.dev>",

            "to": COMPANY_EMAIL,

            "subject": "New EyeTech Pro Waitlist User",

            "html": f"""

            <h2>New Waitlist Signup</h2>

            <p><strong>Name:</strong> {name}</p>

            <p><strong>Email:</strong> {email}</p>

            <p><strong>WhatsApp:</strong> {whatsapp}</p>

            <p><strong>Feedback:</strong></p>

            <p>{feedback}</p>

            """

        })

        # ============================================
        # SEND CONFIRMATION EMAIL TO USER
        # ============================================
resend.Emails.send({

    "from": "EyeTech Pro <onboarding@resend.dev>",

    "to": "eyetech.engineering2026@gmail.com",

    "subject": f"New Waitlist User - {name}",

    "html": f"""

    <div style="font-family:Arial;padding:20px;">

        <h2>New EyeTech Pro Signup</h2>

        <p><strong>Name:</strong> {name}</p>

        <p><strong>Email:</strong> {email}</p>

        <p><strong>WhatsApp:</strong> {whatsapp}</p>

        <p><strong>Feedback:</strong></p>

        <p>{feedback}</p>

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

            model="gpt-4o-mini",

            messages=[

                {
                    "role": "system",
                    "content": """
You are EyeTech Pro AI Assistant.

You help Somali users understand:
- electricity bills
- appliance consumption
- energy efficiency
- electricity savings

Always answer in Somali language.
Be helpful and intelligent.
"""
                },

                {
                    "role": "user",
                    "content": user_message
                }

            ],

            max_tokens=400
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

        if "image" not in request.files:

            return jsonify({
                "success": False,
                "error": "No image uploaded"
            }), 400

        file = request.files["image"]

        image_bytes = file.read()

        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {
                    "role": "system",
                    "content": """
Analyze the appliance image.

Return ONLY JSON.

Format:

{
  "appliance": "string",
  "wattage": number,
  "monthly_cost": number,
  "efficiency": "string",
  "somali_tip": "string"
}
"""
                },

                {
                    "role": "user",
                    "content": [

                        {
                            "type": "text",
                            "text": "Analyze this appliance image."
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

            max_tokens=300
        )

        result = response.choices[0].message.content

        parsed = json.loads(result)

        return jsonify(parsed)

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

        # Somalia estimated electricity price
        price_per_kwh = 0.35

        daily_kwh = (wattage * hours) / 1000

        daily_cost = daily_kwh * price_per_kwh

        monthly_cost = daily_cost * 30

        yearly_cost = daily_cost * 365

        return jsonify({

            "daily": round(daily_cost, 2),

            "monthly": round(monthly_cost, 2),

            "yearly": round(yearly_cost, 2)

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# =====================================================
# 404
# =====================================================

@app.errorhandler(404)
def not_found(e):

    return jsonify({
        "error": "Route not found"
    }), 404

# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )

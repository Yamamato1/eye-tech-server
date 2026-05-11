import os
import json
import base64

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# LOAD ENV
load_dotenv()

# APP
app = Flask(__name__)

# ENABLE CORS
CORS(app)

# OPENAI API KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing")

# OPENAI CLIENT
client = OpenAI(api_key=OPENAI_API_KEY)

# ==============================
# HOME ROUTE
# ==============================

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "message": "EyeTech Pro AI Server Running"
    })

# ==============================
# AI CHAT ASSISTANT
# ==============================

@app.route('/api/assistant', methods=['POST'])
def assistant():

    try:

        data = request.json

        user_message = data.get('message', '')

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[

                {
                    "role": "system",
                    "content": """
You are EyeTech Pro AI Assistant.

You are:
- professional
- futuristic
- intelligent
- Somali + English speaking

You help users:
- understand appliances
- reduce electricity bills
- understand wattage
- save energy
- understand smart home systems

Keep answers short, modern, and intelligent.
"""
                },

                {
                    "role": "user",
                    "content": user_message
                }

            ]
        )

        return jsonify({
            "response": response.choices[0].message.content
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# ==============================
# IMAGE ANALYSIS
# ==============================

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():

    try:

        # CHECK IMAGE
        if 'image' not in request.files:
            return jsonify({
                "error": "No image uploaded"
            }), 400

        image = request.files['image']

        image_bytes = image.read()

        # CONVERT TO BASE64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # OPENAI VISION
        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[
                {
                    "role": "user",
                    "content": [

                        {
                            "type": "text",
                            "text": """
Analyze this appliance image.

Return ONLY valid JSON:

{
  "appliance": "",
  "wattage": "",
  "monthly_cost": "",
  "efficiency": "",
  "somali_tip": ""
}

Rules:
- wattage = estimated watts
- monthly_cost = estimated Somalia electricity monthly cost in USD
- efficiency = Low / Medium / High
- somali_tip = short Somali energy-saving tip
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
            ],

            response_format={
                "type": "json_object"
            }

        )

        result = json.loads(
            response.choices[0].message.content
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# ==============================
# ENERGY CALCULATOR
# ==============================

@app.route('/api/calculate', methods=['POST'])
def calculate():

    try:

        data = request.json

        wattage = float(data.get("wattage", 0))
        hours = float(data.get("hours", 0))

        # SOMALIA AVG RATE
        rate = 0.50

        daily_kwh = (wattage * hours) / 1000

        daily_cost = daily_kwh * rate
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

# ==============================
# WAITLIST
# ==============================

@app.route('/api/waitlist', methods=['POST'])
def waitlist():

    try:

        data = request.json

        name = data.get("name")
        email = data.get("email")
        whatsapp = data.get("whatsapp")
        feedback = data.get("feedback")

        print("\n========= NEW WAITLIST =========")
        print("NAME:", name)
        print("EMAIL:", email)
        print("WHATSAPP:", whatsapp)
        print("FEEDBACK:", feedback)
        print("================================\n")

        return jsonify({
            "success": True,
            "message": "Waad ku mahadsantahay ku biirista EyeTech Pro."
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# ==============================
# START SERVER
# ==============================

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 5000))
    )

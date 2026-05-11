# ============================================
# app.py
# FULL READY TO GO EYETECH SERVER
# ============================================

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import resend
import os
import base64
import json

# ============================================
# FLASK
# ============================================

app = Flask(__name__)
CORS(app)

# ============================================
# ENV VARIABLES
# ============================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL")

# ============================================
# OPENAI
# ============================================

client = OpenAI(
    api_key=OPENAI_API_KEY
)

# ============================================
# RESEND
# ============================================

resend.api_key = RESEND_API_KEY

# ============================================
# HOME PAGE
# ============================================

@app.route("/")
def home():

    return """
    <!DOCTYPE html>
    <html lang="en">

    <head>

        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>EyeTech Pro AI Server</title>

        <script src="https://cdn.tailwindcss.com"></script>

        <style>

            body{
                background:#0a0f1e;
                color:white;
                font-family:Arial;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
                overflow:hidden;
                margin:0;
            }

            .card{
                width:90%;
                max-width:700px;
                background:rgba(255,255,255,0.05);
                border:1px solid rgba(255,255,255,0.1);
                border-radius:40px;
                padding:60px;
                text-align:center;
                backdrop-filter:blur(20px);
                box-shadow:0 0 60px rgba(34,211,238,0.1);
            }

            .glow{
                position:absolute;
                width:500px;
                height:500px;
                background:#22d3ee;
                opacity:0.15;
                filter:blur(120px);
                z-index:-1;
            }

        </style>

    </head>

    <body>

        <div class="glow"></div>

        <div class="card">

            <h1 style="font-size:70px;font-weight:900;">
                EYETECH
                <span style="color:#22d3ee;">
                    PRO
                </span>
            </h1>

            <p style="font-size:22px;color:#94a3b8;margin-top:20px;">
                AI Energy Intelligence Server
            </p>

            <div style="
                margin-top:40px;
                background:rgba(34,211,238,0.08);
                border:1px solid rgba(34,211,238,0.2);
                padding:25px;
                border-radius:25px;
            ">

                <p style="
                    color:#22d3ee;
                    font-weight:bold;
                    font-size:18px;
                ">
                    Server Status: ONLINE
                </p>

            </div>

            <div style="
                margin-top:40px;
                color:#64748b;
                font-size:14px;
                letter-spacing:3px;
                text-transform:uppercase;
            ">
                Somalia's AI Energy Revolution
            </div>

        </div>

    </body>

    </html>
    """

# ============================================
# WAITLIST
# ============================================

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

            <div style="font-family:Arial;padding:30px;background:#0a0f1e;color:white;">

                <h1 style="color:#22d3ee;">
                    New EyeTech User
                </h1>

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

            <div style="font-family:Arial;padding:30px;background:#0a0f1e;color:white;">

                <h1 style="color:#22d3ee;">
                    Waad ku mahadsantahay!
                </h1>

                <p>
                    Salaam {name}
                </p>

                <p>
                    Waxaad si rasmi ah ugu biirtay EyeTech Pro.
                </p>

                <p>
                    Waxaan kuu soo diri doonaa updates iyo AI news.
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

# ============================================
# AI CHAT
# ============================================

@app.route("/api/assistant", methods=["POST"])
def assistant():

    try:

        data = request.json

        user_message = data.get("message")

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[

                {
                    "role":"system",
                    "content":"""

                    You are EyeTech AI Assistant.

                    You help Somali users reduce electricity bills.

                    Always answer in Somali language.

                    Give real practical energy advice.

                    """
                },

                {
                    "role":"user",
                    "content":user_message
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

# ============================================
# CALCULATOR
# ============================================

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
            "daily": round(daily,2),
            "monthly": round(monthly,2),
            "yearly": round(yearly,2)
        })

    except Exception as e:

        print("CALCULATOR ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500

# ============================================
# IMAGE AI ANALYSIS
# ============================================

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
                    "role":"user",

                    "content":[

                        {
                            "type":"text",

                            "text":"""

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
                            "type":"image_url",

                            "image_url":{
                                "url":f"data:image/jpeg;base64,{base64_image}"
                            }
                        }

                    ]
                }

            ]
        )

        raw = completion.choices[0].message.content

        clean = raw.replace("```json","").replace("```","")

        result = json.loads(clean)

        return jsonify(result)

    except Exception as e:

        print("VISION ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500

# ============================================
# START SERVER
# ============================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )

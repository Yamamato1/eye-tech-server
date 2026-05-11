from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import base64

app = Flask(__name__)
CORS(app)

# =========================
# OPENAI CLIENT
# =========================
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# =========================
# HOME PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# HEALTH CHECK
# =========================
@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "ai": "connected",
        "company": "EyeTech Pro"
    })

# =========================
# ENERGY CALCULATOR
# =========================
@app.route("/api/calculate", methods=["POST"])
def calculate():

    data = request.get_json()

    wattage = float(data.get("wattage", 0))
    hours = float(data.get("hours", 0))

    somali_rate = 0.35

    daily = ((wattage * hours) / 1000) * somali_rate
    monthly = daily * 30
    yearly = monthly * 12

    return jsonify({
        "daily": round(daily, 2),
        "monthly": round(monthly, 2),
        "yearly": round(yearly, 2)
    })

# =========================
# REAL OPENAI CHAT
# =========================
@app.route("/api/assistant", methods=["POST"])
def assistant():

    data = request.get_json()
    message = data.get("message", "")

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                You are EyeTech Pro AI Assistant.
                You help Somali users understand:
                - electricity usage
                - appliance costs
                - energy saving
                - smart home systems

                Speak naturally in Somali and English.
                """
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    reply = completion.choices[0].message.content

    return jsonify({
        "response": reply
    })

# =========================
# REAL AI IMAGE ANALYSIS
# =========================
@app.route("/api/analyze-image", methods=["POST"])
def analyze_image():

    image = request.files["image"]

    image_bytes = image.read()

    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                Analyze appliance images.

                Return:
                appliance name,
                estimated wattage,
                monthly electricity cost in Somalia,
                efficiency class,
                Somali energy saving tip.
                """
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this appliance."
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

    return jsonify({
        "result": result
    })

# =========================
# WAITLIST
# =========================
@app.route("/api/waitlist", methods=["POST"])
def waitlist():

    data = request.get_json()

    print("NEW USER:", data)

    return jsonify({
        "success": True
    })

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

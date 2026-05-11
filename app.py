from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "company": "EyeTech Pro",
        "server": "running"
    })


# -----------------------------
# ENERGY CALCULATOR API
# -----------------------------
@app.route("/api/calculate", methods=["POST"])
def calculate():

    data = request.get_json()

    wattage = float(data.get("wattage", 0))
    hours = float(data.get("hours", 0))

    # Somalia estimated electricity rate
    rate = 0.35

    daily = ((wattage * hours) / 1000) * rate
    monthly = daily * 30
    yearly = monthly * 12

    return jsonify({
        "daily": round(daily, 2),
        "monthly": round(monthly, 2),
        "yearly": round(yearly, 2)
    })


# -----------------------------
# AI CHAT ASSISTANT
# -----------------------------
@app.route("/api/assistant", methods=["POST"])
def assistant():

    data = request.get_json()
    user_message = data.get("message", "").lower()

    responses = [
        "Waxaan kuu xisaabin karaa kharashka korontada qalabkaaga.",
        "Fadlan ii sheeg watt-ka iyo saacadaha isticmaalka.",
        "Qalabkaasi wuxuu isticmaali karaa koronto badan.",
        "Waxaan kugula talinayaa inaad isticmaasho qalab energy-saving ah.",
        "EyeTech AI ayaa kaa caawinaya dhimista biilka korontada."
    ]

    if "ac" in user_message:
        reply = "AC-ga wuxuu isticmaalaa koronto badan gaar ahaan habeenkii."
    elif "tv" in user_message:
        reply = "TV-ga casriga ah wuxuu isticmaalaa koronto yar marka loo eego kuwii hore."
    elif "bill" in user_message:
        reply = "Waxaan kaa caawin karaa fahamka biilka korontada."
    else:
        reply = random.choice(responses)

    return jsonify({
        "response": reply
    })


# -----------------------------
# IMAGE ANALYSIS API
# -----------------------------
@app.route("/api/analyze-image", methods=["POST"])
def analyze_image():

    appliances = [
        {
            "appliance": "Air Conditioner",
            "wattage": 2200,
            "monthly_cost": 231,
            "efficiency": "Medium Efficiency",
            "somali_tip": "Isticmaal AC-ga marka kuleylku sareeyo oo keliya."
        },
        {
            "appliance": "Refrigerator",
            "wattage": 350,
            "monthly_cost": 44,
            "efficiency": "High Efficiency",
            "somali_tip": "Hubi in albaabka fridge-ka si fiican u xirmayo."
        },
        {
            "appliance": "Television",
            "wattage": 120,
            "monthly_cost": 15,
            "efficiency": "Excellent",
            "somali_tip": "Dami TV-ga marka aan la isticmaaleyn."
        }
    ]

    result = random.choice(appliances)

    return jsonify(result)


# -----------------------------
# WAITLIST API
# -----------------------------
@app.route("/api/waitlist", methods=["POST"])
def waitlist():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")

    print(f"NEW USER: {name} - {email}")

    return jsonify({
        "success": True,
        "message": "Successfully joined waitlist"
    })


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

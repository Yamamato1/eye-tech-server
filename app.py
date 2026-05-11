from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import google.generativeai as genai

app = Flask(__name__)

# =========================
# CONFIG
# =========================

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# =========================
# GEMINI API KEY
# =========================

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# CHAT API
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    user_message = data.get("message")

    prompt = f"""
    Waxaad tahay EyeTech Core, sirdoonka rasmiga ah ee EyeTech Pro Somalia.
    Hadalkaaga oo dhan waa Soomaali.
    Marna ha sheegin magac kale oo AI ah.
    U sharax dadka sida cilmiyeysan ee ay korontada u badbaadin karaan.
    Noqo mid caqli badan, casri ah, oo Soomaali ah.

    User:
    {user_message}
    """

    try:
        response = model.generate_content(prompt)

        return jsonify({
            "response": response.text
        })

    except Exception as e:
        return jsonify({
            "response": f"Error: {str(e)}"
        })


# =========================
# IMAGE ANALYSIS API
# =========================

@app.route("/analyze-image", methods=["POST"])
def analyze_image():

    if "image" not in request.files:
        return jsonify({
            "response": "Sawir lama helin."
        })

    image = request.files["image"]

    filename = secure_filename(image.filename)

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    image.save(filepath)

    prompt = """
    Waa maxay qalabkani?
    Sidee korontadiisa loo badbaadin karaa?
    Sharaxaad dheeraad ah sii qof Soomaali ah oo raba inuu biilka dhimo.
    """

    try:

        uploaded_file = genai.upload_file(filepath)

        response = model.generate_content([
            prompt,
            uploaded_file
        ])

        return jsonify({
            "response": response.text
        })

    except Exception as e:
        return jsonify({
            "response": f"Error: {str(e)}"
        })


# =========================
# FEEDBACK API
# =========================

@app.route("/feedback", methods=["POST"])
def feedback():

    data = request.json

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    message = data.get("message")

    print("========= NEW FEEDBACK =========")
    print("Name:", name)
    print("Email:", email)
    print("Phone:", phone)
    print("Message:", message)
    print("================================")

    return jsonify({
        "success": True
    })


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)

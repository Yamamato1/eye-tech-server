from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from openai import OpenAI
import os
import base64

app = Flask(__name__)

# =========================
# CONFIG
# =========================

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# =========================
# OPENAI API
# =========================

client = OpenAI(
    api_key="YOUR_OPENAI_API_KEY"
)

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

    try:

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                    Waxaad tahay EyeTech Core,
                    sirdoonka rasmiga ah ee EyeTech Pro Somalia.

                    Hadalkaaga oo dhan waa Soomaali.
                    Marna ha sheegin AI kale.
                    Dadka bar sida korontada loo badbaadiyo.
                    """
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        reply = response.choices[0].message.content

        return jsonify({
            "response": reply
        })

    except Exception as e:

        return jsonify({
            "response": str(e)
        })

# =========================
# IMAGE ANALYSIS
# =========================

@app.route("/analyze-image", methods=["POST"])
def analyze_image():

    if "image" not in request.files:

        return jsonify({
            "response": "Sawir lama helin"
        })

    image = request.files["image"]

    filename = secure_filename(image.filename)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    image.save(filepath)

    with open(filepath, "rb") as img_file:

        base64_image = base64.b64encode(
            img_file.read()
        ).decode("utf-8")

    try:

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                    Waxaad tahay EyeTech Core.
                    Falanqee qalabka sawirka ku jira.
                    Sharax sida koronto loo badbaadin karo.
                    """
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
                            Waa maxay qalabkani?
                            Sidee korontadiisa loo yareyn karaa?
                            """
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )

        reply = response.choices[0].message.content

        return jsonify({
            "response": reply
        })

    except Exception as e:

        return jsonify({
            "response": str(e)
        })

# =========================
# FEEDBACK
# =========================

@app.route("/feedback", methods=["POST"])
def feedback():

    data = request.json

    print("NEW FEEDBACK")
    print(data)

    return jsonify({
        "success": True
    })

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)

import os
import base64
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates")
CORS(app)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# FRONTEND WEBSITE
@app.route('/')
def home():
    return render_template('index.html')

# AI CHAT
@app.route('/api/assistant', methods=['POST'])
def assistant():
    try:
        data = request.json
        user_message = data.get("message", "")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are EyeTech Pro AI Assistant from Mogadishu Somalia. You help users with AI, energy systems, smart homes, and technology in Somali and English."
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
        return jsonify({"error": str(e)}), 500

# IMAGE ANALYSIS
@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    try:
        data = request.json
        base64_image = data.get("image")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
Identify this appliance and return JSON with:
name,
wattage,
monthly_cost_usd,
efficiency_level,
somali_tip
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
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# WAITLIST
@app.route('/api/waitlist', methods=['POST'])
def waitlist():
    data = request.json
    email = data.get("email")

    return jsonify({
        "status": "success",
        "message": f"{email} added successfully"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

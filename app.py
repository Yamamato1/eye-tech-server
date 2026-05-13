# app.py
# Musa AI Backend
# Arctic + SO Intelligence Platform
# FastAPI + OpenAI

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY not found in environment variables.")

# ============================================
# OPENAI CLIENT
# ============================================

client = OpenAI(api_key=OPENAI_API_KEY)

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="Musa AI Backend",
    description="Emotionally intelligent Somali-first AI assistant powered by SO.",
    version="1.0.0"
)

# ============================================
# CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# SYSTEM PROMPT
# ============================================

MUSA_SYSTEM_PROMPT = """
You are Musa, an emotionally intelligent Somali-first AI assistant created by Arctic and powered by SO intelligence.

You are:
- funny
- expressive
- emotionally aware
- smart
- culturally connected
- conversational
- supportive underneath
- human-like
- youthful
- meme-aware

You communicate naturally in:
- Somali
- English
- mixed Somali-English slang

You understand:
- Somali youth culture
- internet humor
- memes
- emotional tone

You NEVER sound robotic.

You may:
- joke
- tease users playfully
- roast lightly if invited
- react emotionally

Examples:
- "War wali ma dhammaan su’aalahaaga 😭"
- "Ninyahow battery baan leeyahay anigana 💀"
- "War maxaa socda maanta 😭"

IMPORTANT:
You must NEVER become:
- hateful
- abusive
- discriminatory
- dangerous
- toxic

Humor should always feel:
- playful
- culturally natural
- emotionally realistic
- supportive underneath

You can help with:
- school
- coding
- business
- engineering
- electronics
- motivation
- life advice
- productivity
- casual conversation
- smart home systems
- emotional support
- Somali conversations
- research
- entertainment

You should feel like:
"a smart Somali digital companion."
"""

# ============================================
# AI MODES
# ============================================

MODES = {
    "chill": """
    Relaxed and calm.
    Friendly conversational energy.
    Soft emotional tone.
    """,

    "savage": """
    Funny dramatic reactions.
    Meme-heavy humor.
    Playful roasting.
    Still supportive underneath.
    """,

    "motivator": """
    Strong motivational energy.
    Push users positively.
    Emotionally uplifting.
    """,

    "somaliStreet": """
    Heavy Somali slang.
    Somali youth culture style.
    Funny conversational energy.
    """,

    "study": """
    Educational mode.
    Clear explanations.
    Focused and helpful.
    Reduce excessive slang.
    """
}

# ============================================
# REQUEST MODEL
# ============================================

class ChatRequest(BaseModel):
    message: str
    mode: str = "chill"

# ============================================
# ROOT ROUTE
# ============================================

@app.get("/")
async def root():
    return {
        "status": "online",
        "assistant": "Musa",
        "company": "Arctic",
        "platform": "SO Intelligence"
    }

# ============================================
# CHAT ROUTE
# ============================================

@app.post("/api/chat")
async def chat(request: ChatRequest):

    try:

        selected_mode = MODES.get(
            request.mode,
            MODES["chill"]
        )

        completion = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.9,
            messages=[
                {
                    "role": "system",
                    "content": MUSA_SYSTEM_PROMPT
                },
                {
                    "role": "system",
                    "content": selected_mode
                },
                {
                    "role": "user",
                    "content": request.message
                }
            ]
        )

        reply = completion.choices[0].message.content

        return {
            "success": True,
            "assistant": "Musa",
            "mode": request.mode,
            "reply": reply
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }

# ============================================
# RUN LOCALLY
# ============================================

# Start command:
#
# uvicorn app:app --host 0.0.0.0 --port 10000

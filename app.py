import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

import chatbot_config as cfg

load_dotenv()

app = Flask(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


@app.route("/")
def index():
    return render_template("index.html", bot_name=cfg.BOT_NAME, tagline=cfg.TAGLINE)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify(error="Please type a question."), 400

    contents = [
        types.Content(role=turn["role"], parts=[types.Part(text=turn["text"])])
        for turn in data.get("history", [])[-12:]
        if turn.get("role") in ("user", "model") and turn.get("text")
    ]
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    try:
        response = client.models.generate_content(
            model=cfg.MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=cfg.SYSTEM_PROMPT,
                temperature=0.4,
            ),
        )
        return jsonify(reply=response.text)
    except Exception:
        return jsonify(error="Something went wrong. Please try again."), 500


if __name__ == "__main__":
    app.run(debug=True)

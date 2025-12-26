import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# Create chat session (keeps memory)
chat = model.start_chat(history=[])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_quote", methods=["POST"])
def get_quote():
    # We send a specific "system" instruction to Gemini for this feature
    prompt = "Give me a famous inspirational quote and a brief sentence of encouragement."
    try:
        response = model.generate_content(prompt)
        return jsonify({"quote": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/chat", methods=["POST"])
def chat_with_gemini():
    user_message = request.json.get("message")
    response = chat.send_message(user_message)
    return jsonify({"reply": response.text})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
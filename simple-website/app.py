import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import markdown
import datetime
load_dotenv()

app = Flask(__name__)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# Store chat sessions per user (in production, use Redis or database)
chat_sessions = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_quote", methods=["POST"])
def get_quote():
    prompt = "Give me a famous inspirational quote with the author's name, followed by a brief encouraging message. Format: Quote by Author, then encouragement."
    try:
        response = model.generate_content(prompt)
        return jsonify({"quote": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat_with_gemini():
    try:
        user_message = request.json.get("message")
        session_id = request.json.get("session_id", "default")
        
        # Get or create chat session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = model.start_chat(history=[])
        
        chat = chat_sessions[session_id]
        response = chat.send_message(user_message)
        
        # Convert markdown to HTML for better formatting
        formatted_response = markdown.markdown(
            response.text,
            extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
        )
        
        return jsonify({
            "reply": response.text,
            "formatted_reply": formatted_response,
            "timestamp": datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear_chat", methods=["POST"])
def clear_chat():
    try:
        session_id = request.json.get("session_id", "default")
        if session_id in chat_sessions:
            chat_sessions[session_id] = model.start_chat(history=[])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/summarize", methods=["POST"])
def summarize_text():
    try:
        text = request.json.get("text")
        prompt = f"Please provide a concise summary of the following text:\n\n{text}"
        response = model.generate_content(prompt)
        return jsonify({"summary": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/explain_code", methods=["POST"])
def explain_code():
    try:
        code = request.json.get("code")
        language = request.json.get("language", "unknown")
        prompt = f"Explain this {language} code in simple terms, including what it does and how it works:\n\n```{language}\n{code}\n```"
        response = model.generate_content(prompt)
        return jsonify({"explanation": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate_idea", methods=["POST"])
def generate_idea():
    try:
        category = request.json.get("category", "project")
        prompt = f"Generate a creative and innovative {category} idea with a brief description and 3-5 key features or implementation steps."
        response = model.generate_content(prompt)
        return jsonify({"idea": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/quick_action", methods=["POST"])
def quick_action():
    try:
        action_type = request.json.get("type", "general")
        
        prompts = {
            "sport": "Suggest a sport or workout routine for today with benefits and tips. Keep it motivating and practical!",
            "food": "Suggest a delicious and healthy meal idea with ingredients and brief cooking instructions.",
            "education": "Suggest an interesting topic to learn today with why it's valuable and where to start.",
            "entertainment": "Suggest an entertaining activity, movie, or show with a brief description and why it's worth trying.",
            "productivity": "Suggest a productivity tip or technique to improve focus and efficiency today.",
            "wellness": "Suggest a wellness practice or self-care activity for mental and physical health.",
            "hobby": "Suggest a fun hobby or creative activity to try with beginner tips.",
            "travel": "Suggest an interesting travel destination with highlights and travel tips."
        }
        
        prompt = prompts.get(action_type, "Give me a helpful suggestion for today.")
        response = model.generate_content(prompt)
        return jsonify({"suggestion": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
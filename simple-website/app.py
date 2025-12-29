import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import markdown
import datetime
load_dotenv(override=True)

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



@app.route("/generate_readme", methods=["POST"])
def generate_readme():
    try:
        code = request.json.get("code", "")
        project_name = request.json.get("project_name", "")
        description = request.json.get("description", "")
        
        prompt = f"""
        Generate a professional, comprehensive README.md file for this project.
        
        Project Name: {project_name if project_name else "Not specified"}
        Description: {description if description else "Not specified"}
        
        Code:
        ```
        {code}
        ```
        
        Create a README with these sections:
        1. Project Title and Description
        2. Features (based on the code)
        3. Technologies Used (identify from code)
        4. Installation Instructions
        5. Usage Examples
        6. API Documentation (if applicable)
        7. Configuration/Environment Variables (if needed)
        8. Project Structure
        9. Contributing Guidelines
        10. License
        
        Make it professional, clear, and include code examples where relevant.
        Use proper markdown formatting with headers, code blocks, lists, and badges where appropriate.
        """
        
        response = model.generate_content(prompt)
        return jsonify({"readme": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/add_comments", methods=["POST"])
def add_comments():
    try:
        code = request.json.get("code", "")
        language = request.json.get("language", "python")
        comment_level = request.json.get("level", "medium")  # basic, medium, detailed
        
        level_instructions = {
            "basic": "Add minimal inline comments only for complex logic.",
            "medium": "Add inline comments for functions, classes, and non-obvious code sections. Include docstrings.",
            "detailed": "Add comprehensive comments explaining the purpose, parameters, return values, and logic for every function and complex code block. Include examples in docstrings."
        }
        
        prompt = f"""
        Add clear, professional comments to this {language} code.
        Comment Level: {comment_level} - {level_instructions.get(comment_level, level_instructions['medium'])}
        
        Code:
        ```{language}
        {code}
        ```
        
        Requirements:
        1. Preserve all original code exactly
        2. Add {comment_level} level comments
        3. For functions: Add docstrings with purpose, parameters, and return values
        4. For complex logic: Add inline comments explaining what's happening
        5. For classes: Add class-level docstrings
        6. Use proper comment syntax for {language}
        7. Keep comments concise but informative
        
        Return ONLY the commented code, no explanations before or after.
        """
        
        response = model.generate_content(prompt)
        return jsonify({"commented_code": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/design_system", methods=["POST"])
def design_system():
    try:
        description = request.json.get("description", "")
        diagram_type = request.json.get("type", "architecture")  # architecture, database, flowchart, sequence
        
        diagram_instructions = {
            "architecture": "Create a system architecture diagram description with components, layers, and their interactions. Include frontend, backend, database, external services, and data flow.",
            "database": "Create a database schema diagram with tables, fields, data types, relationships (one-to-many, many-to-many), and constraints. Use ER diagram format.",
            "flowchart": "Create a detailed flowchart showing the process flow with decision points, actions, start/end points, and different paths.",
            "sequence": "Create a sequence diagram showing the interactions between different components/actors over time, with messages and responses.",
            "class": "Create a UML class diagram showing classes, attributes, methods, relationships (inheritance, composition, association), and visibility modifiers."
        }
        
        prompt = f"""
        Based on this project description, generate a detailed software design and planning document with diagrams.
        
        Project Description:
        {description}
        
        Diagram Type Requested: {diagram_type}
        
        Create a comprehensive design document with:
        
        1. **System Overview**
           - Purpose and goals
           - Key features
           - Target users
        
        2. **{diagram_type.title()} Diagram**
           {diagram_instructions.get(diagram_type, diagram_instructions['architecture'])}
           
           Provide the diagram in TWO formats:
           a) **Mermaid syntax** (for rendering) - Use proper mermaid.js syntax
           b) **ASCII art** (for quick visualization)
           c) **Detailed text description** explaining each component
        
        3. **Component Descriptions**
           - Detailed explanation of each component/module
           - Technologies recommended
           - Responsibilities and interactions
        
        4. **Data Flow**
           - How data moves through the system
           - API endpoints (if applicable)
           - Database operations
        
        5. **Technical Stack Recommendations**
           - Frontend technologies
           - Backend technologies
           - Database choices
           - Third-party services
        
        6. **Implementation Plan**
           - Phase 1: Core features
           - Phase 2: Additional features
           - Phase 3: Optimization and scaling
        
        7. **Potential Challenges and Solutions**
           - Technical challenges
           - Scalability concerns
           - Security considerations
        
        Make it professional, detailed, and actionable. Use proper markdown formatting.
        """
        
        response = model.generate_content(prompt)
        return jsonify({"design": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
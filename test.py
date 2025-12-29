

import google.generativeai as genai

# 🔑 Replace with your API key
genai.configure(api_key="AIzaSyAYGQ5w3FiMx5AaWMIXg15Yc3KZ_I7TXxw")

# Choose a model
model = genai.GenerativeModel("gemini-2.5-flash")

# Start a chat session (keeps conversation memory)
chat = model.start_chat(history=[])

print("🤖 Gemini Chatbot")
print("Type 'exit' to quit\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Goodbye 👋")
        break

    response = chat.send_message(user_input)

    print("Gemini:", response.text)



    
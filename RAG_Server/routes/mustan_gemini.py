from flask import Blueprint, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
from langchain.schema import SystemMessage, HumanMessage, AIMessage

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

router = Blueprint('mustan_gemini', __name__)

# In-memory chat history
chat_history = [
    SystemMessage(content="You are a helpful assistant.")
]


@router.route('/prompt', methods=['POST'])
def get_human_input():
    data = request.get_json()
    human = data.get("prompt", "")

    # Add human message to history
    chat_history.append(HumanMessage(content=human))

    # Build context from chat history
    context = "\n".join(
        f"{type(msg).__name__}: {msg.content}" for msg in chat_history
    )

    # Send context to Gemini model
    ai_response = model.generate_content(context, generation_config={
        "temperature": 0,
        "top_k": 10,
        "top_p": 0.8
    }).text

    # Add AI response to history
    chat_history.append(AIMessage(content=ai_response))

    return jsonify({
        "response": ai_response
    })


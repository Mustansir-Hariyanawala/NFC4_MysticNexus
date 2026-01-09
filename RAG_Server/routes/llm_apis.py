"""
LLM API Routes

This module provides RESTful endpoints for interacting with Google Gemini LLM,
integrated with MongoDB for chat history management.

Endpoints:
    - POST   /generate_response         : Generate LLM response (with/without history)
    - GET    /test_mongo_connection    : Test MongoDB API connection
    - GET    /fetch_history/<chat_id>  : Fetch chat history from MongoDB
    - GET    /health                   : Health check for LLM APIs

Expected JSON payload for POST /generate_response:
    {
        "prompt": "string (required)",
        "chat_id": "string (required)",
        "temperature": 0.7,        // optional
        "top_k": 40,               // optional
        "top_p": 0.8,              // optional
        "save_to_mongo": true,     // optional
        "use_history": true,       // optional
        "prompt_docs": []          // optional
    }
"""

from flask import Blueprint, request, jsonify
import google.generativeai as genai
import os
import requests
from dotenv import load_dotenv
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint for LLM APIs
router = Blueprint('llm_apis', __name__)

class GoogleAIManager:
    """
    Handles Google Gemini LLM interactions and MongoDB chat history management.
    """
    def __init__(self, mongo_api_base_url: Optional[str] = None):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.mongo_api_base_url = mongo_api_base_url or os.getenv("MONGO_API_BASE_URL", "http://localhost:3000/api")
        self.default_system_message = SystemMessage(
            content="You are a helpful assistant. Provide accurate and helpful responses based on the conversation history."
        )
        logger.info("Google AI Manager initialized successfully with MongoDB integration")

    async def fetch_chat_history_from_mongo(self, chat_id: str) -> List[Dict[str, Any]]:
        """
        Fetch chat history from MongoDB via API call.
        Returns a list of message dicts.
        """
        try:
            url = f"{self.mongo_api_base_url}/chat/history/{chat_id}"
            logger.info(f"Fetching chat history from MongoDB for chat_id: {chat_id}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "messages" in data:
                    messages = data["messages"]
                elif "history" in data:
                    messages = data["history"]
                elif isinstance(data, list):
                    messages = data
                else:
                    logger.warning(f"Unexpected response format from MongoDB API: {data}")
                    return []
                logger.info(f"Successfully fetched {len(messages)} messages for chat_id: {chat_id}")
                return messages
            elif response.status_code == 404:
                logger.info(f"No chat history found for chat_id: {chat_id}")
                return []
            else:
                logger.error(f"Failed to fetch chat history. Status: {response.status_code}, Response: {response.text}")
                return []
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching chat history for chat_id: {chat_id}")
            return []
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error while fetching chat history for chat_id: {chat_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching chat history from MongoDB for chat_id {chat_id}: {str(e)}")
            return []

    def _convert_mongo_to_langchain_messages(self, mongo_messages: List[Dict[str, Any]]) -> List[Any]:
        """
        Convert MongoDB message format to LangChain message objects.
        """
        langchain_messages = [self.default_system_message]
        try:
            for msg in mongo_messages:
                prompt_data = msg.get("prompt", {})
                prompt_text = prompt_data.get("text", "")
                prompt_docs = prompt_data.get("docs", [])
                resp_data = msg.get("resp", {})
                resp_text = resp_data.get("text", "")
                resp_citations = resp_data.get("citations", [])
                if not prompt_text and not resp_text:
                    continue
                if prompt_text:
                    docs_info = f" [Referenced {len(prompt_docs)} documents]" if prompt_docs else ""
                    langchain_messages.append(HumanMessage(content=prompt_text + docs_info))
                if resp_text:
                    citations_info = f"\n\n[Citations: {len(resp_citations)} sources]" if resp_citations else ""
                    langchain_messages.append(AIMessage(content=resp_text + citations_info))
            logger.info(f"Converted {len(mongo_messages)} MongoDB message pairs to {len(langchain_messages)} LangChain messages")
            return langchain_messages
        except Exception as e:
            logger.error(f"Error converting MongoDB messages to LangChain format: {str(e)}")
            return [self.default_system_message]

    def _build_context_from_messages(self, messages: List[Any]) -> str:
        """
        Build context string from LangChain message objects.
        """
        context = "\n".join(
            f"{type(msg).__name__}: {msg.content}" for msg in messages
        )
        return context

    async def save_message_to_mongo(self, chat_id: str, prompt_text: str, response_text: str, 
                                  prompt_docs: List[Dict] = None, response_citations: List[Dict] = None) -> bool:
        """
        Save a complete conversation turn to MongoDB via API call.
        """
        try:
            url = f"{self.mongo_api_base_url}/chat/message"
            payload = {
                "chat_id": chat_id,
                "prompt": {
                    "text": prompt_text,
                    "docs": prompt_docs or []
                },
                "resp": {
                    "text": response_text,
                    "citations": response_citations or []
                },
                "timestamp": datetime.now().isoformat()
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code in [200, 201]:
                logger.info(f"Successfully saved conversation turn to MongoDB for chat_id: {chat_id}")
                return True
            else:
                logger.error(f"Failed to save conversation turn to MongoDB. Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error saving conversation turn to MongoDB for chat_id {chat_id}: {str(e)}")
            return False

    async def generate_response_with_mongo_history(self, prompt: str, chat_id: str, 
                                                 temperature: float = 0.7, top_k: int = 40, 
                                                 top_p: float = 0.8, 
                                                 save_to_mongo: bool = True,
                                                 prompt_docs: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate response using Google AI with MongoDB chat history.
        """
        try:
            mongo_messages = await self.fetch_chat_history_from_mongo(chat_id)
            langchain_messages = self._convert_mongo_to_langchain_messages(mongo_messages)
            langchain_messages.append(HumanMessage(content=prompt))
            context = self._build_context_from_messages(langchain_messages)
            logger.info(f"Generating response for chat_id: {chat_id} with {len(langchain_messages)} messages in context")
            response = self.model.generate_content(
                context, 
                generation_config={
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p
                }
            )
            ai_response_text = response.text
            if save_to_mongo:
                await self.save_message_to_mongo(
                    chat_id=chat_id,
                    prompt_text=prompt,
                    response_text=ai_response_text,
                    prompt_docs=prompt_docs,
                    response_citations=[]
                )
            return {
                "status": "success",
                "response": ai_response_text,
                "chat_id": chat_id,
                "context_messages": len(langchain_messages),
                "mongo_history_loaded": len(mongo_messages),
                "saved_to_mongo": save_to_mongo,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating response with MongoDB history for chat_id {chat_id}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "chat_id": chat_id,
                "timestamp": datetime.now().isoformat()
            }

    async def generate_response_without_history(self, prompt: str, 
                                              temperature: float = 0.7, top_k: int = 40, 
                                              top_p: float = 0.8) -> Dict[str, Any]:
        """
        Generate response without any chat history (one-off query).
        """
        try:
            context = f"{self.default_system_message.content}\nHumanMessage: {prompt}"
            response = self.model.generate_content(
                context, 
                generation_config={
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p
                }
            )
            ai_response_text = response.text
            return {
                "status": "success",
                "response": ai_response_text,
                "context_messages": 2,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating response without history: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def test_mongo_connection(self) -> Dict[str, Any]:
        """
        Test connection to MongoDB API.
        """
        try:
            test_url = f"{self.mongo_api_base_url}/health"
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "MongoDB API connection successful",
                    "mongo_api_url": self.mongo_api_base_url
                }
            else:
                return {
                    "status": "warning",
                    "message": f"MongoDB API responded with status: {response.status_code}",
                    "mongo_api_url": self.mongo_api_base_url
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to connect to MongoDB API: {str(e)}",
                "mongo_api_url": self.mongo_api_base_url
            }

# Global instance - initialized when server starts
google_ai_manager = None

def initialize_google_ai(mongo_api_base_url: Optional[str] = None):
    """
    Initialize Google AI Manager with MongoDB integration - called when server starts.
    """
    global google_ai_manager
    try:
        google_ai_manager = GoogleAIManager(mongo_api_base_url=mongo_api_base_url)
        logger.info("Google AI Manager with MongoDB integration initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Google AI Manager: {str(e)}")
        return False

# ---------------------------
# API Endpoints
# ---------------------------

@router.route('/generate_response', methods=['POST'])
def generate_response():
    """
    Generate response using Google AI Gemini with MongoDB chat history.

    Request Body:
        See module docstring for details.
    """
    try:
        if not google_ai_manager:
            return jsonify({
                "status": "error",
                "error": "Google AI Manager not initialized"
            }), 500
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "error": "No JSON data provided"
            }), 400
        prompt = data.get("prompt")
        chat_id = data.get("chat_id")
        if not prompt:
            return jsonify({
                "status": "error",
                "error": "Missing required field: prompt"
            }), 400
        temperature = data.get("temperature", 0.7)
        top_k = data.get("top_k", 40)
        top_p = data.get("top_p", 0.8)
        save_to_mongo = data.get("save_to_mongo", True)
        use_history = data.get("use_history", False)
        prompt_docs = data.get("prompt_docs", [])
        if not (0.0 <= temperature <= 2.0):
            return jsonify({
                "status": "error",
                "error": "temperature must be between 0.0 and 2.0"
            }), 400
        if not (1 <= top_k <= 100):
            return jsonify({
                "status": "error",
                "error": "top_k must be between 1 and 100"
            }), 400
        if not (0.0 <= top_p <= 1.0):
            return jsonify({
                "status": "error",
                "error": "top_p must be between 0.0 and 1.0"
            }), 400
        import asyncio
        if use_history and chat_id:
            result = asyncio.run(google_ai_manager.generate_response_with_mongo_history(
                prompt=prompt,
                chat_id=chat_id,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                save_to_mongo=save_to_mongo,
                prompt_docs=prompt_docs
            ))
        else:
            result = asyncio.run(google_ai_manager.generate_response_without_history(
                prompt=prompt,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p
            ))
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    except Exception as e:
        logger.error(f"Error in generate_response endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@router.route('/test_mongo_connection', methods=['GET'])
def test_mongo_connection():
    """
    Test connection to MongoDB API.
    """
    try:
        if not google_ai_manager:
            return jsonify({
                "status": "error",
                "error": "Google AI Manager not initialized"
            }), 500
        import asyncio
        result = asyncio.run(google_ai_manager.test_mongo_connection())
        if result["status"] == "success":
            return jsonify(result), 200
        elif result["status"] == "warning":
            return jsonify(result), 206
        else:
            return jsonify(result), 500
    except Exception as e:
        logger.error(f"Error testing MongoDB connection: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@router.route('/fetch_history/<chat_id>', methods=['GET'])
def fetch_chat_history(chat_id: str):
    """
    Fetch chat history from MongoDB for debugging purposes.
    """
    try:
        if not google_ai_manager:
            return jsonify({
                "status": "error",
                "error": "Google AI Manager not initialized"
            }), 500
        import asyncio
        mongo_messages = asyncio.run(google_ai_manager.fetch_chat_history_from_mongo(chat_id))
        return jsonify({
            "status": "success",
            "chat_id": chat_id,
            "messages": mongo_messages,
            "message_count": len(mongo_messages),
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@router.route('/health', methods=['GET'])
def llm_health():
    """
    Health check for LLM APIs.
    """
    try:
        if not google_ai_manager:
            return jsonify({
                "status": "unhealthy",
                "error": "Google AI Manager not initialized"
            }), 500
        import asyncio
        mongo_status = asyncio.run(google_ai_manager.test_mongo_connection())
        return jsonify({
            "status": "healthy",
            "service": "Google AI LLM APIs with MongoDB",
            "mongo_connection": mongo_status["status"],
            "mongo_api_url": google_ai_manager.mongo_api_base_url,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500
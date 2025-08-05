#!/usr/bin/env python3
"""
Test script for LLM APIs with MongoDB chat history format
Demonstrates how the MongoDB conversation format is handled
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:5000/api/llm"

def test_mongodb_format_conversion():
    """Test the MongoDB format conversion with sample data"""
    print("=== Testing MongoDB Format Conversion ===")
    
    # Sample MongoDB chat history in your format
    sample_mongo_history = [
        {
            "prompt": {
                "text": "What is artificial intelligence?",
                "docs": []
            },
            "resp": {
                "text": "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that can think, learn, and problem-solve like humans. It involves developing algorithms and systems that can perform tasks that typically require human intelligence.",
                "citations": []
            }
        },
        {
            "prompt": {
                "text": "Can you explain machine learning?",
                "docs": [
                    {"id": "doc1", "title": "ML Basics"},
                    {"id": "doc2", "title": "Neural Networks"}
                ]
            },
            "resp": {
                "text": "Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms to analyze data, identify patterns, and make predictions or decisions.",
                "citations": [
                    {"source": "ML Textbook", "page": 15},
                    {"source": "Research Paper", "page": 3}
                ]
            }
        },
        {
            "prompt": {
                "text": "How does deep learning differ from traditional ML?",
                "docs": []
            },
            "resp": {
                "text": "Deep learning uses neural networks with multiple layers (hence 'deep') to model and understand complex patterns in data. Unlike traditional ML which often requires manual feature engineering, deep learning can automatically learn features from raw data.",
                "citations": []
            }
        }
    ]
    
    print("Sample MongoDB Chat History:")
    print(json.dumps(sample_mongo_history, indent=2))
    
    return sample_mongo_history

def test_generate_response_with_mongo_format():
    """Test generating response with MongoDB chat history format"""
    print("\n=== Testing Generate Response with MongoDB Format ===")
    
    url = f"{BASE_URL}/generate_response"
    
    # Test data that assumes MongoDB history exists
    test_data = {
        "prompt": "What are the practical applications of these AI technologies?",
        "chat_id": "test_mongo_format_chat",
        "temperature": 0.7,
        "save_to_mongo": True,
        "use_history": True,
        "prompt_docs": [
            {"id": "app_doc1", "title": "AI Applications in Healthcare"},
            {"id": "app_doc2", "title": "AI in Finance"}
        ]
    }
    
    try:
        response = requests.post(url, json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_fetch_history_debug():
    """Test fetching history for debugging"""
    print("\n=== Testing Fetch History (Debug) ===")
    
    chat_id = "test_mongo_format_chat"
    url = f"{BASE_URL}/fetch_history/{chat_id}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_sample_mongo_api_response():
    """Create sample response that your MongoDB API should return"""
    print("\n=== Sample MongoDB API Response Format ===")
    
    sample_api_response = {
        "status": "success",
        "chat_id": "test_mongo_format_chat",
        "history": [
            {
                "prompt": {
                    "text": "What is artificial intelligence?",
                    "docs": []
                },
                "resp": {
                    "text": "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that can think, learn, and problem-solve like humans.",
                    "citations": []
                }
            },
            {
                "prompt": {
                    "text": "Can you explain machine learning?",
                    "docs": [
                        {"id": "doc1", "title": "ML Basics", "filename": "ml_basics.pdf"},
                        {"id": "doc2", "title": "Neural Networks", "filename": "neural_nets.pdf"}
                    ]
                },
                "resp": {
                    "text": "Machine Learning is a subset of AI that enables computers to learn from data without explicit programming.",
                    "citations": [
                        {"source": "ML Textbook", "page": 15, "confidence": 0.95},
                        {"source": "Research Paper", "page": 3, "confidence": 0.87}
                    ]
                }
            }
        ],
        "message_count": 2,
        "timestamp": datetime.now().isoformat()
    }
    
    print("Your MongoDB API should return this format:")
    print("GET /api/chat/history/{chat_id}")
    print(json.dumps(sample_api_response, indent=2))
    
    return sample_api_response

def create_sample_mongo_save_request():
    """Create sample request for saving to MongoDB"""
    print("\n=== Sample MongoDB Save Request Format ===")
    
    sample_save_request = {
        "chat_id": "test_mongo_format_chat",
        "prompt": {
            "text": "What are the practical applications of AI?",
            "docs": [
                {"id": "app_doc1", "title": "AI Applications in Healthcare"},
                {"id": "app_doc2", "title": "AI in Finance"}
            ]
        },
        "resp": {
            "text": "AI has numerous practical applications including: 1) Healthcare - medical diagnosis, drug discovery, personalized treatment. 2) Finance - fraud detection, algorithmic trading, risk assessment. 3) Transportation - autonomous vehicles, route optimization.",
            "citations": []
        },
        "timestamp": datetime.now().isoformat()
    }
    
    print("Your MongoDB API should accept this format:")
    print("POST /api/chat/message")
    print(json.dumps(sample_save_request, indent=2))
    
    return sample_save_request

def create_curl_examples():
    """Create curl command examples"""
    print("\n=== cURL Command Examples ===")
    
    # Example 1: Basic chat with MongoDB history
    curl_basic = '''# Basic chat with MongoDB history
curl -X POST http://localhost:5000/api/llm/generate_response \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "What are the latest AI trends?",
    "chat_id": "user_123_session",
    "temperature": 0.7,
    "save_to_mongo": true,
    "use_history": true
  }'
'''

    # Example 2: Chat with document references
    curl_with_docs = '''# Chat with document references
curl -X POST http://localhost:5000/api/llm/generate_response \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "Summarize the key points from these documents",
    "chat_id": "research_session_456",
    "temperature": 0.3,
    "save_to_mongo": true,
    "use_history": true,
    "prompt_docs": [
      {"id": "doc1", "title": "AI Research Paper", "filename": "ai_research.pdf"},
      {"id": "doc2", "title": "ML Guidelines", "filename": "ml_guide.docx"}
    ]
  }'
'''

    # Example 3: One-off query without history
    curl_no_history = '''# One-off query without history
curl -X POST http://localhost:5000/api/llm/generate_response \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "What is 2+2?",
    "chat_id": "",
    "temperature": 0.1,
    "save_to_mongo": false,
    "use_history": false
  }'
'''

    # Example 4: Test MongoDB connection
    curl_test_mongo = '''# Test MongoDB connection
curl -X GET http://localhost:5000/api/llm/test_mongo_connection
'''

    # Example 5: Fetch chat history for debugging
    curl_fetch_history = '''# Fetch chat history for debugging
curl -X GET http://localhost:5000/api/llm/fetch_history/user_123_session
'''

    print(curl_basic)
    print(curl_with_docs)
    print(curl_no_history)
    print(curl_test_mongo)
    print(curl_fetch_history)

def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("Starting Comprehensive LLM API Tests with MongoDB Format...")
    print("=" * 70)
    
    # Test 1: Show MongoDB format
    test_mongodb_format_conversion()
    
    # Test 2: Create sample API responses
    create_sample_mongo_api_response()
    create_sample_mongo_save_request()
    
    # Test 3: Show curl examples
    create_curl_examples()
    
    # Test 4: Try actual API calls (will work when server is running)
    print("\n=== Live API Tests (requires server running) ===")
    try:
        # Test MongoDB connection
        test_url = f"{BASE_URL}/test_mongo_connection"
        response = requests.get(test_url, timeout=5)
        print(f"MongoDB Connection Test: {response.status_code}")
        
        # Test generate response
        test_generate_response_with_mongo_format()
        
        # Test fetch history
        test_fetch_history_debug()
        
    except requests.exceptions.ConnectionError:
        print("Server not running - skipping live tests")
        print("Start server with: python app.py")
    except Exception as e:
        print(f"Error in live tests: {e}")
    
    print("\n" + "=" * 70)
    print("All tests completed!")
    
    print("\n📋 MongoDB API Requirements:")
    print("1. GET /api/chat/history/{chat_id} - Return chat history in specified format")
    print("2. POST /api/chat/message - Save conversation turn in specified format")
    print("3. GET /api/health - Health check endpoint (optional)")
    
    print("\n🔧 Environment Setup:")
    print("1. Add to .env: MONGO_API_BASE_URL=http://localhost:3000/api")
    print("2. Add to .env: GOOGLE_API_KEY=your_gemini_api_key")
    print("3. Install dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    run_comprehensive_test()

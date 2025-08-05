#!/usr/bin/env python3
"""
Test script for the RAG-powered FastAPI Chat System
This script tests the main components of the system.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

async def test_chromadb():
    """Test ChromaDB functionality"""
    print("🧪 Testing ChromaDB...")
    
    try:
        from config.chromadb import (
            get_chroma_client, 
            create_chat_collection, 
            add_document_to_chat, 
            query_chat_documents
        )
        
        # Test basic ChromaDB connection
        client = await get_chroma_client()
        print("✅ ChromaDB client created successfully")
        
        # Test collection creation
        test_chat_id = "test_chat_123"
        test_user_id = "test_user_456"
        
        collection = await create_chat_collection(test_chat_id, test_user_id)
        print(f"✅ Created test collection: {collection.name}")
        
        # Test document addition
        test_chunks = [
            {
                "id": "doc1_chunk1",
                "text": "This is the first chunk of a test document about artificial intelligence.",
                "metadata": {"filename": "test.txt", "chunk_index": 0}
            },
            {
                "id": "doc1_chunk2", 
                "text": "This is the second chunk discussing machine learning and neural networks.",
                "metadata": {"filename": "test.txt", "chunk_index": 1}
            }
        ]
        
        await add_document_to_chat(test_chat_id, test_chunks)
        print(f"✅ Added {len(test_chunks)} chunks to collection")
        
        # Test query
        results = await query_chat_documents(test_chat_id, "artificial intelligence", top_k=2)
        print(f"✅ Query returned {len(results['documents'][0])} results")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        return False

async def test_document_processing():
    """Test document processing functionality"""
    print("\n🧪 Testing Document Processing...")
    
    try:
        from utils.document_manager import (
            extract_text_from_file,
            clean_text,
            chunk_text,
            generate_embeddings
        )
        
        # Test text extraction with sample content
        test_content = b"This is a test document.\nIt has multiple lines.\nAnd some text to process."
        
        text = await extract_text_from_file(test_content, "test.txt")
        print(f"✅ Text extraction successful: {len(text)} characters")
        
        # Test text cleaning
        cleaned = await clean_text(text)
        print(f"✅ Text cleaning successful: {len(cleaned)} characters")
        
        # Test chunking
        chunks = await chunk_text(cleaned, max_chunk_size=50, overlap_size=10)
        print(f"✅ Text chunking successful: {len(chunks)} chunks")
        
        # Test embedding generation
        embeddings = await generate_embeddings([chunk["text"] for chunk in chunks])
        print(f"✅ Embedding generation successful: {len(embeddings)} embeddings")
        
        return True
        
    except Exception as e:
        print(f"❌ Document processing test failed: {e}")
        return False

async def test_rag_workflow():
    """Test RAG workflow functionality"""
    print("\n🧪 Testing RAG Workflow...")
    
    try:
        from utils.rag_langgraph import RAGWorkflow
        
        # Initialize RAG workflow
        rag = RAGWorkflow(
            model_name="llama2:7b-chat",
            ollama_url="http://localhost:11434"
        )
        
        print("✅ RAG workflow initialized")
        
        # Test document processing (without LLM call)
        test_document = {
            "filename": "test_rag.txt",
            "content": b"This is a test document for RAG processing. It contains information about machine learning and artificial intelligence concepts."
        }
        
        # Note: This would require Ollama to be running for full test
        # For now, just test the workflow initialization
        print("✅ RAG workflow ready (Ollama connection not tested)")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG workflow test failed: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection"""
    print("\n🧪 Testing Ollama Connection...")
    
    try:
        import requests
        
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama is running with {len(models)} models")
            
            # Check for required models
            model_names = [model["name"] for model in models]
            required_models = ["llama2:7b-chat", "mistral:7b-instruct"]
            
            for model in required_models:
                if any(model in name for name in model_names):
                    print(f"✅ Found compatible model for {model}")
                else:
                    print(f"⚠️  Model {model} not found. Install with: ollama pull {model}")
            
            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False

async def test_fastapi_imports():
    """Test FastAPI and related imports"""
    print("\n🧪 Testing FastAPI Imports...")
    
    try:
        # Test main imports
        from fastapi import FastAPI
        from controllers.chat import ChatController
        from models.chat import ChatCreate
        from config.mongodb import get_database
        
        print("✅ FastAPI imports successful")
        
        # Test route imports
        from routes.chat_apis import router
        print("✅ Route imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI import test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 RAG System Component Tests")
    print("=" * 40)
    
    test_results = []
    
    # Test FastAPI imports first
    result = await test_fastapi_imports()
    test_results.append(("FastAPI Imports", result))
    
    # Test ChromaDB
    result = await test_chromadb()
    test_results.append(("ChromaDB", result))
    
    # Test document processing
    result = await test_document_processing()
    test_results.append(("Document Processing", result))
    
    # Test RAG workflow
    result = await test_rag_workflow()
    test_results.append(("RAG Workflow", result))
    
    # Test Ollama connection
    result = test_ollama_connection()
    test_results.append(("Ollama Connection", result))
    
    # Print summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

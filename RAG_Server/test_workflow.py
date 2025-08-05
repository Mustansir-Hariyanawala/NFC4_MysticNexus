#!/usr/bin/env python3
"""
Test script for RAG Server workflow
Demonstrates basic functionality and API usage
"""

import asyncio
import base64
import json
import os
from pathlib import Path

# Test the document utilities
async def test_document_utilities():
    """Test document processing utilities"""
    print("🧪 Testing Document Utilities...")
    
    from utils.doc_utils import MustanDocumentManager, DocumentHandler
    
    # Initialize document manager
    doc_manager = MustanDocumentManager()
    doc_handler = DocumentHandler(doc_manager)
    
    # Test text cleaning
    sample_text = "This is a test document!!! It contains multiple sentences... We will test text processing capabilities."
    print(f"Original text: {sample_text}")
    
    # Test original cleaning
    cleaned_original = await doc_manager.clean_text(sample_text)
    print(f"Original cleaning: {cleaned_original}")
    
    # Test improved cleaning (if available)
    if hasattr(doc_manager, '_sonnet_clean_text_advanced'):
        cleaned_sonnet = await doc_manager._sonnet_clean_text_advanced(sample_text)
        print(f"Sonnet cleaning: {cleaned_sonnet}")
    
    # Test chunking
    chunks = await doc_manager.chunk_text(sample_text, max_chunk_size=50, overlap_size=10)
    print(f"Generated {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}: {chunk['text'][:30]}...")
    
    # Test embedding generation
    chunk_texts = [chunk["text"] for chunk in chunks]
    embeddings = await doc_manager.generate_embeddings(chunk_texts)
    print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")
    
    return True

def test_chromadb_manager():
    """Test ChromaDB manager functionality"""
    print("\n🗄️ Testing ChromaDB Manager...")
    
    from config.chromaDB import chroma_manager
    
    test_chat_id = "test_chat_123"
    
    # Test collection creation
    print("Creating test collection...")
    result = chroma_manager.create_collection(test_chat_id)
    print(f"Creation result: {result}")
    
    # Test collection listing
    print("Listing collections...")
    collections = chroma_manager.list_collections()
    print(f"Collections: {collections}")
    
    # Test collection deletion
    print("Deleting test collection...")
    delete_result = chroma_manager.delete_collection(test_chat_id)
    print(f"Deletion result: {delete_result}")
    
    return True

async def test_langgraph_workflow():
    """Test LangGraph workflow with sample data"""
    print("\n🔄 Testing LangGraph Workflow...")
    
    try:
        from utils.langgraph_workflow import create_rag_workflow
        
        # Create workflow
        workflow = create_rag_workflow()
        
        # Sample query and documents
        query_text = "What is the main topic of this document?"
        
        # Create a sample document (text file)
        sample_document_content = """
        This is a sample research document about artificial intelligence and machine learning.
        
        Introduction:
        Artificial Intelligence (AI) has become one of the most transformative technologies of our time.
        Machine learning, a subset of AI, enables computers to learn and improve from experience without being explicitly programmed.
        
        Key Concepts:
        1. Neural Networks: Computational models inspired by biological neural networks
        2. Deep Learning: A subset of machine learning using neural networks with multiple layers
        3. Natural Language Processing: AI's ability to understand and generate human language
        
        Applications:
        - Computer Vision
        - Speech Recognition
        - Recommendation Systems
        - Autonomous Vehicles
        
        Conclusion:
        The future of AI holds immense potential for solving complex problems across various industries.
        """
        
        # Convert to bytes (simulate file content)
        doc_content = sample_document_content.encode('utf-8')
        
        documents = [{
            "filename": "ai_research.txt",
            "content": doc_content
        }]
        
        # Run workflow
        print("Running RAG workflow...")
        result = await workflow.run_workflow(query_text, documents, "test_workflow_123")
        
        print("Workflow completed!")
        print(f"Chat ID: {result['chat_id']}")
        print(f"Query: {result['query']}")
        print(f"Response: {result['response'][:200]}...")
        print(f"Errors: {result['errors']}")
        print(f"Doc Processing Completed: {result['doc_processing_completed']}")
        print(f"Retrieved Docs Count: {result['retrieved_docs_count']}")
        print(f"Total Chunks Processed: {result['total_chunks_processed']}")
        
        return True
        
    except Exception as e:
        print(f"Error in workflow test: {e}")
        return False

def create_sample_api_requests():
    """Create sample API request examples"""
    print("\n📝 Creating Sample API Requests...")
    
    # Create sample document content
    sample_text = """
    Sample Research Paper: The Future of Technology
    
    Abstract:
    This paper explores emerging technologies and their potential impact on society.
    We examine artificial intelligence, quantum computing, and biotechnology.
    
    1. Introduction
    Technology continues to evolve at an unprecedented pace. This study analyzes
    three key areas that will shape our future.
    
    2. Artificial Intelligence
    AI has demonstrated remarkable capabilities in natural language processing,
    computer vision, and decision-making systems.
    
    3. Quantum Computing
    Quantum computers promise to solve complex problems that are intractable
    for classical computers.
    
    4. Biotechnology
    Advances in gene editing and synthetic biology open new possibilities
    for medicine and agriculture.
    
    5. Conclusion
    These technologies will transform how we work, live, and interact.
    """
    
    # Encode to base64
    sample_content_b64 = base64.b64encode(sample_text.encode('utf-8')).decode('utf-8')
    
    # Create sample requests
    sample_requests = {
        "complete_rag_process": {
            "url": "POST /api/rag/process_rag",
            "payload": {
                "queryText": "What are the three key technology areas discussed?",
                "documents": [
                    {
                        "filename": "future_tech.txt",
                        "content": sample_content_b64
                    }
                ],
                "chatID": "tech_discussion_1"
            }
        },
        "query_only": {
            "url": "POST /api/rag/query_only",
            "payload": {
                "queryText": "Tell me more about quantum computing",
                "chatID": "tech_discussion_1"
            }
        },
        "check_status": {
            "url": "GET /api/rag/rag_status/tech_discussion_1",
            "payload": None
        },
        "get_logs": {
            "url": "GET /api/rag/get_logs/tech_discussion_1",
            "payload": None
        },
        "create_collection": {
            "url": "POST /api/create_collection",
            "payload": {
                "chatID": "tech_discussion_1"
            }
        },
        "list_collections": {
            "url": "GET /api/list_collections",
            "payload": None
        }
    }
    
    # Save to file
    with open("sample_api_requests.json", "w", encoding='utf-8') as f:
        json.dump(sample_requests, f, indent=2, ensure_ascii=False)
    
    print("Sample API requests saved to 'sample_api_requests.json'")
    
    # Also create curl commands
    curl_commands = f"""
# Sample cURL commands for testing RAG Server

# 1. Health Check
curl -X GET http://localhost:5000/health

# 2. Create Collection
curl -X POST http://localhost:5000/api/create_collection \\
  -H "Content-Type: application/json" \\
  -d '{{"chatID": "tech_discussion_1"}}'

# 3. Process RAG (with sample document)
curl -X POST http://localhost:5000/api/rag/process_rag \\
  -H "Content-Type: application/json" \\
  -d @sample_rag_request.json

# 4. Query Only
curl -X POST http://localhost:5000/api/rag/query_only \\
  -H "Content-Type: application/json" \\
  -d '{{"queryText": "Tell me about quantum computing", "chatID": "tech_discussion_1"}}'

# 5. Check RAG Status
curl -X GET http://localhost:5000/api/rag/rag_status/tech_discussion_1

# 6. Get Processing Logs
curl -X GET http://localhost:5000/api/rag/get_logs/tech_discussion_1

# 7. List Collections
curl -X GET http://localhost:5000/api/list_collections

# 8. Delete Collection
curl -X DELETE http://localhost:5000/api/delete_collection \\
  -H "Content-Type: application/json" \\
  -d '{{"chatID": "tech_discussion_1"}}'
"""
    
    with open("sample_curl_commands.sh", "w", encoding='utf-8') as f:
        f.write(curl_commands)
    
    # Create sample RAG request file
    with open("sample_rag_request.json", "w", encoding='utf-8') as f:
        json.dump(sample_requests["complete_rag_process"]["payload"], f, indent=2)
    
    print("Sample cURL commands saved to 'sample_curl_commands.sh'")
    print("Sample RAG request saved to 'sample_rag_request.json'")

async def main():
    """Run all tests"""
    print("🚀 Starting RAG Server Tests...\n")
    
    try:
        # Test document utilities
        doc_test = await test_document_utilities()
        print(f"✅ Document utilities test: {'PASSED' if doc_test else 'FAILED'}")
        
        # Test ChromaDB manager
        chromadb_test = test_chromadb_manager()
        print(f"✅ ChromaDB manager test: {'PASSED' if chromadb_test else 'FAILED'}")
        
        # Test LangGraph workflow (might fail without proper dependencies)
        workflow_test = await test_langgraph_workflow()
        print(f"✅ LangGraph workflow test: {'PASSED' if workflow_test else 'FAILED'}")
        
        # Create sample API requests
        create_sample_api_requests()
        print("✅ Sample API requests created")
        
        print("\n🎉 All tests completed!")
        print("\nNext steps:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Install spaCy model: python -m spacy download en_core_web_sm")
        print("3. Start the server: python app.py")
        print("4. Test the APIs using the sample requests in 'sample_api_requests.json'")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

from flask import Blueprint, request, jsonify
import asyncio
import base64
from typing import Dict, List, Any
from utils.langgraph_workflow import create_rag_workflow
from utils.logger_utils import setup_langgraph_logger
import logging

# Create blueprint for RAG operations
rag_router = Blueprint('rag_router', __name__)

# Global workflow instance
rag_workflow = None

def get_workflow():
    """Get or create workflow instance"""
    global rag_workflow
    if rag_workflow is None:
        rag_workflow = create_rag_workflow()
    return rag_workflow

@rag_router.route('/process_rag', methods=['POST'])
def process_rag():
    """
    Process RAG workflow with query and documents
    
    Expected JSON payload:
    {
        "queryText": "What is the main topic?",
        "documents": [
            {
                "filename": "document.pdf",
                "content": "base64_encoded_content"
            }
        ],
        "chatID": "optional_chat_id"
    }
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        # Extract required fields
        query_text = data.get('queryText')
        documents_data = data.get('documents', [])
        chat_id = data.get('chatID')
        
        # Validate query
        if not query_text:
            return jsonify({
                "status": "error",
                "message": "queryText is required"
            }), 400
        
        # Process documents
        processed_documents = []
        for doc_data in documents_data:
            try:
                filename = doc_data.get('filename', 'unknown')
                content_b64 = doc_data.get('content', '')
                
                if content_b64:
                    # Decode base64 content
                    content_bytes = base64.b64decode(content_b64)
                    processed_documents.append({
                        "filename": filename,
                        "content": content_bytes
                    })
            except Exception as e:
                logging.error(f"Error processing document {doc_data.get('filename', 'unknown')}: {e}")
                continue
        
        # Run workflow asynchronously
        workflow = get_workflow()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                workflow.run_workflow(query_text, processed_documents, chat_id)
            )
        finally:
            loop.close()
        
        return jsonify({
            "status": "success",
            "data": result
        }), 200
        
    except Exception as e:
        logging.error(f"Error in RAG processing: {e}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@rag_router.route('/rag_status/<chat_id>', methods=['GET'])
def get_rag_status(chat_id: str):
    """
    Get the status of RAG processing for a chat ID
    """
    try:
        from config.chromaDB import chroma_manager
        
        # Check if collection exists and get count
        collections_info = chroma_manager.list_collections()
        
        if collections_info["status"] == "success":
            collection_exists = chat_id in collections_info["collections"]
            
            if collection_exists:
                collection = chroma_manager.get_collection(chat_id)
                if collection:
                    count = collection.count()
                    return jsonify({
                        "status": "success",
                        "chat_id": chat_id,
                        "collection_exists": True,
                        "document_chunks": count,
                        "processing_completed": True
                    }), 200
            
            return jsonify({
                "status": "success",
                "chat_id": chat_id,
                "collection_exists": False,
                "document_chunks": 0,
                "processing_completed": False
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to check collections"
            }), 500
            
    except Exception as e:
        logging.error(f"Error checking RAG status: {e}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@rag_router.route('/query_only', methods=['POST'])
def query_only():
    """
    Process query against existing documents in ChromaDB
    
    Expected JSON payload:
    {
        "queryText": "What is the main topic?",
        "chatID": "existing_chat_id"
    }
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        query_text = data.get('queryText')
        chat_id = data.get('chatID')
        
        if not query_text:
            return jsonify({
                "status": "error",
                "message": "queryText is required"
            }), 400
        
        if not chat_id:
            return jsonify({
                "status": "error",
                "message": "chatID is required for query-only mode"
            }), 400
        
        # Run workflow with empty documents (query-only mode)
        workflow = get_workflow()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                workflow.run_workflow(query_text, [], chat_id)
            )
        finally:
            loop.close()
        
        return jsonify({
            "status": "success",
            "data": result
        }), 200
        
    except Exception as e:
        logging.error(f"Error in query-only processing: {e}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@rag_router.route('/get_logs/<chat_id>', methods=['GET'])
def get_logs(chat_id: str):
    """
    Get processing logs for a specific chat ID
    """
    try:
        import os
        from pathlib import Path
        
        logs_dir = Path("./logs")
        log_files = list(logs_dir.glob(f"langgraph_{chat_id}_*.txt"))
        
        if not log_files:
            return jsonify({
                "status": "error",
                "message": f"No logs found for chat_id: {chat_id}"
            }), 404
        
        # Get the most recent log file
        latest_log = max(log_files, key=os.path.getctime)
        
        with open(latest_log, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        return jsonify({
            "status": "success",
            "chat_id": chat_id,
            "log_file": latest_log.name,
            "log_content": log_content
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving logs: {e}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

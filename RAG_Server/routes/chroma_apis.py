from flask import Blueprint, request, jsonify
from config.chromaDB import chroma_manager

"""
ChromaDB API Routes

This module provides RESTful endpoints for managing ChromaDB collections.
Endpoints:
    - GET    /api/collections           : List all collections
    - GET    /api/collections/<chat_id> : Get details of a specific collection
    - POST   /api/collections           : Create a new collection
    - DELETE /api/collections           : Delete a collection

Expected JSON payload for POST/DELETE:
    {
        "chat_id": "unique_chat_identifier"
    }
"""

router = Blueprint('chroma_apis', __name__)

# ---------------------------
# Utility Functions
# ---------------------------

def error_response(message, status_code=400):
    """Helper to format error responses."""
    return jsonify({
        "status": "error",
        "message": message
    }), status_code

# ---------------------------
# API Endpoints
# ---------------------------

@router.route('/api/collections', methods=['GET'])
def list_collections():
    """
    List all existing ChromaDB collections.

    Returns:
        JSON response with collection list and status.
    """
    try:
        result = chroma_manager.list_collections()
        status_code = 200 if result.get("status") == "success" else 500
        return jsonify(result), status_code
    except Exception as e:
        return error_response(f"Internal server error: {str(e)}", 500)

@router.route('/api/collections/<chat_id>', methods=['GET'])
def get_collection(chat_id):
    """
    Get details of a specific ChromaDB collection by chat ID.

    Args:
        chat_id (str): Unique identifier for the collection.

    Returns:
        JSON response with collection details or error.
    """
    if not chat_id:
        return error_response("chat_id is required", 400)
    try:
        collection = chroma_manager.get_collection(chat_id)
        if collection:
            return jsonify({
                "status": "success",
                "collection": collection.name,
            }), 200
        else:
            return error_response(f"Collection '{chat_id}' not found", 404)
    except Exception as e:
        return error_response(f"Internal server error: {str(e)}", 500)

@router.route('/api/collections', methods=['POST'])
def create_collection():
    """
    Create a new ChromaDB collection for a chat ID.

    Request JSON:
        {
            "chat_id": "unique_chat_identifier"
        }

    Returns:
        JSON response with creation status.
    """
    data = request.get_json()
    if not data:
        return error_response("No JSON data provided", 400)
    chat_id = data.get('chat_id')
    if not chat_id:
        return error_response("chat_id is required", 400)
    if not isinstance(chat_id, str):
        return error_response("chat_id must be a string", 400)

    try:
        # Check if collection already exists
        existing_collection = chroma_manager.get_collection(chat_id)
        if existing_collection is not None:
            return jsonify({
                "status": "warning",
                "message": "Collection already exists"
            }), 200

        # Create collection
        res = chroma_manager.create_collection(chat_id)
        if res.get("status") == "success":
            return jsonify(res), 201
        elif res.get("status") == "warning":
            return jsonify(res), 200
        else:
            return jsonify(res), 500
    except Exception as e:
        return error_response(f"Internal server error: {str(e)}", 500)

@router.route('/api/collections', methods=['DELETE'])
def delete_collection():
    """
    Delete a ChromaDB collection for a chat ID.

    Request JSON:
        {
            "chat_id": "unique_chat_identifier"
        }

    Returns:
        JSON response with deletion status.
    """
    data = request.get_json()
    if not data:
        return error_response("No JSON data provided", 400)
    chat_id = data.get('chat_id')
    if not chat_id:
        return error_response("chat_id is required", 400)
    if not isinstance(chat_id, str):
        return error_response("chat_id must be a string", 400)

    try:
        result = chroma_manager.delete_collection(chat_id)
        if result.get("status") == "success":
            return jsonify(result), 200
        elif result.get("status") == "warning":
            return jsonify(result), 404
        else:
            return jsonify(result), 500
    except Exception as e:
        return error_response(f"Internal server error: {str(e)}", 500)
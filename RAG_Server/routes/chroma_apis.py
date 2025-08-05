from flask import Blueprint, request, jsonify
import json
from config.chromaDB import chroma_manager

router = Blueprint('chroma_apis', __name__)


@router.route('/api/collections', methods=['GET'])
def list_collections():
    """
    List all existing ChromaDB collections
    """
    try:
        result = chroma_manager.list_collections()
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@router.route('/api/collections/<chat_id>', methods=['GET'])
def get_collection(chat_id):
    """
    Get details of a specific ChromaDB collection by chat ID
    """
    try:
        if not chat_id:
            return jsonify({
                "status": "error",
                "message": "chat_id is required"
            }), 400

        # Retrieve collection details using ChromaDB manager
        collection = chroma_manager.get_collection(chat_id)

        print("Collection : ", collection)

        if collection:
            return jsonify({
                "status": "success",
                "collection": collection.name,
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Collection '{chat_id}' not found"
            }), 404
        

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@router.route('/api/collections', methods=['POST'])
def create_collection():
    """
    Create a new ChromaDB collection for a chat ID
    
    Expected JSON payload:
    {
        "chat_id": "unique_chat_identifier"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()

        print("Data Recieved : ", data)
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        chat_id = data['chat_id']
        
        print(1)

        if not chat_id:
            return jsonify({
                "status": "error",
                "message": "chat_id is required"
            }), 400
        
        print(2)

        if not isinstance(chat_id, str):
            return jsonify({
                "status": "error",
                "message": "chat_id must be a string"
            }), 400
        
        print(3)
        
        # Check if collection already exists
        existing_collection = chroma_manager.get_collection(chat_id)

        
        print(4)

        if existing_collection != None:
            return jsonify({
                "status": "warning",
                "message": "Collection already exists"
            }), 200
        
        print(5)
        
        # Create collection using ChromaDB manager
        res = chroma_manager.create_collection(chat_id)

        

        print(6)
        
        # Return appropriate status code based on result
        if res["status"] == "success":
            return jsonify(res), 201
        elif res["status"] == "warning":
            return jsonify(res), 200
        else:
            return jsonify(res), 500
        

            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@router.route('/api/collections', methods=['DELETE'])
def delete_collection():
    """
    Delete a ChromaDB collection for a chat ID
    
    Expected JSON payload:
    {
        "chat_id": "unique_chat_identifier"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        chat_id = data.get('chat_id')
        
        if not chat_id:
            return jsonify({
                "status": "error",
                "message": "chat_id is required"
            }), 400
        
        if not isinstance(chat_id, str):
            return jsonify({
                "status": "error",
                "message": "chat_id must be a string"
            }), 400
        
        # Delete collection using ChromaDB manager
        result = chroma_manager.delete_collection(chat_id)
        
        # Return appropriate status code based on result
        if result["status"] == "success":
            return jsonify(result), 200
        elif result["status"] == "warning":
            return jsonify(result), 404
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

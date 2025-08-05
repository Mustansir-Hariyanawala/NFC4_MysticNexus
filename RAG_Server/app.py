from flask import Flask, jsonify
from flask_cors import CORS
from routes.main_router import main_router
from routes.rag_router import rag_router
from config.chromaDB import chroma_manager
import logging
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

# Register blueprints
app.register_blueprint(main_router, url_prefix='/api')
app.register_blueprint(rag_router, url_prefix='/api/rag')

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the RAG Server with ChromaDB!",
        "endpoints": {
            "chromadb": "/api/",
            "rag": "/api/rag/",
            "health": "/health"
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check if ChromaDB is accessible
        collections_info = chroma_manager.list_collections()
        return jsonify({
            "status": "healthy",
            "chromadb": "connected",
            "collections_count": collections_info.get("count", 0),
            "services": {
                "chromadb": "operational",
                "rag_workflow": "ready"
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    try:
        # Initialize ChromaDB on server start
        logger.info("Starting RAG Server...")
        logger.info("ChromaDB initialized successfully")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise
import os
import chromadb
import logging
from chromadb.config import Settings
from typing import Optional, Dict, List, Any
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDBManager:
    client: Optional[chromadb.Client] = None
    collections: Dict[str, chromadb.Collection] = {}

# ChromaDB configuration
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chromadb_collections")

async def connect_to_chroma():
    """Initialize ChromaDB connection - Collections will be created per chat"""
    try:
        # Ensure the data directory exists
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        ChromaDBManager.client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        logger.info(f"Connected successfully to ChromaDB")
        logger.info(f"ChromaDB storage path: {CHROMA_DB_PATH}")
        
    except Exception as e:
        logger.error(f"Failed to connect to ChromaDB: {e}")
        raise

async def close_chroma_connection():
    """Close ChromaDB connection"""
    try:
        if ChromaDBManager.client:
            ChromaDBManager.collections.clear()
            ChromaDBManager.client = None
            logger.info("Closed ChromaDB connection")
    except Exception as e:
        logger.error(f"Error closing ChromaDB connection: {e}")

def get_chroma_client():
    """Get ChromaDB client instance"""
    return ChromaDBManager.client

async def create_chat_collection(chat_id: str, user_id: str) -> chromadb.Collection:
    """
    Create a new collection for a specific chat
    
    Args:
        chat_id (str): Unique chat identifier
        user_id (str): User identifier
    
    Returns:
        ChromaDB Collection instance
    """
    try:
        if not ChromaDBManager.client:
            raise ValueError("ChromaDB client is not initialized")
        
        collection_name = f"chat_{chat_id}"
        
        # Check if collection already exists in cache
        if collection_name in ChromaDBManager.collections:
            return ChromaDBManager.collections[collection_name]
        
        # Create or get collection
        collection = ChromaDBManager.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "description": f"Document embeddings for chat {chat_id}",
                "chat_id": chat_id,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        # Cache the collection
        ChromaDBManager.collections[collection_name] = collection
        
        logger.info(f"Created/Retrieved collection for chat {chat_id}")
        return collection
        
    except Exception as e:
        logger.error(f"Error creating chat collection: {e}")
        raise

async def get_chat_collection(chat_id: str) -> Optional[chromadb.Collection]:
    """
    Get an existing collection for a specific chat
    
    Args:
        chat_id (str): Unique chat identifier
    
    Returns:
        ChromaDB Collection instance or None if not found
    """
    try:
        if not ChromaDBManager.client:
            raise ValueError("ChromaDB client is not initialized")
        
        collection_name = f"chat_{chat_id}"
        
        # Check cache first
        if collection_name in ChromaDBManager.collections:
            return ChromaDBManager.collections[collection_name]
        
        # Try to get from ChromaDB
        try:
            collection = ChromaDBManager.client.get_collection(name=collection_name)
            ChromaDBManager.collections[collection_name] = collection
            return collection
        except Exception:
            # Collection doesn't exist
            return None
        
    except Exception as e:
        logger.error(f"Error getting chat collection: {e}")
        raise

async def delete_chat_collection(chat_id: str) -> bool:
    """
    Delete a collection for a specific chat
    
    Args:
        chat_id (str): Unique chat identifier
    
    Returns:
        bool: True if successfully deleted, False otherwise
    """
    try:
        if not ChromaDBManager.client:
            raise ValueError("ChromaDB client is not initialized")
        
        collection_name = f"chat_{chat_id}"
        
        # Remove from cache
        if collection_name in ChromaDBManager.collections:
            del ChromaDBManager.collections[collection_name]
        
        # Delete from ChromaDB
        ChromaDBManager.client.delete_collection(name=collection_name)
        
        logger.info(f"Deleted collection for chat {chat_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting chat collection: {e}")
        return False

async def add_document_to_chat(
    chat_id: str,
    doc_text: str,
    cleaned_text: str,
    embeddings: List[float],
    metadata: Dict[str, Any]
) -> str:
    """Add a document chunk to a chat's collection"""
    try:
        collection = await get_chat_collection(chat_id)
        if not collection:
            raise ValueError(f"No collection found for chat {chat_id}")
        
        # Generate unique ID for this chunk
        chunk_id = f"chunk_{datetime.utcnow().timestamp()}_{len(cleaned_text)}"
        
        # Add to collection
        collection.add(
            documents=[cleaned_text],
            embeddings=[embeddings],
            metadatas=[{
                **metadata,
                "original_text": doc_text[:1000],  # Store first 1000 chars of original
                "chunk_id": chunk_id,
                "added_at": datetime.utcnow().isoformat()
            }],
            ids=[chunk_id]
        )
        
        logger.info(f"Added document chunk {chunk_id} to chat {chat_id}")
        return chunk_id
        
    except Exception as e:
        logger.error(f"Error adding document to chat: {e}")
        raise

async def query_chat_documents(
    chat_id: str,
    query_embeddings: List[float],
    n_results: int = 5
) -> Optional[Dict]:
    """Query documents in a chat's collection"""
    try:
        collection = await get_chat_collection(chat_id)
        if not collection:
            return None
        
        # Query the collection
        results = collection.query(
            query_embeddings=[query_embeddings],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        logger.info(f"Queried {n_results} documents from chat {chat_id}")
        return results
        
    except Exception as e:
        logger.error(f"Error querying chat documents: {e}")
        raise

async def get_document_by_id(chat_id: str, chunk_id: str) -> Optional[Dict]:
    """
    Get a specific document chunk by ID from a chat's collection
    
    Args:
        chat_id (str): Chat identifier
        chunk_id (str): Document chunk identifier
    
    Returns:
        Dict: Document data or None if not found
    """
    try:
        collection = await get_chat_collection(chat_id)
        if not collection:
            return None
        
        result = collection.get(ids=[chunk_id])
        
        if result and result.get('documents'):
            return {
                'id': chunk_id,
                'document': result['documents'][0],
                'metadata': result['metadatas'][0] if result.get('metadatas') else {},
                'embedding': result['embeddings'][0] if result.get('embeddings') else None
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting document by ID: {e}")
        return None

async def delete_document_from_chat(chat_id: str, chunk_ids: List[str]) -> bool:
    """
    Delete specific document chunks from a chat's collection
    
    Args:
        chat_id (str): Chat identifier
        chunk_ids (List[str]): List of document chunk IDs to delete
    
    Returns:
        bool: True if successfully deleted
    """
    try:
        collection = await get_chat_collection(chat_id)
        if not collection:
            return False
        
        collection.delete(ids=chunk_ids)
        logger.info(f"Deleted {len(chunk_ids)} documents from chat {chat_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting documents from chat: {e}")
        return False

async def get_chat_document_count(chat_id: str) -> int:
    """
    Get the number of documents in a chat's collection
    
    Args:
        chat_id (str): Chat identifier
    
    Returns:
        int: Number of documents in the collection
    """
    try:
        collection = await get_chat_collection(chat_id)
        if not collection:
            return 0
        
        count = collection.count()
        return count
        
    except Exception as e:
        logger.error(f"Error getting chat document count: {e}")
        return 0

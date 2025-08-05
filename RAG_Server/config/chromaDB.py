import os
import chromadb
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDBManager:
    def __init__(self, persist_directory: str = "./ChromaDB"):
        """
        Initialize ChromaDB Manager
        
        Args:
            persist_directory (str): Directory where ChromaDB collections will be stored
        """
        self.persist_directory = persist_directory
        self.client = None
        self._ensure_directory_exists()
        self._initialize_client()
    
    def _ensure_directory_exists(self) -> None:
        """Create ChromaDB directory if it doesn't exist"""
        try:
            if not os.path.exists(self.persist_directory):
                os.makedirs(self.persist_directory)
                logger.info(f"Created ChromaDB directory: {self.persist_directory}")
            else:
                logger.info(f"ChromaDB directory already exists: {self.persist_directory}")
        except Exception as e:
            logger.error(f"Error creating ChromaDB directory: {str(e)}")
            raise
    
    def _initialize_client(self) -> None:
        """Initialize ChromaDB client with persistent storage"""
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            logger.info("ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {str(e)}")
            raise
    
    def create_collection(self, chat_id: str) -> Dict[str, str]:
        """
        Create a new collection for a specific chat ID
        
        Args:
            chat_id (str): Unique identifier for the chat
            
        Returns:
            Dict[str, str]: Success/error message with status
        """
        try:
            if not chat_id or not isinstance(chat_id, str):
                return {"status": "error", "message": "Invalid chat_id. Must be a non-empty string."}
            
            # Check if collection already exists
            existing_collections = self.client.list_collections()
            collection_names = [col.name for col in existing_collections]
            
            if chat_id in collection_names:
                return {"status": "warning", "message": f"Collection '{chat_id}' already exists."}
            
            # Create new collection
            collection = self.client.create_collection(name=chat_id)
            logger.info(f"Created collection: {chat_id}")
            
            return {
                "status": "success", 
                "message": f"Collection '{chat_id}' created successfully.",
                "collection_name": chat_id
            }
            
        except Exception as e:
            logger.error(f"Error creating collection '{chat_id}': {str(e)}")
            return {"status": "error", "message": f"Failed to create collection: {str(e)}"}
    
    def delete_collection(self, chat_id: str) -> Dict[str, str]:
        """
        Delete a collection for a specific chat ID
        
        Args:
            chat_id (str): Unique identifier for the chat
            
        Returns:
            Dict[str, str]: Success/error message with status
        """
        try:
            if not chat_id or not isinstance(chat_id, str):
                return {"status": "error", "message": "Invalid chat_id. Must be a non-empty string."}
            
            # Check if collection exists
            existing_collections = self.client.list_collections()
            collection_names = [col.name for col in existing_collections]
            
            if chat_id not in collection_names:
                return {"status": "warning", "message": f"Collection '{chat_id}' does not exist."}
            
            # Delete collection
            self.client.delete_collection(name=chat_id)
            logger.info(f"Deleted collection: {chat_id}")
            
            return {
                "status": "success", 
                "message": f"Collection '{chat_id}' deleted successfully.",
                "collection_name": chat_id
            }
            
        except Exception as e:
            logger.error(f"Error deleting collection '{chat_id}': {str(e)}")
            return {"status": "error", "message": f"Failed to delete collection: {str(e)}"}
    
    def get_collection(self, chat_id: str) -> Optional[object]:
        """
        Get a collection by chat ID
        
        Args:
            chat_id (str): Unique identifier for the chat
            
        Returns:
            Optional[object]: ChromaDB collection object or None if not found
        """
        try:
            return self.client.get_collection(name=chat_id)
        except Exception as e:
            logger.error(f"Error getting collection '{chat_id}': {str(e)}")
            return None
    
    def list_collections(self) -> Dict[str, any]:
        """
        List all existing collections
        
        Returns:
            Dict[str, any]: List of collection names and status
        """
        try:
            collections = self.client.list_collections()
            collection_names = [col.name for col in collections]
            
            return {
                "status": "success",
                "collections": collection_names,
                "count": len(collection_names)
            }
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            return {"status": "error", "message": f"Failed to list collections: {str(e)}"}

# Global instance
chroma_manager = ChromaDBManager()
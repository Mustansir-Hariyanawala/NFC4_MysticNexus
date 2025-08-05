import os
import tempfile
from typing import List, Dict, Optional
from fastapi import UploadFile, HTTPException
from utils.document_manager import get_document_processor
from config.chromadb import add_document_to_chat, query_chat_documents, get_chat_document_count
import logging

logger = logging.getLogger(__name__)

class DocumentController:
    def __init__(self):
        self.processor = get_document_processor()
        
    async def upload_and_process_document(
        self, 
        chat_id: str, 
        file: UploadFile,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> Dict:
        """
        Upload, process, and store a document for a specific chat
        
        Args:
            chat_id (str): Chat identifier
            file (UploadFile): Uploaded file
            chunk_size (int): Maximum characters per chunk
            overlap (int): Characters to overlap between chunks
        
        Returns:
            Dict: Processing results with chunk IDs and metadata
        """
        try:
            # Validate file type
            if not file.content_type:
                raise ValueError("File content type not specified")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            try:
                # Process the document
                logger.info(f"Processing document {file.filename} for chat {chat_id}")
                
                text_chunks, cleaned_chunks, embeddings, metadata_list = self.processor.process_document(
                    file_path=tmp_file_path,
                    file_type=file.content_type,
                    filename=file.filename,
                    chunk_size=chunk_size,
                    overlap=overlap
                )
                
                # Store each chunk in ChromaDB
                chunk_ids = []
                for i, (doc_text, cleaned_text, embedding, metadata) in enumerate(
                    zip(text_chunks, cleaned_chunks, embeddings, metadata_list)
                ):
                    # Add file processing metadata
                    enhanced_metadata = {
                        **metadata,
                        "original_filename": file.filename,
                        "file_size": len(content),
                        "content_type": file.content_type
                    }
                    
                    chunk_id = await add_document_to_chat(
                        chat_id=chat_id,
                        doc_text=doc_text,
                        cleaned_text=cleaned_text,
                        embeddings=embedding,
                        metadata=enhanced_metadata,
                        chunk_id=metadata["chunk_id"]
                    )
                    
                    chunk_ids.append(chunk_id)
                
                logger.info(f"Successfully processed and stored {len(chunk_ids)} chunks for chat {chat_id}")
                
                return {
                    "success": True,
                    "filename": file.filename,
                    "chunks_created": len(chunk_ids),
                    "chunk_ids": chunk_ids,
                    "total_size": len(content),
                    "content_type": file.content_type,
                    "embedding_dimension": len(embeddings[0]) if embeddings else 0
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    
    async def search_documents(
        self, 
        chat_id: str, 
        query: str, 
        top_k: int = 5
    ) -> Dict:
        """
        Search for relevant documents in a chat using semantic similarity
        
        Args:
            chat_id (str): Chat identifier
            query (str): Search query
            top_k (int): Number of top results to return
        
        Returns:
            Dict: Search results with similar documents
        """
        try:
            # Clean and embed the query
            cleaned_query = self.processor.clean_text(query)
            query_embeddings = self.processor.generate_embeddings([cleaned_query])[0]
            
            # Search in ChromaDB
            results = await query_chat_documents(
                chat_id=chat_id,
                query_embeddings=query_embeddings,
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results.get('documents') and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    formatted_results.append({
                        "chunk_id": results['ids'][0][i],
                        "content": doc,
                        "original_text": metadata.get('doc_text', ''),
                        "filename": metadata.get('filename', ''),
                        "chunk_index": metadata.get('chunk_index', 0),
                        "similarity_score": 1 - distance,  # Convert distance to similarity
                        "metadata": metadata
                    })
            
            return {
                "query": query,
                "results_count": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")
    
    async def get_chat_documents_info(self, chat_id: str) -> Dict:
        """
        Get information about documents stored in a chat
        
        Args:
            chat_id (str): Chat identifier
        
        Returns:
            Dict: Information about chat documents
        """
        try:
            document_count = await get_chat_document_count(chat_id)
            
            return {
                "chat_id": chat_id,
                "total_chunks": document_count,
                "has_documents": document_count > 0
            }
            
        except Exception as e:
            logger.error(f"Error getting chat documents info: {e}")
            raise HTTPException(status_code=500, detail=f"Error getting chat documents info: {str(e)}")

# Global document controller instance
document_controller = DocumentController()

def get_document_controller() -> DocumentController:
    """Get the global document controller instance"""
    return document_controller

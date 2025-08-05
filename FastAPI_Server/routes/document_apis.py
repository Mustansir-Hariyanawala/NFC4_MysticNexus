from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from controllers.document import get_document_controller, DocumentController
from controllers.auth import get_current_user
from models.user import UserResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/upload/{chat_id}")
async def upload_document(
    chat_id: str,
    file: UploadFile = File(...),
    chunk_size: int = Form(1000, description="Maximum characters per chunk"),
    overlap: int = Form(200, description="Characters to overlap between chunks"),
    current_user: UserResponse = Depends(get_current_user),
    document_controller: DocumentController = Depends(get_document_controller)
):
    """
    Upload and process a document for a specific chat
    
    - **chat_id**: ID of the chat to associate the document with
    - **file**: Document file to upload (PDF, DOCX, TXT)
    - **chunk_size**: Maximum characters per text chunk (default: 1000)
    - **overlap**: Characters to overlap between chunks (default: 200)
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size (limit to 50MB)
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")
        
        # Reset file pointer
        await file.seek(0)
        
        # Process the document
        result = await document_controller.upload_and_process_document(
            chat_id=chat_id,
            file=file,
            chunk_size=chunk_size,
            overlap=overlap
        )
        
        return {
            "message": "Document uploaded and processed successfully",
            **result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_document endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search/{chat_id}")
async def search_documents(
    chat_id: str,
    query: str = Query(..., description="Search query text"),
    top_k: int = Query(5, description="Number of top results to return", ge=1, le=20),
    current_user: UserResponse = Depends(get_current_user),
    document_controller: DocumentController = Depends(get_document_controller)
):
    """
    Search for relevant documents in a chat using semantic similarity
    
    - **chat_id**: ID of the chat to search documents in
    - **query**: Search query text
    - **top_k**: Number of top similar results to return (1-20)
    """
    try:
        result = await document_controller.search_documents(
            chat_id=chat_id,
            query=query,
            top_k=top_k
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in search_documents endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/info/{chat_id}")
async def get_chat_documents_info(
    chat_id: str,
    current_user: UserResponse = Depends(get_current_user),
    document_controller: DocumentController = Depends(get_document_controller)
):
    """
    Get information about documents stored in a chat
    
    - **chat_id**: ID of the chat to get document information for
    """
    try:
        result = await document_controller.get_chat_documents_info(chat_id)
        return result
        
    except Exception as e:
        logger.error(f"Error in get_chat_documents_info endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported document formats
    """
    return {
        "supported_formats": [
            {
                "format": "PDF",
                "mime_types": ["application/pdf"],
                "extensions": [".pdf"]
            },
            {
                "format": "Microsoft Word",
                "mime_types": [
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "application/msword"
                ],
                "extensions": [".docx", ".doc"]
            },
            {
                "format": "Plain Text",
                "mime_types": ["text/plain", "text/csv"],
                "extensions": [".txt", ".csv", ".md"]
            }
        ],
        "max_file_size": "50MB",
        "features": [
            "Automatic text extraction",
            "Text chunking with overlap",
            "Stopword removal and cleaning",
            "Semantic embedding generation",
            "Per-chat document storage",
            "Similarity-based search"
        ]
    }

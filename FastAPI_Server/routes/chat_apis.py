from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
import logging

from controllers.chat import ChatController
from models.chat import ChatCreate, AddMessageRequest, AddResponseRequest
from config.mongodb import get_database
from utils.rag_langgraph import RAGWorkflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize RAG workflow with LOCAL Ollama
rag_workflow = RAGWorkflow(
    model_name="llama2:7b-chat",  # or "mistral:7b-instruct"
    ollama_url="http://localhost:11434"  # Local Ollama
)

@router.post("/api/chat", tags=["Chats"])
async def create_chat(
    chat_data: ChatCreate,
    user_id: str,
    db = Depends(get_database)
):
    """Create a new chat"""
    try:
        chat_controller = ChatController(db)
        chat = await chat_controller.create_chat(user_id, chat_data)
        logger.info(f"Created new chat {chat.id} for user {user_id}")
        return {"status": "success", "data": chat}
    except Exception as e:
        logger.error(f"Error creating chat: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/chat/{chat_id}/uploadDoc", tags=["Chats"])
async def upload_document(
    chat_id: str,
    user_id: str,
    file: UploadFile = File(...),
    db = Depends(get_database)
):
    """Upload a document to a chat (standalone upload)"""
    try:
        # Verify chat belongs to user
        chat_controller = ChatController(db)
        chat = await chat_controller.get_chat(chat_id, user_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Validate file size (max 10MB)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        
        # Read file content
        file_content = await file.read()
        
        logger.info(f"Processing document upload: {file.filename} for chat {chat_id}")
        
        # Process document through RAG workflow (document only, no query)
        result = await rag_workflow.process_rag_request(
            chat_id=chat_id,
            user_id=user_id,
            query="Document uploaded for processing",  # Minimal query for document processing
            document={
                "filename": file.filename,
                "content": file_content
            }
        )
        
        if result["error"]:
            logger.error(f"Document processing error: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"Document {file.filename} processed successfully with {len(result['doc_chunk_ids'])} chunks")
        
        return {
            "status": "success",
            "message": f"Document '{file.filename}' uploaded and processed successfully",
            "doc_chunk_ids": result["doc_chunk_ids"],
            "chunks_count": len(result["doc_chunk_ids"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in document upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/chat/{chat_id}/prompt", tags=["Chats"])
async def process_prompt(
    chat_id: str,
    user_id: str,
    prompt: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db = Depends(get_database)
):
    """Process a prompt with optional document upload using LOCAL RAG pipeline"""
    try:
        # Verify chat belongs to user
        chat_controller = ChatController(db)
        chat = await chat_controller.get_chat(chat_id, user_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Validate prompt
        if not prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Prepare document data if file uploaded
        document_data = None
        if file:
            # Validate file size
            if file.size and file.size > 10 * 1024 * 1024:
                raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
            
            file_content = await file.read()
            document_data = {
                "filename": file.filename,
                "content": file_content
            }
            logger.info(f"Processing prompt with document: {file.filename}")
        else:
            logger.info(f"Processing prompt without document")
        
        # Add message to chat first
        message_request = AddMessageRequest(
            prompt_text=prompt,
            document_metadata={"filename": file.filename} if file else None
        )
        await chat_controller.add_message(chat_id, user_id, message_request)
        
        # Process through RAG workflow
        logger.info(f"Starting LOCAL RAG processing for chat {chat_id}")
        rag_result = await rag_workflow.process_rag_request(
            chat_id=chat_id,
            user_id=user_id,
            query=prompt,
            document=document_data
        )
        
        # Add response to chat
        response_request = AddResponseRequest(
            response_text=rag_result["response"],
            citations=rag_result["citations"],
            doc_chunk_ids=rag_result["doc_chunk_ids"]
        )
        
        updated_chat = await chat_controller.add_response(
            chat_id, user_id, response_request
        )
        
        logger.info(f"LOCAL RAG processing completed for chat {chat_id} with status: {rag_result['status']}")
        
        return {
            "status": "success",
            "data": {
                "chat": updated_chat,
                "response": rag_result["response"],
                "citations": rag_result["citations"],
                "processing_status": rag_result["status"],
                "has_context": bool(rag_result["citations"])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in prompt processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/chat/{chat_id}", tags=["Chats"])
async def get_chat(
    chat_id: str,
    user_id: str,
    db = Depends(get_database)
):
    """Get a specific chat"""
    try:
        chat_controller = ChatController(db)
        chat = await chat_controller.get_chat(chat_id, user_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"status": "success", "data": chat}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/chat", tags=["Chats"])
async def get_user_chats(
    user_id: str,
    limit: int = 50,
    skip: int = 0,
    db = Depends(get_database)
):
    """Get all chats for the current user"""
    try:
        chat_controller = ChatController(db)
        chats = await chat_controller.get_user_chats(user_id, limit, skip)
        return {"status": "success", "data": chats}
    except Exception as e:
        logger.error(f"Error retrieving user chats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/chat/{chat_id}", tags=["Chats"])
async def delete_chat(
    chat_id: str,
    user_id: str,
    db = Depends(get_database)
):
    """Delete a chat and its associated documents"""
    try:
        chat_controller = ChatController(db)
        deleted = await chat_controller.delete_chat(chat_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        logger.info(f"Deleted chat {chat_id} for user {user_id}")
        return {"status": "success", "message": "Chat deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

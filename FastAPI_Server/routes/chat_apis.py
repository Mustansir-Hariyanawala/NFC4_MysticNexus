from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from controllers.chat import ChatController
from models.chat import (
    ChatCreate, ChatResponse, AddMessageRequest, 
    AddResponseRequest, UpdateChatStatusRequest
)
from config.mongodb import get_database

router = APIRouter(prefix="/api/chats", tags=["chats"])

def get_chat_controller(db = Depends(get_database)) -> ChatController:
    return ChatController(db)

@router.post("/", response_model=ChatResponse)
async def create_chat(
    chat_data: ChatCreate,
    user_id: str,
    controller: ChatController = Depends(get_chat_controller)
):
    """Create a new chat for a user"""
    try:
        return await controller.create_chat(user_id, chat_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: str,
    user_id: str,
    controller: ChatController = Depends(get_chat_controller)
):
    """Get a specific chat by ID"""
    try:
        chat = await controller.get_chat(chat_id, user_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ChatResponse])
async def get_user_chats(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    controller: ChatController = Depends(get_chat_controller)
):
    """Get all chats for a user with pagination"""
    try:
        return await controller.get_user_chats(user_id, limit, skip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{chat_id}/messages", response_model=ChatResponse)
async def add_message(
    chat_id: str,
    user_id: str,
    message_data: AddMessageRequest,
    controller: ChatController = Depends(get_chat_controller)
):
    """Add a new message to a chat"""
    try:
        return await controller.add_message(chat_id, user_id, message_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{chat_id}/responses", response_model=ChatResponse)
async def add_response(
    chat_id: str,
    user_id: str,
    response_data: AddResponseRequest,
    controller: ChatController = Depends(get_chat_controller)
):
    """Add a response to the latest message in a chat"""
    try:
        return await controller.add_response(chat_id, user_id, response_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{chat_id}/status", response_model=ChatResponse)
async def update_chat_status(
    chat_id: str,
    user_id: str,
    status_data: UpdateChatStatusRequest,
    controller: ChatController = Depends(get_chat_controller)
):
    """Update the status of the latest message in a chat"""
    try:
        return await controller.update_chat_status(chat_id, user_id, status_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{chat_id}/title", response_model=ChatResponse)
async def update_chat_title(
    chat_id: str,
    user_id: str,
    title: str,
    controller: ChatController = Depends(get_chat_controller)
):
    """Update the title of a chat"""
    try:
        return await controller.update_chat_title(chat_id, user_id, title)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    user_id: str,
    controller: ChatController = Depends(get_chat_controller)
):
    """Delete a chat"""
    try:
        success = await controller.delete_chat(chat_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"message": "Chat deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

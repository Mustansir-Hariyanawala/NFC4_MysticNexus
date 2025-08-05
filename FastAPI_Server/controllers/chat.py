from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from bson import ObjectId
from models.chat import (
    Chat, ChatCreate, ChatResponse, AddMessageRequest, 
    AddResponseRequest, UpdateChatStatusRequest, HistoryEntry, 
    Prompt, Response, ChatStatus, PyObjectId
)
from config.chromadb import create_chat_collection, delete_chat_collection

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase

class ChatController:
    def __init__(self, database):
        self.db = database
        self.chat_collection = database.chats
        self.user_collection = database.users

    async def create_chat(self, user_id: str, chat_data: ChatCreate) -> ChatResponse:
        """Create a new chat for a user"""
        try:
            user_object_id = PyObjectId(user_id)
            
            # Verify user exists
            user = await self.user_collection.find_one({"_id": user_object_id})
            if not user:
                raise ValueError("User not found")
            
            # Create new chat
            chat = Chat(
                user_id=user_object_id,
                title=chat_data.title,
                history=[],
                docs=[]
            )
            
            # Insert chat into database
            chat_dict = chat.model_dump(by_alias=True, exclude={"id"})
            result = await self.chat_collection.insert_one(chat_dict)
            
            # Create ChromaDB collection for this chat
            chat_id_str = str(result.inserted_id)
            await create_chat_collection(chat_id_str, user_id)
            
            # Update user's chat_ids
            await self.user_collection.update_one(
                {"_id": user_object_id},
                {"$addToSet": {"chat_ids": result.inserted_id}}
            )
            
            # Return the created chat
            created_chat = await self.chat_collection.find_one({"_id": result.inserted_id})
            return ChatResponse(**created_chat)
            
        except Exception as e:
            raise Exception(f"Error creating chat: {str(e)}")

    async def get_chat(self, chat_id: str, user_id: str) -> Optional[ChatResponse]:
        """Get a specific chat by ID if it belongs to the user"""
        try:
            chat_object_id = PyObjectId(chat_id)
            user_object_id = PyObjectId(user_id)
            
            chat = await self.chat_collection.find_one({
                "_id": chat_object_id,
                "user_id": user_object_id
            })
            
            if chat:
                return ChatResponse(**chat)
            return None
            
        except Exception as e:
            raise Exception(f"Error retrieving chat: {str(e)}")

    async def get_user_chats(self, user_id: str, limit: int = 50, skip: int = 0) -> List[ChatResponse]:
        """Get all chats for a user with pagination"""
        try:
            user_object_id = PyObjectId(user_id)
            
            cursor = self.chat_collection.find(
                {"user_id": user_object_id}
            ).sort("updated_at", -1).limit(limit).skip(skip)
            
            chats = []
            async for chat in cursor:
                chats.append(ChatResponse(**chat))
            
            return chats
            
        except Exception as e:
            raise Exception(f"Error retrieving user chats: {str(e)}")

    async def add_message(self, chat_id: str, user_id: str, message_data: AddMessageRequest) -> ChatResponse:
        """Add a new message to a chat"""
        try:
            chat_object_id = PyObjectId(chat_id)
            user_object_id = PyObjectId(user_id)
            
            # Verify chat exists and belongs to user
            chat = await self.chat_collection.find_one({
                "_id": chat_object_id,
                "user_id": user_object_id
            })
            
            if not chat:
                raise ValueError("Chat not found or doesn't belong to user")
            
            # Create new history entry
            prompt = Prompt(
                doc=message_data.document_metadata,
                text=message_data.prompt_text
            )
            
            history_entry = HistoryEntry(
                prompt=prompt,
                status=ChatStatus.PENDING
            )
            
            # Update chat
            await self.chat_collection.update_one(
                {"_id": chat_object_id},
                {
                    "$push": {"history": history_entry.model_dump()},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Return updated chat
            updated_chat = await self.chat_collection.find_one({"_id": chat_object_id})
            return ChatResponse(**updated_chat)
            
        except Exception as e:
            raise Exception(f"Error adding message: {str(e)}")

    async def add_response(self, chat_id: str, user_id: str, response_data: AddResponseRequest) -> ChatResponse:
        """Add a response to the latest message in a chat"""
        try:
            chat_object_id = PyObjectId(chat_id)
            user_object_id = PyObjectId(user_id)
            
            # Verify chat exists and belongs to user
            chat = await self.chat_collection.find_one({
                "_id": chat_object_id,
                "user_id": user_object_id
            })
            
            if not chat:
                raise ValueError("Chat not found or doesn't belong to user")
            
            if not chat.get("history"):
                raise ValueError("No messages in chat to respond to")
            
            # Create response
            response = Response(
                citations=response_data.citations,
                text=response_data.response_text
            )
            
            # Update the latest history entry with response
            update_query = {
                "$set": {
                    f"history.{len(chat['history']) - 1}.response": response.model_dump(),
                    f"history.{len(chat['history']) - 1}.status": ChatStatus.COMPLETED,
                    "updated_at": datetime.utcnow()
                }
            }
            
            # Add document chunk IDs to chat docs if provided
            if response_data.doc_chunk_ids:
                update_query["$addToSet"] = {"docs": {"$each": response_data.doc_chunk_ids}}
            
            await self.chat_collection.update_one({"_id": chat_object_id}, update_query)
            
            # Return updated chat
            updated_chat = await self.chat_collection.find_one({"_id": chat_object_id})
            return ChatResponse(**updated_chat)
            
        except Exception as e:
            raise Exception(f"Error adding response: {str(e)}")

    async def update_chat_status(self, chat_id: str, user_id: str, status_data: UpdateChatStatusRequest) -> ChatResponse:
        """Update the status of the latest message in a chat"""
        try:
            chat_object_id = PyObjectId(chat_id)
            user_object_id = PyObjectId(user_id)
            
            # Verify chat exists and belongs to user
            chat = await self.chat_collection.find_one({
                "_id": chat_object_id,
                "user_id": user_object_id
            })
            
            if not chat:
                raise ValueError("Chat not found or doesn't belong to user")
            
            if not chat.get("history"):
                raise ValueError("No messages in chat to update")
            
            # Update the latest history entry status
            await self.chat_collection.update_one(
                {"_id": chat_object_id},
                {
                    "$set": {
                        f"history.{len(chat['history']) - 1}.status": status_data.status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Return updated chat
            updated_chat = await self.chat_collection.find_one({"_id": chat_object_id})
            return ChatResponse(**updated_chat)
            
        except Exception as e:
            raise Exception(f"Error updating chat status: {str(e)}")

    async def delete_chat(self, chat_id: str, user_id: str) -> bool:
        """Delete a chat and its ChromaDB collection"""
        try:
            chat_object_id = PyObjectId(chat_id)
            user_object_id = PyObjectId(user_id)
            
            # Verify chat exists and belongs to user
            chat = await self.chat_collection.find_one({
                "_id": chat_object_id,
                "user_id": user_object_id
            })
            
            if not chat:
                return False
            
            # Delete ChromaDB collection for this chat
            await delete_chat_collection(chat_id)
            
            # Remove chat from user's chat_ids
            await self.user_collection.update_one(
                {"_id": user_object_id},
                {"$pull": {"chat_ids": chat_object_id}}
            )
            
            # Delete the chat
            result = await self.chat_collection.delete_one({"_id": chat_object_id})
            return result.deleted_count > 0
            
        except Exception as e:
            raise Exception(f"Error deleting chat: {str(e)}")

    async def update_chat_title(self, chat_id: str, user_id: str, title: str) -> ChatResponse:
        """Update the title of a chat"""
        try:
            chat_object_id = PyObjectId(chat_id)
            user_object_id = PyObjectId(user_id)
            
            # Update the chat title
            result = await self.chat_collection.update_one(
                {"_id": chat_object_id, "user_id": user_object_id},
                {
                    "$set": {
                        "title": title,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count == 0:
                raise ValueError("Chat not found or doesn't belong to user")
            
            # Return updated chat
            updated_chat = await self.chat_collection.find_one({"_id": chat_object_id})
            return ChatResponse(**updated_chat)
            
        except Exception as e:
            raise Exception(f"Error updating chat title: {str(e)}")

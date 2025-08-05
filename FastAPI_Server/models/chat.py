from pydantic import BaseModel, Field, ConfigDict, GetJsonSchemaHandler
from typing import Optional, Any, List, Dict
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from enum import Enum

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x),
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def _validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema.update(type="string", format="objectid")
        return json_schema

class ChatStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class DocumentMetadata(BaseModel):
    filename: str = Field(..., description="Name of the uploaded file")
    size: int = Field(..., description="Size of the file in bytes")
    type: str = Field(..., description="MIME type of the file")
    upload_time: datetime = Field(default_factory=datetime.utcnow, description="When the document was uploaded")
    chunk_count: Optional[int] = Field(None, description="Number of chunks the document was split into")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class Prompt(BaseModel):
    doc: Optional[DocumentMetadata] = Field(None, description="Document metadata if a document was uploaded with this prompt")
    text: str = Field(..., description="The user's text prompt")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class Citation(BaseModel):
    doc_chunk_id: str = Field(..., description="ID of the document chunk from ChromaDB")
    page_number: Optional[int] = Field(None, description="Page number in the original document")
    chunk_text: Optional[str] = Field(None, description="Snippet of the cited text")
    
    model_config = ConfigDict(populate_by_name=True)

class Response(BaseModel):
    citations: List[Citation] = Field(default_factory=list, description="List of citations for the response")
    text: str = Field(..., description="The AI's response text")
    
    model_config = ConfigDict(populate_by_name=True)

class HistoryEntry(BaseModel):
    prompt: Prompt = Field(..., description="User's prompt")
    response: Optional[Response] = Field(None, description="AI's response")
    status: ChatStatus = Field(default=ChatStatus.PENDING, description="Status of this chat entry")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this entry was created")
    
    model_config = ConfigDict(populate_by_name=True)

class Chat(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(..., description="ID of the user who owns this chat")
    title: Optional[str] = Field(None, description="Optional title for the chat")
    history: List[HistoryEntry] = Field(default_factory=list, description="Chat history entries")
    docs: List[str] = Field(default_factory=list, description="List of document chunk IDs from ChromaDB")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the chat was created")
    updated_at: Optional[datetime] = Field(None, description="When the chat was last updated")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Request/Response models for API endpoints
class ChatCreate(BaseModel):
    title: Optional[str] = Field(None, description="Optional title for the chat")
    
    model_config = ConfigDict(populate_by_name=True)

class ChatResponse(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    user_id: PyObjectId
    title: Optional[str] = None
    history: List[HistoryEntry] = Field(default_factory=list)
    docs: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class AddMessageRequest(BaseModel):
    prompt_text: str = Field(..., description="The user's text prompt")
    document_metadata: Optional[DocumentMetadata] = Field(None, description="Metadata of uploaded document")
    
    model_config = ConfigDict(populate_by_name=True)

class AddResponseRequest(BaseModel):
    response_text: str = Field(..., description="The AI's response text")
    citations: List[Citation] = Field(default_factory=list, description="Citations for the response")
    doc_chunk_ids: List[str] = Field(default_factory=list, description="Document chunk IDs to add to chat")
    
    model_config = ConfigDict(populate_by_name=True)

class UpdateChatStatusRequest(BaseModel):
    status: ChatStatus = Field(..., description="New status for the latest chat entry")
    
    model_config = ConfigDict(populate_by_name=True)

from pydantic import BaseModel, Field, EmailStr, ConfigDict, GetJsonSchemaHandler
from typing import Optional, Any, List
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue

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

class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    chat_ids: List[PyObjectId] = Field(default_factory=list, description="List of chat IDs associated with the user")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserInDB(UserBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    chat_ids: List[PyObjectId] = Field(default_factory=list, description="List of chat IDs associated with the user")
    salt: str
    password_hash: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserLogin(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class ChangePassword(BaseModel):
    email: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, alias="newPassword")

    model_config = ConfigDict(populate_by_name=True)

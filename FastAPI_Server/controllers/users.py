from fastapi import HTTPException, status
from config.mongodb import get_database
from models.user import UserCreate, UserResponse, UserInDB, ChangePassword
from utils.password_utils import generate_password_hash
from bson import ObjectId
from typing import List
from datetime import datetime

class UserController:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.Users

    async def get_all_users(self) -> List[UserResponse]:
        """Get all users"""
        try:
            cursor = self.collection.find()
            users = []
            async for user_doc in cursor:
                user_doc["id"] = str(user_doc["_id"])
                users.append(UserResponse(**user_doc))
            return users
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching users: {str(e)}"
            )

    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """Get a single user by ID"""
        try:
            if not ObjectId.is_valid(user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID format"
                )
            
            user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user_doc["id"] = str(user_doc["_id"])
            return UserResponse(**user_doc)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching user: {str(e)}"
            )

    async def get_user_by_username(self, username: str) -> UserResponse:
        """Get a single user by username"""
        try:
            user_doc = await self.collection.find_one({"username": username})
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user_doc["id"] = str(user_doc["_id"])
            return UserResponse(**user_doc)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching user: {str(e)}"
            )

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        try:
            # Check if username already exists
            existing_user = await self.collection.find_one({"username": user_data.username})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists"
                )
            
            # Check if email already exists
            existing_email = await self.collection.find_one({"email": user_data.email})
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists"
                )
            
            # Generate password hash
            salt, password_hash = generate_password_hash(user_data.username, user_data.password)
            
            # Create user document
            user_doc = {
                "username": user_data.username,
                "email": user_data.email,
                "chat_ids": [],  # Initialize empty chat_ids list
                "salt": salt,
                "password_hash": password_hash,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert user
            result = await self.collection.insert_one(user_doc)
            user_doc["_id"] = result.inserted_id
            user_doc["id"] = str(result.inserted_id)
            
            return UserResponse(**user_doc)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating user: {str(e)}"
            )

    async def change_password(self, change_data: ChangePassword) -> dict:
        """Change password for a user"""
        try:
            # Find user
            user_doc = await self.collection.find_one({"username": change_data.username})
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Generate new password hash
            salt, password_hash = generate_password_hash(change_data.username, change_data.new_password)
            
            # Update user
            await self.collection.update_one(
                {"username": change_data.username},
                {
                    "$set": {
                        "salt": salt,
                        "password_hash": password_hash,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {"message": "Password updated successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating password: {str(e)}"
            )

    async def delete_user(self, user_id: str) -> dict:
        """Delete a user by ID"""
        try:
            if not ObjectId.is_valid(user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID format"
                )
            
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return {"message": "User deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting user: {str(e)}"
            )

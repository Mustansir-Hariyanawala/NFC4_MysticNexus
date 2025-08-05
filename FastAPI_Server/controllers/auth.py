from fastapi import HTTPException, status
from config.mongodb import get_database
from models.user import UserLogin, UserCreate, UserResponse
from utils.password_utils import generate_password_hash, verify_password
from datetime import datetime

class AuthController:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.Users

    async def login(self, login_data: UserLogin) -> dict:
        """Handle user login"""
        try:
            print("User data Recieved : ", login_data)

            # Find user by email
            user_doc = await self.collection.find_one({"email": login_data.email})
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Verify password using email for salting
            is_valid = verify_password(
                login_data.password,
                user_doc["email"],  # Use email for salting
                user_doc["salt"],
                user_doc["password_hash"]
            )
            
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password"
                )
            
            # Return success response
            return {
                "success": True,
                "message": "Login successful",
                "data": {
                    "username": user_doc["username"],
                    "email": user_doc["email"]
                }
            }
        except Exception as e:
            print("Error : ", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def signup(self, signup_data: UserCreate) -> dict:
        """Handle user signup"""
        try:
            # Check if username already exists
            existing_user = await self.collection.find_one({"username": signup_data.username})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists"
                )
            
            # Check if email already exists
            existing_email = await self.collection.find_one({"email": signup_data.email})
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists"
                )
            
            # Generate password hash using email for salting
            salt, password_hash = generate_password_hash(signup_data.email, signup_data.password)
            
            # Create user document
            user_doc = {
                "username": signup_data.username,
                "email": signup_data.email,
                "salt": salt,
                "password_hash": password_hash,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert user
            result = await self.collection.insert_one(user_doc)
            user_doc["_id"] = result.inserted_id
            user_doc["id"] = str(result.inserted_id)
            
            # Return success response (excluding sensitive data)
            return {
                "success": True,
                "message": "Signup successful",
                "user": {
                    "id": str(user_doc["_id"]),
                    "username": user_doc["username"],
                    "email": user_doc["email"],
                    "created_at": user_doc["created_at"]
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

from fastapi import APIRouter, Depends
from controllers.users import UserController
from models.user import UserCreate, UserResponse, ChangePassword
from typing import List

router = APIRouter()

def get_user_controller():
    return UserController()

@router.get("/", response_model=List[UserResponse])
async def get_all_users(controller: UserController = Depends(get_user_controller)):
    """Get all users"""
    return await controller.get_all_users()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, controller: UserController = Depends(get_user_controller)):
    """Get a single user by ID"""
    return await controller.get_user_by_id(user_id)

@router.get("/username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, controller: UserController = Depends(get_user_controller)):
    """Get a single user by username"""
    return await controller.get_user_by_username(username)

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate, controller: UserController = Depends(get_user_controller)):
    """Create a new user"""
    return await controller.create_user(user_data)

@router.put("/change-password")
async def change_password(change_data: ChangePassword, controller: UserController = Depends(get_user_controller)):
    """Change password for a user"""
    return await controller.change_password(change_data)

@router.delete("/{user_id}")
async def delete_user(user_id: str, controller: UserController = Depends(get_user_controller)):
    """Delete a user by ID"""
    return await controller.delete_user(user_id)

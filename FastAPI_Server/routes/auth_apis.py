from fastapi import APIRouter, Depends
from controllers.auth import AuthController
from models.user import UserLogin, UserCreate

router = APIRouter()

def get_auth_controller():
    return AuthController()

@router.post("/login")
async def login(login_data: UserLogin, controller: AuthController = Depends(get_auth_controller)):
    """Login endpoint"""
    print(f"Login attempt for user: {login_data}")
    return await controller.login(login_data)

@router.post("/signup")
async def signup(signup_data: UserCreate, controller: AuthController = Depends(get_auth_controller)):
    """Signup endpoint"""
    return await controller.signup(signup_data)

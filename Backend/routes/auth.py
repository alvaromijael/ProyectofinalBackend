from fastapi import APIRouter
from services.auth_service import register,login
from models.User import User,UserLogin
router = APIRouter(prefix="/auth", tags=["register"])

@router.post("/register")
def register_route(user:User):
    return register(user)

@router.post("/login")
def login_route(user_login:UserLogin):
    email = user_login.email
    password = user_login.password
    return login(email,password)
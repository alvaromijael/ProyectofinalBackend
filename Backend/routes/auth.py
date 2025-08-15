from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from database.db import SessionLocal
from services.auth_service import register
from models.User import User,AuthUser

router = APIRouter(prefix="/auth", tags=["register"])

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""@router.post("/register")
def register_route(user:User):
    return register(user)"""

@router.post("/register")
def register_route(user: User, db: Session = Depends(get_db)):
    return register(user, db)


"""@router.post("/login")
def login_route(user_login:UserLogin):
    email = user_login.email
    password = user_login.password
    return login(email,password)"""
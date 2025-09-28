from fastapi import APIRouter, Request, HTTPException
from services.user_service import get_users, update_user, get_user, delete_user, get_roles, change_user_password
from models.User import UserUpdate, PasswordChange
from fastapi.params import Depends
from sqlalchemy.orm import Session
from database.db import SessionLocal, get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def get_users_route(request: Request,db: Session = Depends(get_db), role: str = None, first_name: str = None,  start_birth_date: str = None, end_birth_date: str = None):
    #if not hasattr(request.state, "user"):
    #    raise HTTPException(status_code=401, detail="Unauthorized")
    return get_users(db=db,role=role, first_name=first_name, start_birth_date=start_birth_date, end_birth_date=end_birth_date)

@router.get("/roles")
def get_roles_route(request: Request,db: Session = Depends(get_db)):
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return get_roles(db)


@router.put("/{user_id}")
def update_user_router(
        request: Request,
        user_id: int,
        user: UserUpdate,
        db: Session = Depends(get_db)
):
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return update_user(db=db, user_id=user_id, user_data=user)

@router.post("/change-password")
def change_password_route(
    request: Request,
    data: PasswordChange,
    db: Session = Depends(get_db)
):
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = request.state.user.id
    return change_user_password(db=db, user_id=user_id, data=data)


@router.get("/{user_id}")
def get_user_route(request: Request, user_id: int):
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return get_user(user_id)

@router.delete("/{user_id}")
def delete_user_route(request: Request, user_id: int, db: Session = Depends(get_db)):
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return delete_user(db,user_id)
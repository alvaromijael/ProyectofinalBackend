from fastapi import APIRouter, Request, HTTPException

from services.user_service import get_users, update_user, get_user, delete_user
from models.User import UserUpdate
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def get_users_route(request: Request, role: str = None, first_name: str = None,  start_birth_date: str = None, end_birth_date: str = None):
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return get_users(role=role, first_name=first_name, start_birth_date=start_birth_date, end_birth_date=end_birth_date)


@router.put("/{user_id}")
def update_user_router(request: Request, user_id: str, user: UserUpdate):
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return update_user(user_id = user_id, user= user)

@router.get("/{user_id}")
def get_user_route(request: Request, user_id: str):
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return get_user(user_id)

@router.delete("/{user_id}")
def delete_user_route(request: Request, user_id: str):
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return delete_user(user_id)

from bson import ObjectId
from sqlalchemy.orm import Session
from models.User import AuthUser, Role
from typing import Optional
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import and_
from database.db import SessionLocal, get_db

def get_users(
    db: Session,
    role: Optional[str] = None,
    first_name: Optional[str] = None,
    start_birth_date: Optional[str] = None,
    end_birth_date: Optional[str] = None
):
    query = db.query(AuthUser).join(Role)

    if role:
        query = query.filter(Role.name == role)
    if first_name:
        query = query.filter(AuthUser.first_name == first_name)
    if start_birth_date and end_birth_date:
        try:
            start = datetime.strptime(start_birth_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_birth_date, "%Y-%m-%d").date()
            query = query.filter(AuthUser.birth_date.between(start, end))
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD.")

    users = query.all()

    results = []
    for user in users:
        user_dict = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            "role": user.role.name if user.role else None,
            "created_at": user.created_at.isoformat(),
            "is_active": user.is_active
        }
        results.append(user_dict)

    return {"message": "Ok", "data": results}


def update_user(db: Session, user_id: int, user_data):
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Actualizar campos (asumiendo que user_data es un Pydantic model)
    for field, value in user_data.model_dump().items():
        if hasattr(user, field):
            setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return {"message": "User updated successfully"}


def get_user(db: Session, user_id: int):
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_dict = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "birth_date": user.birth_date.isoformat() if user.birth_date else None,
        "role": user.role.name if user.role else None,
        "created_at": user.created_at.isoformat(),
        "is_active": user.is_active,
        "password": None  # ocultar password
    }
    return {"message": "Ok", "data": user_dict}


def delete_user(db: Session, user_id: int):
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

def get_roles(db: Session):
    try:
        roles = db.query(Role).all()
    except:
        raise HTTPException(status_code=404, detail="Role not found")

    return [{"id": role.id, "name": role.name} for role in roles]
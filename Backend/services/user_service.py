from bson import ObjectId
from sqlalchemy.orm import Session
from models.User import AuthUser, Role, PasswordChange
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
            "cedula": user.cedula,  # ← AGREGAR ESTE CAMPO
            "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            "role": user.role.name if user.role else None,
            "created_at": user.created_at.isoformat(),
            "is_active": user.is_active
        }
        results.append(user_dict)

    return {"message": "Ok", "data": results}


def update_user(db: Session, user_id: int, user_data):
    # Buscar el usuario
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Convertir los datos del Pydantic model
    update_data = user_data.model_dump(exclude_unset=True)

    # ← AGREGAR VALIDACIÓN DE CÉDULA ÚNICA
    if 'cedula' in update_data:
        existing_user = db.query(AuthUser).filter(
            AuthUser.cedula == update_data['cedula'],
            AuthUser.id != user_id  # Excluir el usuario actual
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="La cédula ya está registrada")

    # Manejar el rol especialmente
    if 'role' in update_data:
        role_name = update_data.pop('role')  # Quitar role del dict
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise HTTPException(status_code=400, detail=f"Rol '{role_name}' no encontrado")
        user.role_id = role.id

    # Manejar birth_date si viene (convertir string a date)
    if 'birth_date' in update_data and update_data['birth_date']:
        try:
            birth_date_str = update_data.pop('birth_date')
            user.birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD.")
    elif 'birth_date' in update_data and not update_data['birth_date']:
        update_data.pop('birth_date')  # Quitar si es None o vacío

    # Actualizar resto de campos normales (first_name, last_name, email, cedula, is_active)
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al actualizar usuario")

    return {
        "message": "Usuario actualizado correctamente",
        "data": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "cedula": user.cedula,  # ← AGREGAR ESTE CAMPO
            "role": user.role.name if user.role else None,
            "is_active": user.is_active
        }
    }

def change_user_password(db: Session, user_id: int, data: PasswordChange):
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verifica la contraseña actual
    if not user.verify_password(data.current_password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")

    # Actualiza la contraseña
    user.set_password(data.new_password)
    db.commit()
    db.refresh(user)

    return {"message": "Contraseña actualizada correctamente"}


def get_user(db: Session, user_id: int):
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_dict = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "cedula": user.cedula,  # ← AGREGAR ESTE CAMPO
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


def get_by_role_services(
        db: Session,
        role_id: Optional[int] = None,
):
    query = db.query(AuthUser).join(Role)
    print(f"Role ID recibido: {role_id}")

    if role_id:
        query = query.filter(Role.id == role_id)

    users = query.all()

    results = []
    for user in users:
        user_dict = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "cedula": user.cedula,  # ← AGREGAR ESTE CAMPO
            "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            "role": user.role.name if user.role else None,
            "created_at": user.created_at.isoformat(),
            "is_active": user.is_active
        }
        results.append(user_dict)

    return {"message": "Ok", "data": results}
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from models.User import AuthUser,User

"""from database.mongo import db"""
import bcrypt
import jwt
import os



salt=bcrypt.gensalt()

"""Registro con mongo"""

"""
    user_db=db["users"]
    def register (user):
    data_user=user.model_dump()

    result_exist = user_db.find_one({'email': data_user['email']})
    if result_exist:
        return {'message': 'User already exists'}

    hash_password = bcrypt.hashpw(
        password=data_user['password'].encode('utf-8'),
        salt=salt
    ).decode('utf-8')
    data_user['password'] = hash_password
    data_user['role']='user'
    data_user['status']='active'
    user_db.insert_one(data_user)
    return {'message': 'User registered successfully'}"""

def register(user: User, db: Session):
    # Verificar si el usuario ya existe
    existing_user = db.query(AuthUser).filter(AuthUser.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Generar un nuevo salt y hashear la contraseña
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(
        password=user.password.encode('utf-8'),
        salt=salt
    ).decode('utf-8')

    # Crear nueva instancia del usuario
    new_user = AuthUser(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_pwd,
        birth_date=user.birth_date,
        role_id=2,
        is_active=True,
        created_at=datetime.utcnow()
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error during registration")

    return {"message": "User registered successfully"}



""" 
def login(email,password):
    user_exist=user_db.find_one({'email': email})
    if not user_exist:
        return {'message': 'User does not exist'}
    check_password=bcrypt.checkpw(password.encode('utf-8'),user_exist['password'].encode('utf-8'))
    if not check_password:
        return {'message': 'Password incorrect'}
    user_exist['_id']=str(user_exist['_id'])
    user_exist['password']=None
    secret_key=os.getenv('JWT_SECRET_KEY')
    payload={
        "email":user_exist['email'],
        "last_name":user_exist['last_name'],
        "first_name":user_exist['first_name'],
        "exp":datetime.utcnow() + timedelta(hours=1)
    }

    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return{'message': 'Logged in successfully','user':user_exist,"token":token}
print(login('<EMAIL>','<PASSWORD>'))
"""
def login(email: str, password: str, db: Session):
    user_exist = db.query(AuthUser).filter(AuthUser.email == email).first()

    if not user_exist:
        return {'message': 'User does not exist'}

    check_password = bcrypt.checkpw(password.encode('utf-8'), user_exist.password.encode('utf-8'))
    if not check_password:
        return {'message': 'Password incorrect'}

    # Prepara el payload del JWT
    secret_key = os.getenv('JWT_SECRET_KEY')
    payload = {
        "email": user_exist.email,
        "last_name": user_exist.last_name,
        "first_name": user_exist.first_name,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    token = jwt.encode(payload, secret_key, algorithm='HS256')

    return {
        'message': 'Logged in successfully',
        'user': {
            "email": user_exist.email,
            "first_name": user_exist.first_name,
            "last_name": user_exist.last_name,
            "role": user_exist.role
        },
        "token": token
    }




def profile_user(request: Request):
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Token required")
    return {"message": request.state.user['user_name']}




def get_user_by_email(email: str, db: Session):
    result = db.query(AuthUser).filter(AuthUser.email == email).first()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    result = result.__dict__
    result.pop('password', None)
    result['id'] = str(result['id'])  # si prefieres mantener el ID como string

    return result



from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from database.mongo import db
import bcrypt
import jwt
import os

user_db=db["users"]
salt=bcrypt.gensalt()

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
    return {'message': 'User registered successfully'}


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


def profile_user(request: Request):
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Token required")
    return {"message": request.state.user['user_name']}

def get_user_by_email(email: str):
    result = user_db.find_one({'email': email})
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    result['_id'] = str(result['_id'])
    result.pop('password', None)
    return result


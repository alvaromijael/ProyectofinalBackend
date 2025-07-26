from fastapi import Depends, FastAPI
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
    token = jwt.encode(user_exist, salt, algorithm='HS256')
    return{'message': 'Logged in successfully','user':user_exist,"token":token}



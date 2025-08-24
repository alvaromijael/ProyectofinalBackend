from starlette.middleware.base import BaseHTTPMiddleware
from services.auth_service import get_user_by_email
from fastapi import Request
import jwt
from database.db import SessionLocal, get_db

def verify_token(token: str):
    try:
        return jwt.decode(token, 'secret123', algorithms=["HS256"])
        print("decode ok")
    except jwt.ExpiredSignatureError:
        print("Token expirado")
        return None
        print("Token inválido")
    except jwt.InvalidTokenError:
        return None


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            payload = verify_token(token)
            if payload:
                db = next(get_db())
                request.state.user = get_user_by_email(payload['email'],db)
        return await call_next(request)
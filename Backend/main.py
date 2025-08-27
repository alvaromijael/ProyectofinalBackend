from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from middleware.auth import AuthMiddleware

from routes import auth
from routes import users

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(patient.router)
app.include_router(appointment.router)

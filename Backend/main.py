from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from middleware.auth import AuthMiddleware

from routes import auth
from routes import users
from routes import patient
from routes import appointment
from routes import report

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://fenixweb.j8hx8gh0jmcw8.us-east-1.cs.amazonlightsail.com",
    "http://44.211.190.95:5173",
    "https://44.211.190.95:5173"
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

app.include_router(report.router)

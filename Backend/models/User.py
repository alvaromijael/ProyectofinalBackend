import datetime

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Date, UniqueConstraint, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.db import Base
from models.Appointment import Appointment
from passlib.context import CryptContext

# Agregar esta línea al inicio del archivo (después de los imports)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    birth_date: str


class UserLogin(BaseModel):
    email: str
    password: str

from typing import Optional

class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: bool
    birth_date: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class AuthUser(Base):
    __tablename__ = 'auth_users'
    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
        {'schema': 'auth'}
    )

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    birth_date = Column(Date, nullable=True)
    role_id = Column(Integer, ForeignKey('auth.roles.id'), nullable=False)  # FK a roles.id
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False)

    # Relaciones
    role = relationship("Role", back_populates="users")
    appointments = relationship("Appointment", back_populates="user")

    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    def __repr__(self):
        return f"<AuthUser(id={self.id}, email='{self.email}')>"

class Role(Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'auth'}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # Relaciones
    users = relationship("AuthUser", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role")

class RolePermission(Base):
    __tablename__ = 'role_permissions'
    __table_args__ = (
        UniqueConstraint('role_id', 'modulo', name='uq_role_modulo'),
        {'schema': 'auth'}
    )

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('auth.roles.id'), nullable=False)  # FK a roles.id
    modulo = Column(String(100), nullable=False)
    ver = Column(Boolean, nullable=False, default=False)
    crear = Column(Boolean, nullable=False, default=False)
    editar = Column(Boolean, nullable=False, default=False)
    eliminar = Column(Boolean, nullable=False, default=False)

    role = relationship("Role", back_populates="permissions")



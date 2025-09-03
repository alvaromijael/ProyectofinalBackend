import datetime

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Date, UniqueConstraint, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.db import Base


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    birth_date: str


class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    email: str
    birth_date: str
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

    # Relaciones
    role = relationship("Role", back_populates="permissions")

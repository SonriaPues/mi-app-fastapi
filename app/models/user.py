"""
Modelos Pydantic para la colección 'users'.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class UserInDB(BaseModel):
    """Modelo interno completo del usuario (con hash de contraseña)."""
    id: Optional[str] = None
    username: str
    password_hash: str
    role: str = "user"          # "user" | "admin"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserPublic(BaseModel):
    """Modelo público del usuario (sin contraseña)."""
    id: str
    username: str
    role: str
    is_active: bool
    created_at: datetime


class UserCreate(BaseModel):
    """Datos necesarios para registrar un nuevo usuario."""
    username: str
    password: str


class UserLogin(BaseModel):
    """Datos para iniciar sesión."""
    username: str
    password: str

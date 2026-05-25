"""
Logica de autenticacion JWT con cookies HttpOnly.
Incluye helpers para hash/verificacion de contrasenas.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import Cookie, Depends, HTTPException, Request, status
from jose import JWTError, jwt

from app.config import get_settings
from app.database import get_database

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────
# Utilidades de contrasena
# ──────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Genera el hash bcrypt de una contrasena."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica si una contrasena coincide con su hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def validate_password_strength(password: str) -> bool:
    """
    Valida que la contrasena tenga al menos 8 caracteres,
    una letra y un numero.
    """
    if len(password) < 8:
        return False
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_letter and has_digit


# ──────────────────────────────────────────
# Utilidades JWT
# ──────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """Crea un JWT con expiracion configurable."""
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_expire_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    """Decodifica y valida un JWT. Retorna None si es invalido."""
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None


# ──────────────────────────────────────────
# Dependencias FastAPI
# ──────────────────────────────────────────

async def get_current_user(request: Request):
    """
    Dependencia que extrae y valida el usuario desde la cookie JWT.
    Retorna el documento del usuario o None si no esta autenticado.
    """
    token = request.cookies.get("access_token")
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    username: str = payload.get("sub")
    if not username:
        return None

    db = get_database()
    user = await db.users.find_one({"username": username})
    if not user or not user.get("is_active", True):
        return None

    # Convertir ObjectId a string para facilitar uso en templates
    user["id"] = str(user["_id"])
    return user


async def require_auth(request: Request):
    """Dependencia que exige autenticacion. Lanza 401 si no hay sesion."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes iniciar sesion para acceder a este recurso."
        )
    return user


async def require_admin(request: Request):
    """Dependencia que exige rol admin. Lanza 403 si no es admin."""
    user = await require_auth(request)
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de administrador."
        )
    return user

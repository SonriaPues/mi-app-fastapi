"""
Rutas de autenticacion: registro, login, logout.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.jwt import (
    hash_password, verify_password, create_access_token,
    validate_password_strength, get_current_user
)
from app.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request=request, name="auth/login.html", context={"error": None})


@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = get_database()
    user = await db.users.find_one({"username": username.strip().lower()})

    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(request=request, name="auth/login.html",
            context={"error": "Usuario o contrasena incorrectos."}, status_code=401)

    if not user.get("is_active", True):
        return templates.TemplateResponse(request=request, name="auth/login.html",
            context={"error": "Tu cuenta esta bloqueada. Contacta al administrador."}, status_code=403)

    token = create_access_token({"sub": user["username"]})
    redirect = RedirectResponse("/", status_code=302)
    redirect.set_cookie(key="access_token", value=token, httponly=True, max_age=60*60*24*7, samesite="lax")
    return redirect


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request=request, name="auth/register.html", context={"error": None})


@router.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    db = get_database()
    username = username.strip().lower()

    if len(username) < 3 or len(username) > 30:
        return templates.TemplateResponse(request=request, name="auth/register.html",
            context={"error": "El nombre de usuario debe tener entre 3 y 30 caracteres."}, status_code=400)

    if password != confirm_password:
        return templates.TemplateResponse(request=request, name="auth/register.html",
            context={"error": "Las contrasenas no coinciden."}, status_code=400)

    if not validate_password_strength(password):
        return templates.TemplateResponse(request=request, name="auth/register.html",
            context={"error": "La contrasena debe tener al menos 8 caracteres, una letra y un numero."}, status_code=400)

    existing = await db.users.find_one({"username": username})
    if existing:
        return templates.TemplateResponse(request=request, name="auth/register.html",
            context={"error": "Ese nombre de usuario ya esta en uso."}, status_code=400)

    new_user = {
        "username": username,
        "password_hash": hash_password(password),
        "role": "user",
        "is_active": True,
        "created_at": datetime.utcnow(),
    }
    await db.users.insert_one(new_user)

    token = create_access_token({"sub": username})
    redirect = RedirectResponse("/", status_code=302)
    redirect.set_cookie(key="access_token", value=token, httponly=True, max_age=60*60*24*7, samesite="lax")
    return redirect


@router.get("/logout")
async def logout():
    redirect = RedirectResponse("/login", status_code=302)
    redirect.delete_cookie("access_token")
    return redirect

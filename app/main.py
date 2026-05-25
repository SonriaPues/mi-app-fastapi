"""
Punto de entrada principal de la aplicacion FastAPI.
Registra routers, gestiona eventos de inicio/cierre y configura errores.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.database import connect_db, close_db
from app.routes import auth, books, admin, api
from app.auth.jwt import get_current_user

# Configuracion de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida: conecta a MongoDB al iniciar y cierra al terminar."""
    await connect_db()
    yield
    await close_db()


settings = get_settings()

app = FastAPI(
    title="Book Hub",
    description="Catalogo colaborativo de libros",
    version="1.0.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
    lifespan=lifespan,
)

# Archivos estaticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Registrar routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(admin.router)
app.include_router(api.router)


# Manejadores de errores globales
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    user = await get_current_user(request)
    return templates.TemplateResponse(
        request=request,
        name="errors/404.html",
        context={"user": user},
        status_code=404,
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name="errors/500.html",
        context={"user": None},
        status_code=500,
    )


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    user = await get_current_user(request)
    return templates.TemplateResponse(
        request=request,
        name="errors/403.html",
        context={"user": user},
        status_code=403,
    )

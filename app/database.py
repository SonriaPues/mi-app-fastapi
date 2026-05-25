"""
Gestión de la conexión a MongoDB Atlas con motor (async).
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings

logger = logging.getLogger(__name__)

# Cliente global de Motor
_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """Abre la conexión a MongoDB Atlas."""
    global _client, _db
    settings = get_settings()
    logger.info("Conectando a MongoDB Atlas...")
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _db = _client[settings.database_name]

    # Crear índices
    await _db.users.create_index("username", unique=True)
    await _db.favorites.create_index(
        [("user_id", 1), ("book_id", 1)], unique=True
    )
    await _db.reviews.create_index([("user_id", 1), ("book_id", 1)])
    await _db.books.create_index([("title", "text"), ("author", "text")])
    logger.info("Conexión establecida y índices creados.")


async def close_db() -> None:
    """Cierra la conexión a MongoDB Atlas."""
    global _client
    if _client:
        _client.close()
        logger.info("Conexión a MongoDB cerrada.")


def get_database() -> AsyncIOMotorDatabase:
    """Retorna la instancia de base de datos activa."""
    if _db is None:
        raise RuntimeError("Base de datos no inicializada. Llama a connect_db() primero.")
    return _db

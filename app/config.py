"""
Configuración central de la aplicación.
Lee las variables de entorno desde el archivo .env
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Base de datos
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "bookhub"

    # JWT
    jwt_secret_key: str = "cambiar-por-clave-secreta"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7

    # Admin inicial
    admin_username: str = "admin"
    admin_password: str = "Admin123456"

    # Entorno
    environment: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Retorna la instancia singleton de configuración."""
    return Settings()

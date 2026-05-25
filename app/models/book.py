"""
Modelos Pydantic para la colección 'books'.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BookInDB(BaseModel):
    """Modelo interno completo de un libro."""
    id: Optional[str] = None
    title: str
    author: str
    description: str = ""
    cover_url: str = ""
    external_link: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None    # user_id del admin que lo creó


class BookCreate(BaseModel):
    """Datos para crear un libro (validación de entrada)."""
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=150)
    description: str = Field(default="", max_length=2000)
    cover_url: str = Field(default="")
    external_link: str = Field(default="")


class BookUpdate(BaseModel):
    """Datos opcionales para actualizar un libro."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    cover_url: Optional[str] = None
    external_link: Optional[str] = None

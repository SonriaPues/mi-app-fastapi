"""
Modelos Pydantic para colecciones 'favorites' y 'reviews'.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ──────────────────────────────────────────
# Favoritos
# ──────────────────────────────────────────

class FavoriteInDB(BaseModel):
    """Registro de favorito en base de datos."""
    user_id: str
    book_id: str
    added_at: datetime = Field(default_factory=datetime.utcnow)


# ──────────────────────────────────────────
# Reseñas
# ──────────────────────────────────────────

class ReviewInDB(BaseModel):
    """Modelo interno completo de una reseña."""
    id: Optional[str] = None
    user_id: str
    book_id: str
    rating: int = Field(..., ge=1, le=5)    # 1 a 5 estrellas
    comment: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewCreate(BaseModel):
    """Datos para crear/editar una reseña."""
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(default="", max_length=1000)

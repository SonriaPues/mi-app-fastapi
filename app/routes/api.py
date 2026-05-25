"""
API endpoints para favoritos y reseñas (JSON).
Prefijo: /api/v1/
"""
import logging
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.jwt import require_auth
from app.database import get_database
from app.models.review import ReviewCreate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["api"])


# ──────────────────────────────────────────
# Favoritos
# ──────────────────────────────────────────

@router.post("/books/{book_id}/favorite")
async def toggle_favorite(book_id: str, request: Request, user=Depends(require_auth)):
    """Agrega o quita un libro de favoritos (toggle)."""
    db = get_database()

    # Verificar que el libro existe
    try:
        oid = ObjectId(book_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")
    book = await db.books.find_one({"_id": oid})
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    user_id = str(user["_id"])
    existing = await db.favorites.find_one({"user_id": user_id, "book_id": book_id})

    if existing:
        await db.favorites.delete_one({"user_id": user_id, "book_id": book_id})
        return {"action": "removed", "message": "Libro eliminado de favoritos."}
    else:
        await db.favorites.insert_one({
            "user_id": user_id,
            "book_id": book_id,
            "added_at": datetime.utcnow(),
        })
        return {"action": "added", "message": "Libro agregado a favoritos."}


# ──────────────────────────────────────────
# Reseñas
# ──────────────────────────────────────────

@router.post("/books/{book_id}/reviews")
async def create_review(book_id: str, review: ReviewCreate, request: Request, user=Depends(require_auth)):
    """Crea una nueva reseña para un libro."""
    db = get_database()

    # Verificar libro existente
    try:
        oid = ObjectId(book_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")
    if not await db.books.find_one({"_id": oid}):
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    user_id = str(user["_id"])

    # El usuario solo puede tener una reseña por libro
    existing = await db.reviews.find_one({"user_id": user_id, "book_id": book_id})
    if existing:
        raise HTTPException(status_code=400, detail="Ya escribiste una reseña para este libro. Puedes editarla.")

    new_review = {
        "user_id": user_id,
        "book_id": book_id,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": datetime.utcnow(),
    }
    result = await db.reviews.insert_one(new_review)
    return {"id": str(result.inserted_id), "message": "Reseña creada exitosamente."}


@router.put("/reviews/{review_id}")
async def update_review(review_id: str, review: ReviewCreate, request: Request, user=Depends(require_auth)):
    """Actualiza una reseña propia."""
    db = get_database()
    user_id = str(user["_id"])

    try:
        oid = ObjectId(review_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Reseña no encontrada.")

    existing = await db.reviews.find_one({"_id": oid, "user_id": user_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Reseña no encontrada o no tienes permiso para editarla.")

    await db.reviews.update_one(
        {"_id": oid},
        {"$set": {"rating": review.rating, "comment": review.comment}}
    )
    return {"message": "Reseña actualizada exitosamente."}


@router.delete("/reviews/{review_id}")
async def delete_review(review_id: str, request: Request, user=Depends(require_auth)):
    """Elimina una reseña propia (o cualquiera si es admin)."""
    db = get_database()
    user_id = str(user["_id"])

    try:
        oid = ObjectId(review_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Reseña no encontrada.")

    # Admin puede eliminar cualquier reseña; usuario solo las propias
    query = {"_id": oid}
    if user.get("role") != "admin":
        query["user_id"] = user_id

    result = await db.reviews.delete_one(query)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reseña no encontrada o no tienes permiso para eliminarla.")

    return {"message": "Reseña eliminada."}

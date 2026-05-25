"""
Rutas HTML para el catalogo de libros, detalle, busqueda y favoritos.
"""
import logging
from bson import ObjectId
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth.jwt import get_current_user, require_auth
from app.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(tags=["books"])
templates = Jinja2Templates(directory="app/templates")


def book_doc_to_dict(doc: dict) -> dict:
    doc["id"] = str(doc["_id"])
    return doc


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, q: str = "", page: int = 1):
    user = await get_current_user(request)
    db = get_database()
    page_size = 12
    skip = (page - 1) * page_size

    query = {}
    if q:
        query = {"$text": {"$search": q}}

    total = await db.books.count_documents(query)
    cursor = db.books.find(query).sort("title", 1).skip(skip).limit(page_size)
    books = [book_doc_to_dict(b) async for b in cursor]

    fav_ids = set()
    if user:
        favs = db.favorites.find({"user_id": str(user["_id"])})
        async for fav in favs:
            fav_ids.add(str(fav["book_id"]))

    total_pages = (total + page_size - 1) // page_size

    return templates.TemplateResponse(request=request, name="books/catalog.html", context={
        "user": user, "books": books, "fav_ids": fav_ids,
        "query": q, "page": page, "total_pages": total_pages, "total": total,
    })


@router.get("/books/{book_id}", response_class=HTMLResponse)
async def book_detail(request: Request, book_id: str):
    user = await get_current_user(request)
    db = get_database()

    try:
        oid = ObjectId(book_id)
    except Exception:
        return templates.TemplateResponse(request=request, name="errors/404.html", context={"user": user}, status_code=404)

    book = await db.books.find_one({"_id": oid})
    if not book:
        return templates.TemplateResponse(request=request, name="errors/404.html", context={"user": user}, status_code=404)

    book = book_doc_to_dict(book)

    reviews_cursor = db.reviews.find({"book_id": book_id}).sort("created_at", -1)
    reviews = []
    async for rev in reviews_cursor:
        rev["id"] = str(rev["_id"])
        author = await db.users.find_one({"_id": ObjectId(rev["user_id"])})
        rev["username"] = author["username"] if author else "Usuario"
        reviews.append(rev)

    avg_rating = 0
    if reviews:
        avg_rating = round(sum(r["rating"] for r in reviews) / len(reviews), 1)

    is_fav = False
    user_review = None
    if user:
        fav = await db.favorites.find_one({"user_id": str(user["_id"]), "book_id": book_id})
        is_fav = fav is not None
        ur = await db.reviews.find_one({"user_id": str(user["_id"]), "book_id": book_id})
        if ur:
            ur["id"] = str(ur["_id"])
            user_review = ur

    return templates.TemplateResponse(request=request, name="books/detail.html", context={
        "user": user, "book": book, "reviews": reviews,
        "avg_rating": avg_rating, "is_fav": is_fav, "user_review": user_review,
    })


@router.get("/mis-favoritos", response_class=HTMLResponse)
async def my_favorites(request: Request, user=Depends(require_auth)):
    db = get_database()
    favs_cursor = db.favorites.find({"user_id": str(user["_id"])}).sort("added_at", -1)
    books = []
    async for fav in favs_cursor:
        book = await db.books.find_one({"_id": ObjectId(fav["book_id"])})
        if book:
            books.append(book_doc_to_dict(book))

    return templates.TemplateResponse(request=request, name="books/favorites.html", context={
        "user": user, "books": books,
    })

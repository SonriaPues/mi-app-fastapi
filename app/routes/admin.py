"""
Rutas del panel de administracion.
Solo accesibles para usuarios con rol 'admin'.
"""
import logging
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.jwt import require_admin
from app.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


def book_doc_to_dict(doc):
    doc["id"] = str(doc["_id"])
    return doc

def user_doc_to_dict(doc):
    doc["id"] = str(doc["_id"])
    return doc


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request, user=Depends(require_admin)):
    db = get_database()
    total_books = await db.books.count_documents({})
    total_users = await db.users.count_documents({})
    total_reviews = await db.reviews.count_documents({})
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users = await db.users.count_documents({"created_at": {"$gte": week_ago}})

    pipeline = [
        {"$group": {"_id": "$book_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1},
    ]
    top_fav = None
    async for doc in db.favorites.aggregate(pipeline):
        book = await db.books.find_one({"_id": ObjectId(doc["_id"])})
        if book:
            top_fav = {"title": book["title"], "author": book["author"], "count": doc["count"]}

    return templates.TemplateResponse(request=request, name="admin/dashboard.html", context={
        "user": user,
        "stats": {"total_books": total_books, "total_users": total_users,
                  "total_reviews": total_reviews, "new_users": new_users, "top_fav": top_fav},
    })


@router.get("/books", response_class=HTMLResponse)
async def admin_books(request: Request, user=Depends(require_admin)):
    db = get_database()
    cursor = db.books.find({}).sort("title", 1)
    books = [book_doc_to_dict(b) async for b in cursor]
    return templates.TemplateResponse(request=request, name="admin/books.html", context={
        "user": user, "books": books, "error": None, "success": None,
    })


@router.post("/books/create")
async def create_book(request: Request, user=Depends(require_admin),
    title: str = Form(...), author: str = Form(...), description: str = Form(""),
    cover_url: str = Form(""), external_link: str = Form("")):
    db = get_database()
    await db.books.insert_one({
        "title": title.strip(), "author": author.strip(), "description": description.strip(),
        "cover_url": cover_url.strip(), "external_link": external_link.strip(),
        "created_at": datetime.utcnow(), "created_by": str(user["_id"]),
    })
    return RedirectResponse("/admin/books?success=Libro+creado+exitosamente", status_code=302)


@router.get("/books/{book_id}/edit", response_class=HTMLResponse)
async def edit_book_page(request: Request, book_id: str, user=Depends(require_admin)):
    db = get_database()
    book = await db.books.find_one({"_id": ObjectId(book_id)})
    if not book:
        return RedirectResponse("/admin/books", status_code=302)
    book = book_doc_to_dict(book)
    return templates.TemplateResponse(request=request, name="admin/edit_book.html", context={
        "user": user, "book": book, "error": None,
    })


@router.post("/books/{book_id}/edit")
async def edit_book(request: Request, book_id: str, user=Depends(require_admin),
    title: str = Form(...), author: str = Form(...), description: str = Form(""),
    cover_url: str = Form(""), external_link: str = Form("")):
    db = get_database()
    await db.books.update_one({"_id": ObjectId(book_id)}, {"$set": {
        "title": title.strip(), "author": author.strip(), "description": description.strip(),
        "cover_url": cover_url.strip(), "external_link": external_link.strip(),
    }})
    return RedirectResponse("/admin/books?success=Libro+actualizado+exitosamente", status_code=302)


@router.post("/books/{book_id}/delete")
async def delete_book(request: Request, book_id: str, user=Depends(require_admin)):
    db = get_database()
    await db.books.delete_one({"_id": ObjectId(book_id)})
    await db.reviews.delete_many({"book_id": book_id})
    await db.favorites.delete_many({"book_id": book_id})
    return RedirectResponse("/admin/books?success=Libro+eliminado", status_code=302)


@router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, user=Depends(require_admin)):
    db = get_database()
    cursor = db.users.find({}).sort("created_at", -1)
    users = [user_doc_to_dict(u) async for u in cursor]
    return templates.TemplateResponse(request=request, name="admin/users.html", context={
        "user": user, "users": users,
    })


@router.post("/users/{target_id}/toggle-active")
async def toggle_user_active(request: Request, target_id: str, user=Depends(require_admin)):
    db = get_database()
    if target_id == str(user["_id"]):
        return RedirectResponse("/admin/users?error=No+puedes+bloquearte+a+ti+mismo", status_code=302)
    target = await db.users.find_one({"_id": ObjectId(target_id)})
    if not target:
        return RedirectResponse("/admin/users", status_code=302)
    new_status = not target.get("is_active", True)
    await db.users.update_one({"_id": ObjectId(target_id)}, {"$set": {"is_active": new_status}})
    action = "desbloqueado" if new_status else "bloqueado"
    return RedirectResponse(f"/admin/users?success=Usuario+{action}", status_code=302)


@router.post("/users/{target_id}/toggle-role")
async def toggle_user_role(request: Request, target_id: str, user=Depends(require_admin)):
    db = get_database()
    if target_id == str(user["_id"]):
        return RedirectResponse("/admin/users?error=No+puedes+cambiar+tu+propio+rol", status_code=302)
    target = await db.users.find_one({"_id": ObjectId(target_id)})
    if not target:
        return RedirectResponse("/admin/users", status_code=302)
    new_role = "admin" if target.get("role") == "user" else "user"
    await db.users.update_one({"_id": ObjectId(target_id)}, {"$set": {"role": new_role}})
    return RedirectResponse(f"/admin/users?success=Rol+actualizado+a+{new_role}", status_code=302)

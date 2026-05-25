"""
Script de seed: crea el admin inicial e inserta los 20 libros si la coleccion esta vacia.
Uso: python scripts/seed_database.py
"""
import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Agregar el directorio raiz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings
from app.auth.jwt import hash_password


async def seed():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]

    print("[*] Conectando a MongoDB...")

    # 1. Crear usuario admin si no existe
    admin = await db.users.find_one({"username": settings.admin_username})
    if not admin:
        await db.users.insert_one({
            "username": settings.admin_username,
            "password_hash": hash_password(settings.admin_password),
            "role": "admin",
            "is_active": True,
            "created_at": datetime.utcnow(),
        })
        print(f"[OK] Admin '{settings.admin_username}' creado.")
    else:
        print(f"[i] Admin '{settings.admin_username}' ya existe.")

    # 2. Insertar libros si la coleccion esta vacia
    count = await db.books.count_documents({})
    if count == 0:
        books_file = Path(__file__).parent / "seed_books.json"
        with open(books_file, "r", encoding="utf-8") as f:
            books = json.load(f)
        for book in books:
            book["created_at"] = datetime.utcnow()
            book["created_by"] = "seed"
        await db.books.insert_many(books)
        print(f"[OK] {len(books)} libros insertados.")
    else:
        print(f"[i] Ya hay {count} libros en la BD. No se insertaron duplicados.")

    # 3. Crear indices
    await db.users.create_index("username", unique=True)
    await db.favorites.create_index([("user_id", 1), ("book_id", 1)], unique=True)
    await db.books.create_index([("title", "text"), ("author", "text")])
    print("[OK] Indices creados.")

    client.close()
    print("[OK] Seed completado exitosamente.")


if __name__ == "__main__":
    asyncio.run(seed())

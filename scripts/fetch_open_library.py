"""
Script opcional para popular mas libros desde Open Library.
Uso: python scripts/fetch_open_library.py
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

API_URL = "https://openlibrary.org/search.json"
SUBJECTS = ["classic_literature", "fiction", "latin_american_literature"]


async def fetch_books():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]
    added = 0

    async with httpx.AsyncClient(timeout=30) as http:
        for subject in SUBJECTS:
            print(f"[*] Buscando: {subject}...")
            try:
                res = await http.get(API_URL, params={"subject": subject, "limit": 10, "language": "spa"})
                res.raise_for_status()
                data = res.json()
            except Exception as e:
                print(f"  [!] Error: {e}")
                continue

            for doc in data.get("docs", []):
                title = doc.get("title", "").strip()
                author = ", ".join(doc.get("author_name", ["Desconocido"]))
                if not title:
                    continue
                exists = await db.books.find_one({"title": title, "author": author})
                if exists:
                    continue
                cover_id = doc.get("cover_i")
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else ""
                first_sentence = doc.get("first_sentence", "")
                if isinstance(first_sentence, list) and first_sentence:
                    first_sentence = first_sentence[0]
                elif isinstance(first_sentence, dict):
                    first_sentence = first_sentence.get("value", "")
                elif not isinstance(first_sentence, str):
                    first_sentence = ""

                await db.books.insert_one({
                    "title": title,
                    "author": author,
                    "description": str(first_sentence)[:500],
                    "cover_url": cover_url,
                    "external_link": f"https://openlibrary.org{doc['key']}" if doc.get("key") else "",
                    "created_at": datetime.utcnow(),
                    "created_by": "open_library_import",
                })
                added += 1
                print(f"  [+] {title.encode('ascii', 'replace').decode()} - {author.encode('ascii', 'replace').decode()}")
            # Rate limiting
            await asyncio.sleep(1)

    client.close()
    print(f"[OK] {added} libros nuevos importados.")

if __name__ == "__main__":
    asyncio.run(fetch_books())

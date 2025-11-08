import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Movie

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Flix backend running"}

# Helper to serialize Mongo documents

def serialize_movie(doc: dict) -> dict:
    if not doc:
        return {}
    return {
        "id": str(doc.get("_id")),
        "title": doc.get("title"),
        "image": doc.get("image"),
        "category": doc.get("category"),
        "description": doc.get("description"),
        "year": doc.get("year"),
        "rating": doc.get("rating"),
    }

# Seed endpoint (idempotent): insert a small catalogue if empty
@app.post("/api/seed")
async def seed_movies():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    existing = db["movie"].count_documents({})
    if existing > 0:
        return {"status": "ok", "inserted": 0, "message": "Movies already seeded"}

    sample_movies = [
        {
            "title": "Inception",
            "image": "https://image.tmdb.org/t/p/w780/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
            "category": "Popular on FLIX",
            "description": "A thief who steals corporate secrets through dream-sharing tech.",
            "year": 2010,
            "rating": 8.8,
        },
        {
            "title": "Interstellar",
            "image": "https://image.tmdb.org/t/p/w780/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg",
            "category": "Trending Now",
            "description": "A team travels through a wormhole in search of a new home for mankind.",
            "year": 2014,
            "rating": 8.6,
        },
        {
            "title": "The Dark Knight",
            "image": "https://image.tmdb.org/t/p/w780/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
            "category": "Top Picks for You",
            "description": "Batman faces the Joker, a criminal mastermind.",
            "year": 2008,
            "rating": 9.0,
        },
        {
            "title": "Dune",
            "image": "https://image.tmdb.org/t/p/w780/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",
            "category": "Because you watched Sci‑Fi",
            "description": "Paul Atreides must travel to the most dangerous planet in the universe.",
            "year": 2021,
            "rating": 8.2,
        },
        {
            "title": "Joker",
            "image": "https://image.tmdb.org/t/p/w780/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg",
            "category": "Popular on FLIX",
            "description": "The origin story of the iconic villain.",
            "year": 2019,
            "rating": 8.4,
        },
        {
            "title": "Spider‑Verse",
            "image": "https://image.tmdb.org/t/p/w780/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg",
            "category": "Trending Now",
            "description": "Miles Morales returns for the next chapter of the Spider‑Verse saga.",
            "year": 2023,
            "rating": 8.7,
        },
        {
            "title": "Oppenheimer",
            "image": "https://image.tmdb.org/t/p/w780/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
            "category": "Top Picks for You",
            "description": "The story of J. Robert Oppenheimer and the atomic bomb.",
            "year": 2023,
            "rating": 8.5,
        },
        {
            "title": "Barbie",
            "image": "https://image.tmdb.org/t/p/w780/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg",
            "category": "Because you watched Sci‑Fi",
            "description": "Barbie and Ken's adventures in the real world.",
            "year": 2023,
            "rating": 7.2,
        },
        {
            "title": "Avatar: The Way of Water",
            "image": "https://image.tmdb.org/t/p/w780/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg",
            "category": "Popular on FLIX",
            "description": "Jake Sully lives with his newfound family on Pandora.",
            "year": 2022,
            "rating": 7.6,
        },
        {
            "title": "John Wick 4",
            "image": "https://image.tmdb.org/t/p/w780/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg",
            "category": "Trending Now",
            "description": "John Wick uncovers a path to defeating The High Table.",
            "year": 2023,
            "rating": 7.9,
        },
    ]

    inserted = 0
    for m in sample_movies:
        create_document("movie", m)
        inserted += 1

    return {"status": "ok", "inserted": inserted}

# Public API: group movies by category for rows
@app.get("/api/rows")
async def get_rows():
    try:
        docs = get_documents("movie")
    except Exception:
        # If DB not set, return an empty dataset so frontend still works
        docs = []
    movies = [serialize_movie(d) for d in docs]

    rows = {}
    for m in movies:
        cat = m.get("category") or "Featured"
        rows.setdefault(cat, []).append(m)

    # Fall back to sample rows if database empty
    if not rows:
        fallback = {
            "Popular on FLIX": [
                {
                    "id": "1",
                    "title": "Inception",
                    "image": "https://image.tmdb.org/t/p/w780/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
                },
                {
                    "id": "2",
                    "title": "Interstellar",
                    "image": "https://image.tmdb.org/t/p/w780/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg",
                },
            ],
            "Trending Now": [
                {
                    "id": "3",
                    "title": "The Dark Knight",
                    "image": "https://image.tmdb.org/t/p/w780/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
                },
                {
                    "id": "4",
                    "title": "Dune",
                    "image": "https://image.tmdb.org/t/p/w780/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",
                },
            ],
            "Top Picks for You": [
                {
                    "id": "5",
                    "title": "Joker",
                    "image": "https://image.tmdb.org/t/p/w780/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg",
                },
            ],
            "Because you watched Sci‑Fi": [
                {
                    "id": "6",
                    "title": "Spider‑Verse",
                    "image": "https://image.tmdb.org/t/p/w780/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg",
                },
            ],
        }
        return fallback

    return rows

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

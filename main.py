import os
from typing import List, Any, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Project, Submission

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
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Mongo document to JSON-serializable dict"""
    if not doc:
        return {}
    d = dict(doc)
    _id = d.pop("_id", None)
    if _id is not None:
        d["id"] = str(_id)
    # Convert datetime fields to isoformat if present
    for k in ("created_at", "updated_at"):
        if k in d and hasattr(d[k], "isoformat"):
            d[k] = d[k].isoformat()
    return d


@app.get("/api/projects")
def list_projects(limit: int = 24):
    try:
        items = get_documents("project", {}, limit)
        return {"items": [_serialize(i) for i in items]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/submissions")
def list_submissions(limit: int = 24):
    try:
        items = get_documents("submission", {}, limit)
        return {"items": [_serialize(i) for i in items]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/portfolio")
def combined_portfolio(limit: int = 30):
    """Return a combined list of curated projects and user submissions"""
    try:
        projects = get_documents("project", {}, limit)
        submissions = get_documents("submission", {}, limit)
        # Normalize into a common shape for the frontend
        normalized: List[Dict[str, Any]] = []
        for p in projects:
            d = _serialize(p)
            normalized.append({
                "id": d.get("id"),
                "type": "project",
                "title": d.get("title"),
                "description": d.get("description"),
                "image": d.get("image_url"),
                "demo": d.get("demo_url"),
                "source": d.get("source_url"),
                "author": d.get("author"),
                "tags": d.get("tags", []),
            })
        for s in submissions:
            d = _serialize(s)
            normalized.append({
                "id": d.get("id"),
                "type": "submission",
                "title": d.get("title"),
                "description": d.get("description"),
                "image": d.get("thumbnail"),
                "demo": d.get("link"),
                "source": None,
                "author": d.get("name"),
                "tags": d.get("tags", []),
            })
        # Sort newest first by updated_at or created_at
        def sort_key(x):
            return x.get("updated_at") or x.get("created_at") or ""
        normalized = list(reversed(normalized))  # basic freshness order
        return {"items": normalized[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/submit")
def submit_portfolio(item: Submission):
    try:
        new_id = create_document("submission", item)
        return {"success": True, "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        # Database comes from imported module
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

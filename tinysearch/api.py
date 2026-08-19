from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .engine import SearchEngine
from .models import Document
from .storage import SQLiteStore


class DocumentInput(BaseModel):
    id: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1)
    url: str = ""
    metadata: dict = Field(default_factory=dict)


def create_app(db_path: str | Path | None = None) -> FastAPI:
    path = Path(db_path or os.getenv("TINYSEARCH_DB", "tinysearch.db"))
    engine = SQLiteStore(path).load() if path.exists() else SearchEngine()
    app = FastAPI(
        title="TinySearch Lab API",
        description="Explainable BM25 search over a compact inverted index.",
        version="1.0.0",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/stats")
    def stats() -> dict:
        return engine.stats()

    @app.get("/search")
    def search(q: str = Query(min_length=1), limit: int = Query(default=10, ge=1, le=50)) -> dict:
        results = engine.search(q, limit=limit)
        return {"query": q, "count": len(results), "results": [item.to_dict() for item in results]}

    @app.post("/documents", status_code=201)
    def add_document(payload: DocumentInput) -> dict:
        try:
            engine.add(Document(**payload.model_dump()))
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        SQLiteStore(path).save(engine)
        return {"indexed": payload.id, "stats": engine.stats()}

    app.state.engine = engine
    return app


app = create_app()


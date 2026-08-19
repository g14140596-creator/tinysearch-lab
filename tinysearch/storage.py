from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .engine import SearchEngine
from .models import Document


class SQLiteStore:
    """Transactional persistence for documents and the computed inverted index."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def save(self, engine: SearchEngine) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection:
            connection.executescript(
                """
                DROP TABLE IF EXISTS documents;
                DROP TABLE IF EXISTS postings;
                DROP TABLE IF EXISTS index_meta;
                CREATE TABLE documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    url TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    doc_length REAL NOT NULL
                );
                CREATE TABLE postings (
                    term TEXT NOT NULL,
                    doc_id TEXT NOT NULL,
                    frequency REAL NOT NULL,
                    PRIMARY KEY (term, doc_id),
                    FOREIGN KEY (doc_id) REFERENCES documents(id)
                );
                CREATE INDEX postings_by_term ON postings(term);
                CREATE TABLE index_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                """
            )
            connection.executemany(
                "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        doc.id,
                        doc.title,
                        doc.body,
                        doc.url,
                        json.dumps(doc.metadata, ensure_ascii=False),
                        engine.doc_lengths[doc.id],
                    )
                    for doc in engine.documents.values()
                ],
            )
            connection.executemany(
                "INSERT INTO postings VALUES (?, ?, ?)",
                [
                    (term, doc_id, frequency)
                    for term, posting in engine.postings.items()
                    for doc_id, frequency in posting.items()
                ],
            )
            connection.executemany(
                "INSERT INTO index_meta VALUES (?, ?)",
                [("k1", str(engine.k1)), ("b", str(engine.b)), ("title_boost", str(engine.title_boost))],
            )

    def load(self) -> SearchEngine:
        if not self.path.exists():
            raise FileNotFoundError(f"index database not found: {self.path}")
        with sqlite3.connect(self.path) as connection:
            meta = dict(connection.execute("SELECT key, value FROM index_meta"))
            engine = SearchEngine(
                k1=float(meta.get("k1", 1.5)),
                b=float(meta.get("b", 0.75)),
                title_boost=float(meta.get("title_boost", 2.0)),
            )
            for row in connection.execute(
                "SELECT id, title, body, url, metadata_json, doc_length FROM documents"
            ):
                doc = Document(row[0], row[1], row[2], row[3], json.loads(row[4]))
                engine.documents[doc.id] = doc
                engine.doc_lengths[doc.id] = row[5]
            for term, doc_id, frequency in connection.execute(
                "SELECT term, doc_id, frequency FROM postings"
            ):
                engine.postings[term][doc_id] = frequency
                engine.document_frequency[term] += 1
            return engine


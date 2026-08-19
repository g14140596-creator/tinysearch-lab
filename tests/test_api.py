from fastapi.testclient import TestClient

from tinysearch import Document, SearchEngine
from tinysearch.api import create_app
from tinysearch.storage import SQLiteStore


def test_search_api_returns_explainable_result(tmp_path):
    database = tmp_path / "index.db"
    engine = SearchEngine()
    engine.add(Document("ir", "Information Retrieval", "BM25 uses an inverted index."))
    SQLiteStore(database).save(engine)

    client = TestClient(create_app(database))
    assert client.get("/health").json() == {"status": "ok"}
    response = client.get("/search", params={"q": "BM25"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["results"][0]["document"]["id"] == "ir"
    assert payload["results"][0]["matched_terms"] == ["bm25"]

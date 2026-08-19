from tinysearch import Document, SearchEngine
from tinysearch.storage import SQLiteStore


def test_sqlite_round_trip_preserves_ranking(tmp_path):
    engine = SearchEngine()
    engine.build(
        [
            Document("a", "Search", "bm25 inverted index", metadata={"topic": "ir"}),
            Document("b", "Other", "network packets"),
        ]
    )
    store = SQLiteStore(tmp_path / "index.db")
    store.save(engine)
    restored = store.load()
    assert restored.search("bm25")[0].document.id == "a"
    assert restored.documents["a"].metadata == {"topic": "ir"}
    assert restored.stats() == engine.stats()


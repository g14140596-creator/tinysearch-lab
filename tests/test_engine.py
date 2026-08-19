from tinysearch import Document, SearchEngine


def test_bm25_ranks_title_match_first():
    engine = SearchEngine(title_boost=3.0)
    engine.build(
        [
            Document("1", "Inverted Index", "A compact data structure for search."),
            Document("2", "Databases", "A database may use an index for efficient retrieval."),
            Document("3", "Networks", "Packets travel through routers."),
        ]
    )
    results = engine.search("inverted index")
    assert results[0].document.id == "1"
    assert results[0].score > results[1].score
    assert results[0].matched_terms == ["index", "inverted"]


def test_empty_or_unknown_query_returns_no_results():
    engine = SearchEngine()
    engine.add(Document("1", "Example", "Known words only"))
    assert engine.search("") == []
    assert engine.search("unfindable") == []


def test_duplicate_ids_are_rejected():
    engine = SearchEngine()
    engine.add(Document("same", "First", "body"))
    try:
        engine.add(Document("same", "Second", "body"))
    except ValueError as exc:
        assert "duplicate document id" in str(exc)
    else:
        raise AssertionError("duplicate id was accepted")


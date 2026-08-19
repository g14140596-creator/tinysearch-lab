from tinysearch.tokenizer import tokenize


def test_tokenizer_normalizes_and_removes_stop_words():
    assert tokenize("The Python API and C++ engine") == ["python", "api", "c++", "engine"]


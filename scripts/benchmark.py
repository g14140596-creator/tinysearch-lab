from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tinysearch import Document, SearchEngine


def main() -> None:
    documents = [
        Document(str(i), f"Document {i}", f"python search engine inverted index term {i % 100}")
        for i in range(10_000)
    ]
    started = time.perf_counter()
    engine = SearchEngine()
    engine.build(documents)
    index_seconds = time.perf_counter() - started

    timings = []
    for _ in range(100):
        started = time.perf_counter()
        engine.search("python inverted index", limit=10)
        timings.append((time.perf_counter() - started) * 1000)

    print(f"documents: {len(documents):,}")
    print(f"index time: {index_seconds:.3f} s")
    print(f"median query latency: {statistics.median(timings):.3f} ms")
    print(f"p95 query latency: {sorted(timings)[94]:.3f} ms")


if __name__ == "__main__":
    main()

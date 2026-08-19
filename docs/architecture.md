# Architecture

TinySearch separates retrieval into five stages:

1. **Loading** discovers supported files and converts them into `Document` values.
2. **Analysis** normalizes text and removes a small stop-word set.
3. **Indexing** creates term-to-document postings and document statistics.
4. **Ranking** calculates BM25 scores with title boosting and term-level explanations.
5. **Serving** exposes the same engine through a CLI and FastAPI REST interface.

SQLite is a persistence boundary, not the ranking engine. The application loads
the compact index into memory so search remains simple and fast. This design is
appropriate for learning and small corpora; a distributed production engine
would shard postings, stream updates, and replicate data.

## Ranking formula

For query term `q` and document `D`:

```text
score(q, D) = IDF(q) * tf(q,D) * (k1 + 1)
                         -------------------------
                         tf(q,D) + k1(1-b+b|D|/avgdl)
```

Defaults are `k1=1.5`, `b=0.75`, and a `2.0x` title boost.


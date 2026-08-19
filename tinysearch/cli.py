from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import SearchEngine
from .loaders import load_directory
from .storage import SQLiteStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tinysearch", description="Index and search local text documents.")
    parser.add_argument("--db", default="tinysearch.db", help="SQLite index path")
    commands = parser.add_subparsers(dest="command", required=True)

    index = commands.add_parser("index", help="Build an index from a directory")
    index.add_argument("directory")

    search = commands.add_parser("search", help="Search the index")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--json", action="store_true")

    commands.add_parser("stats", help="Show index statistics")

    serve = commands.add_parser("serve", help="Run the REST API")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = SQLiteStore(Path(args.db))

    if args.command == "index":
        documents = load_directory(args.directory)
        engine = SearchEngine()
        engine.build(documents)
        store.save(engine)
        print(f"Indexed {len(documents)} documents into {args.db}")
        print(json.dumps(engine.stats(), indent=2))
        return 0

    if args.command == "serve":
        import os
        import uvicorn

        os.environ["TINYSEARCH_DB"] = args.db
        uvicorn.run("tinysearch.api:app", host=args.host, port=args.port, reload=False)
        return 0

    engine = store.load()
    if args.command == "stats":
        print(json.dumps(engine.stats(), indent=2))
        return 0

    results = engine.search(args.query, limit=args.limit)
    if args.json:
        print(json.dumps([result.to_dict() for result in results], indent=2, ensure_ascii=False))
    else:
        for position, result in enumerate(results, 1):
            print(f"{position}. {result.document.title}  score={result.score:.4f}")
            print(f"   {result.snippet}")
            print(f"   matched: {', '.join(result.matched_terms)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


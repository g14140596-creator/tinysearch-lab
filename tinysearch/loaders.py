from __future__ import annotations

import re
from pathlib import Path

from .models import Document

SUPPORTED_SUFFIXES = {".md", ".txt", ".html", ".htm"}


def load_directory(path: str | Path) -> list[Document]:
    root = Path(path)
    if not root.is_dir():
        raise NotADirectoryError(root)
    documents: list[Document] = []
    for file_path in sorted(root.rglob("*")):
        if file_path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        raw = file_path.read_text(encoding="utf-8")
        body = re.sub(r"<[^>]+>", " ", raw) if file_path.suffix.lower() in {".html", ".htm"} else raw
        title = _title_from_text(body, file_path.stem)
        documents.append(
            Document(
                id=file_path.relative_to(root).as_posix(),
                title=title,
                body=body,
                url=file_path.resolve().as_uri(),
                metadata={"source": "filesystem", "suffix": file_path.suffix.lower()},
            )
        )
    return documents


def _title_from_text(text: str, fallback: str) -> str:
    for line in text.splitlines():
        cleaned = line.lstrip("# ").strip()
        if cleaned:
            return cleaned[:120]
    return fallback.replace("-", " ").title()

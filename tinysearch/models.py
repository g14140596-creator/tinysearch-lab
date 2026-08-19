from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Document:
    id: str
    title: str
    body: str
    url: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SearchResult:
    document: Document
    score: float
    snippet: str
    matched_terms: list[str]
    term_scores: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "document": self.document.to_dict(),
            "score": round(self.score, 6),
            "snippet": self.snippet,
            "matched_terms": self.matched_terms,
            "term_scores": {key: round(value, 6) for key, value in self.term_scores.items()},
        }


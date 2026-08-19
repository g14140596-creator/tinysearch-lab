from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Iterable

from .models import Document, SearchResult
from .tokenizer import tokenize


class SearchEngine:
    """In-memory inverted index with BM25 relevance ranking."""

    def __init__(self, *, k1: float = 1.5, b: float = 0.75, title_boost: float = 2.0) -> None:
        self.k1 = k1
        self.b = b
        self.title_boost = title_boost
        self.documents: dict[str, Document] = {}
        self.postings: dict[str, dict[str, float]] = defaultdict(dict)
        self.doc_lengths: dict[str, float] = {}
        self.document_frequency: Counter[str] = Counter()

    @property
    def average_document_length(self) -> float:
        if not self.doc_lengths:
            return 0.0
        return sum(self.doc_lengths.values()) / len(self.doc_lengths)

    def build(self, documents: Iterable[Document]) -> None:
        self.documents.clear()
        self.postings.clear()
        self.doc_lengths.clear()
        self.document_frequency.clear()
        for document in documents:
            self.add(document)

    def add(self, document: Document) -> None:
        if document.id in self.documents:
            raise ValueError(f"duplicate document id: {document.id}")

        title_counts = Counter(tokenize(document.title))
        body_counts = Counter(tokenize(document.body))
        weighted_counts: Counter[str] = Counter(body_counts)
        for term, count in title_counts.items():
            weighted_counts[term] += count * self.title_boost

        self.documents[document.id] = document
        self.doc_lengths[document.id] = max(1.0, float(sum(weighted_counts.values())))
        for term, frequency in weighted_counts.items():
            self.postings[term][document.id] = float(frequency)
            self.document_frequency[term] += 1

    def search(self, query: str, *, limit: int = 10) -> list[SearchResult]:
        terms = list(dict.fromkeys(tokenize(query)))
        if not terms or not self.documents or limit <= 0:
            return []

        scores: defaultdict[str, float] = defaultdict(float)
        explanations: defaultdict[str, dict[str, float]] = defaultdict(dict)
        total_documents = len(self.documents)
        avgdl = self.average_document_length or 1.0

        for term in terms:
            posting = self.postings.get(term, {})
            df = self.document_frequency.get(term, 0)
            if not posting or not df:
                continue
            idf = math.log(1.0 + (total_documents - df + 0.5) / (df + 0.5))
            for doc_id, tf in posting.items():
                length_norm = self.k1 * (
                    1.0 - self.b + self.b * self.doc_lengths[doc_id] / avgdl
                )
                contribution = idf * (tf * (self.k1 + 1.0)) / (tf + length_norm)
                scores[doc_id] += contribution
                explanations[doc_id][term] = contribution

        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:limit]
        return [
            SearchResult(
                document=self.documents[doc_id],
                score=score,
                snippet=self._snippet(self.documents[doc_id].body, terms),
                matched_terms=sorted(explanations[doc_id]),
                term_scores=explanations[doc_id],
            )
            for doc_id, score in ranked
        ]

    def stats(self) -> dict[str, float | int]:
        return {
            "documents": len(self.documents),
            "unique_terms": len(self.postings),
            "postings": sum(len(items) for items in self.postings.values()),
            "average_document_length": round(self.average_document_length, 2),
        }

    @staticmethod
    def _snippet(body: str, terms: list[str], radius: int = 90) -> str:
        lowered = body.lower()
        positions = [lowered.find(term) for term in terms if lowered.find(term) >= 0]
        center = min(positions) if positions else 0
        start = max(0, center - radius)
        end = min(len(body), center + radius)
        text = " ".join(body[start:end].split())
        return f"{'…' if start else ''}{text}{'…' if end < len(body) else ''}"


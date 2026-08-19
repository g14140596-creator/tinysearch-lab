from __future__ import annotations

import re
from collections.abc import Iterable

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[+#.]{1,2}[a-z0-9]*)*", re.IGNORECASE)

DEFAULT_STOP_WORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "has", "in", "is", "it", "of", "on", "or", "that", "the", "to",
        "was", "were", "will", "with",
    }
)


def tokenize(text: str, stop_words: Iterable[str] = DEFAULT_STOP_WORDS) -> list[str]:
    """Normalize text into lowercase searchable terms."""
    blocked = set(stop_words)
    return [token.lower() for token in TOKEN_RE.findall(text) if token.lower() not in blocked]

"""TinySearch Lab: a compact information-retrieval engine."""

from .engine import SearchEngine
from .models import Document, SearchResult

__all__ = ["Document", "SearchEngine", "SearchResult"]
__version__ = "1.0.0"


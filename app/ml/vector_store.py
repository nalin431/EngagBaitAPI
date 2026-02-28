"""
Actian VectorAI DB integration (Phase 2b).

Actian VectorAI DB is "coming soon" — when SDK/API is available, implement:
- init_vector_store(): Connect via ACTIAN_* env vars
- upsert_examples(): Insert seed embeddings with metadata
- search_similar(): k-NN vector search

Until then, scorer falls back to in-memory centroid scoring (Phase 2a).
"""

import os
from typing import Any


def _actian_available() -> bool:
    """True if Actian VectorAI DB is configured (when SDK is available)."""
    return bool(os.environ.get("USE_ACTIAN", "").lower() == "true") and bool(
        os.environ.get("ACTIAN_API_KEY") or os.environ.get("ACTIAN_HOST")
    )


def init_vector_store() -> bool:
    """
    Connect to Actian VectorAI DB. Create collection/table for embeddings.
    Returns True if ready. When SDK unavailable, returns False.
    """
    if not _actian_available():
        return False
    # TODO: When Actian VectorAI DB SDK is released, implement connection
    # per https://www.actian.com/databases/vectorai-db/
    return False


def upsert_examples(
    embeddings: list[list[float]], labels: list[str], texts: list[str]
) -> bool:
    """
    Insert seed examples with embeddings and metadata into Actian.
    Returns True on success.
    """
    if not init_vector_store():
        return False
    # TODO: Implement when Actian SDK available
    return False


def search_similar(embedding: list[float], k: int = 5) -> list[dict[str, Any]]:
    """
    Return k nearest neighbors with labels.
    Format: [{"label": "bait"|"neutral", "text": "...", "distance": float}, ...]
    Returns empty list when Actian unavailable.
    """
    if not init_vector_store():
        return []
    # TODO: Implement when Actian SDK available
    return []

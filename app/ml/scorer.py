"""ML scorer: engagement_bait_score from seed embeddings."""

import json
import os
from pathlib import Path

from app.ml.embeddings import get_embedding


def _cosine_sim(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _mean_embedding(embeddings: list[list[float]]) -> list[float] | None:
    """Mean of embeddings (centroid)."""
    if not embeddings:
        return None
    n = len(embeddings)
    dim = len(embeddings[0])
    out = [0.0] * dim
    for emb in embeddings:
        for i, v in enumerate(emb):
            out[i] += v
    return [x / n for x in out]


_bait_centroid: list[float] | None = None
_neutral_centroid: list[float] | None = None
_initialized = False


def _ensure_centroids() -> bool:
    """Load seed examples, embed them, compute centroids. Returns True if ready."""
    global _bait_centroid, _neutral_centroid, _initialized
    if _initialized:
        return _bait_centroid is not None and _neutral_centroid is not None

    path = Path(__file__).resolve().parent.parent.parent / "data" / "seed_examples.json"
    if not path.exists():
        _initialized = True
        return False

    with path.open() as f:
        examples = json.load(f)

    bait_embs: list[list[float]] = []
    neutral_embs: list[list[float]] = []

    for ex in examples:
        text = ex.get("text", "")
        label = ex.get("label", "").lower()
        emb = get_embedding(text)
        if emb is None:
            _initialized = True
            return False
        if label == "bait":
            bait_embs.append(emb)
        elif label == "neutral":
            neutral_embs.append(emb)

    _bait_centroid = _mean_embedding(bait_embs)
    _neutral_centroid = _mean_embedding(neutral_embs)
    _initialized = True
    return _bait_centroid is not None and _neutral_centroid is not None


def _score_from_centroids(emb: list[float]) -> float:
    """Score from bait vs neutral centroid similarity."""
    if _bait_centroid is None or _neutral_centroid is None:
        return 0.0
    sim_bait = _cosine_sim(emb, _bait_centroid)
    sim_neutral = _cosine_sim(emb, _neutral_centroid)
    diff = sim_bait - sim_neutral
    score = (diff + 1) / 2
    return max(0.0, min(1.0, score))


def compute_engagement_bait_score(text: str) -> float | None:
    """
    Compute engagement_bait_score (0–1).
    When USE_ACTIAN=true and Actian available: k-NN from vector store.
    Else: centroid similarity (Phase 2a). Returns None if OpenAI unavailable.
    """
    emb = get_embedding(text)
    if emb is None:
        return None

    # Phase 2b: Actian VectorAI DB k-NN when available
    from app.ml.vector_store import search_similar
    neighbors = search_similar(emb, k=5)
    if neighbors:
        bait_count = sum(1 for n in neighbors if n.get("label") == "bait")
        return bait_count / len(neighbors)

    # Phase 2a: in-memory centroids
    if not _ensure_centroids():
        return None
    return _score_from_centroids(emb)

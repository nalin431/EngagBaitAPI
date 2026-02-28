"""ML layer: OpenAI embeddings and engagement bait scoring."""

from app.ml.embeddings import get_embedding
from app.ml.scorer import compute_engagement_bait_score

__all__ = ["get_embedding", "compute_engagement_bait_score"]

import os

from app.models import AnalyzeMeta, AnalyzeResponse

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


def analyze_text(text: str, ml: bool | None = None) -> AnalyzeResponse:
    """Analyze text and return heuristic metrics plus optional ML score."""
    from app.analyzers.arousal import analyze_arousal
    from app.analyzers.claim_volume import analyze_claim_volume
    from app.analyzers.narrative import analyze_counterargument_absence
    from app.analyzers.evidence import analyze_evidence
    from app.analyzers.urgency import analyze_urgency
    from app.analyzers.lexical_diversity import analyze_lexical_diversity

    openai_available = bool(os.environ.get("OPENAI_API_KEY", "").strip().startswith("sk-"))
    embeddings_requested = ml if ml is not None else openai_available
    embeddings_used = embeddings_requested and openai_available

    engagement_bait_score = None
    vector_backend = "none"
    if embeddings_used:
        from app.ml.scorer import compute_engagement_bait_result

        engagement_bait_score, vector_backend = compute_engagement_bait_result(text)

    return AnalyzeResponse(
        urgency_pressure=analyze_urgency(text),
        evidence_density=analyze_evidence(text),
        arousal_intensity=analyze_arousal(text),
        counterargument_absence=analyze_counterargument_absence(text),
        claim_volume_vs_depth=analyze_claim_volume(text),
        lexical_diversity=analyze_lexical_diversity(text),
        engagement_bait_score=engagement_bait_score,
        meta=AnalyzeMeta(
            embeddings_requested=embeddings_requested,
            embeddings_used=embeddings_used,
            openai_available=openai_available,
            vector_backend=vector_backend,
        ),
    )

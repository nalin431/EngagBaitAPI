import os

from app.models import AnalyzeMeta, AnalyzeResponse


def analyze_text(text: str, ml: bool | None = None) -> AnalyzeResponse:
    """Analyze text and return heuristic metrics plus optional ML score."""
    from app.analyzers.arousal import analyze_arousal
    from app.analyzers.claim_volume import analyze_claim_volume
    from app.analyzers.narrative import analyze_counterargument_absence
    from app.analyzers.evidence import analyze_evidence
    from app.analyzers.urgency import analyze_urgency

    openai_available = bool(os.environ.get("OPENAI_API_KEY", "").strip().startswith("sk-"))
    ml_requested = ml if ml is not None else openai_available
    ml_used = ml_requested and openai_available

    engagement_bait_score = None
    vector_backend = "none"
    if ml_used:
        from app.ml.scorer import compute_engagement_bait_result

        engagement_bait_score, vector_backend = compute_engagement_bait_result(text)

    return AnalyzeResponse(
        urgency_pressure=analyze_urgency(text),
        evidence_density=analyze_evidence(text),
        arousal_intensity=analyze_arousal(text),
        counterargument_absence=analyze_counterargument_absence(text),
        claim_volume_vs_depth=analyze_claim_volume(text),
        engagement_bait_score=engagement_bait_score,
        meta=AnalyzeMeta(
            ml_requested=ml_requested,
            ml_used=ml_used,
            openai_available=openai_available,
            vector_backend=vector_backend,
        ),
    )

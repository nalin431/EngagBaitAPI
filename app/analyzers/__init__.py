import os

from app.models import AnalyzeResponse


def analyze_text(text: str, ml: bool | None = None) -> AnalyzeResponse:
    """Analyze text and return all 5 metrics plus optional ML engagement_bait_score."""
    from app.analyzers.urgency import analyze_urgency
    from app.analyzers.evidence import analyze_evidence
    from app.analyzers.arousal import analyze_arousal
    from app.analyzers.narrative import analyze_narrative
    from app.analyzers.claim_volume import analyze_claim_volume

    has_openai = bool(os.environ.get("OPENAI_API_KEY", "").strip().startswith("sk-"))
    use_ml = ml if ml is not None else has_openai

    engagement_bait_score = None
    if use_ml and has_openai:
        from app.ml.scorer import compute_engagement_bait_score
        engagement_bait_score = compute_engagement_bait_score(text)

    return AnalyzeResponse(
        urgency_pressure=analyze_urgency(text),
        evidence_density=analyze_evidence(text),
        arousal_intensity=analyze_arousal(text),
        narrative_simplification=analyze_narrative(text),
        claim_volume_vs_depth=analyze_claim_volume(text),
        engagement_bait_score=engagement_bait_score,
    )

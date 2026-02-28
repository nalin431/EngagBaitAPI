from app.models import AnalyzeResponse


def analyze_text(text: str) -> AnalyzeResponse:
    """Analyze text and return all 7 metrics with sub-metric breakdowns."""
    # Stub: will be implemented when engines are wired
    from app.analyzers.urgency import analyze_urgency
    from app.analyzers.evidence import analyze_evidence
    from app.analyzers.overconfidence import analyze_overconfidence
    from app.analyzers.arousal import analyze_arousal
    from app.analyzers.ingroup import analyze_ingroup
    from app.analyzers.narrative import analyze_narrative
    from app.analyzers.claim_volume import analyze_claim_volume

    return AnalyzeResponse(
        urgency_pressure=analyze_urgency(text),
        evidence_density=analyze_evidence(text),
        overconfidence=analyze_overconfidence(text),
        arousal_intensity=analyze_arousal(text),
        ingroup_outgroup=analyze_ingroup(text),
        narrative_simplification=analyze_narrative(text),
        claim_volume_vs_depth=analyze_claim_volume(text),
    )

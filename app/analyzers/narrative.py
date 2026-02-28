from app.analyzers.base import clamp_score
from app.lexicons.loader import get_conditional_terms, get_tradeoff_terms
from app.models import MetricBreakdown

_TRADEOFF = get_tradeoff_terms() or {
    "however",
    "although",
    "trade-off",
    "tradeoff",
    "on the other hand",
}
_CONDITIONAL = get_conditional_terms() or {"if", "when", "unless", "depending on"}


def analyze_counterargument_absence(text: str) -> MetricBreakdown:
    t = text.lower()
    words = t.split()
    wc = len(words) or 1

    tradeoff = sum(1 for w in words if w.rstrip(".,;:!?") in _TRADEOFF)
    conditional = sum(1 for w in words if w.rstrip(".,;:!?") in _CONDITIONAL)

    s_tradeoff_absence = clamp_score(1 - tradeoff / max(1, wc / 30))
    s_conditional_absence = clamp_score(1 - conditional / max(1, wc / 25))
    score = (s_tradeoff_absence + s_conditional_absence) / 2

    return MetricBreakdown(
        score=round(clamp_score(score), 2),
        breakdown={
            "tradeoff_absence": round(s_tradeoff_absence, 2),
            "conditional_absence": round(s_conditional_absence, 2),
        },
    )

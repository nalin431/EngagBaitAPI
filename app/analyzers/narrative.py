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


def _count_markers(text: str, terms: frozenset[str]) -> int:
    token_hits: set[str] = set()
    phrase_hits: set[str] = set()
    tokens = {w.rstrip(".,;:!?") for w in text.split()}

    for term in terms:
        if " " in term:
            if term in text:
                phrase_hits.add(term)
        elif term in tokens:
            token_hits.add(term)

    return len(token_hits) + len(phrase_hits)


def analyze_counterargument_absence(text: str) -> MetricBreakdown:
    t = text.lower()
    wc = len(t.split()) or 1

    tradeoff = _count_markers(t, _TRADEOFF)
    conditional = _count_markers(t, _CONDITIONAL)

    s_tradeoff_absence = clamp_score(1 - tradeoff / max(1, wc / 20))
    s_conditional_absence = clamp_score(1 - conditional / max(1, wc / 18))
    score = (s_tradeoff_absence + s_conditional_absence) / 2

    return MetricBreakdown(
        score=round(clamp_score(score), 2),
        breakdown={
            "tradeoff_absence": round(s_tradeoff_absence, 2),
            "conditional_absence": round(s_conditional_absence, 2),
        },
    )

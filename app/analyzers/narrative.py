import re
from app.models import MetricBreakdown
from app.analyzers.base import clamp_score
from app.lexicons.loader import (
    get_binary_connectors,
    get_single_cause_markers,
    get_tradeoff_terms,
    get_conditional_terms,
)

_BINARY = get_binary_connectors() or {"either or", "either-or", "or else", "us versus them", "us vs them"}
_SINGLE_CAUSE = get_single_cause_markers() or {"the reason", "root cause", "the cause", "it's all"}
_TRADEOFF = get_tradeoff_terms() or {"however", "although", "trade-off", "tradeoff", "on the other hand"}
_CONDITIONAL = get_conditional_terms() or {"if", "when", "unless", "depending on"}


def _count_phrases(text: str, phrases: set[str]) -> int:
    t = text.lower()
    return sum(1 for p in phrases if p in t)


def analyze_narrative(text: str) -> MetricBreakdown:
    t = text.lower()
    words = t.split()
    wc = len(words) or 1

    binary = _count_phrases(t, _BINARY)
    single_cause = _count_phrases(t, _SINGLE_CAUSE)
    tradeoff = sum(1 for w in words if w.rstrip(".,;:!?") in _TRADEOFF)
    conditional = sum(1 for w in words if w.rstrip(".,;:!?") in _CONDITIONAL)

    s_binary = clamp_score(min(1, binary / 2))
    s_single = clamp_score(min(1, single_cause / 5))
    s_tradeoff_absence = clamp_score(1 - tradeoff / max(1, wc / 30))
    s_conditional_absence = clamp_score(1 - conditional / max(1, wc / 25))

    score = (s_binary + s_single + s_tradeoff_absence + s_conditional_absence) / 4
    return MetricBreakdown(
        score=round(clamp_score(score), 2),
        breakdown={
            "binary_connectors": round(s_binary, 2),
            "single_cause": round(s_single, 2),
            "tradeoff_absence": round(s_tradeoff_absence, 2),
            "conditional_absence": round(s_conditional_absence, 2),
        },
    )

import re
from app.models import MetricBreakdown
from app.analyzers.base import count_to_score, clamp_score
from app.lexicons.loader import get_urgency_terms

_TIME_PRESSURE = {
    "act now", "do it now", "hurry", "limited time", "last chance", "don't miss",
    "expires soon", "before it's too late", "urgency", "urgent", "immediately",
    "right now", "today only", "ends soon", "final hours", "countdown", "deadline",
    "now or never", "must act",
}
_SCARCITY = {
    "limited", "exclusive", "only a few left", "sold out", "almost gone",
    "last remaining", "one of a kind", "rare", "scarce", "first come first served",
    "supplies limited",
}
_FOMO = {
    "don't miss out", "you'll regret", "everyone else is", "join thousands",
    "see what others are missing", "be the first", "act before everyone else",
    "limited availability", "going fast", "running out",
}


def _count_phrases(text: str, phrases: set[str]) -> int:
    t = text.lower()
    return sum(1 for p in phrases if p in t)


def analyze_urgency(text: str) -> MetricBreakdown:
    t = text.lower()
    time_pressure = _count_phrases(t, _TIME_PRESSURE)
    scarcity = _count_phrases(t, _SCARCITY)
    fomo = _count_phrases(t, _FOMO)

    s_time = count_to_score(time_pressure, (1, 4))
    s_scarcity = count_to_score(scarcity, (1, 4))
    s_fomo = count_to_score(fomo, (1, 4))
    score = clamp_score((s_time + s_scarcity + s_fomo) / 3)
    return MetricBreakdown(
        score=round(score, 2),
        breakdown={"time_pressure": round(s_time, 2), "scarcity": round(s_scarcity, 2), "fomo": round(s_fomo, 2)},
    )

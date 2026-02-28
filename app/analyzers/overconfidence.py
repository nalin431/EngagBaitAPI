import re
from app.models import MetricBreakdown
from app.analyzers.base import count_to_score, clamp_score
from app.lexicons.loader import get_absolutist_terms, get_hedging_terms, get_strong_modal_terms

_ABSOLUTIST = get_absolutist_terms() or {"always", "never", "guaranteed", "definitely", "absolutely", "every", "everyone"}
_HEDGING = get_hedging_terms() or {"may", "might", "could", "possibly", "perhaps", "likely", "probably"}
_STRONG_MODALS = get_strong_modal_terms() or {"must", "will", "shall", "cannot", "can't", "won't", "have to"}
_PREDICTIVE = re.compile(r"\b(?:will|shall|going to)\s+\w+", re.I)
_PROBABILISTIC = re.compile(r"\b(?:likely|probably|perhaps|possibly|might)\b", re.I)


def _word_count(text: str) -> int:
    return len(text.split()) or 1


def analyze_overconfidence(text: str) -> MetricBreakdown:
    t = text.lower()
    words = t.split()
    wc = len(words) or 1

    absolutist = sum(1 for w in words if w.rstrip(".,;:!?") in _ABSOLUTIST)
    strong_modals = sum(1 for w in words if w.rstrip(".,;:!?") in _STRONG_MODALS)
    hedging = sum(1 for w in words if w.rstrip(".,;:!?") in _HEDGING)
    predictive = len(_PREDICTIVE.findall(text))
    probabilistic = len(_PROBABILISTIC.findall(text))

    s_absolutist = count_to_score(absolutist, (2, 6))
    s_strong_modals = count_to_score(strong_modals, (1, 4))
    s_hedging_absence = clamp_score(1 - hedging / max(1, wc * 0.05))
    s_predictive = clamp_score(predictive / max(1, wc / 20)) if predictive > 0 and probabilistic == 0 else clamp_score(predictive / max(2, wc / 15))

    score = (s_absolutist + s_strong_modals + s_hedging_absence + s_predictive) / 4
    return MetricBreakdown(
        score=round(clamp_score(score), 2),
        breakdown={
            "absolutist": round(s_absolutist, 2),
            "strong_modals": round(s_strong_modals, 2),
            "hedging_absence": round(s_hedging_absence, 2),
            "predictive_unqualified": round(s_predictive, 2),
        },
    )

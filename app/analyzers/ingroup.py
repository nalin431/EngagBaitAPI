import re
from app.models import MetricBreakdown
from app.analyzers.base import count_to_score, clamp_score
from app.lexicons.loader import get_ingroup_terms

_US_THEM = {"we", "they", "us", "them", "our", "their"}
_INGROUP = get_ingroup_terms()


def analyze_ingroup(text: str) -> MetricBreakdown:
    t = text.lower()
    words = t.split()
    wc = len(words) or 1

    us_them = sum(1 for w in words if w.rstrip(".,;:!?") in _US_THEM)
    tribal = sum(1 for w in words if w.rstrip(".,;:!?") in _INGROUP and w.rstrip(".,;:!?") not in _US_THEM)

    s_us_them = count_to_score(us_them, (2, 8))
    s_tribal = count_to_score(tribal, (1, 5))
    score = (s_us_them + s_tribal) / 2
    return MetricBreakdown(
        score=round(clamp_score(score), 2),
        breakdown={"us_them_markers": round(s_us_them, 2), "tribal_language": round(s_tribal, 2)},
    )

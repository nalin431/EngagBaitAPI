import re
from app.models import MetricBreakdown
from app.analyzers.base import clamp_score

_CLAIM_INDICATORS = re.compile(
    r"\b(?:is|are|was|were|will|must|should|always|never|proves?|shows?|means?|causes?|results?\s+in)\b",
    re.I,
)


def analyze_claim_volume(text: str) -> MetricBreakdown:
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    words = text.split()
    wc = len(words) or 1
    sc = len(sentences) or 1

    claims = sum(1 for s in sentences if _CLAIM_INDICATORS.search(s))
    claims_per_word = claims / wc
    avg_sent_len = sum(len(s.split()) for s in sentences) / sc
    has_because = "because" in text.lower() or "since" in text.lower()
    explanation_depth = clamp_score(min(1, avg_sent_len / 25) * (0.7 if has_because else 0.3))

    # High claims_per_word + low explanation_depth = engagement bait
    s_claims = clamp_score(min(1, claims_per_word * 30))
    s_depth_inv = clamp_score(1 - explanation_depth)
    score = (s_claims + s_depth_inv) / 2
    return MetricBreakdown(
        score=round(clamp_score(score), 2),
        breakdown={"claims_per_word": round(s_claims, 2), "explanation_depth": round(1 - s_depth_inv, 2)},
    )

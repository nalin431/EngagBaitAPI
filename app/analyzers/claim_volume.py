import re
from app.models import MetricBreakdown
from app.analyzers.base import clamp_score

_CLAIM_INDICATORS = re.compile(
    r"\b(?:proves?|shows?|means?|causes?|reveals?|confirms?|always|never|must|should|obvious|truth|lying|everyone\s+knows|no\s+middle\s+ground)\b",
    re.I,
)
_LISTICLE_PATTERNS = [
    re.compile(r"(?:top|best|worst)\s+\d+", re.I),
    re.compile(r"\d+\s+(?:reasons|ways|things|tips|secrets|facts|signs)", re.I),
]


def analyze_claim_volume(text: str) -> MetricBreakdown:
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    words = text.split()
    wc = len(words) or 1
    sc = len(sentences) or 1

    claims = sum(1 for s in sentences if _CLAIM_INDICATORS.search(s))
    listicle_matches = sum(len(p.findall(text)) for p in _LISTICLE_PATTERNS)
    claims_per_word = claims / wc
    avg_sent_len = sum(len(s.split()) for s in sentences) / sc
    has_because = "because" in text.lower() or "since" in text.lower()
    explanation_depth = clamp_score(min(1, avg_sent_len / 25) * (0.7 if has_because else 0.3))

    # High claims_per_word + low explanation_depth = engagement bait; listicle boosts
    s_claims = clamp_score(min(1, claims_per_word * 50))
    s_listicle = clamp_score(min(1, listicle_matches / 2))
    s_depth_inv = clamp_score(1 - explanation_depth)
    score = (s_claims + s_depth_inv + s_listicle) / 3
    return MetricBreakdown(
        score=round(clamp_score(score), 2),
        breakdown={
            "claims_per_word": round(s_claims, 2),
            "explanation_depth": round(1 - s_depth_inv, 2),
            "listicle": round(s_listicle, 2),
        },
    )

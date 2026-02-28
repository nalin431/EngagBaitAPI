import re
from app.models import MetricBreakdown
from app.analyzers.base import clamp_score

_CITATION_PATTERNS = [
    re.compile(r"\[\s*\d+\s*\]"),
    re.compile(r"\(\s*[Ss]ource\s*[:\s]"),
    re.compile(r"\([A-Za-z]+\s+et\s+al\.?\s*\d{4}\)"),
    re.compile(r"\d+\s*%\s*(?:of|from)"),
]
_STATS_PATTERNS = [
    re.compile(r"\d+\.?\d*\s*%"),
    re.compile(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(?:people|users|studies|percent)"),
    re.compile(r"\d+\s*(?:million|billion|thousand)"),
    re.compile(r"study\s+(?:shows|found|reveals)"),
    re.compile(r"research\s+(?:shows|indicates|suggests)"),
]
_EXTERNAL_PATTERNS = [
    re.compile(r"https?://\S+"),
    re.compile(r"according\s+to\s+\w+"),
    re.compile(r"(?:study|research|report|survey)\s+(?:by|from|at)"),
]


def _count_matches(text: str, patterns: list[re.Pattern]) -> int:
    return sum(len(p.findall(text)) for p in patterns)


def analyze_evidence(text: str) -> MetricBreakdown:
    citations = _count_matches(text, _CITATION_PATTERNS)
    stats = _count_matches(text, _STATS_PATTERNS)
    external = _count_matches(text, _EXTERNAL_PATTERNS)

    # Evidence density: higher = more evidence. Inverse for "engagement bait" score:
    # low evidence density = more bait-like. So we invert: score = 1 - normalized_evidence
    words = len(text.split()) or 1
    scale = max(1, words / 40)  # unified scaling for citations, stats, external
    c_norm = clamp_score(1 - min(1, citations / scale))
    s_norm = clamp_score(1 - min(1, stats / scale))
    e_norm = clamp_score(1 - min(1, external / scale))
    score = (c_norm + s_norm + e_norm) / 3
    return MetricBreakdown(
        score=round(score, 2),
        breakdown={"citations": round(c_norm, 2), "stats": round(s_norm, 2), "external_sources": round(e_norm, 2)},
    )

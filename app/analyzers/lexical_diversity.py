from app.models import MetricBreakdown
from app.analyzers.base import clamp_score


def _mattr(tokens: list[str], base_window: int = 40) -> float:
    # Moving Average Type-Token Ratio — slide a window across the token list,
    # compute unique/window at each step, then average. Length-invariant unlike raw TTR.
    # Falls back to plain TTR when the text is too short for a sliding window.
    n = len(tokens)
    if n == 0:
        return 0.0
    window = min(base_window, max(10, n // 2))
    if n < window * 2:
        # not enough tokens for at least 2 windows, just use TTR
        return len(set(tokens)) / n
    ratios = [
        len(set(tokens[i : i + window])) / window
        for i in range(n - window + 1)
    ]
    return sum(ratios) / len(ratios)


def analyze_lexical_diversity(text: str) -> MetricBreakdown:
    # strip punctuation and lowercase so "angry!" and "angry" count as the same word
    tokens = [w.lower().rstrip(".,;:!?\"'") for w in text.split()]
    tokens = [w for w in tokens if w]
    n = len(tokens)

    if n == 0:
        return MetricBreakdown(score=0.0, breakdown={"mattr": 0.0, "type_token_ratio": 0.0})

    ttr = len(set(tokens)) / n
    mattr_val = _mattr(tokens)

    # low diversity = repetitive vocab = bait signal, so invert
    bait_score = clamp_score(1.0 - mattr_val)

    return MetricBreakdown(
        score=round(bait_score, 2),
        breakdown={
            "mattr": round(mattr_val, 2),
            "type_token_ratio": round(ttr, 2),
        },
    )

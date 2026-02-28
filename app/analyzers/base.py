from app.models import MetricBreakdown


def clamp_score(value: float) -> float:
    """Clamp score to [0, 1]."""
    return max(0.0, min(1.0, value))


def count_to_score(count: int, thresholds: tuple[int, int]) -> float:
    """
    Map raw count to 0-1 score using thresholds.
    thresholds = (low, high): count >= low -> start rising, count >= high -> 1.0
    """
    low, high = thresholds
    if count <= low:
        return 0.0
    if count >= high:
        return 1.0
    return clamp_score((count - low) / (high - low))

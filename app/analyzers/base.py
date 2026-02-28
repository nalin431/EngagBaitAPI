from app.models import MetricBreakdown

# ---------------------------------------------------------------------------
# Negation and degree-modifier vocabularies (used by arousal + urgency)
# ---------------------------------------------------------------------------

_NEGATORS: frozenset[str] = frozenset({
    "not", "no", "never", "without", "nobody", "nothing", "neither", "nor",
    "don't", "doesn't", "didn't", "won't", "can't", "isn't", "aren't",
    "wasn't", "weren't", "hardly", "barely", "seldom",
})

_AMPLIFIERS: frozenset[str] = frozenset({
    "very", "extremely", "absolutely", "incredibly", "totally", "utterly",
    "seriously", "deeply", "completely", "especially", "remarkably", "wildly",
    "intensely", "fiercely", "terribly",
})

# Single-token roots: "kind" covers "kind of", "sort" covers "sort of" —
# only fires when within 2 tokens of the hit, so "kind person was angry"
# (distance > 2) is unaffected.
_DIMINISHERS: frozenset[str] = frozenset({
    "slightly", "barely", "somewhat", "fairly", "rather", "relatively",
    "mildly", "vaguely", "kind", "sort",
})


def clamp_score(value: float) -> float:
    """Clamp score to [0, 1]."""
    return max(0.0, min(1.0, value))


def count_to_score(count: float, thresholds: tuple[float, float]) -> float:
    """
    Map a raw count to a 0-1 score using linear interpolation between thresholds.
    Accepts floats to support weighted hit accumulation from negation/modifier logic.
    """
    low, high = thresholds
    if count < low:
        return 0.0
    if count >= high:
        return 1.0
    return clamp_score((count - low) / (high - low))


def length_confidence(word_count: int, full_scale: int = 80) -> float:
    """
    Returns 1.0 for texts >= full_scale words, scales linearly toward 0 below.
    Applied to density-based sub-scores (exclamation, caps, etc.) so that a
    single '!' in a 10-word email doesn't immediately max out the score.
    """
    return min(1.0, word_count / full_scale)


def is_negated(tokens: list[str], hit_index: int, window: int = 3) -> bool:
    """True if any negation word appears within `window` tokens before `hit_index`."""
    start = max(0, hit_index - window)
    return any(tokens[i] in _NEGATORS for i in range(start, hit_index))


def is_phrase_negated(text: str, phrase_start: int, window: int = 3) -> bool:
    """
    True if a negation word appears in the `window` tokens immediately
    preceding `phrase_start` in `text`. Used for phrase-level urgency matching.
    """
    pre_tokens = text[:phrase_start].split()
    return any(tok in _NEGATORS for tok in pre_tokens[-window:])


def get_modifier(tokens: list[str], hit_index: int, window: int = 2) -> float:
    """
    Return a degree-modifier multiplier from the tokens preceding `hit_index`.
    Amplifiers → 1.3, diminishers → 0.7, no modifier → 1.0.
    Values are conservative approximations of VADER's empirically derived ±29%
    adjustment; they can be tuned against the benchmark in scripts/.
    """
    start = max(0, hit_index - window)
    for i in range(start, hit_index):
        if tokens[i] in _AMPLIFIERS:
            return 1.3
        if tokens[i] in _DIMINISHERS:
            return 0.7
    return 1.0

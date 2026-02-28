"""Load and cache custom lexicons. One term per line, comments with #."""
from pathlib import Path

_LEXICON_DIR = Path(__file__).resolve().parent / "custom"
_CACHE: dict[str, frozenset[str]] = {}
_WEIGHTED_CACHE: dict[str, dict[str, float]] = {}

# Valence tier → weight mapping. Tiers are annotated in lexicon files as word:N.
# Conservative values; tune against scripts/run_ml_benchmark.py if needed.
_TIER_WEIGHTS: dict[int, float] = {1: 1.0, 2: 1.3, 3: 1.6}


def load_lexicon(name: str) -> frozenset[str]:
    """Load lexicon from custom/<name>.txt, lowercase, strip, skip comments."""
    if name in _CACHE:
        return _CACHE[name]
    path = _LEXICON_DIR / f"{name}.txt"
    if not path.exists():
        _CACHE[name] = frozenset()
        return _CACHE[name]
    terms = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip().lower()
        if line and not line.startswith("#"):
            terms.add(line)
    _CACHE[name] = frozenset(terms)
    return _CACHE[name]


def load_weighted_lexicon(name: str) -> dict[str, float]:
    """
    Load lexicon with optional ':N' valence tier annotations (N = 1, 2, or 3).
    Returns {word: weight}. Bare entries (no colon) default to weight 1.0.
    Cached separately from load_lexicon.
    """
    if name in _WEIGHTED_CACHE:
        return _WEIGHTED_CACHE[name]
    path = _LEXICON_DIR / f"{name}.txt"
    if not path.exists():
        _WEIGHTED_CACHE[name] = {}
        return {}
    result: dict[str, float] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip().lower()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            word, _, tier_str = line.rpartition(":")
            word = word.strip()
            try:
                weight = _TIER_WEIGHTS.get(int(tier_str.strip()), 1.0)
            except ValueError:
                weight = 1.0
        else:
            word = line
            weight = 1.0
        result[word] = weight
    _WEIGHTED_CACHE[name] = result
    return result


def get_arousal_terms() -> frozenset[str]:
    """Return arousal words as a frozenset (tier annotations stripped)."""
    return frozenset(load_weighted_lexicon("arousal").keys())


def get_arousal_weighted_terms() -> dict[str, float]:
    """Return {word: valence_weight} for the arousal lexicon."""
    return load_weighted_lexicon("arousal")


def get_urgency_terms() -> frozenset[str]:
    return load_lexicon("urgency")


def get_urgency_sections() -> dict[str, frozenset[str]]:
    """Return {time_pressure, scarcity, fomo} from urgency.txt with # section headers."""
    path = _LEXICON_DIR / "urgency.txt"
    result: dict[str, set[str]] = {"time_pressure": set(), "scarcity": set(), "fomo": set()}
    current: str | None = None
    if not path.exists():
        return {k: frozenset() for k in result}
    for line in path.read_text(encoding="utf-8").splitlines():
        line_lower = line.strip().lower()
        if not line_lower:
            continue
        if line_lower.startswith("#"):
            rest = line_lower[1:].strip()
            if "time pressure" in rest or "urgency" in rest:
                current = "time_pressure"
            elif "scarcity" in rest:
                current = "scarcity"
            elif "fomo" in rest:
                current = "fomo"
            continue
        if current:
            result[current].add(line_lower)
    return {k: frozenset(v) if v else frozenset() for k, v in result.items()}


def get_moralized_terms() -> frozenset[str]:
    return load_lexicon("moralized")

def get_tradeoff_terms() -> frozenset[str]:
    return load_lexicon("tradeoff")


def get_conditional_terms() -> frozenset[str]:
    return load_lexicon("conditional")


def get_curiosity_gap_phrases() -> frozenset[str]:
    return load_lexicon("curiosity_gap")


def get_superlative_terms() -> frozenset[str]:
    return load_lexicon("superlatives")

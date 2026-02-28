"""Load and cache custom lexicons. One term per line, comments with #."""
from pathlib import Path

_LEXICON_DIR = Path(__file__).resolve().parent / "custom"
_CACHE: dict[str, frozenset[str]] = {}


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


def get_binary_connectors() -> frozenset[str]:
    return load_lexicon("binary_connectors")


def get_single_cause_markers() -> frozenset[str]:
    return load_lexicon("single_cause")


def get_tradeoff_terms() -> frozenset[str]:
    return load_lexicon("tradeoff")


def get_conditional_terms() -> frozenset[str]:
    return load_lexicon("conditional")


def get_arousal_terms() -> frozenset[str]:
    return load_lexicon("arousal")


def get_curiosity_gap_phrases() -> frozenset[str]:
    return load_lexicon("curiosity_gap")


def get_superlative_terms() -> frozenset[str]:
    return load_lexicon("superlatives")

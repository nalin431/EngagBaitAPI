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


def get_absolutist_terms() -> frozenset[str]:
    return load_lexicon("absolutist")


def get_hedging_terms() -> frozenset[str]:
    return load_lexicon("hedging")


def get_strong_modal_terms() -> frozenset[str]:
    return load_lexicon("strong_modals")


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


def get_ingroup_terms() -> frozenset[str]:
    return load_lexicon("ingroup")


def get_arousal_terms() -> frozenset[str]:
    return load_lexicon("arousal")

"""Optional NRC Emotion Lexicon loader. Uses custom arousal.txt if NRC file not present."""
from pathlib import Path

_NRC_PATH = Path(__file__).resolve().parent / "nrc_emotion.csv"
_HIGH_AROUSAL = {"anger", "fear", "disgust"}
_CACHE: set[str] | None = None


def get_nrc_arousal_words() -> frozenset[str]:
    """Return high-arousal emotion words from NRC if file exists, else empty set."""
    global _CACHE
    if _CACHE is not None:
        return frozenset(_CACHE)
    if not _NRC_PATH.exists():
        _CACHE = set()
        return frozenset()
    words = set()
    for line in _NRC_PATH.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split("\t")
        if len(parts) >= 3 and parts[2] == "1" and parts[1] in _HIGH_AROUSAL:
            words.add(parts[0].lower())
    _CACHE = words
    return frozenset(words)

from app.models import MetricBreakdown
from app.analyzers.base import (
    count_to_score, clamp_score,
    is_negated, get_modifier, length_confidence,
)
from app.lexicons.loader import (
    get_arousal_weighted_terms, get_moralized_terms,
    get_curiosity_gap_phrases, get_superlative_terms,
)
from app.lexicons.nrc import get_nrc_arousal_words

_EMOTION_WEIGHTED = get_arousal_weighted_terms()
_NRC = get_nrc_arousal_words()
_MORALIZED = get_moralized_terms() or {
    "wrong", "evil", "traitor", "betray", "sin", "corrupt", "immoral",
    "disgrace", "shameful", "outrage", "outrageous", "vile", "wicked",
}
_CURIOSITY_GAP = get_curiosity_gap_phrases()
_SUPERLATIVES = get_superlative_terms() or {
    "best", "worst", "most", "least", "incredible", "astonishing",
    "unbelievable", "shocking",
}


def _count_phrases(text: str, phrases: frozenset[str]) -> int:
    t = text.lower()
    return sum(1 for p in phrases if p in t)


def _count_terms(tokens: list[str], terms) -> float:
    # for each token that matches, skip it if preceded by a negation word,
    # otherwise scale it by any nearby amplifier/diminisher
    total = 0.0
    for i, w in enumerate(tokens):
        cleaned = w.rstrip(".,;:!?")
        base = terms.get(cleaned, 0.0) if isinstance(terms, dict) else (
            1.0 if cleaned in terms else 0.0
        )
        if base > 0.0 and not is_negated(tokens, i):
            total += base * get_modifier(tokens, i)
    return total


def analyze_arousal(text: str) -> MetricBreakdown:
    t = text.lower()
    tokens = [w.rstrip(".,;:!?") for w in t.split()]
    wc = len(tokens) or 1
    lc = length_confidence(wc)

    # arousal.txt words carry tier weights; NRC words default to 1.0
    merged_emotion: dict[str, float] = {**{w: 1.0 for w in _NRC}, **_EMOTION_WEIGHTED}
    emotion_weighted = _count_terms(tokens, merged_emotion)

    exclamations = text.count("!")
    exclamation_density = exclamations / wc
    questions = text.count("?")
    question_density = questions / wc

    # need original case for caps — lowercased words never pass isupper()
    orig_words = text.split()
    caps_count = sum(1 for w in orig_words if len(w) > 2 and w.isupper())
    caps_ratio = caps_count / wc

    moralized_weighted = _count_terms(tokens, _MORALIZED)
    superlative_weighted = _count_terms(tokens, _SUPERLATIVES)
    curiosity_count = _count_phrases(t, _CURIOSITY_GAP) if _CURIOSITY_GAP else 0

    s_emotion = count_to_score(emotion_weighted, (0, 6))
    # density scores scaled by text length so short texts don't spike on one punctuation mark
    s_exclamation = clamp_score(min(1, exclamation_density * 20) * lc)
    s_question = clamp_score(min(1, question_density * 20) * lc)
    s_caps = clamp_score(min(1, caps_ratio * 15) * lc)
    s_moralized = count_to_score(moralized_weighted, (0, 4))
    s_superlative = count_to_score(superlative_weighted, (0, 5))
    s_curiosity = count_to_score(curiosity_count, (0, 2))

    score = (
        s_emotion + s_exclamation + s_question + s_caps
        + s_moralized + s_superlative + s_curiosity
    ) / 7
    return MetricBreakdown(
        score=round(clamp_score(score), 2),
        breakdown={
            "emotion_words": round(s_emotion, 2),
            "exclamation_density": round(s_exclamation, 2),
            "question_density": round(s_question, 2),
            "caps_ratio": round(s_caps, 2),
            "moralized_language": round(s_moralized, 2),
            "superlative_density": round(s_superlative, 2),
            "curiosity_gap": round(s_curiosity, 2),
        },
    )

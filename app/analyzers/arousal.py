from app.models import MetricBreakdown
from app.analyzers.base import count_to_score, clamp_score
from app.lexicons.loader import get_arousal_terms, get_moralized_terms, get_curiosity_gap_phrases, get_superlative_terms
from app.lexicons.nrc import get_nrc_arousal_words

_EMOTION_TERMS = get_arousal_terms()
_NRC = get_nrc_arousal_words()
_MORALIZED = get_moralized_terms() or {"wrong", "evil", "traitor", "betray", "sin", "corrupt", "immoral", "disgrace", "shameful", "outrage", "outrageous", "vile", "wicked"}
_CURIOSITY_GAP = get_curiosity_gap_phrases()
_SUPERLATIVES = get_superlative_terms() or {"best", "worst", "most", "least", "incredible", "astonishing", "unbelievable", "shocking"}


def _count_phrases(text: str, phrases: frozenset[str]) -> int:
    t = text.lower()
    return sum(1 for p in phrases if p in t)


def analyze_arousal(text: str) -> MetricBreakdown:
    t = text.lower()
    words = t.split()
    wc = len(words) or 1

    emotion_set = _EMOTION_TERMS | _NRC
    emotion_count = sum(1 for w in words if w.rstrip(".,;:!?") in emotion_set)
    exclamations = text.count("!")
    exclamation_density = exclamations / wc
    questions = text.count("?")
    question_density = questions / wc
    caps_count = sum(1 for w in words if len(w) > 2 and w.isupper())
    caps_ratio = caps_count / wc
    moralized_count = sum(1 for w in words if w.rstrip(".,;:!?") in _MORALIZED)
    superlative_count = sum(1 for w in words if w.rstrip(".,;:!?") in _SUPERLATIVES)
    curiosity_count = _count_phrases(t, _CURIOSITY_GAP) if _CURIOSITY_GAP else 0

    s_emotion = count_to_score(emotion_count, (0, 6))
    s_exclamation = clamp_score(min(1, exclamation_density * 20))
    s_question = clamp_score(min(1, question_density * 20))
    s_caps = clamp_score(min(1, caps_ratio * 15))
    s_moralized = count_to_score(moralized_count, (0, 4))
    s_superlative = count_to_score(superlative_count, (0, 5))
    s_curiosity = count_to_score(curiosity_count, (0, 2))  # 1 phrase = 0.5, 2+ = 1

    score = (s_emotion + s_exclamation + s_question + s_caps + s_moralized + s_superlative + s_curiosity) / 7
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

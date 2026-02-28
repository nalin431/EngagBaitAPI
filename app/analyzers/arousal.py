from app.models import MetricBreakdown
from app.analyzers.base import count_to_score, clamp_score
from app.lexicons.loader import get_arousal_terms
from app.lexicons.nrc import get_nrc_arousal_words

_EMOTION_TERMS = get_arousal_terms()
_NRC = get_nrc_arousal_words()
_MORALIZED = {"wrong", "evil", "traitor", "betray", "sin", "corrupt", "immoral", "disgrace", "shameful", "outrage", "outrageous", "vile", "wicked"}


def analyze_arousal(text: str) -> MetricBreakdown:
    t = text.lower()
    words = t.split()
    wc = len(words) or 1

    emotion_set = _EMOTION_TERMS | _NRC
    emotion_count = sum(1 for w in words if w.rstrip(".,;:!?") in emotion_set)
    exclamations = text.count("!")
    exclamation_density = exclamations / wc
    moralized_count = sum(1 for w in words if w.rstrip(".,;:!?") in _MORALIZED)

    s_emotion = count_to_score(emotion_count, (2, 8))
    s_exclamation = clamp_score(min(1, exclamation_density * 20))
    s_moralized = count_to_score(moralized_count, (1, 5))

    score = (s_emotion + s_exclamation + s_moralized) / 3
    return MetricBreakdown(
        score=round(clamp_score(score), 2),
        breakdown={
            "emotion_words": round(s_emotion, 2),
            "exclamation_density": round(s_exclamation, 2),
            "moralized_language": round(s_moralized, 2),
        },
    )

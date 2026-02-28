from app.analyzers.urgency import analyze_urgency
from app.analyzers.evidence import analyze_evidence
from app.analyzers.arousal import analyze_arousal
from app.analyzers.narrative import analyze_counterargument_absence
from app.analyzers.claim_volume import analyze_claim_volume


def test_urgency_high():
    t = "Act now! Limited time! Don't miss out! Last chance! Hurry!"
    r = analyze_urgency(t)
    assert r.score >= 0.3
    assert "time_pressure" in r.breakdown


def test_urgency_low():
    t = "This is a calm, informative piece with no pressure. Consider it when you have time."
    r = analyze_urgency(t)
    assert r.score <= 0.5


def test_urgency_prose_style():
    t = "Act now before they scrub this from public view. Smart people know the truth will be buried if we wait until tomorrow."
    r = analyze_urgency(t)
    assert r.score > 0.0


def test_evidence_low():
    t = "Everyone knows this is true. No citations needed. Just trust me."
    r = analyze_evidence(t)
    assert r.score >= 0.5


def test_evidence_analytical_text():
    t = "A review of 38 climate adaptation studies found modest benefits for coastal planning, although authors noted significant variation in methodology and regional constraints."
    r = analyze_evidence(t)
    assert r.score < 1.0


def test_arousal_high():
    t = "You won't believe this! The BEST and MOST incredible thing! EVIL! Terrifying! Outrageous! We must fight!"
    r = analyze_arousal(t)
    assert r.score >= 0.25


def test_counterargument_absence_high():
    t = "This is the only path forward. The answer is obvious. We should do it now."
    r = analyze_counterargument_absence(t)
    assert r.score >= 0.7
    assert "tradeoff_absence" in r.breakdown
    assert "conditional_absence" in r.breakdown


def test_counterargument_absence_low():
    t = "This approach may help in some cases, although the tradeoffs depend on cost, staffing, and whether implementation succeeds locally."
    r = analyze_counterargument_absence(t)
    assert r.score <= 0.5


def test_counterargument_absence_contrastive_text():
    t = "Supporters say the policy could protect consumers quickly, but critics argue the timeline is unrealistic and the data is still incomplete."
    r = analyze_counterargument_absence(t)
    assert r.score < 1.0


def test_claim_volume():
    t = "This proves it. That shows the truth. It reveals everything. Must act. Always."
    r = analyze_claim_volume(t)
    assert r.score >= 0.3
    neutral = "The weather is nice. The meeting was productive. We will discuss later."
    r2 = analyze_claim_volume(neutral)
    assert r.score >= r2.score

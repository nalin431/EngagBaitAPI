from app.analyzers.urgency import analyze_urgency
from app.analyzers.evidence import analyze_evidence
from app.analyzers.overconfidence import analyze_overconfidence
from app.analyzers.arousal import analyze_arousal
from app.analyzers.ingroup import analyze_ingroup
from app.analyzers.narrative import analyze_narrative
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


def test_evidence_low():
    t = "Everyone knows this is true. No citations needed. Just trust me."
    r = analyze_evidence(t)
    assert r.score >= 0.5


def test_overconfidence_high():
    t = "This will always happen. It never fails. Everyone must act. It is guaranteed."
    r = analyze_overconfidence(t)
    assert r.score >= 0.5


def test_arousal_high():
    t = "This is outrageous! Evil! Terrifying! We must fight! Attack!"
    r = analyze_arousal(t)
    assert r.score >= 0.5


def test_ingroup_high():
    t = "We must stand against them. They are our enemies. We the people versus the elite."
    r = analyze_ingroup(t)
    assert r.score >= 0.3


def test_narrative_simple():
    t = "Because of X everything failed. Either you support us or you are against us. No trade-offs."
    r = analyze_narrative(t)
    assert r.score >= 0.4


def test_claim_volume():
    t = "This is true. That is wrong. It will happen. They must act. Always."
    r = analyze_claim_volume(t)
    assert 0 <= r.score <= 1

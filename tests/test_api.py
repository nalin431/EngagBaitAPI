from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "docs" in r.json()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_analyze_ok():
    text = "You must act now! This is the last chance. Everyone knows they are evil and we must fight back. The truth is simple: they are always wrong and we will never give up. Do not miss out!"
    r = client.post("/analyze", json={"text": text})
    assert r.status_code == 200
    data = r.json()
    assert "urgency_pressure" in data
    assert "evidence_density" in data
    assert "arousal_intensity" in data
    assert "narrative_simplification" in data
    assert "claim_volume_vs_depth" in data
    for k, v in data.items():
        if k == "engagement_bait_score":
            assert v is None or isinstance(v, (int, float))
        else:
            assert "score" in v
            assert "breakdown" in v


def test_analyze_validation_short():
    r = client.post("/analyze", json={"text": "Too short"})
    assert r.status_code == 422

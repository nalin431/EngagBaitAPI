from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["docs"] == "/docs"
    assert data["demo"] == "/demo"
    assert data["analyze_batch"] == "/analyze/batch"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "openai_enabled" in data
    assert "actian_enabled" in data


def test_demo_page():
    r = client.get("/demo")
    assert r.status_code == 200
    assert "Detect structural engagement bait patterns in text." in r.text


def test_analyze_ok():
    text = "You must act now! This is the last chance. Everyone knows they are evil and we must fight back. The truth is simple: they are always wrong and we will never give up. Do not miss out!"
    r = client.post("/analyze", json={"text": text})
    assert r.status_code == 200
    data = r.json()
    assert "urgency_pressure" in data
    assert "evidence_density" in data
    assert "arousal_intensity" in data
    assert "counterargument_absence" in data
    assert "claim_volume_vs_depth" in data
    assert data["meta"]["vector_backend"] in {"none", "centroid", "actian"}
    for key in (
        "urgency_pressure",
        "evidence_density",
        "arousal_intensity",
        "counterargument_absence",
        "claim_volume_vs_depth",
    ):
        assert "score" in data[key]
        assert "breakdown" in data[key]

    assert "tradeoff_absence" in data["counterargument_absence"]["breakdown"]
    assert "conditional_absence" in data["counterargument_absence"]["breakdown"]


def test_analyze_ml_false_meta():
    text = "You must act now! This is the last chance. Everyone knows they are evil and we must fight back. The truth is simple: they are always wrong and we will never give up. Do not miss out!"
    r = client.post("/analyze?ml=false", json={"text": text})
    assert r.status_code == 200
    data = r.json()
    assert data["engagement_bait_score"] is None
    assert data["meta"] == {
        "ml_requested": False,
        "ml_used": False,
        "openai_available": False,
        "vector_backend": "none",
    }


def test_analyze_ml_true_without_openai_meta():
    text = "You must act now! This is the last chance. Everyone knows they are evil and we must fight back. The truth is simple: they are always wrong and we will never give up. Do not miss out!"
    r = client.post("/analyze?ml=true", json={"text": text})
    assert r.status_code == 200
    data = r.json()
    assert data["engagement_bait_score"] is None
    assert data["meta"] == {
        "ml_requested": True,
        "ml_used": False,
        "openai_available": False,
        "vector_backend": "none",
    }


def test_analyze_batch_ok():
    r = client.post(
        "/analyze/batch?ml=false",
        json={
            "items": [
                {
                    "id": "first",
                    "text": "You must act now! This is the last chance. Everyone knows they are evil and we must fight back. The truth is simple: they are always wrong and we will never give up. Do not miss out!",
                },
                {
                    "id": "second",
                    "text": "A new policy brief reviewed three implementation options for transit funding. According to the report, ridership increased by 14 percent in pilot cities, but the authors note cost tradeoffs, timeline risks, and the need for further evaluation before statewide rollout.",
                },
            ]
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert [item["id"] for item in data["items"]] == ["first", "second"]
    assert data["items"][0]["result"]["meta"]["vector_backend"] == "none"


def test_analyze_batch_empty():
    r = client.post("/analyze/batch", json={"items": []})
    assert r.status_code == 422
    assert r.json()["detail"] == "Value error, Batch must include at least 1 item"


def test_analyze_batch_too_large():
    items = [
        {
            "id": f"item-{i}",
            "text": "A new policy brief reviewed three implementation options for transit funding. According to the report, ridership increased by 14 percent in pilot cities, but the authors note cost tradeoffs, timeline risks, and the need for further evaluation before statewide rollout.",
        }
        for i in range(11)
    ]
    r = client.post("/analyze/batch", json={"items": items})
    assert r.status_code == 422
    assert r.json()["detail"] == "Value error, Batch must include at most 10 items"


def test_analyze_batch_invalid_item_text():
    r = client.post(
        "/analyze/batch",
        json={"items": [{"id": "short", "text": "Too short"}]},
    )
    assert r.status_code == 422


def test_analyze_validation_short():
    r = client.post("/analyze", json={"text": "Too short"})
    assert r.status_code == 422

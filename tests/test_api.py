from fastapi.testclient import TestClient

from app.main import app
from app.sample_data import SAMPLE_BRIEFINGS


client = TestClient(app)


def test_healthcheck_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_briefings_returns_array() -> None:
    response = client.get("/api/briefings")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload
    assert "briefing_id" in payload[0]


def test_analyze_briefing_returns_score_and_status() -> None:
    response = client.post("/api/analyze/briefing", json=SAMPLE_BRIEFINGS[0].model_dump())
    assert response.status_code == 200
    payload = response.json()
    assert "score" in payload
    assert "status" in payload
    assert "recommended_next_actions" in payload


def test_dashboard_summary_returns_signal_counts() -> None:
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["briefings"] >= 1
    assert payload["signals"] >= 1


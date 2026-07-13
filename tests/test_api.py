from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_and_index_without_model(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    assert client.get("/").status_code == 200
    health = client.get("/api/health")
    assert health.json() == {"status": "ok", "model_configured": False, "model_exists": False}


def test_rejects_non_video_upload(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    response = client.post("/api/analyze", files={"file": ("report.txt", b"text", "text/plain")})
    assert response.status_code == 400
    assert "仅支持" in response.json()["detail"]


def test_requires_model_before_analysis(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    response = client.post("/api/analyze", files={"file": ("video.mp4", b"not-a-real-video", "video/mp4")})
    assert response.status_code == 503
    assert "MODEL_PATH" in response.json()["detail"]


def test_returns_404_for_missing_report(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    response = client.get("/api/reports/unknown")
    assert response.status_code == 404


def test_saves_and_reads_generated_report(monkeypatch, tmp_path: Path) -> None:
    app = create_app(tmp_path, model_path=tmp_path / "configured.pt")
    app.state.detector = object()
    monkeypatch.setattr(
        "app.main.analyze_video",
        lambda *_: {"sampled_frames": 3, "event_count": 1, "highest_risk": "high", "counts": {"knife": 1}, "events": []},
    )
    client = TestClient(app)
    response = client.post("/api/analyze", files={"file": ("video.mp4", b"video", "video/mp4")})

    assert response.status_code == 200
    report_id = response.json()["report_id"]
    saved = client.get(f"/api/reports/{report_id}")
    assert saved.status_code == 200
    assert saved.json()["event_count"] == 1

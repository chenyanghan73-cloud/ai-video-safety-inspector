from __future__ import annotations


def demo_report() -> dict:
    """Return a clearly labeled, deterministic report for product demonstration."""
    return {
        "report_id": "demo-2026",
        "video": "campus-security-demo.mp4",
        "sample_seconds": 2.0,
        "confidence_threshold": 0.5,
        "sampled_frames": 36,
        "event_count": 4,
        "highest_risk": "high",
        "counts": {"person": 2, "knife": 1, "wallet": 1},
        "events": [
            {"timestamp_seconds": 4.0, "label": "person", "confidence": 0.932, "risk": "low"},
            {"timestamp_seconds": 18.0, "label": "wallet", "confidence": 0.861, "risk": "low"},
            {"timestamp_seconds": 26.0, "label": "knife", "confidence": 0.788, "risk": "high"},
            {"timestamp_seconds": 28.0, "label": "person", "confidence": 0.904, "risk": "low"},
        ],
        "demo": True,
    }

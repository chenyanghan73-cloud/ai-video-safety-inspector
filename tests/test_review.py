from app.review import Detection, review_frames, risk_for


class FakeDetector:
    def detect(self, frame: object, confidence: float):
        return frame


def test_risk_mapping_has_safe_default() -> None:
    assert risk_for("knife") == "high"
    assert risk_for("person") == "low"
    assert risk_for("unknown") == "medium"


def test_review_aggregates_events_and_filters_confidence() -> None:
    frames = [
        (0.0, [Detection("person", 0.9), Detection("knife", 0.82)]),
        (2.0, [Detection("wallet", 0.3)]),
    ]
    report = review_frames(FakeDetector(), frames, confidence=0.5)

    assert report["sampled_frames"] == 2
    assert report["event_count"] == 2
    assert report["highest_risk"] == "high"
    assert report["counts"] == {"person": 1, "knife": 1}
    assert report["events"][1]["timestamp_seconds"] == 0.0


def test_review_handles_no_detection() -> None:
    report = review_frames(FakeDetector(), [(1.5, [])])
    assert report["event_count"] == 0
    assert report["highest_risk"] == "low"

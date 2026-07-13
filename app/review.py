from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float


@dataclass(frozen=True)
class Event:
    timestamp_seconds: float
    label: str
    confidence: float
    risk: str


class Detector(Protocol):
    def detect(self, frame: object, confidence: float) -> list[Detection]: ...


RISK_BY_LABEL = {
    "knife": "high",
    "weapon": "high",
    "fire": "high",
    "person": "low",
    "wallet": "low",
}
RISK_ORDER = {"low": 1, "medium": 2, "high": 3}


def risk_for(label: str) -> str:
    return RISK_BY_LABEL.get(label.lower(), "medium")


def review_frames(
    detector: Detector,
    frames: list[tuple[float, object]],
    confidence: float = 0.5,
) -> dict:
    events: list[Event] = []
    for timestamp, frame in frames:
        for detection in detector.detect(frame, confidence):
            if detection.confidence >= confidence:
                events.append(
                    Event(
                        timestamp_seconds=round(timestamp, 2),
                        label=detection.label,
                        confidence=round(detection.confidence, 3),
                        risk=risk_for(detection.label),
                    )
                )

    counts: dict[str, int] = {}
    for event in events:
        counts[event.label] = counts.get(event.label, 0) + 1
    highest_risk = max((event.risk for event in events), key=RISK_ORDER.get, default="low")
    return {
        "sampled_frames": len(frames),
        "event_count": len(events),
        "highest_risk": highest_risk,
        "counts": counts,
        "events": [asdict(event) for event in events],
    }

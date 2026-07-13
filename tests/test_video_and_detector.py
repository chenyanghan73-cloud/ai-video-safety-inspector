from pathlib import Path

import pytest

from app.detector import YOLODetector
from app.review import Detection
from app.video import analyze_video, sample_video


class FakeCapture:
    def __init__(self, frames):
        self.frames = iter(frames)
        self.released = False

    def isOpened(self):
        return True

    def get(self, _):
        return 2.0

    def read(self):
        try:
            return True, next(self.frames)
        except StopIteration:
            return False, None

    def release(self):
        self.released = True


class EmptyCapture:
    def isOpened(self):
        return False


class FakeDetector:
    def detect(self, frame, confidence):
        return [Detection("knife", 0.9)] if frame == "risk" else []


def test_sample_video_extracts_frames_at_interval(monkeypatch, tmp_path: Path) -> None:
    capture = FakeCapture(["first", "skip", "risk", "skip"])
    monkeypatch.setattr("app.video.cv2.VideoCapture", lambda _: capture)

    sampled = sample_video(tmp_path / "video.mp4", sample_seconds=1.0)

    assert sampled == [(0.0, "first"), (1.0, "risk")]
    assert capture.released is True


def test_sample_video_rejects_unreadable_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.video.cv2.VideoCapture", lambda _: EmptyCapture())
    with pytest.raises(ValueError, match="无法读取"):
        sample_video(tmp_path / "bad.mp4", sample_seconds=1.0)


def test_analyze_video_adds_video_metadata(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.video.sample_video", lambda *_: [(2.0, "risk")])
    report = analyze_video(tmp_path / "scene.mp4", FakeDetector(), sample_seconds=2.0, confidence=0.5)

    assert report["video"] == "scene.mp4"
    assert report["highest_risk"] == "high"


def test_detector_reports_missing_model(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="模型文件不存在"):
        YOLODetector(tmp_path / "missing.pt")


def test_detector_requires_ultralytics_when_model_file_exists(tmp_path: Path) -> None:
    model = tmp_path / "model.pt"
    model.write_bytes(b"placeholder")
    with pytest.raises(RuntimeError, match="requirements-vision"):
        YOLODetector(model)


def test_detector_maps_ultralytics_boxes_without_loading_model() -> None:
    class Box:
        cls = [0]
        conf = [0.81]

    class Result:
        names = {0: "knife"}
        boxes = [Box()]

    class Model:
        def __call__(self, frame, conf, verbose):
            return [Result()]

    detector = object.__new__(YOLODetector)
    detector.model = Model()
    assert detector.detect("frame", 0.5) == [Detection("knife", 0.81)]

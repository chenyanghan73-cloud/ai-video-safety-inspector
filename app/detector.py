from __future__ import annotations

from pathlib import Path

from .review import Detection


class YOLODetector:
    """Lazy Ultralytics adapter so the base project can be tested without model dependencies."""

    def __init__(self, model_path: Path):
        if not model_path.exists():
            raise FileNotFoundError(f"模型文件不存在：{model_path}")
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError("请安装 requirements-vision.txt 以启用 YOLO 推理。") from exc
        self.model = YOLO(str(model_path))

    def detect(self, frame: object, confidence: float) -> list[Detection]:
        result = self.model(frame, conf=confidence, verbose=False)[0]
        names = result.names
        detections: list[Detection] = []
        for box in result.boxes:
            label = names[int(box.cls[0])]
            detections.append(Detection(label=str(label), confidence=float(box.conf[0])))
        return detections

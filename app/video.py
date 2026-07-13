from __future__ import annotations

from pathlib import Path

import cv2

from .review import Detector, review_frames


def sample_video(video_path: Path, sample_seconds: float, max_frames: int = 120) -> list[tuple[float, object]]:
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError("无法读取视频文件。")
    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    step = max(int(fps * sample_seconds), 1)
    frames: list[tuple[float, object]] = []
    frame_index = 0
    while len(frames) < max_frames:
        ok, frame = capture.read()
        if not ok:
            break
        if frame_index % step == 0:
            frames.append((frame_index / fps, frame))
        frame_index += 1
    capture.release()
    if not frames:
        raise ValueError("视频中没有可分析的画面。")
    return frames


def analyze_video(video_path: Path, detector: Detector, sample_seconds: float, confidence: float) -> dict:
    frames = sample_video(video_path, sample_seconds)
    report = review_frames(detector, frames, confidence)
    report.update({
        "video": video_path.name,
        "sample_seconds": sample_seconds,
        "confidence_threshold": confidence,
    })
    return report

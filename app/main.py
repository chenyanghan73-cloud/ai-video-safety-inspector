from __future__ import annotations

import json
import os
import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .detector import YOLODetector
from .video import analyze_video

ROOT = Path(__file__).resolve().parent.parent
STATIC = Path(__file__).resolve().parent / "static"
ALLOWED_VIDEO_TYPES = {".mp4", ".avi", ".mov", ".mkv"}


def create_app(data_dir: Path | None = None, model_path: Path | None = None) -> FastAPI:
    data = data_dir or ROOT / "data"
    uploads = data / "uploads"
    reports = data / "reports"
    uploads.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    configured_model = model_path or (Path(os.getenv("MODEL_PATH")) if os.getenv("MODEL_PATH") else None)

    app = FastAPI(title="AI 视频安全巡检台", version="1.0.0")
    app.state.uploads = uploads
    app.state.reports = reports
    app.state.model_path = configured_model
    app.state.detector = None
    app.mount("/static", StaticFiles(directory=STATIC), name="static")

    def detector() -> YOLODetector:
        if app.state.model_path is None:
            raise HTTPException(status_code=503, detail="未配置 MODEL_PATH，无法执行模型推理。")
        if app.state.detector is None:
            try:
                app.state.detector = YOLODetector(app.state.model_path)
            except (FileNotFoundError, RuntimeError) as exc:
                raise HTTPException(status_code=503, detail=str(exc)) from exc
        return app.state.detector

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    @app.get("/api/health")
    def health() -> dict:
        return {
            "status": "ok",
            "model_configured": bool(app.state.model_path),
            "model_exists": bool(app.state.model_path and app.state.model_path.exists()),
        }

    @app.post("/api/analyze")
    def analyze(
        file: UploadFile = File(...),
        sample_seconds: float = Form(2.0, ge=0.2, le=10.0),
        confidence: float = Form(0.5, ge=0.1, le=0.95),
    ) -> dict:
        filename = Path(file.filename or "").name
        if Path(filename).suffix.lower() not in ALLOWED_VIDEO_TYPES:
            raise HTTPException(status_code=400, detail="仅支持 MP4、AVI、MOV、MKV 视频。")
        report_id = uuid.uuid4().hex[:10]
        target = uploads / f"{report_id}_{filename}"
        with target.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)
        try:
            report = analyze_video(target, detector(), sample_seconds, confidence)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        report["report_id"] = report_id
        (reports / f"{report_id}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return report

    @app.get("/api/reports/{report_id}")
    def get_report(report_id: str) -> dict:
        report_file = reports / f"{report_id}.json"
        if not report_file.exists():
            raise HTTPException(status_code=404, detail="报告不存在。")
        return json.loads(report_file.read_text(encoding="utf-8"))

    return app


app = create_app()

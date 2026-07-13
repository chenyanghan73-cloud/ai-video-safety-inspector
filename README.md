# AI 视频安全巡检台

一个面向校园、园区和安防场景的视频审核应用。用户上传视频后，服务按时间间隔抽帧，调用 YOLO 模型识别风险目标，生成事件时间线、类别统计和可追溯的审计报告。

> 本项目用于 AI 视频分析作品集演示。模型预测不能替代人工复核或安全应急决策。

## 功能

- 上传 MP4、AVI、MOV 视频并按固定间隔抽帧
- 通过 Ultralytics YOLO 模型检测目标，保留时间戳、类别和置信度
- 基于规则将刀具等高风险类别标记为“高风险”，生成事件时间线与统计摘要
- 输出 JSON 审计报告，支持前端查看关键帧和事件详情
- 模型路径通过 `MODEL_PATH` 环境变量配置，模型权重不进入仓库

## 技术栈

`Python` · `FastAPI` · `OpenCV` · `Ultralytics YOLO` · `HTML/CSS/JavaScript`

## 快速开始

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-vision.txt
$env:MODEL_PATH="C:\path\to\best.pt"
uvicorn app.main:app --reload --port 8001
```

访问 `http://127.0.0.1:8001`。首次上传视频前必须配置模型路径。

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/health` | 服务和模型配置状态 |
| `POST` | `/api/analyze` | 上传视频并生成巡检报告 |
| `GET` | `/api/reports/{report_id}` | 获取历史报告 |

## 测试

```bash
pytest --cov=app --cov-report=term-missing
```

## 简历描述

**AI 视频安全巡检台 | 个人项目**

- 基于 FastAPI 与 OpenCV 搭建视频安全巡检服务，支持视频上传、定时抽帧、目标检测、事件时间线和 JSON 审计报告输出；
- 集成 Ultralytics YOLO 推理接口，记录目标类别、置信度和发生时间，并通过可配置规则划分高/中/低风险事件；
- 设计模型路径、阈值、抽帧间隔等可配置参数，避免将模型权重耦合进代码仓库；
- 编写巡检规则、报告聚合和 API 输入校验测试，覆盖无事件、风险事件和异常文件场景。

## 下一步

- 支持实时 RTSP 流与异步任务队列
- 增加目标跟踪、危险区域和告警推送
- 将报告写入 SQLite/PostgreSQL，支持按时间和风险级别检索
- 增加视频片段裁剪和关键帧标注导出

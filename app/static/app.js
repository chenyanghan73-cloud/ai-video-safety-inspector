const form = document.querySelector("#analysis-form");
const fileInput = document.querySelector("#video-file");
const filename = document.querySelector("#filename");
const status = document.querySelector("#form-status");
const modelState = document.querySelector("#model-state");
const riskBadge = document.querySelector("#risk-badge");

function secondsToTime(value) {
  const minutes = Math.floor(value / 60).toString().padStart(2, "0");
  const seconds = Math.floor(value % 60).toString().padStart(2, "0");
  return `00:${minutes}:${seconds}`;
}

function renderReport(report) {
  document.querySelector("#sampled-frames").textContent = report.sampled_frames;
  document.querySelector("#event-count").textContent = report.event_count;
  document.querySelector("#target-count").textContent = Object.keys(report.counts).length;
  riskBadge.textContent = `${report.highest_risk.toUpperCase()} RISK`;
  riskBadge.className = `risk-badge ${report.highest_risk}`;
  const timeline = document.querySelector("#timeline");
  if (!report.events.length) {
    timeline.className = "timeline empty";
    timeline.textContent = "未检测到超过当前阈值的目标。";
    return;
  }
  timeline.className = "timeline";
  timeline.innerHTML = report.events.map((event) => `
    <article class="event"><time>${secondsToTime(event.timestamp_seconds)}</time><strong>${event.label}</strong><span>${event.risk} · ${(event.confidence * 100).toFixed(1)}%</span></article>`).join("");
}

fileInput.addEventListener("change", () => { filename.textContent = fileInput.files[0]?.name || "尚未选择文件"; });

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = fileInput.files[0];
  if (!file) return;
  const payload = new FormData();
  payload.append("file", file);
  payload.append("sample_seconds", document.querySelector("#sample-seconds").value);
  payload.append("confidence", document.querySelector("#confidence").value);
  status.textContent = "正在抽帧并执行模型推理，请稍候...";
  try {
    const response = await fetch("/api/analyze", { method:"POST", body:payload });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "分析失败");
    renderReport(data); status.textContent = `报告 ${data.report_id} 已生成。`;
  } catch (error) { status.textContent = error.message; }
});

fetch("/api/health").then((response) => response.json()).then((data) => {
  modelState.textContent = data.model_exists ? "模型已就绪" : "需配置 MODEL_PATH";
}).catch(() => { modelState.textContent = "服务不可用"; });

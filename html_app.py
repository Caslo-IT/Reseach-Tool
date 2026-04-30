import html
import json
import mimetypes
import os
import threading
import traceback
import uuid
from http import HTTPStatus
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from main import generate_report_assets


BASE_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000

jobs = {}
jobs_lock = threading.Lock()


APP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sacred Art Research Generator</title>
  <style>
    :root {
      --ink: #17303e;
      --muted: #647785;
      --accent: #bb6432;
      --accent-deep: #96471f;
      --bg-top: #f6ede2;
      --bg-bottom: #e8eff3;
      --panel: rgba(255, 255, 255, 0.84);
      --panel-strong: rgba(255, 255, 255, 0.94);
      --line: rgba(58, 83, 98, 0.14);
      --shadow: 0 24px 60px rgba(27, 47, 59, 0.12);
      --success: #356c46;
      --warn: #9d572d;
      --error: #a53b3b;
      --mono: "SFMono-Regular", "Menlo", monospace;
      --sans: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: var(--sans);
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(219, 182, 139, 0.34), transparent 22%),
        radial-gradient(circle at top right, rgba(141, 177, 195, 0.22), transparent 24%),
        linear-gradient(180deg, var(--bg-top), var(--bg-bottom));
    }

    .shell {
      width: min(1200px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }

    .hero, .panel {
      border: 1px solid var(--line);
      border-radius: 26px;
      background: var(--panel);
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }

    .hero {
      padding: 24px;
      background:
        linear-gradient(135deg, rgba(255, 250, 242, 0.96), rgba(247, 251, 253, 0.90)),
        radial-gradient(circle at top right, rgba(187, 100, 50, 0.10), transparent 32%);
      margin-bottom: 22px;
    }

    .eyebrow {
      display: inline-block;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(187, 100, 50, 0.11);
      color: var(--accent-deep);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    h1 {
      margin: 14px 0 8px;
      font-size: clamp(2rem, 4vw, 3rem);
      line-height: 1.05;
      letter-spacing: -0.04em;
    }

    .hero p, .help, .subtle { color: var(--muted); }
    .grid {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 22px;
    }

    .panel { padding: 22px; }
    .panel h2 { margin: 0 0 6px; font-size: 1.1rem; }

    label {
      display: block;
      margin-bottom: 10px;
      font-size: 0.92rem;
      font-weight: 700;
    }

    textarea {
      width: 100%;
      min-height: 180px;
      resize: vertical;
      padding: 16px;
      border-radius: 18px;
      border: 1px solid rgba(86, 111, 125, 0.18);
      background: rgba(255, 255, 255, 0.9);
      color: var(--ink);
      font: inherit;
      line-height: 1.55;
    }

    .examples {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 14px;
    }

    .chip {
      border: 1px solid rgba(86, 111, 125, 0.15);
      background: rgba(255, 255, 255, 0.78);
      color: #284252;
      padding: 10px 12px;
      border-radius: 999px;
      cursor: pointer;
      font-size: 0.9rem;
    }

    .actions {
      display: flex;
      gap: 12px;
      margin-top: 18px;
    }

    button {
      border: none;
      border-radius: 999px;
      padding: 13px 18px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }

    .primary {
      background: linear-gradient(135deg, var(--accent), var(--accent-deep));
      color: #fff;
      box-shadow: 0 14px 28px rgba(169, 82, 40, 0.24);
    }

    .secondary {
      background: rgba(255, 255, 255, 0.86);
      color: #284252;
      border: 1px solid rgba(86, 111, 125, 0.18);
    }

    .status-card {
      border-radius: 20px;
      border: 1px solid rgba(72, 102, 119, 0.12);
      padding: 18px;
      background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(246,249,250,0.92));
    }

    .status-top {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }

    .status-label {
      display: block;
      margin-bottom: 6px;
      font-size: 0.78rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }

    .status-value {
      font-size: 1.9rem;
      line-height: 1;
      font-weight: 700;
    }

    .badge {
      padding: 8px 12px;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
    }

    .idle { background: rgba(115, 139, 153, 0.14); color: #3e5a69; }
    .running { background: rgba(201, 111, 59, 0.14); color: var(--warn); }
    .done { background: rgba(88, 144, 102, 0.16); color: var(--success); }
    .error { background: rgba(165, 59, 59, 0.14); color: var(--error); }

    .progress {
      height: 10px;
      background: rgba(126, 147, 158, 0.18);
      border-radius: 999px;
      overflow: hidden;
      margin-top: 14px;
    }

    .progress-bar {
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, #d08b5c, #a85428);
      transition: width 0.3s ease;
    }

    .metric-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin-top: 16px;
    }

    .metric {
      padding: 16px;
      border-radius: 18px;
      border: 1px solid rgba(91, 115, 128, 0.12);
      background: var(--panel-strong);
    }

    .metric-label {
      display: block;
      font-size: 0.78rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #6a7f8e;
      margin-bottom: 8px;
    }

    .metric-value {
      display: block;
      font-size: 1.7rem;
      font-weight: 700;
    }

    .metric-note {
      margin-top: 8px;
      color: #5b6f7d;
      font-size: 0.92rem;
    }

    .downloads {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 16px;
    }

    .download-link {
      display: inline-block;
      text-decoration: none;
      color: #134968;
      background: rgba(255, 255, 255, 0.9);
      border: 1px solid rgba(86, 111, 125, 0.18);
      padding: 10px 12px;
      border-radius: 999px;
    }

    .section-stack {
      display: grid;
      gap: 22px;
      margin-top: 22px;
    }

    .preview {
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.6;
      background: rgba(255, 255, 255, 0.86);
      border: 1px solid rgba(86, 111, 125, 0.14);
      border-radius: 18px;
      padding: 16px;
      max-height: 520px;
      overflow: auto;
    }

    .code {
      font-family: var(--mono);
      font-size: 0.88rem;
    }

    .hidden { display: none; }

    @media (max-width: 960px) {
      .grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 640px) {
      .shell { width: min(100vw - 20px, 100%); padding-top: 18px; }
      .hero, .panel { padding: 18px; border-radius: 22px; }
      .metric-grid { grid-template-columns: 1fr; }
      .actions { flex-direction: column; }
      button { width: 100%; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <span class="eyebrow">Sacred Art Research Generator</span>
      <h1>HTML interface for research, previews, and downloads.</h1>
      <p>Generate the Sinhala report, Word file, PDF, and sketch prompt JSON from one browser page.</p>
    </section>

    <section class="grid">
      <div class="panel">
        <h2>Input</h2>
        <p class="help">Describe the deity, statue, or sacred figure you want researched.</p>
        <form id="generator-form">
          <label for="subject">Research Subject</label>
          <textarea id="subject" name="subject" placeholder="Example: Kataragama deviyo statue design for Sri Lankan sculptural reference with traditional ornaments and symbolic attributes"></textarea>
          <div class="examples">
            <button type="button" class="chip" data-example="Kataragama deviyo statue design for Sri Lankan sculptural reference">Kataragama deviyo</button>
            <button type="button" class="chip" data-example="Pattini deviyo sacred statue study with ornaments, symbolism, and regional worship context">Pattini deviyo</button>
            <button type="button" class="chip" data-example="Avalokiteshvara bodhisattva statue reference for temple mural and sculpture design in Sri Lanka">Avalokiteshvara</button>
            <button type="button" class="chip" data-example="Natha deviyo standing statue with traditional crown, hand gestures, and pedestal symbolism">Natha deviyo</button>
          </div>
          <div class="actions">
            <button type="submit" class="primary" id="run-button">Generate Research Package</button>
            <button type="button" class="secondary" id="clear-button">Clear Workspace</button>
          </div>
        </form>
      </div>

      <div class="panel">
        <h2>Output</h2>
        <div class="status-card">
          <div class="status-top">
            <div>
              <span class="status-label">Run Status</span>
              <div class="status-value" id="status-value">Ready</div>
            </div>
            <span class="badge idle" id="status-badge">Ready</span>
          </div>
          <p class="subtle" id="status-detail">Enter a subject to begin.</p>
          <div class="progress"><div class="progress-bar" id="progress-bar"></div></div>
        </div>

        <div class="metric-grid" id="metrics">
          <div class="metric">
            <span class="metric-label">Requests</span>
            <span class="metric-value">0</span>
            <div class="metric-note">Gemini calls used in this generation</div>
          </div>
          <div class="metric">
            <span class="metric-label">Total Tokens</span>
            <span class="metric-value">0</span>
            <div class="metric-note">Prompt and response tokens combined</div>
          </div>
          <div class="metric">
            <span class="metric-label">Generation Time</span>
            <span class="metric-value">0.00s</span>
            <div class="metric-note">Measured end-to-end for this run</div>
          </div>
          <div class="metric">
            <span class="metric-label">Output Tokens</span>
            <span class="metric-value">0</span>
            <div class="metric-note">Input 0 tokens</div>
          </div>
        </div>

        <div class="downloads hidden" id="downloads"></div>
      </div>
    </section>

    <section class="section-stack">
      <div class="panel">
        <h2>Processing Log</h2>
        <div class="preview code" id="log-preview">Generation updates will appear here.</div>
      </div>

      <div class="panel">
        <h2>Report Preview</h2>
        <div class="preview" id="report-preview">Generated report preview will appear here.</div>
      </div>

      <div class="panel">
        <h2>Sketch Prompt Preview</h2>
        <div class="preview code" id="json-preview">[
  {
    "id": 1,
    "title": "Preview pending",
    "prompt": "Run the generator to preview the statue sketch prompts."
  }
]</div>
      </div>
    </section>
  </main>

  <script>
    const form = document.getElementById("generator-form");
    const subjectInput = document.getElementById("subject");
    const runButton = document.getElementById("run-button");
    const clearButton = document.getElementById("clear-button");
    const statusValue = document.getElementById("status-value");
    const statusBadge = document.getElementById("status-badge");
    const statusDetail = document.getElementById("status-detail");
    const progressBar = document.getElementById("progress-bar");
    const metrics = document.getElementById("metrics");
    const downloads = document.getElementById("downloads");
    const logPreview = document.getElementById("log-preview");
    const reportPreview = document.getElementById("report-preview");
    const jsonPreview = document.getElementById("json-preview");

    let activeJobId = null;
    let pollTimer = null;

    const defaultJson = `[
  {
    "id": 1,
    "title": "Preview pending",
    "prompt": "Run the generator to preview the statue sketch prompts."
  }
]`;

    document.querySelectorAll("[data-example]").forEach((button) => {
      button.addEventListener("click", () => {
        subjectInput.value = button.dataset.example;
      });
    });

    function setStatus({ label, detail, state, progress }) {
      statusValue.textContent = label;
      statusDetail.textContent = detail;
      statusBadge.textContent = state.charAt(0).toUpperCase() + state.slice(1);
      statusBadge.className = `badge ${state}`;
      progressBar.style.width = `${Math.max(0, Math.min(progress || 0, 100))}%`;
    }

    function renderMetrics(data) {
      const values = data || {};
      metrics.innerHTML = `
        <div class="metric">
          <span class="metric-label">Requests</span>
          <span class="metric-value">${values.requests || 0}</span>
          <div class="metric-note">Gemini calls used in this generation</div>
        </div>
        <div class="metric">
          <span class="metric-label">Total Tokens</span>
          <span class="metric-value">${Number(values.total_tokens || 0).toLocaleString()}</span>
          <div class="metric-note">Prompt and response tokens combined</div>
        </div>
        <div class="metric">
          <span class="metric-label">Generation Time</span>
          <span class="metric-value">${Number(values.generation_time_seconds || 0).toFixed(2)}s</span>
          <div class="metric-note">Measured end-to-end for this run</div>
        </div>
        <div class="metric">
          <span class="metric-label">Output Tokens</span>
          <span class="metric-value">${Number(values.output_tokens || 0).toLocaleString()}</span>
          <div class="metric-note">Input ${Number(values.input_tokens || 0).toLocaleString()} tokens</div>
        </div>
      `;
    }

    function renderDownloads(jobId, files) {
      if (!files) {
        downloads.classList.add("hidden");
        downloads.innerHTML = "";
        return;
      }

      downloads.classList.remove("hidden");
      downloads.innerHTML = `
        <a class="download-link" href="/download/${jobId}/pdf">Download PDF</a>
        <a class="download-link" href="/download/${jobId}/docx">Download Word File</a>
        <a class="download-link" href="/download/${jobId}/json">Download JSON</a>
      `;
    }

    function resetWorkspace() {
      activeJobId = null;
      if (pollTimer) {
        clearTimeout(pollTimer);
        pollTimer = null;
      }
      form.reset();
      setStatus({ label: "Ready", detail: "Enter a subject to begin.", state: "idle", progress: 0 });
      renderMetrics();
      renderDownloads(null, null);
      logPreview.textContent = "Generation updates will appear here.";
      reportPreview.textContent = "Generated report preview will appear here.";
      jsonPreview.textContent = defaultJson;
      runButton.disabled = false;
    }

    async function pollJob(jobId) {
      try {
        const response = await fetch(`/api/jobs/${jobId}`);
        const job = await response.json();

        setStatus({
          label: `${job.progress}%`,
          detail: job.detail || "Working through the report pipeline.",
          state: job.state,
          progress: job.progress
        });

        logPreview.textContent = (job.logs && job.logs.length) ? job.logs.join("\\n") : "Generation updates will appear here.";

        if (job.state === "done") {
          renderMetrics(job.metrics);
          reportPreview.textContent = job.report_text || "Generated report preview will appear here.";
          jsonPreview.textContent = JSON.stringify(job.sketch_prompts || [], null, 2);
          renderDownloads(jobId, job.files);
          runButton.disabled = false;
          return;
        }

        if (job.state === "error") {
          renderMetrics();
          reportPreview.textContent = "Generation failed before a report could be prepared.";
          jsonPreview.textContent = defaultJson;
          renderDownloads(null, null);
          runButton.disabled = false;
          return;
        }

        pollTimer = setTimeout(() => pollJob(jobId), 1200);
      } catch (error) {
        setStatus({
          label: "Error",
          detail: "The browser could not read the current job status.",
          state: "error",
          progress: 100
        });
        runButton.disabled = false;
      }
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const subject = subjectInput.value.trim();
      if (!subject) {
        setStatus({
          label: "Missing input",
          detail: "Research subject input is required.",
          state: "error",
          progress: 100
        });
        return;
      }

      if (pollTimer) {
        clearTimeout(pollTimer);
      }

      runButton.disabled = true;
      renderDownloads(null, null);
      renderMetrics();
      reportPreview.textContent = "Preparing generation workflow...";
      jsonPreview.textContent = defaultJson;
      logPreview.textContent = "2% - Preparing generation workflow";
      setStatus({
        label: "2%",
        detail: "Setting up the report pipeline and validating the research request.",
        state: "running",
        progress: 2
      });

      const response = await fetch("/api/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8" },
        body: new URLSearchParams({ subject })
      });

      const payload = await response.json();
      activeJobId = payload.job_id;
      pollJob(activeJobId);
    });

    clearButton.addEventListener("click", resetWorkspace);
  </script>
</body>
</html>
"""


def json_response(start_response, payload, status=HTTPStatus.OK):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    start_response(f"{status.value} {status.phrase}", headers)
    return [body]


def text_response(start_response, body, status=HTTPStatus.OK, content_type="text/plain; charset=utf-8"):
    payload = body.encode("utf-8")
    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(payload))),
    ]
    start_response(f"{status.value} {status.phrase}", headers)
    return [payload]


def get_job(job_id):
    with jobs_lock:
        return jobs.get(job_id)


def update_job(job_id, **updates):
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id].update(updates)


def append_job_log(job_id, entry):
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id]["logs"].append(entry)


def serialize_job(job):
    payload = {
        "id": job["id"],
        "state": job["state"],
        "progress": job["progress"],
        "detail": job["detail"],
        "logs": job["logs"],
        "metrics": job.get("metrics"),
        "report_text": job.get("report_text"),
        "sketch_prompts": job.get("sketch_prompts"),
        "files": job.get("files"),
        "error": job.get("error"),
    }
    return payload


def run_job(job_id, subject):
    def progress_callback(fraction, message):
        percentage = int(round(fraction * 100))
        append_job_log(job_id, f"{percentage}% - {message}")
        update_job(
            job_id,
            progress=percentage,
            detail=message,
            state="running",
        )

    try:
        result = generate_report_assets(subject, progress_callback=progress_callback)
        update_job(
            job_id,
            state="done",
            progress=100,
            detail="Completed. Your report files are ready to download.",
            report_text=result["report_text"],
            sketch_prompts=result["sketch_prompts"],
            metrics=result["metrics"],
            files={
                "pdf": result["pdf_path"],
                "docx": result["docx_path"],
                "json": result["json_path"],
            },
        )
    except Exception as exc:
        append_job_log(job_id, f"100% - Failed: {exc}")
        update_job(
            job_id,
            state="error",
            progress=100,
            detail=str(exc),
            error={
                "message": str(exc),
                "traceback": traceback.format_exc(),
            },
        )


def create_job(subject):
    job_id = uuid.uuid4().hex
    with jobs_lock:
        jobs[job_id] = {
            "id": job_id,
            "subject": subject,
            "state": "running",
            "progress": 2,
            "detail": "Preparing generation workflow",
            "logs": ["2% - Preparing generation workflow"],
            "metrics": None,
            "report_text": None,
            "sketch_prompts": None,
            "files": None,
            "error": None,
        }

    worker = threading.Thread(target=run_job, args=(job_id, subject), daemon=True)
    worker.start()
    return job_id


def parse_form(environ):
    try:
        length = int(environ.get("CONTENT_LENGTH", "0") or "0")
    except ValueError:
        length = 0
    body = environ["wsgi.input"].read(length).decode("utf-8")
    data = parse_qs(body)
    return {key: values[0] for key, values in data.items() if values}


def resolve_download(job, file_kind):
    files = job.get("files") or {}
    selected = files.get(file_kind)
    if not selected:
        return None

    path = Path(selected).resolve()
    try:
        path.relative_to(BASE_DIR)
    except ValueError:
        return None

    if not path.exists() or not path.is_file():
        return None
    return path


def serve_file(start_response, path):
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    data = path.read_bytes()
    headers = [
        ("Content-Type", mime_type),
        ("Content-Length", str(len(data))),
        ("Content-Disposition", f'attachment; filename="{path.name}"'),
    ]
    start_response(f"{HTTPStatus.OK.value} {HTTPStatus.OK.phrase}", headers)
    return [data]


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/")

    if method == "GET" and path == "/":
        return text_response(start_response, APP_HTML, content_type="text/html; charset=utf-8")

    if method == "POST" and path == "/api/jobs":
        form = parse_form(environ)
        subject = (form.get("subject") or "").strip()
        if not subject:
            return json_response(
                start_response,
                {"error": "Research subject input is required."},
                status=HTTPStatus.BAD_REQUEST,
            )
        job_id = create_job(subject)
        return json_response(start_response, {"job_id": job_id}, status=HTTPStatus.ACCEPTED)

    if method == "GET" and path.startswith("/api/jobs/"):
        job_id = path.rsplit("/", 1)[-1]
        job = get_job(job_id)
        if not job:
            return json_response(
                start_response,
                {"error": "Job not found."},
                status=HTTPStatus.NOT_FOUND,
            )
        return json_response(start_response, serialize_job(job))

    if method == "GET" and path.startswith("/download/"):
        parts = [part for part in path.split("/") if part]
        if len(parts) != 3:
            return text_response(start_response, "Not found.", status=HTTPStatus.NOT_FOUND)
        _, job_id, file_kind = parts
        job = get_job(job_id)
        if not job:
            return text_response(start_response, "Job not found.", status=HTTPStatus.NOT_FOUND)
        file_path = resolve_download(job, file_kind)
        if not file_path:
            return text_response(start_response, "File not found.", status=HTTPStatus.NOT_FOUND)
        return serve_file(start_response, file_path)

    not_found = html.escape(f"{method} {path} not found.")
    return text_response(start_response, not_found, status=HTTPStatus.NOT_FOUND)


def main():
    with make_server(HOST, PORT, app) as server:
        print(f"HTML interface running at http://{HOST}:{PORT}")
        server.serve_forever()


if __name__ == "__main__":
    main()

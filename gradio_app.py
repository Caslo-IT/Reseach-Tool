import json

import gradio as gr

from main import generate_report_assets


APP_CSS = """
:root {
    --ink: #18303f;
    --muted: #5d7180;
    --panel: rgba(255, 252, 247, 0.82);
    --panel-strong: rgba(255, 255, 255, 0.92);
    --line: rgba(59, 84, 99, 0.14);
    --accent: #c96f3b;
    --accent-deep: #a34f24;
    --sage: #d9e6d1;
    --mist: #d8e7ef;
    --shadow: 0 24px 60px rgba(27, 47, 59, 0.12);
}

.gradio-container {
    background:
        radial-gradient(circle at 0% 0%, rgba(222, 191, 149, 0.34), transparent 28%),
        radial-gradient(circle at 100% 0%, rgba(145, 183, 201, 0.24), transparent 30%),
        linear-gradient(180deg, #f8f1e7 0%, #f6f8f7 40%, #edf3f6 100%);
    color: var(--ink);
}

.gradio-container .block-container {
    max-width: 1280px;
    padding-top: 28px;
    padding-bottom: 40px;
}

.app-shell {
    display: flex;
    flex-direction: column;
    gap: 22px;
}

.hero-panel,
.surface-panel,
.soft-panel {
    border: 1px solid var(--line);
    box-shadow: var(--shadow);
    backdrop-filter: blur(10px);
}

.hero-panel {
    padding: 22px;
    border-radius: 26px;
    background:
        linear-gradient(135deg, rgba(255, 250, 242, 0.96), rgba(247, 251, 253, 0.90)),
        radial-gradient(circle at top right, rgba(201, 111, 59, 0.10), transparent 30%);
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(201, 111, 59, 0.10);
    color: var(--accent-deep);
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 700;
}

.hero-title {
    margin: 14px 0 0;
    font-size: clamp(2rem, 4vw, 3rem);
    line-height: 1.05;
    letter-spacing: -0.04em;
    font-weight: 700;
    color: #142936;
}

.surface-panel {
    border-radius: 26px;
    background: var(--panel);
    padding: 22px;
}

.soft-panel {
    border-radius: 22px;
    background: var(--panel-strong);
    padding: 18px;
}

.section-title {
    margin: 0 0 6px;
    font-size: 1.1rem;
    font-weight: 700;
    color: #173142;
}

.section-copy {
    margin: 0;
    color: var(--muted);
    line-height: 1.6;
}

.status-card {
    border-radius: 20px;
    border: 1px solid rgba(72, 102, 119, 0.12);
    padding: 18px;
    background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(246, 249, 250, 0.92));
}

.status-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 14px;
}

.status-label {
    display: block;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 6px;
}

.status-value {
    font-size: 1.85rem;
    line-height: 1;
    font-weight: 700;
    color: #132a37;
}

.status-badge {
    padding: 8px 12px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.status-idle {
    background: rgba(115, 139, 153, 0.14);
    color: #3e5a69;
}

.status-running {
    background: rgba(201, 111, 59, 0.14);
    color: #9c542d;
}

.status-done {
    background: rgba(88, 144, 102, 0.16);
    color: #376f46;
}

.status-subtext {
    margin: 0;
    color: var(--muted);
    line-height: 1.55;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.metric-card {
    padding: 18px;
    border-radius: 20px;
    border: 1px solid rgba(91, 115, 128, 0.12);
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(247,250,252,0.92));
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
    font-size: 1.9rem;
    line-height: 1.08;
    color: #132c38;
    font-weight: 700;
}

.metric-note {
    display: block;
    margin-top: 8px;
    color: #5b6f7d;
    font-size: 0.94rem;
}

.gradio-container h1,
.gradio-container h2,
.gradio-container h3,
.gradio-container label,
.gradio-container .prose,
.gradio-container .prose p,
.gradio-container .prose li,
.gradio-container .prose strong,
.gradio-container .prose code,
.gradio-container .prose td,
.gradio-container .prose th,
.gradio-container .prose blockquote {
    color: var(--ink) !important;
}

.gradio-container .prose a {
    color: #0d557f !important;
}

.gradio-container .gr-textbox,
.gradio-container .gr-code,
.gradio-container .gr-file,
.gradio-container .gr-markdown,
.gradio-container .tabitem,
.gradio-container .gr-accordion {
    border-radius: 20px !important;
    border-color: rgba(86, 111, 125, 0.14) !important;
    background: rgba(255, 255, 255, 0.78) !important;
}

.gradio-container .gr-button-primary {
    background: linear-gradient(135deg, #c96f3b, #a85124) !important;
    border: none !important;
    box-shadow: 0 14px 28px rgba(169, 82, 40, 0.24);
}

.gradio-container .gr-button-secondary {
    border-color: rgba(68, 97, 111, 0.18) !important;
    color: #254151 !important;
}

.gradio-container .gr-form {
    border: none !important;
}

@media (max-width: 980px) {
    .metric-grid {
        grid-template-columns: 1fr 1fr;
    }
}

@media (max-width: 640px) {
    .hero-panel,
    .surface-panel,
    .soft-panel {
        padding: 18px;
        border-radius: 22px;
    }

    .metric-grid {
        grid-template-columns: 1fr;
    }

    .status-top {
        flex-direction: column;
        align-items: flex-start;
    }
}
"""


def build_metric_cards(metrics=None):
    metrics = metrics or {}
    cards = [
        ("Requests", str(metrics.get("requests", 0)), "Gemini calls used in this generation"),
        ("Total Tokens", f"{metrics.get('total_tokens', 0):,}", "Prompt and response tokens combined"),
        ("Generation Time", f"{metrics.get('generation_time_seconds', 0):.2f}s", "Measured end-to-end for this run"),
        (
            "Output Tokens",
            f"{metrics.get('output_tokens', 0):,}",
            f"Input {metrics.get('input_tokens', 0):,} tokens",
        ),
    ]

    html = ['<div class="metric-grid">']
    for label, value, note in cards:
        html.append(
            f"""
            <div class="metric-card">
                <span class="metric-label">{label}</span>
                <span class="metric-value">{value}</span>
                <span class="metric-note">{note}</span>
            </div>
            """
        )
    html.append("</div>")
    return "".join(html)


def build_status_card(progress_label="Ready", detail="Enter a subject to begin.", state="idle"):
    state_map = {
        "idle": ("Ready", "status-idle"),
        "running": ("Working", "status-running"),
        "done": ("Completed", "status-done"),
    }
    badge_text, badge_class = state_map.get(state, state_map["idle"])
    return f"""
    <div class="status-card">
        <div class="status-top">
            <div>
                <span class="status-label">Run Status</span>
                <div class="status-value">{progress_label}</div>
            </div>
            <span class="status-badge {badge_class}">{badge_text}</span>
        </div>
        <p class="status-subtext">{detail}</p>
    </div>
    """


def default_report_preview():
    return (
        "Generated report preview will appear here."
    )


def default_json_preview():
    return (
        '[\n'
        '  {\n'
        '    "id": 1,\n'
        '    "title": "Preview pending",\n'
        '    "prompt": "Run the generator to preview the statue sketch prompts."\n'
        "  }\n"
        "]"
    )


def build_reset_state():
    return (
        "",
        build_status_card(),
        "",
        build_metric_cards(),
        default_report_preview(),
        default_json_preview(),
        None,
        None,
        None,
    )


def run_generation(subject, progress=gr.Progress(track_tqdm=False)):
    if not subject or not subject.strip():
        raise gr.Error("Research subject input is required.")

    status_messages = []

    def push_update(fraction, message):
        percentage = int(round(fraction * 100))
        status_messages.append(f"{percentage}% - {message}")
        progress(fraction, desc=message)

    def progress_callback(fraction, message):
        push_update(fraction, message)

    push_update(0.02, "Preparing generation workflow")
    yield (
        build_status_card(
            "2%",
            "Setting up the report pipeline and validating the research request.",
            "running",
        ),
        "\n".join(status_messages),
        build_metric_cards(),
        "",
        "",
        None,
        None,
        None,
    )

    try:
        result = generate_report_assets(subject, progress_callback=progress_callback)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc

    json_preview = json.dumps(result["sketch_prompts"], ensure_ascii=False, indent=2)
    latest_message = status_messages[-1] if status_messages else "Generation completed."

    yield (
        build_status_card(
            "100%",
            f"{latest_message} Your report files are ready to download.",
            "done",
        ),
        "\n".join(status_messages),
        build_metric_cards(result["metrics"]),
        result["report_text"],
        json_preview,
        result["pdf_path"],
        result["docx_path"],
        result["json_path"],
    )


with gr.Blocks(title="Sacred Art Research Generator") as demo:
    gr.HTML(
        """
        <div class="app-shell">
            <section class="hero-panel">
                <span class="eyebrow">Sacred Art Research Generator</span>
                <h1 class="hero-title">Input and output, kept simple.</h1>
            </section>
        </div>
        """
    )

    with gr.Row(equal_height=True):
        with gr.Column(scale=7):
            gr.HTML(
                """
                <section class="surface-panel">
                    <h2 class="section-title">Input</h2>
                </section>
                """
            )
            subject_input = gr.Textbox(
                label="Research Subject",
                placeholder="Example: Kataragama deviyo statue design for Sri Lankan sculptural reference with traditional ornaments and symbolic attributes",
                lines=8,
            )
            gr.Examples(
                examples=[
                    ["Kataragama deviyo statue design for Sri Lankan sculptural reference"],
                    ["Pattini deviyo sacred statue study with ornaments, symbolism, and regional worship context"],
                    ["Avalokiteshvara bodhisattva statue reference for temple mural and sculpture design in Sri Lanka"],
                    ["Natha deviyo standing statue with traditional crown, hand gestures, and pedestal symbolism"],
                ],
                inputs=[subject_input],
                label="Quick Start Examples",
            )
            with gr.Row():
                run_button = gr.Button("Generate Research Package", variant="primary", size="lg")
                clear_button = gr.Button("Clear Workspace", variant="secondary", size="lg")

        with gr.Column(scale=5):
            gr.HTML(
                """
                <section class="surface-panel">
                    <h2 class="section-title">Output</h2>
                </section>
                """
            )
            status_output = gr.HTML(value=build_status_card())
            log_output = gr.Textbox(
                label="Processing Log",
                interactive=False,
                lines=8,
                placeholder="Generation updates will appear here.",
            )
            metrics_output = gr.HTML(value=build_metric_cards())
    with gr.Row():
        pdf_output = gr.File(label="Research PDF")
        docx_output = gr.File(label="Research Word File")
        json_output = gr.File(label="Sketch Prompt JSON")

    with gr.Tabs():
        with gr.Tab("Report Preview"):
            report_preview = gr.Markdown(value=default_report_preview())
        with gr.Tab("Sketch Prompt Preview"):
            json_preview = gr.Code(
                label="Sketch Prompt JSON",
                language="json",
                value=default_json_preview(),
            )

    run_button.click(
        fn=run_generation,
        inputs=[subject_input],
        outputs=[
            status_output,
            log_output,
            metrics_output,
            report_preview,
            json_preview,
            pdf_output,
            docx_output,
            json_output,
        ],
    )

    clear_button.click(
        fn=build_reset_state,
        outputs=[
            subject_input,
            status_output,
            log_output,
            metrics_output,
            report_preview,
            json_preview,
            pdf_output,
            docx_output,
            json_output,
        ],
    )


if __name__ == "__main__":
    demo.queue().launch(theme=gr.themes.Soft(), css=APP_CSS)

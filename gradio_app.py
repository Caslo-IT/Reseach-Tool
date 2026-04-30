import json

import gradio as gr

from main import generate_report_assets


APP_CSS = """
.gradio-container {
    background:
        radial-gradient(circle at top left, #f8e8cb 0%, transparent 28%),
        radial-gradient(circle at top right, #dceaf6 0%, transparent 26%),
        linear-gradient(180deg, #f5f0e8 0%, #fbfaf7 46%, #eef3f8 100%);
    color: #102a43;
}

#hero {
    padding: 28px;
    border: 1px solid rgba(70, 88, 102, 0.12);
    border-radius: 24px;
    background: rgba(255, 252, 246, 0.88);
    box-shadow: 0 22px 50px rgba(35, 52, 66, 0.10);
    backdrop-filter: blur(8px);
}

#hero h1 {
    margin-bottom: 10px;
    font-size: 2.4rem;
    color: #102a43;
}

#hero p {
    margin: 0;
    color: #334e68;
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
    color: #102a43 !important;
}

.gradio-container .prose a {
    color: #0f4c81 !important;
}

.gradio-container .tabitem,
.gradio-container .gr-markdown,
.gradio-container .gr-code,
.gradio-container .gr-textbox,
.gradio-container .gr-file {
    background: rgba(255, 255, 255, 0.82);
    border-radius: 18px;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
}

.metric-card {
    padding: 18px;
    border-radius: 18px;
    border: 1px solid rgba(104, 122, 138, 0.12);
    background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(247,250,252,0.92));
    box-shadow: 0 12px 30px rgba(49, 68, 82, 0.08);
}

.metric-label {
    display: block;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 8px;
}

.metric-value {
    display: block;
    font-size: 1.9rem;
    line-height: 1.1;
    color: #102a43;
    font-weight: 700;
}

.metric-note {
    display: block;
    margin-top: 8px;
    color: #52606d;
    font-size: 0.92rem;
}

@media (max-width: 900px) {
    .metric-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 640px) {
    .metric-grid {
        grid-template-columns: 1fr;
    }
}
"""


def build_metric_cards(metrics=None):
    metrics = metrics or {}
    cards = [
        ("Requests", str(metrics.get("requests", 0)), "Gemini calls in this run"),
        ("Total Tokens", f"{metrics.get('total_tokens', 0):,}", "Prompt + output tokens"),
        ("Generation Time", f"{metrics.get('generation_time_seconds', 0):.2f}s", "End-to-end processing"),
        (
            "Output Split",
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
        "2%",
        "\n".join(status_messages),
        build_metric_cards(),
        "",
        "",
        None,
        None,
    )

    result = generate_report_assets(subject, progress_callback=progress_callback)

    json_preview = json.dumps(result["sketch_prompts"], ensure_ascii=False, indent=2)

    yield (
        "100%",
        "\n".join(status_messages),
        build_metric_cards(result["metrics"]),
        result["report_text"],
        json_preview,
        result["pdf_path"],
        result["json_path"],
    )


with gr.Blocks(title="Sacred Art Research Generator", css=APP_CSS, theme=gr.themes.Soft()) as demo:
    gr.HTML(
        """
        <section id="hero">
            <h1>Sacred Art Research Generator</h1>
            <p>
                Generate a Sinhala research report, track token and request usage, measure generation time,
                and download both the PDF and sketch-prompt JSON from one workspace.
            </p>
        </section>
        """
    )

    with gr.Row(equal_height=True):
        with gr.Column(scale=5):
            subject_input = gr.Textbox(
                label="Research Subject",
                placeholder="Example: Kataragama deviyo statue design for Sri Lankan sculptural reference",
                lines=6,
            )
        with gr.Column(scale=2):
            progress_output = gr.Textbox(label="Progress", interactive=False)
            run_button = gr.Button("Generate Report", variant="primary", size="lg")

    metrics_output = gr.HTML(value=build_metric_cards())
    status_output = gr.Textbox(label="Processing Log", interactive=False, lines=8)

    with gr.Row():
        pdf_output = gr.File(label="Research PDF")
        json_output = gr.File(label="Sketch Prompt JSON")

    with gr.Tabs():
        with gr.Tab("Report Preview"):
            report_preview = gr.Markdown(
                value="The generated Sinhala report will appear here after the run completes.",
            )
        with gr.Tab("JSON Preview"):
            json_preview = gr.Code(
                label="Sketch Prompt Preview",
                language="json",
                value='[\n  {\n    "id": 1,\n    "title": "Preview pending",\n    "prompt": "Run the generator to preview sketch prompts."\n  }\n]',
            )

    run_button.click(
        fn=run_generation,
        inputs=[subject_input],
        outputs=[
            progress_output,
            status_output,
            metrics_output,
            report_preview,
            json_preview,
            pdf_output,
            json_output,
        ],
    )


if __name__ == "__main__":
    demo.queue().launch()

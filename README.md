# Sacred Art Research Generator

This project generates:

- A Sinhala research PDF for a statue, deity, or sacred figure
- A `sketch_prompts.json` file with 30 image-generation sketch prompts

It supports both:

- A Gradio web interface
- A command-line run with `main.py`

## Requirements

- Python 3.10 or newer
- A valid Gemini API key

## Setup

1. Create a Python virtual environment:

```bash
python3 -m venv .venv
```

2. Activate the virtual environment:

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

5. When you are done, you can leave the virtual environment with:

```bash
deactivate
```

## Run the Gradio Interface

Start the web app with:

```bash
python3 gradio_app.py
```

After it starts:

1. Open the local Gradio URL shown in the terminal
2. Enter the research subject
3. Click `Run Generation`

The interface will show:

- Processing percentage
- Processing log
- Output file names
- Generated PDF file
- Generated JSON file

## Run from Command Line

You can also run the original command-line version:

```bash
python3 main.py
```

Then enter the statue or deity research subject when prompted.

## Output Location

Generated files are saved inside the `Resources` folder in a timestamped directory:

```text
Resources/report_YYYYMMDD_HHMMSS/
```

Each run creates:

- `research_report.pdf`
- `sketch_prompts.json`

## Project Files

- `gradio_app.py` - Gradio user interface
- `main.py` - Core report and JSON generation pipeline
- `generate_sketch_prompts.py` - Standalone sketch prompt generator
- `requirements.txt` - Python dependencies

## Notes

- The app requires `GEMINI_API_KEY` to be set before running
- The Sinhala PDF rendering depends on the included `fonts/FM Ganganee x.ttf` font
- Each run creates a new output folder, so the application can be used repeatedly without overwriting previous results

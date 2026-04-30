import argparse
import json
import os
import sys
from pathlib import Path

from google.genai import errors as genai_errors


MODEL_NAME = "gemini-2.5-flash"


def load_dotenv():
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return

    with env_path.open(encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def build_client():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Add it to .env or your environment.")
    from google import genai

    return genai.Client(api_key=api_key)


def format_gemini_error(exc):
    message = str(exc)

    if isinstance(exc, genai_errors.ClientError) and exc.status_code == 403:
        return (
            "Gemini request failed with 403 PERMISSION_DENIED.\n"
            "Google accepted the request format, but the API key's project is not allowed to use this model.\n"
            "Most likely fixes:\n"
            "1. Create or use a Gemini API key from Google AI Studio for a project with Gemini API access enabled.\n"
            "2. Replace GEMINI_API_KEY in .env with that key.\n"
            "3. If this key belongs to a restricted or suspended Google Cloud project, switch to a different project.\n"
            "4. If Google already denied the project, contact Google support because the script cannot bypass that restriction."
        )

    return f"Gemini request failed: {message}"


def latest_report_dir():
    resources_dir = Path(__file__).with_name("Resources")
    if not resources_dir.exists():
        raise FileNotFoundError("Resources directory was not found.")

    report_dirs = [path for path in resources_dir.iterdir() if path.is_dir() and path.name.startswith("report_")]
    if not report_dirs:
        raise FileNotFoundError("No report directories were found inside Resources.")

    return max(report_dirs, key=lambda path: path.stat().st_mtime)


def read_source_text(args):
    if args.input_file:
        return Path(args.input_file).read_text(encoding="utf-8").strip()

    if args.subject:
        return args.subject.strip()

    print("Paste the research details or subject for prompt generation, then press Ctrl-D:")
    return sys.stdin.read().strip()


def build_prompt(source_text):
    return f"""You are an expert prompt writer for AI image generation.

Create sketch-image prompts based strictly on the research details below.

Requirements:
- Return JSON array only.
- No markdown.
- No explanation text.
- Generate exactly 30 items.
- Items 1 to 10 must be full-body compositions.
- Items 11 to 30 must be close-up compositions.
- Every prompt must clearly describe a square 1:1 ratio composition.
- Every prompt must be for a pencil or graphite sketch on a clean white paper background.
- Keep the subject visually consistent across all 30 prompts.
- Make each title unique, concise, and descriptive.
- Each object must follow this schema exactly:
  {{
    "id": <number>,
    "title": "<title>",
    "prompt": "<prompt>"
  }}
- The prompt text must be detailed and production-ready for image generation.
- Mention whether the shot is full-body or close-up naturally inside each prompt.
- Emphasize high detail, clean linework, refined shading, and centered composition when appropriate.

Research details:
{source_text}
"""


def extract_json_array(raw_text):
    text = raw_text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("Model response was not a JSON array.")
    if len(data) != 30:
        raise ValueError(f"Expected 30 prompt items, but received {len(data)}.")

    return data


def validate_items(items):
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Item {index} is not an object.")

        if item.get("id") != index:
            raise ValueError(f"Item {index} has an invalid id: {item.get('id')}")

        title = item.get("title")
        prompt = item.get("prompt")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"Item {index} is missing a valid title.")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"Item {index} is missing a valid prompt.")


def output_path_from_args(args):
    if args.output:
        return Path(args.output)

    report_dir = Path(args.report_dir) if args.report_dir else latest_report_dir()
    return report_dir / "sketch_prompts.json"


def main():
    parser = argparse.ArgumentParser(
        description="Generate 30 sketch image prompts as a JSON array and save them beside the research PDF."
    )
    parser.add_argument("--subject", help="Research subject or short description to base the prompts on.")
    parser.add_argument("--input-file", help="Path to a text/markdown file containing detailed research notes.")
    parser.add_argument("--report-dir", help="Specific report directory inside Resources where the JSON should be saved.")
    parser.add_argument("--output", help="Exact output JSON file path.")
    args = parser.parse_args()

    try:
        source_text = read_source_text(args)
        if not source_text:
            raise ValueError("Research details or subject input is required.")

        client = build_client()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=build_prompt(source_text),
        )

        raw_text = response.text or "[]"
        items = extract_json_array(raw_text)
        validate_items(items)

        output_path = output_path_from_args(args)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

        print(json.dumps(items, ensure_ascii=False, indent=2))
        print(f"\nSaved JSON: {output_path}")
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except genai_errors.APIError as exc:
        print(format_gemini_error(exc), file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()

import json
import unittest

from main import extract_json_array, parse_table_row, validate_sketch_prompts


def build_valid_items():
    return [
        {
            "id": index,
            "title": f"Title {index}",
            "prompt": f"Prompt {index}",
        }
        for index in range(1, 31)
    ]


class TestMainHelpers(unittest.TestCase):
    def test_extract_json_array_accepts_fenced_json(self):
        raw_text = "```json\n" + json.dumps(build_valid_items()) + "\n```"

        items = extract_json_array(raw_text)

        self.assertEqual(len(items), 30)
        self.assertEqual(items[0]["id"], 1)
        self.assertEqual(items[-1]["id"], 30)

    def test_extract_json_array_rejects_wrong_item_count(self):
        raw_text = json.dumps(build_valid_items()[:2])

        with self.assertRaisesRegex(ValueError, "Expected 30 sketch prompts"):
            extract_json_array(raw_text)

    def test_validate_sketch_prompts_rejects_invalid_id(self):
        items = build_valid_items()
        items[4]["id"] = 99

        with self.assertRaisesRegex(ValueError, "item 5 has invalid id 99"):
            validate_sketch_prompts(items)

    def test_parse_table_row_splits_markdown_cells(self):
        row = parse_table_row("| Name | Meaning |")

        self.assertEqual(row, ["Name", "Meaning"])


if __name__ == "__main__":
    unittest.main()

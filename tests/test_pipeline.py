"""Executable regression checks for the procedural Markdown conversion pipeline."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import lexer  # noqa: E402
import parser  # noqa: E402
import renderer  # noqa: E402
import utils  # noqa: E402
import validator  # noqa: E402


def convert(source: str):
    """Build an AST and HTML from fresh text, without the desktop dependency."""
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "sample.md"
        path.write_text(source, encoding="utf-8")
        tree = parser.parse(list(lexer.tokenize(str(path))))
    return tree, renderer.to_html(tree)


class PipelineTests(unittest.TestCase):
    def test_headings_paragraphs_and_lists(self):
        tree, output = convert(
            "# Main\\n\\nFirst paragraph\\nsecond line\\n\\n- a\\n- b\\n\\n1. one\\n2. two\\n\\n---\\n"
        )
        self.assertEqual(tree["type"], "document")
        for expected in (
            "<h1>Main</h1>",
            "<p>First paragraph second line</p>",
            "<ul>",
            "<li>a</li>",
            "<li>b</li>",
            "<ol>",
            "<li>one</li>",
            "<li>two</li>",
            "<hr>",
        ):
            self.assertIn(expected, output)

    def test_inline_markup_and_escaping(self):
        _, output = convert(
            '# Heading **bold**\\n\\nHello *italic*, **strong**, '
            '\`code <x>\` and [site](https://example.org/?a=1&b=2). '
            '![A & B](image.png) <script>alert("x")</script>\\n'
        )
        for expected in (
            "<h1>Heading <strong>bold</strong></h1>",
            "<em>italic</em>",
            "<strong>strong</strong>",
            "<code>code &lt;x&gt;</code>",
            'href="https://example.org/?a=1&amp;b=2"',
            'src="image.png" alt="A &amp; B"',
            "&lt;script&gt;",
        ):
            self.assertIn(expected, output)
        self.assertNotIn("<script>", output)

    def test_unsafe_url_generates_diagnostic_not_unsafe_markup(self):
        tree, output = convert("[click](javascript:alert) ![image](data:text/plain,xxx)\\n")
        findings = validator.validate(tree)
        self.assertIn("MD008", {item["code"] for item in findings})
        self.assertIn("MD009", {item["code"] for item in findings})
        self.assertNotIn('href="javascript:', output)
        self.assertNotIn('src="data:', output)
        self.assertIn("click", output)

    def test_inline_escapes_do_not_produce_emphasis(self):
        _, output = convert(r"Not bold: \\*literal\\* and **strong**" + "\\n")
        self.assertIn("<strong>strong</strong>", output)
        self.assertNotIn("<em>literal</em>", output)

    def test_fenced_code_preserves_original_lines_and_escapes(self):
        tree, output = convert("```python\\n# not a heading\\n- not a list\\nprint('<tag>')\\n```\\n".replace("`", "\`"))
        self.assertIn('class="language-python"', output)
        self.assertIn("# not a heading", output)
        self.assertIn("- not a list", output)
        self.assertIn("print(&#x27;&lt;tag&gt;&#x27;)", output)
        self.assertNotIn("<h1>", output)
        self.assertEqual([], validator.validate(tree))

    def test_fenced_code_without_language(self):
        tree, output = convert("```\\nplain text\\n```\\n".replace("`", "\`"))
        self.assertIn("<pre><code>plain text</code></pre>", output)
        self.assertEqual([], validator.validate(tree))

    def test_unclosed_fence_is_an_error(self):
        tree, output = convert("```python\\nprint(1)\\n".replace("`", "\`"))
        self.assertIn("MD004", {item["code"] for item in validator.validate(tree)})
        self.assertIn("<pre><code", output)

    def test_empty_heading_and_list_item_diagnostics(self):
        tree, _ = convert("# Title\\n### Jump\\n#  \\n- \\n")
        codes = {finding["code"] for finding in validator.validate(tree)}
        self.assertTrue({"MD001", "MD003", "MD006"}.issubset(codes), codes)

    def test_repeated_parses_have_independent_asts(self):
        first, _ = convert("# First\\n")
        second, _ = convert("# Second\\n")
        self.assertEqual(len(first["children"]), 1)
        self.assertEqual(len(second["children"]), 1)
        self.assertIsNot(first, second)
        self.assertIn("First", renderer.to_html(first))
        self.assertNotIn("First", renderer.to_html(second))

    def test_existing_css_only(self):
        tree, _ = convert("# Title\\n")
        output = renderer.to_html(tree, css_file="dark")
        self.assertIn('../css/dark.css', output)
        with self.assertRaises(ValueError):
            renderer.to_html(tree, css_file="../arbitrary")

    def test_cli_handles_file_even_without_gui(self):
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "example.md"
            output_path = Path(temp) / "rendered.html"
            input_path.write_text("# From CLI\\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "src" / "main.py"), str(input_path), str(output_path)],
                cwd=ROOT, capture_output=True, text=True, check=False, timeout=25,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.exists())
            self.assertIn("<h1>From CLI</h1>", output_path.read_text(encoding="utf-8"))

    def test_missing_input_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [sys.executable, str(ROOT / "src" / "main.py"), str(Path(temp) / "missing.md")],
                cwd=ROOT, capture_output=True, text=True, check=False, timeout=25,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Error:", result.stderr)


if __name__ == "__main__":
    unittest.main()

# Markdown to HTML Converter

[![Tests](https://github.com/CPX-001/Markdown_to_html/actions/workflows/ci.yml/badge.svg)](https://github.com/CPX-001/Markdown_to_html/actions/workflows/ci.yml)

A small **Markdown-to-HTML converter with its own lexer, parser, AST, validation rules and HTML renderer**. It can be used from the command line or through a Flet desktop interface.

I developed the conversion engine during my Python specialization course, before working with object-oriented programming. The core intentionally uses functions, dictionaries and lists rather than a class hierarchy. The UI is a separate layer.

## Try it

The **CLI needs only Python 3.10+**; no third-party dependencies are required:

~~~bash
python src/main.py tests/test.md
~~~

The generated HTML is saved under `HTML_GEN/` and the AST under `AST_GEN/`. To pick an output location:

~~~bash
python src/main.py tests/test.md example.html
~~~

The sample `tests/test.md` deliberately includes malformed Markdown to demonstrate validator warnings.

### Desktop UI (optional)

~~~bash
python -m pip install -r requirements.txt
python src/main.py --gui
~~~

The GUI uses the Flet 0.23.x API (pinned in requirements.txt). The UI provides file selection, CSS themes, validation messages and HTML export. The CLI still works when Flet is installed: a filename argument selects **CLI mode**, not the GUI.

## Supported Markdown

| Input | HTML result |
| --- | --- |
| `# Heading` through `###### Heading` | `<h1>`–`<h6>` |
| Paragraphs | `<p>` |
| `- item`, `* item`, `1. item` | `<ul>` / `<ol>` |
| `---` | `<hr>` |
| Triple-backtick code blocks, optionally with a language | `<pre><code>` |
| `**bold**`, `*emphasis*`, inline backticks | `<strong>`, `<em>`, `<code>` |
| `[label](url)`, `![alt](url)` | `<a>`, `<img>` |

This implements a **practical Markdown subset**, not the CommonMark specification. Nested lists, tables, complex nested inline styles and advanced Markdown syntax are outside the current scope. No external Markdown parser is used.

## Design

~~~text
Markdown file
    |
    v
lexer.py  ------> block and inline tokens
    |
    v
parser.py ------> document AST (plain Python dictionaries/lists)
    |               |
    |               +--> AST_GEN/*.json
    v
validator.py ---> diagnostics (MD001–MD010)
    |
    v
renderer.py ----> escaped, standalone HTML
    |
    v
HTML_GEN/*.html or an explicit output path
~~~

| Module | Responsibility |
| --- | --- |
| `src/specs.py` | Token patterns, parsing strategies and diagnostic definitions |
| `src/lexer.py` | Line-by-line lexical analysis, including raw fenced-code lines |
| `src/parser.py` | Token grouping and AST construction |
| `src/validator.py` | Rule-based checks over the AST |
| `src/renderer.py` | Recursive HTML generation and escaping |
| `src/main.py` | Pipeline orchestration and CLI/GUI selection |
| `src/ui.py` | Optional Flet desktop interface |
| `src/utils.py` / `src/logging_utils.py` | Shared helpers and file logging |

A fresh AST is created for each conversion. Validation produces **non-blocking diagnostics**: the tool still generates HTML so users can inspect the result. Unclosed code fences, missing text and unsafe URLs are among the detected conditions.

### HTML and styles

Text, inline code and fenced code are HTML-escaped. URLs used in generated links and images are restricted to relative paths or ordinary `http`, `https` and `mailto` schemes; unsafe URLs are reported and rendered without a clickable URL. This is a small converter, **not a full HTML sanitizer**.

The GUI offers bundled CSS styles from `css/`. Their relative paths are intended for HTML saved in `HTML_GEN/`; if you save HTML elsewhere, copy or adjust the stylesheet links accordingly. The CLI produces unstyled HTML by default.

Generated documents, logs and compiled files are excluded from version control.

## Test and review

~~~bash
python -m unittest discover -s tests -p "test_*.py" -v
python -m compileall -q src
~~~

GitHub Actions repeats these checks for pushes and pull requests. The automated suite covers HTML output, AST isolation, fenced code, inline Markdown, validation rules, URL safety and command-line usage. The graphical UI is not exercised by headless tests.

## Intentional limitations

- It is not a complete Markdown parser and does not aim for full CommonMark compliance.
- The validator reports problems but does not rewrite malformed source.
- The Flet interface is a desktop convenience; the CLI and conversion pipeline are independently usable.
- AST and HTML exports are stored locally; there is no server component.

**Why this project matters:** it demonstrates lexical analysis, parsing into an intermediate representation, recursive processing, rule-based validation, careful output escaping, separation of concerns and a usable Python CLI.

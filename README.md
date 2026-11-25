# Markdown to HTML Converter

A Markdown-to-HTML converter written in Python, with a command-line interface and an optional Flet desktop application.

I started this project during my Python specialization course. The conversion engine uses functions, dictionaries and lists, with the desktop UI kept separate from the core.

## Try it

The CLI requires Python 3.10 or later and has no third-party dependencies:

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

The GUI uses the Flet 0.23.x API, pinned in `requirements.txt`. It supports file selection, CSS themes, validation messages and HTML export. Passing a filename selects CLI mode, even if Flet is installed.

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

The converter supports a subset of Markdown, not the full CommonMark specification. Nested lists, tables, complex nested inline styles and advanced Markdown syntax are outside the current scope. No external Markdown parser is used.

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

Each conversion creates a fresh AST. Validation reports diagnostics without preventing HTML generation. Unclosed code fences, missing text and unsafe URLs are among the detected conditions.

### HTML and styles

Text, inline code and fenced code are HTML-escaped. URLs used in generated links and images are restricted to relative paths or ordinary `http`, `https` and `mailto` schemes; unsafe URLs are reported and rendered without a clickable URL. This is a small converter, **not a full HTML sanitizer**.

The GUI offers bundled CSS styles from `css/`. Their relative paths are intended for HTML saved in `HTML_GEN/`; if you save HTML elsewhere, copy or adjust the stylesheet links accordingly. The CLI produces unstyled HTML by default.

Generated documents, logs and compiled files are excluded from version control.

## Limitations

- The validator reports problems but does not rewrite malformed source.
- AST and HTML exports are stored locally; there is no server component.

## Tests

Run the regression tests from the repository root:

~~~bash
python -m unittest discover -s tests -p "test_*.py" -v
~~~

The tests cover conversion, validation, HTML escaping and CLI behavior.

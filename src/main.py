"""CLI entry point and four-stage Markdown conversion pipeline."""
import sys
from datetime import datetime
from pathlib import Path

import lexer
import logging_utils
import parser
import renderer
import validator


def run_pipeline(file_path: str) -> tuple[dict, str]:
    """Tokenize, parse, diagnose and render one input Markdown file."""
    logging_utils.log_pipeline_start(file_path)
    try:
        tokens = list(lexer.tokenize(file_path))
        ast = parser.parse(tokens)
        parser.save_ast_to_file(ast)

        findings = validator.validate(ast)
        for finding in findings:
            level = finding.get("severity", "warning").upper()
            detail = f"{finding['code']} (line {finding['line']}): {finding['message']}"
            if level == "ERROR":
                logging_utils.log_error("VALIDATOR", detail)
            else:
                logging_utils.log_warning("VALIDATOR", detail)

        html = renderer.to_html(ast)
        logging_utils.log_pipeline_end(success=True)
        return ast, html
    except Exception:
        logging_utils.log_pipeline_end(success=False)
        raise


def save_html_to_file(html: str, input_file: str, output_dir: str | None = None) -> str:
    root = Path(__file__).resolve().parent.parent
    directory = Path(output_dir) if output_dir else root / "HTML_GEN"
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{Path(input_file).stem}_{datetime.now():%Y%m%d_%H%M%S_%f}.html"
    path = directory / filename
    path.write_text(html, encoding="utf-8")
    return str(path)


def _launch_ui(initial_file: str | None = None) -> None:
    """Load the optional desktop dependency only when the GUI is requested."""
    try:
        import flet as ft
        import ui
    except ImportError as exc:
        raise RuntimeError("Flet is required for the GUI. Install with: pip install -r requirements.txt") from exc

    ui.INITIAL_FILE = initial_file
    ft.app(target=ui.main)


def main(argv: list[str] | None = None) -> int:
    args = (argv if argv is not None else sys.argv)[1:]
    logging_utils.ensure_directories_exist()
    logging_utils.initialize_logging_system()
    try:
        if not args or args[0] == "--gui":
            if len(args) > 1:
                print("Usage: python src/main.py [input.md [output.html]] | --gui", file=sys.stderr)
                return 2
            _launch_ui()
            return 0

        if len(args) > 2 or args[0].startswith("-"):
            print("Usage: python src/main.py [input.md [output.html]] | --gui", file=sys.stderr)
            return 2

        input_file = args[0]
        _ast, html = run_pipeline(input_file)
        if len(args) == 2:
            output_path = Path(args[1])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html, encoding="utf-8")
            destination = str(output_path)
        else:
            destination = save_html_to_file(html, input_file)
        print(f"HTML saved to: {destination}")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        logging_utils.log_error("SYSTEM", str(exc))
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        logging_utils.close_logging_system()


if __name__ == "__main__":
    raise SystemExit(main())

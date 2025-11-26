import sys
import os
from datetime import datetime
from typing import Dict
import lexer
import parser
import validator
import renderer
import logging_utils

try:
    import flet as ft
    import ui
    FLET_AVAILABLE = True
except ImportError:
    FLET_AVAILABLE = False


def run_pipeline(file_path: str) -> tuple[Dict, str]:
    logging_utils.log_pipeline_start(file_path)
    
    try:
        tokens = lexer.tokenize(file_path)
        tokens_list = list(tokens)
        
        ast = parser.parse(tokens_list)
        output_path = parser.save_ast_to_file(ast)
        
        errors = validator.validate(ast)
        if errors:
            for error in errors:
                severity = error.get('severity', 'ERROR').upper()
                code = error.get('code', 'UNKNOWN')
                message = error.get('message', 'No message')
                line = error.get('line', 'N/A')
                logging_utils.log_warning("VALIDATOR", f"{code} (line {line}): {message}")
        
        html = renderer.to_html(ast)
        
        logging_utils.log_pipeline_end(success=True)
        return ast, html
    
    except Exception as e:
        logging_utils.log_pipeline_end(success=False)
        raise


def save_html_to_file(html: str, input_file: str, output_dir: str = None) -> str:
    if output_dir is None:
        # Determine project root (parent of src)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, "HTML_GEN")
        
    os.makedirs(output_dir, exist_ok=True)
    
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{date_str}.html"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    
    return filepath


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv
    
    # Inicializar sistema de logging y crear carpetas
    logging_utils.ensure_directories_exist()
    logging_utils.initialize_logging_system()
    
    if FLET_AVAILABLE:
        initial_file = argv[1] if len(argv) > 1 else None
        if initial_file:
            ui.INITIAL_FILE = initial_file
        print("[SYSTEM] Opening graphical interface...")
        ft.app(target=ui.main)
        logging_utils.close_logging_system()
        return 0
    else:
        if len(argv) < 2:
            print("[ERROR] Flet is not installed.")
            print("Install dependencies with: pip install -r requirements.txt")
            print("\nOr use CLI mode:")
            print("Usage: python main.py <file.md> [output.html]")
            logging_utils.close_logging_system()
            return 1
        
        file_path = argv[1]
        output_file = argv[2] if len(argv) > 2 else None
        
        ast, html = run_pipeline(file_path)
        
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)
            logging_utils.log_info("SYSTEM", f"HTML saved to: {output_file}")
        else:
            html_path = save_html_to_file(html, file_path)
            logging_utils.log_info("SYSTEM", f"HTML saved to: {html_path}")
        
        logging_utils.log_info("SYSTEM", "Pipeline executed successfully")
        logging_utils.close_logging_system()
        return 0


if __name__ == "__main__":
    main()



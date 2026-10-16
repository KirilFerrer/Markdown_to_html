import flet as ft
import os
from pathlib import Path
from datetime import datetime
import lexer
import parser
import validator
import renderer
import logging_utils
import utils

INITIAL_FILE = None

class MarkdownConverterApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Markdown to HTML Converter"
        self.page.window.width = 1000
        self.page.window.height = 800
        self.page.window.center()
        self.page.padding = 0
        self.page.bgcolor = "#f5f7fa"
        self.page.theme_mode = "light"
        self.page.scroll = ft.ScrollMode.AUTO
        
        self.selected_file_path = INITIAL_FILE
        self.generated_html = None
        self.ast = None
        self.selected_css = None  # CSS seleccionado
        
        # Inicializar sistema de logging
        logging_utils.ensure_directories_exist()
        logging_utils.initialize_logging_system()
        
        self.setup_ui()
        
        if self.selected_file_path and os.path.exists(self.selected_file_path):
            self.load_initial_file()
    
    def setup_ui(self):
        # Textos y controles
        self.file_path_text = ft.Text(
            "[SYSTEM] No file selected",
            size=13,
            color="#64748b",
            weight="normal"
        )
        
        self.select_file_btn = ft.Container(
            content=ft.Row([
                ft.Text("Select File", size=14, color="#ffffff", weight="w500")
            ], tight=True, spacing=8),
            bgcolor="#6366f1",
            padding=20,
            border_radius=8,
            on_click=self.select_file,
            ink=True,
            tooltip="Select Markdown file"
        )
        
        self.convert_btn = ft.Container(
            content=ft.Row([
                ft.Text("Convert", size=14, color="#ffffff", weight="w500")
            ], tight=True, spacing=8),
            bgcolor="#10b981",
            padding=20,
            border_radius=8,
            on_click=self.convert_file,
            disabled=True,
            tooltip="Convert to HTML"
        )
        
        self.save_html_btn = ft.Container(
            content=ft.Row([
                ft.Text("Save HTML", size=14, color="#ffffff", weight="w500")
            ], tight=True, spacing=8),
            bgcolor="#8b5cf6",
            padding=20,
            border_radius=8,
            on_click=self.save_html,
            disabled=True,
            tooltip="Save HTML file"
        )
        
        # Consola de salida tipo terminal
        self.console_lines = ft.Column(
            [],
            scroll=ft.ScrollMode.AUTO,
            spacing=2
        )
        
        self.console_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text("●", color="#ef4444", size=12),
                        padding=2
                    ),
                    ft.Container(
                        content=ft.Text("●", color="#f59e0b", size=12),
                        padding=2
                    ),
                    ft.Container(
                        content=ft.Text("●", color="#10b981", size=12),
                        padding=2
                    ),
                    ft.Container(expand=True),
                    ft.Text("Console Output", size=12, color="#9ca3af", weight="w500")
                ], spacing=4),
                ft.Divider(height=1, color="#374151"),
                ft.Container(
                    content=self.console_lines,
                    bgcolor="#1e1e1e",
                    padding=10,
                    height=400
                )
            ], spacing=5),
            bgcolor="#111827",
            padding=10,
            border_radius=8
        )
        
        self.status_text = ft.Text(
            "[SYSTEM] Waiting for file...",
            size=13,
            color="#64748b",
            weight="normal"
        )
        
        self.progress_bar = ft.ProgressBar(
            visible=False,
            color="#6366f1",
            bgcolor="#e2e8f0",
            height=4
        )
        
        
        # Dropdown para selección de CSS
        # Obtener ruta absoluta a la carpeta css
        current_dir = os.path.dirname(os.path.abspath(__file__))
        css_dir = os.path.join(os.path.dirname(current_dir), "css")
        
        css_files = utils.list_css_files(css_dir)
        css_options = [ft.dropdown.Option("none", "No CSS")] + [ft.dropdown.Option(css, css.capitalize()) for css in css_files]
        
        self.css_dropdown = ft.Dropdown(
            label="Select CSS Style",
            options=css_options,
            value="none",
            width=300,
            on_change=self.on_css_change
        )
        
        # Card para selección de archivo
        file_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("File Selection", size=18, weight="bold", color="#1e293b")
                ], spacing=10),
                ft.Divider(height=10, color="transparent"),
                ft.Container(
                    content=self.file_path_text,
                    bgcolor="#f8fafc",
                    padding=15,
                    border_radius=8,
                ),
                ft.Divider(height=5, color="transparent"),
                self.select_file_btn,
                ft.Divider(height=10, color="transparent"),
                self.css_dropdown
            ], spacing=10),
            bgcolor="#ffffff",
            padding=25,
            border_radius=12,
        )
        
        # Card para conversión
        convert_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Conversion Process", size=18, weight="bold", color="#1e293b")
                ], spacing=10),
                ft.Divider(height=10, color="transparent"),
                ft.Row([
                    self.convert_btn,
                    self.save_html_btn
                ], spacing=10),
                ft.Divider(height=10, color="transparent"),
                self.progress_bar,
                ft.Container(
                    content=self.status_text,
                    padding=10
                )
            ], spacing=8),
            bgcolor="#ffffff",
            padding=25,
            border_radius=12,
        )
        
        # Card para consola de salida
        output_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Console Output", size=18, weight="bold", color="#1e293b")
                ], spacing=10),
                ft.Divider(height=10, color="transparent"),
                self.console_container
            ], spacing=10),
            bgcolor="#ffffff",
            padding=25,
            border_radius=12,
        )
        
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Markdown → HTML",
                    size=32,
                    weight="bold",
                    color="#1e293b"
                ),
                ft.Text(
                    "Convierte archivos Markdown a HTML con validación",
                    size=14,
                    color="#64748b",
                    weight="normal"
                )
            ], spacing=5, horizontal_alignment="center"),
            padding=30,
            alignment=ft.alignment.center
        )
        
        # Container principal centrado con scroll
        main_content = ft.Container(
            content=ft.Column([
                header,
                ft.Container(
                    content=ft.Column([
                        file_section,
                        convert_section,
                        output_section
                    ], spacing=20, scroll=ft.ScrollMode.AUTO),
                    width=700,
                )
            ], horizontal_alignment="center", spacing=0, scroll=ft.ScrollMode.AUTO),
            alignment=ft.alignment.top_center,
            expand=True
        )
        
        self.page.add(
            ft.Container(
                content=main_content,
                expand=True,
                padding=20
            )
        )
        
        # Asegurar que la página tenga scroll
        self.page.scroll = ft.ScrollMode.AUTO
    
    def add_console_line(self, text: str, color: str = "#e5e7eb", prefix: str = ""):
        """Añade una línea a la consola visual"""
        row_controls = []
        if prefix:
            row_controls.append(ft.Text(prefix, color="#6b7280", size=12))
        row_controls.append(ft.Text(text, color=color, size=12, selectable=True))
        
        line = ft.Container(
            content=ft.Row(row_controls, spacing=5),
            padding=5
        )
        self.console_lines.controls.append(line)
    
    def clear_console(self):
        """Limpia la consola visual"""
        self.console_lines.controls.clear()
    
    def add_log_message(self, message: str, level: str = "INFO"):
        """Añade un mensaje a la consola visual con formato de log profesional"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "DEBUG": "#9ca3af",
            "INFO": "#60a5fa",
            "WARNING": "#f59e0b",
            "ERROR": "#ef4444",
            "CRITICAL": "#ef4444"
        }
        
        color = color_map.get(level, "#e5e7eb")
        formatted_message = f"[{timestamp}] [{level:8s}] {message}"
        self.add_console_line(formatted_message, color, prefix="")
    
    
    def load_initial_file(self):
        if self.selected_file_path and os.path.exists(self.selected_file_path):
            self.file_path_text.value = f"[FILE] {Path(self.selected_file_path).name}"
            self.file_path_text.color = "#10b981"
            self.file_path_text.weight = "w500"
            self.convert_btn.disabled = False
            self.convert_btn.bgcolor = "#10b981"
            self.status_text.value = "[OK] File loaded. Ready to convert"
            self.status_text.color = "#10b981"
            self.page.update()
    
    def select_file(self, e):
        def on_result(result: ft.FilePickerResultEvent):
            if result.files:
                file = result.files[0]
                self.selected_file_path = file.path
                self.file_path_text.value = f"[FILE] {Path(file.path).name}"
                self.file_path_text.color = "#10b981"
                self.file_path_text.weight = "w500"
                self.convert_btn.disabled = False
                self.convert_btn.bgcolor = "#10b981"
                self.status_text.value = "[OK] File loaded. Ready to convert"
                self.status_text.color = "#10b981"
                self.page.update()
        
        file_picker = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        file_picker.pick_files(
            allowed_extensions=["md"],
            dialog_title="Select Markdown file"
        )
    
    def on_css_change(self, e):
        """Maneja el cambio de selección de CSS"""
        if e.control.value == "none":
            self.selected_css = None
            console_msg = logging_utils.log_info("SYSTEM", "CSS style removed")
        else:
            self.selected_css = e.control.value
            console_msg = logging_utils.log_info("SYSTEM", f"CSS style selected: {e.control.value}")
        
        self.add_console_line(console_msg, "#60a5fa")
        self.page.update()
    
    def convert_file(self, e):
        if not self.selected_file_path:
            console_msg = logging_utils.log_warning("SYSTEM", "Conversion attempted without file selected")
            self.add_console_line(console_msg, "#f59e0b")
            self.page.update()
            return
        
        self.progress_bar.visible = True
        self.status_text.value = "[PROCESSING] Converting file..."
        self.status_text.color = "#6366f1"
        self.convert_btn.disabled = True
        self.convert_btn.bgcolor = "#94a3b8"
        self.page.update()
        
        try:
            self.clear_console()
            
            # TOKENIZACIÓN
            try:
                tokens = lexer.tokenize(self.selected_file_path)
                tokens_list = list(tokens)
                token_count = len(tokens_list)
                console_msg = logging_utils.log_info("LEXER", f"Tokenization completed: {token_count} tokens generated")
                self.add_console_line(console_msg, "#60a5fa")
                self.page.update()
            except Exception as token_error:
                console_msg = logging_utils.log_error("LEXER", f"Tokenization failed: {str(token_error)}")
                self.add_console_line(console_msg, "#ef4444")
                raise
            
            # PARSING
            try:
                self.ast = parser.parse(tokens_list)
                console_msg = logging_utils.log_info("PARSER", "AST generation completed")
                self.add_console_line(console_msg, "#60a5fa")
                self.page.update()
            except Exception as parse_error:
                console_msg = logging_utils.log_error("PARSER", f"Parsing failed: {str(parse_error)}")
                self.add_console_line(console_msg, "#ef4444")
                raise
            
            # GUARDAR AST
            try:
                ast_path = parser.save_ast_to_file(self.ast)
                console_msg = logging_utils.log_info("PARSER", f"AST saved: {os.path.basename(ast_path)}")
                self.add_console_line(console_msg, "#60a5fa")
                self.page.update()
            except Exception as ast_error:
                console_msg = logging_utils.log_warning("PARSER", f"Failed to save AST: {str(ast_error)}")
                self.add_console_line(console_msg, "#f59e0b")
            
            # VALIDACIÓN
            try:
                errors = validator.validate(self.ast)
                
                if errors:
                    error_count = len([e for e in errors if e.get('severity') == 'error'])
                    warning_count = len([e for e in errors if e.get('severity') == 'warning'])
                    console_msg = logging_utils.log_warning("VALIDATOR", f"Validation completed: {error_count} errors, {warning_count} warnings")
                    self.add_console_line(console_msg, "#f59e0b")
                    
                    # Mostrar TODOS los errores
                    for error in errors:
                        severity = error.get('severity', 'ERROR').upper()
                        code = error.get('code', 'UNKNOWN')
                        message = error.get('message', 'No message')
                        line = error.get('line', 'N/A')
                        console_msg = f"[{datetime.now().strftime('%H:%M:%S')}] [VALIDATOR] {code} (line {line}): {message}"
                        color = "#ef4444" if severity == "ERROR" else "#f59e0b"
                        self.add_console_line(console_msg, color)
                else:
                    console_msg = logging_utils.log_info("VALIDATOR", "Validation completed: document is valid")
                    self.add_console_line(console_msg, "#60a5fa")
            except Exception as val_error:
                console_msg = logging_utils.log_error("VALIDATOR", f"Validation failed: {str(val_error)}")
                self.add_console_line(console_msg, "#ef4444")
                raise

            self.page.update()
            
            # GENERACIÓN HTML
            try:
                self.generated_html = renderer.to_html(self.ast, css_file=self.selected_css)
                html_size = len(self.generated_html)
                console_msg = logging_utils.log_info("RENDERER", f"HTML generation completed: {html_size} characters")
                self.add_console_line(console_msg, "#60a5fa")
            except Exception as render_error:
                console_msg = logging_utils.log_error("RENDERER", f"HTML generation failed: {str(render_error)}")
                self.add_console_line(console_msg, "#ef4444")
                raise
            
            # GUARDAR HTML AUTOMÁTICAMENTE EN HTML_GEN
            try:
                # Usar ruta absoluta para HTML_GEN en la raíz del proyecto
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)
                html_gen_dir = os.path.join(project_root, "HTML_GEN")
                os.makedirs(html_gen_dir, exist_ok=True)
                
                base_name = os.path.splitext(os.path.basename(self.selected_file_path))[0]
                date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{base_name}_{date_str}.html"
                html_path = os.path.join(html_gen_dir, filename)
                
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(self.generated_html)
                
                console_msg = logging_utils.log_info("SYSTEM", f"HTML saved automatically: {filename}")
                self.add_console_line(console_msg, "#60a5fa")
            except Exception as save_error:
                console_msg = logging_utils.log_warning("SYSTEM", f"Failed to auto-save HTML: {str(save_error)}")
                self.add_console_line(console_msg, "#f59e0b")
            
            # ÉXITO
            console_msg = logging_utils.log_pipeline_end(success=True)
            self.add_console_line(console_msg, "#10b981")
            self.progress_bar.visible = False
            self.status_text.value = "[OK] Conversion completed successfully"
            self.status_text.color = "#10b981"
            self.save_html_btn.disabled = False
            self.save_html_btn.bgcolor = "#8b5cf6"
            self.convert_btn.disabled = False
            self.convert_btn.bgcolor = "#10b981"
            
        except Exception as ex:
            console_msg = logging_utils.log_critical("SYSTEM", f"Critical error: {str(ex)}")
            self.add_console_line(console_msg, "#ef4444")
            
            self.progress_bar.visible = False
            self.status_text.value = "[ERROR] Conversion failed"
            self.status_text.color = "#ef4444"
            self.convert_btn.disabled = False
            self.convert_btn.bgcolor = "#10b981"
        
        self.page.update()
    
    def save_html(self, e):
        if not self.generated_html:
            return
        
        def on_result(result: ft.FilePickerResultEvent):
            if result.path:
                try:
                    with open(result.path, "w", encoding="utf-8") as f:
                        f.write(self.generated_html)
                    
                    self.status_text.value = "[OK] HTML saved successfully"
                    self.status_text.color = "#10b981"
                    console_msg = logging_utils.log_info("SYSTEM", f"HTML file saved: {result.path}")
                    self.add_console_line(console_msg, "#60a5fa")
                    
                except Exception as ex:
                    self.status_text.value = "[ERROR] Failed to save file"
                    self.status_text.color = "#ef4444"
                    console_msg = logging_utils.log_error("SYSTEM", f"Failed to save HTML: {str(ex)}")
                    self.add_console_line(console_msg, "#ef4444")
                
                self.page.update()
        
        file_picker = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        default_name = "output.html"
        if self.selected_file_path:
            base_name = Path(self.selected_file_path).stem
            default_name = f"{base_name}.html"
        
        file_picker.save_file(
            file_name=default_name,
            allowed_extensions=["html"],
            dialog_title="Save HTML"
        )



def main(page: ft.Page):
    MarkdownConverterApp(page)


if __name__ == "__main__":
    ft.app(target=main)
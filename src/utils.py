from typing import Any
import os

def read_lines(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            yield line


# Funciones de transformación de metadatos
def transform_level(value: str) -> int:
    return len(value) if value else 0


def transform_to_int(value: str) -> int:
    return int(value) if value else 0


def transform_indent_level(value: str) -> int:
    if not value:
        return 0
    # Contar espacios (asumiendo indentación con espacios)
    return len(value)


def transform_normalize_rule(value: str) -> str:
    if not value:
        return ""
    first_char = value.strip()[0]
    return first_char * 3  # Normaliza a formato estándar


def transform_identity(value: Any) -> Any:
    return value


# Funciones de transformación para elementos inline
def transform_emphasis_type(value: str) -> str:
    if not value:
        return ""
    # * o _ → "italic", ** o __ → "bold"
    return "bold" if len(value) >= 2 else "italic"


def transform_link_text(value: str) -> str:
    return value.strip() if value else ""


def transform_url(value: str) -> str:
    return value.strip() if value else ""


# Función para listar archivos CSS disponibles
def list_css_files(css_dir: str = None) -> list[str]:
    """
    Lista todos los archivos CSS disponibles en el directorio css/
    
    Args:
        css_dir: Directorio donde se encuentran los archivos CSS
        
    Returns:
        Lista de nombres de archivos CSS (sin extensión)
    """
    if css_dir is None:
        # Determine project root (parent of src)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        css_dir = os.path.join(project_root, "css")

    css_files = []
    
    if not os.path.exists(css_dir):
        return css_files
    
    try:
        for filename in os.listdir(css_dir):
            if filename.endswith('.css'):
                # Retornar nombre sin extensión
                css_files.append(filename[:-4])
        
        # Ordenar alfabéticamente
        css_files.sort()
    except Exception:
        pass
    
    return css_files


def get_css_path(css_name: str, css_dir: str = "css") -> str:
    """
    Obtiene la ruta relativa del archivo CSS para usar en HTML
    
    Args:
        css_name: Nombre del archivo CSS (sin extensión)
        css_dir: Directorio base donde se encuentran los archivos CSS
        
    Returns:
        Ruta relativa al archivo CSS desde HTML_GEN hacia css
    """
    return f"../css/{css_name}.css"
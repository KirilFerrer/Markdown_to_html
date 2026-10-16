from typing import Any
from urllib.parse import urlsplit
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


def get_css_path(css_name: str) -> str:
    """Return an existing bundled style, never an arbitrary local file path."""
    if css_name not in list_css_files():
        raise ValueError(f"Unknown CSS style: {css_name}")
    return f"../css/{css_name}.css"


def is_safe_url(url: str) -> bool:
    """Only allow ordinary relative links or safe URL schemes in generated HTML."""
    if not isinstance(url, str) or not url.strip():
        return False
    candidate = url.strip()
    if candidate.startswith("//") or any(char.isspace() for char in candidate):
        return False
    parsed = urlsplit(candidate)
    if parsed.scheme:
        return parsed.scheme.lower() in {"http", "https", "mailto"}
    # Relative URLs and #anchors are fine; do not allow colon-based oddities.
    return ":" not in candidate.split("/", 1)[0]
from typing import Any

def read_lines(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            yield line


# Funciones de transformación de metadatos
def transform_level(value: str) -> int:
    """Convierte '###' a 3"""
    return len(value) if value else 0


def transform_to_int(value: str) -> int:
    """Convierte string a entero"""
    return int(value) if value else 0


def transform_indent_level(value: str) -> int:
    """Calcula el nivel de indentación (número de espacios/tabs)"""
    if not value:
        return 0
    # Contar espacios (asumiendo indentación con espacios)
    return len(value)


def transform_normalize_rule(value: str) -> str:
    """Normaliza el tipo de regla horizontal"""
    if not value:
        return ""
    first_char = value.strip()[0]
    return first_char * 3  # Normaliza a formato estándar


def transform_identity(value: Any) -> Any:
    """No transforma, devuelve el valor tal cual"""
    return value


# Funciones de transformación para elementos inline
def transform_emphasis_type(value: str) -> str:
    """Normaliza el tipo de énfasis (bold vs italic)"""
    if not value:
        return ""
    # * o _ → "italic", ** o __ → "bold"
    return "bold" if len(value) >= 2 else "italic"


def transform_link_text(value: str) -> str:
    """Normaliza el texto del enlace"""
    return value.strip() if value else ""


def transform_url(value: str) -> str:
    """Normaliza la URL (elimina espacios)"""
    return value.strip() if value else ""
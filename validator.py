from __future__ import annotations

# Validador declarativo: reglas + funciones check_*

from typing import List, Dict, Any, Callable


def validate(ast: Dict[str, Any], rules: List[Callable[[Dict[str, Any]], List[Dict[str, Any]]]] | None = None) -> List[Dict[str, Any]]:
    """
    Ejecuta una lista de reglas contra el AST y devuelve issues [{message, node_type}].
    Esqueleto: define aquí o en otro módulo tus reglas (p.ej. check_heading_levels, check_code_block_closing).
    """
    raise NotImplementedError("validator.validate aún no implementado (esqueleto)")



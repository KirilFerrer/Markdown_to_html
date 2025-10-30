from __future__ import annotations

# Este módulo define: símbolos (tipos), regex de tokenización, y orden de bloques.
# Mantén esto como “fuente de verdad” de tu lenguaje markdown reducido.

from typing import List, Tuple, Dict, Any, Optional


# 1) Tipos de token y nodo (strings para evitar POO)
TOKEN = {

}

NODE = {

}


# 2) Especificación de tokens: (tipo, regex)
# Nota: pon antes los patrones más específicos. Mantén sólo 1 ejemplo.
TOKEN_SPECS: List[Tuple[str, str]] = [
    # (TOKEN["HEADING"], r"^#{1,6}\s+"),  # ejemplo: detecta encabezados al inicio de línea
]


# 3) Regex maestro (compilación). Deja esto para cuando implementes el lexer.
# Un valor placeholder (None) evita que el resto del proyecto “haga cosas”.
MASTER_TOKEN_REGEX: Optional[object] = None


# 4) Orden de flush/precedencia de bloques (sólo guía, no funcional)
BLOCK_FLUSH_ORDER: List[str] = [

]


def make_position(line: int, column: int) -> Dict[str, int]:
    # Estructura mínima de posición (útil para mensajes de error/validación)
    return {"line": line, "column": column}



from __future__ import annotations

# Parser de bloques: construye el AST (bloques) a partir de tokens.

from typing import List, Dict, Any


def parse(tokens: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Debe devolver un AST tipo: {"type": "DOCUMENT", "children": [...]}

    Guía (bloques típicos):
      - HEADING: agrupar línea y extraer nivel + texto.
      - LIST/LIST_ITEM: detectar marcadores, anidar items.
      - CODE_BLOCK: cercas ``` hasta su cierre.
      - PARAGRAPH: acumular texto hasta línea en blanco.
    """
    raise NotImplementedError("parser.parse aún no implementado (esqueleto)")



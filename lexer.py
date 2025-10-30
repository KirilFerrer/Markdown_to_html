from __future__ import annotations

# Tokenización (bloques). Mantén esto como funciones puras y simples.

from typing import List, Dict, Any


def tokenize(text: str) -> List[Dict[str, Any]]:
    """
    Devuelve una lista de tokens: {"type", "value", "position"}.
    Esqueleto: no implementado a propósito. Aquí usarás las regex de spec.

    Idea (cuando implementes):
      - Construir un regex maestro a partir de TOKEN_SPECS.
      - Iterar matches: producir tokens y actualizar posición.
    """
    raise NotImplementedError("lexer.tokenize aún no implementado (esqueleto)")



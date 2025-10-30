from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict


def run_pipeline(text: str) -> Dict[str, Any]:
    """
    Orquesta: tokenización -> AST (bloques) -> inline -> validación -> (luego) HTML.
    Esqueleto: deja los pasos por implementar en sus módulos.
    """
    raise NotImplementedError("main.run_pipeline aún no implementado (esqueleto)")


def main(argv: list[str] | None = None) -> int:



if __name__ == "__main__":
    raise SystemExit(main())



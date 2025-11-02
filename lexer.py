# tokenizer.py (o tu archivo principal)
from typing import List, Dict, Any
from specs import (
    PRECOMPILED_TOKEN_PATTERNS, BLOCK_FLUSH_PRIORITY, META_TRANSFORMS,
    PRECOMPILED_INLINE_PATTERNS, INLINE_FLUSH_PRIORITY, META_TRANSFORMS_INLINE
)
import utils

def pretty(obj):
    import json
    print(json.dumps(obj, indent=2, ensure_ascii=False))

md_file_name = "test.txt"


def apply_meta_transforms(token_type: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aplica las transformaciones definidas en META_TRANSFORMS para un token específico.
    Si no hay transformaciones definidas, devuelve los metadatos sin cambios.
    """
    if token_type not in META_TRANSFORMS:
        return meta
    
    transforms = META_TRANSFORMS[token_type]
    transformed_meta = {}
    
    for key, value in meta.items():
        if key in transforms:
            # Aplicar la función de transformación correspondiente
            transform_func = transforms[key]
            transformed_meta[key] = transform_func(value)
        else:
            # Si no hay transformación definida, mantener el valor original
            transformed_meta[key] = value
    
    return transformed_meta


def apply_inline_transforms(inline_type: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aplica las transformaciones definidas en META_TRANSFORMS_INLINE para un elemento inline.
    Si no hay transformaciones definidas, devuelve los metadatos sin cambios.
    """
    if inline_type not in META_TRANSFORMS_INLINE:
        return meta
    
    transforms = META_TRANSFORMS_INLINE[inline_type]
    transformed_meta = {}
    
    for key, value in meta.items():
        if key in transforms:
            transform_func = transforms[key]
            transformed_meta[key] = transform_func(value)
        else:
            transformed_meta[key] = value
    
    return transformed_meta


def tokenize_inline(text: str, line: int, line_start_pos: int = 0) -> List[Dict[str, Any]]:
    """
    Tokeniza elementos inline dentro de un texto de una línea.
    Busca todas las coincidencias de elementos inline en el texto.
    Retorna una lista de tokens inline encontrados ordenados por posición.
    
    Args:
        text: El texto de la línea a tokenizar
        line: Número de línea (empezando en 1)
        line_start_pos: Posición donde empieza la línea en el documento (default: 0)
    """
    all_matches = []
    
    # Buscar todas las coincidencias de todos los tipos inline
    for inline_type in INLINE_FLUSH_PRIORITY:
        pattern = PRECOMPILED_INLINE_PATTERNS[inline_type]
        for match in pattern.finditer(text):
            meta = match.groupdict()
            meta = apply_inline_transforms(inline_type, meta)
            
            # Calcular columna (posición dentro de la línea, empezando en 1)
            column = match.start() + 1
            
            all_matches.append({
                "type": inline_type,
                "line": line,
                "column": column,
                "start": match.start() + line_start_pos,
                "end": match.end() + line_start_pos,
                "meta": meta
            })
    
    # Ordenar por posición de inicio (sin usar lambda)
    # Usamos un bucle simple para ordenar
    sorted_matches = []
    for i in range(len(all_matches)):
        min_idx = 0
        min_start = all_matches[0]["start"]
        for j in range(1, len(all_matches)):
            if all_matches[j]["start"] < min_start:
                min_start = all_matches[j]["start"]
                min_idx = j
        sorted_matches.append(all_matches.pop(min_idx))
    
    return sorted_matches


def tokenize_line(text_line: str, line:int) -> Dict[str, Any]:
    for token_type in BLOCK_FLUSH_PRIORITY:
        pattern = PRECOMPILED_TOKEN_PATTERNS[token_type]
        match = pattern.match(text_line)
        if match:
            meta = match.groupdict()
            meta = apply_meta_transforms(token_type, meta)
            return {
                "type": token_type,
                "line": line,
                "meta": meta
            }
    
    return None

def tokenize_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Tokeniza un archivo Markdown completo.
    Primera pasada: tokeniza bloques línea por línea.
    Segunda pasada: procesa elementos inline dentro del contenido de los bloques.
    """
    # Primera pasada: tokenizar bloques
    block_tokens = []
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        line_start_pos = 0
        
        for i, line in enumerate(lines):
            token = tokenize_line(line.rstrip('\n'), i + 1)
            if token:
                block_tokens.append(token)
            line_start_pos += len(line)
    
    # Segunda pasada: procesar elementos inline
    # Para cada token de bloque que tenga contenido de texto, buscar elementos inline
    processed_tokens = []
    current_pos = 0
    
    for token in block_tokens:
        # Tokens que pueden tener elementos inline en su contenido
        if token["type"] in ["PARAGRAPH", "HEADER", "UNORDERED_LIST_ITEM", "ORDERED_LIST_ITEM"]:
            if "content" in token["meta"]:
                content = token["meta"]["content"]
                # Tokenizar elementos inline en el contenido
                inline_tokens = tokenize_inline(content, token["line"], current_pos)
                # Añadir los tokens inline al meta del token de bloque
                token["meta"]["inline"] = inline_tokens
                current_pos += len(content) + 1  # +1 por el salto de línea
        else:
            # Para otros tokens, solo actualizar posición aproximada
            if "content" in token["meta"]:
                current_pos += len(token["meta"]["content"]) + 1
            else:
                current_pos += 1  # Línea en blanco o token sin contenido
        
        processed_tokens.append(token)
    
    return processed_tokens


pretty(tokenize_file("test.md"))
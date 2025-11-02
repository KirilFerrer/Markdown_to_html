# specs.py
from typing import List, Tuple, Dict, Any, Optional, Callable
import re
import utils

TOKEN_PATTERNS_NAMES = ["HEADER", "CODE_BLOCK_END", "CODE_BLOCK_START", "HORIZONTAL_RULE", "UNORDERED_LIST_ITEM", "ORDERED_LIST_ITEM", "BLANK_LINE", "PARAGRAPH"]
BLOCK_FLUSH_PRIORITY = ["HEADER", "CODE_BLOCK_END", "CODE_BLOCK_START", "HORIZONTAL_RULE", "UNORDERED_LIST_ITEM", "ORDERED_LIST_ITEM", "BLANK_LINE", "PARAGRAPH"]
NODES = ["DOCUMENT", "HEADER"]

# Patrones para elementos inline (ordenados de más específico a menos específico)
INLINE_TOKEN_PATTERNS = {
    "IMAGE"         : r"!\[(?P<alt>.+?)\]\((?P<url>[^)]+?)\)",            # ![alt](url)
    "LINK"          : r"\[(?P<text>.+?)\]\((?P<url>[^)]+?)\)",            # [text](url)
    "CODE_INLINE"   : r"`(?P<content>[^`]+?)`",                           # `code`
    "STRONG"        : r"\*\*(?P<content>.+?)\*\*",                       # **text**
    "EMPHASIS"      : r"\*(?P<content>[^*]+?)\*",                        # *text* (simple, sin bold)
}

INLINE_FLUSH_PRIORITY = ["IMAGE", "LINK", "CODE_INLINE", "STRONG", "EMPHASIS"]

TOKEN_PATTERNS = {
    "HEADER"             : r"^(?P<level>#{1,6})\s+(?P<content>.+)$",
    "CODE_BLOCK_END"     : r"^```\s*$",
    "CODE_BLOCK_START"   : r"^```(?P<language>\w+)\s*$",
    "HORIZONTAL_RULE"    : r"^(?P<rule>-{3,}|\*{3,}|_{3,})\s*$",
    "UNORDERED_LIST_ITEM": r"^(?P<indent>\s*)(?P<marker>[-*+])\s+(?P<content>.+)$",
    "ORDERED_LIST_ITEM"  : r"^(?P<indent>\s*)(?P<number>\d+)\.\s+(?P<content>.+)$",
    "BLANK_LINE"         : r"^\s*$",
    "PARAGRAPH"          : r"^(?P<content>.+)$",
}

# Mapa de transformaciones de metadatos para cada token
# Cada token puede tener un dict que mapea nombres de campos a funciones de transformación
META_TRANSFORMS: Dict[str, Dict[str, Callable]] = {
    "HEADER": {
        "level": utils.transform_level,
        "content": utils.transform_identity,
    },
    "CODE_BLOCK_START": {
        "language": utils.transform_identity,  # Mantener como string o None
    },
    "HORIZONTAL_RULE": {
        "rule": utils.transform_normalize_rule,
    },
    "UNORDERED_LIST_ITEM": {
        "indent": utils.transform_indent_level,
        "marker": utils.transform_identity,
        "content": utils.transform_identity,
    },
    "ORDERED_LIST_ITEM": {
        "indent": utils.transform_indent_level,
        "number": utils.transform_to_int,
        "content": utils.transform_identity,
    },
    "PARAGRAPH": {
        "content": utils.transform_identity,
    },
}

# Mapa de transformaciones de metadatos para elementos inline
META_TRANSFORMS_INLINE: Dict[str, Dict[str, Callable]] = {
    "STRONG": {
        "content": utils.transform_identity,
    },
    "EMPHASIS": {
        "content": utils.transform_identity,
    },
    "CODE_INLINE": {
        "content": utils.transform_identity,
    },
    "LINK": {
        "text": utils.transform_link_text,
        "url": utils.transform_url,
    },
    "IMAGE": {
        "alt": utils.transform_link_text,
        "url": utils.transform_url,
    },
}


PRECOMPILED_TOKEN_PATTERNS = None


def precompile_inline_patterns(token_patterns: dict[str, str]) -> dict[str, re.Pattern]:
    """Compila los patrones regex para elementos inline"""
    compiled = {}
    for token_name, pattern in token_patterns.items():
        compiled[token_name] = re.compile(pattern)
    return compiled

def precompile_block_patterns(token_patterns: dict[str, str]) -> dict[str, re.Pattern]:
    compiled = {}
    
    for token_name, pattern in token_patterns.items():
        compiled[token_name] = re.compile(pattern, re.MULTILINE)
    
    return compiled


PRECOMPILED_TOKEN_PATTERNS = precompile_block_patterns(TOKEN_PATTERNS)
PRECOMPILED_INLINE_PATTERNS = precompile_inline_patterns(INLINE_TOKEN_PATTERNS)
# specs.py
from typing import Dict, Any, Callable
import re
import utils

BLOCK_FLUSH_PRIORITY = ["HEADER", "HORIZONTAL_RULE", "UNORDERED_LIST_ITEM", "ORDERED_LIST_ITEM", "BLANK_LINE", "PARAGRAPH"]

INLINE_TOKEN_PATTERNS = {
    "IMAGE"         : r"!\[(?P<alt>.*?)\]\((?P<url>[^)]+?)\)",            # ![alt](url)
    "LINK"          : r"\[(?P<text>.+?)\]\((?P<url>[^)]+?)\)",            # [text](url)
    "CODE_INLINE"   : r"`(?P<content>[^`]+?)`",                           # `code`
    "STRONG"        : r"\*\*(?P<content>.+?)\*\*",                       # **text**
    "EMPHASIS"      : r"\*(?P<content>[^*]+?)\*",                        # *text* (simple, sin bold)
}

INLINE_FLUSH_PRIORITY = ["IMAGE", "LINK", "CODE_INLINE", "STRONG", "EMPHASIS"]

TOKEN_PATTERNS = {
    "HEADER"             : r"^(?P<level>#{1,6})\s+(?P<content>.*)$",                    # # heading
    "HORIZONTAL_RULE"    : r"^(?P<rule>-{3,}|\*{3,}|_{3,})\s*$",                       # ---
    "UNORDERED_LIST_ITEM": r"^(?P<indent>\s*)(?P<marker>[-*+])\s+(?P<content>.*)$",     # - item
    "ORDERED_LIST_ITEM"  : r"^(?P<indent>\s*)(?P<number>\d+)\.\s+(?P<content>.*)$",     # 1. item
    "BLANK_LINE"         : r"^\s*$",                                                     # empty
    "PARAGRAPH"          : r"^(?P<content>.+)$",                                         # text
}

META_TRANSFORMS: Dict[str, Dict[str, Callable]] = {
    "HEADER": {
        "level": utils.transform_level,
        "content": utils.transform_identity,
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

TOKEN_GROUPING_STRATEGY: Dict[str, Dict[str, Any]] = {
    "HEADER": {
        "type": "o2o", # 1:1
        "node_type": "heading",
    },
    "HORIZONTAL_RULE": {
        "type": "o2o",
        "node_type": "hr",
    },
    "PARAGRAPH": {
        "type": "m2o", # N:1
        "node_type": "paragraph",
        "buffer_token": "PARAGRAPH",
    },
    "CODE_BLOCK_START": {
        "type": "stateful",
        "node_type": "code_block",
        "start_token": "CODE_BLOCK_START",
        "end_token": "CODE_BLOCK_END",
    },
    "CODE_BLOCK_END": {
        "type": "stateful",
        "node_type": "code_block",
        "start_token": "CODE_BLOCK_START",
        "end_token": "CODE_BLOCK_END",
    },
    "UNORDERED_LIST_ITEM": {
        "type": "series",
        "node_type": "list",
        "item_node_type": "list_item",
        "buffer_token": "UNORDERED_LIST_ITEM",
        "ordered": False,
    },
    "ORDERED_LIST_ITEM": {
        "type": "series",
        "node_type": "list",
        "item_node_type": "list_item",
        "buffer_token": "ORDERED_LIST_ITEM",
        "ordered": True,
    },
    "BLANK_LINE": {
        "type": "new_line",
    },
}

def precompile_inline_patterns(token_patterns: dict[str, str]) -> dict[str, re.Pattern]:
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

VALIDATION_CONSTRAINTS = {
    "MIN_HEADING_LEVEL": 1,
    "MAX_HEADING_LEVEL": 6,
    "MIN_LIST_ITEMS": 1,
}

VALIDATION_RULES: Dict[str, Dict[str, Any]] = {
    "MD001": {
        "name": "heading-increment",
        "description": "Heading levels must increment by one",
        "severity": "warning",
    },
    "MD002": {
        "name": "heading-level-range",
        "description": "Heading levels must be between 1 and 6",
        "severity": "error",
    },
    "MD003": {
        "name": "heading-content-required",
        "description": "Headings must have content",
        "severity": "error",
    },
    "MD004": {
        "name": "code-block-closed",
        "description": "Code blocks must be closed",
        "severity": "error",
    },
    "MD005": {
        "name": "list-has-items",
        "description": "Lists must have at least one item",
        "severity": "warning",
    },
    "MD006": {
        "name": "list-item-has-content",
        "description": "List items must have content",
        "severity": "warning",
    },
    "MD007": {
        "name": "paragraph-has-content",
        "description": "Paragraphs must have content",
        "severity": "warning",
    },
    "MD008": {
        "name": "link-has-url",
        "description": "Links must have a valid URL",
        "severity": "error",
    },
    "MD009": {
        "name": "image-has-url",
        "description": "Images must have a valid URL",
        "severity": "error",
    },
    "MD010": {
        "name": "code-block-has-content",
        "description": "Code blocks must have content",
        "severity": "warning",
    },
}
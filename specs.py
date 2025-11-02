# specs.py
from typing import List, Tuple, Dict, Any, Optional
import re

TOKEN_PATTERNS_NAMES = ["HEADER", "BLANK_LINE"]
BLOCK_FLUSH_PRIORITY = ["HEADER", "BLANK_LINE"]
NODES = ["DOCUMENT", "HEADER"]

TOKEN_PATTERNS = {
    "HEADER"     : r"^(?P<level>#{1,6})\s+(?P<content>.+)$",
    "BLANK_LINE" : r"^\s*$",
}


PRECOMPILED_TOKEN_PATTERNS = None


def precompile_inline_patterns(token_patterns: dict[str, re.Pattern]) -> dict[str, re.Pattern]:
    pass

def precompile_block_patterns(token_patterns: dict[str, str]) -> dict[str, re.Pattern]:
    compiled = {}
    
    for token_name, pattern in token_patterns.items():
        compiled[token_name] = re.compile(pattern, re.MULTILINE)
    
    return compiled


PRECOMPILED_TOKEN_PATTERNS = precompile_block_patterns(TOKEN_PATTERNS)
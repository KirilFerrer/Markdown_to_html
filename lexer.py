# tokenizer.py (o tu archivo principal)
from typing import List, Dict, Any
from specs import PRECOMPILED_TOKEN_PATTERNS, BLOCK_FLUSH_PRIORITY
import utils

def pretty(obj):
    import json
    print(json.dumps(obj, indent=2, ensure_ascii=False))

md_file_name = "test.txt"


def tokenize_line(text_line: str, line:int) -> Dict[str, Any]:
    for token_type in BLOCK_FLUSH_PRIORITY:
        pattern = PRECOMPILED_TOKEN_PATTERNS[token_type]
        match = pattern.match(text_line)
        
        if match:
            meta = match.groupdict()
            
            # Procesar 'level' si existe
            if "level" in meta:
                meta["level"] = len(meta["level"])
            
            return {
                "type": token_type,
                "line": line,
                "meta": meta
            }
    
    return None


pretty(tokenize_line("### hola que tal", 3))
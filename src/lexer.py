import utils
import logging_utils
from typing import List, Dict, Any

from specs import (
    PRECOMPILED_TOKEN_PATTERNS, BLOCK_FLUSH_PRIORITY, META_TRANSFORMS,
    PRECOMPILED_INLINE_PATTERNS, INLINE_FLUSH_PRIORITY, META_TRANSFORMS_INLINE
)


def apply_block_meta_transforms(token_type: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    if token_type not in META_TRANSFORMS:
        return meta
    transforms = META_TRANSFORMS[token_type]
    transformed_meta = {}
    for key, value in meta.items():
        if key in transforms:
            transform_func = transforms[key]
            transformed_meta[key] = transform_func(value)
        else:
            transformed_meta[key] = value
    return transformed_meta

def apply_inline_meta_transforms(inline_type: str, meta: Dict[str, Any]) -> Dict[str, Any]:
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
    all_matches = []
    for inline_type in INLINE_FLUSH_PRIORITY:
        pattern = PRECOMPILED_INLINE_PATTERNS[inline_type]
        for match in pattern.finditer(text):
            meta = match.groupdict()
            meta = apply_inline_meta_transforms(inline_type, meta)
            column = match.start() + 1
            all_matches.append({
                "type": inline_type,
                "line": line,
                "column": column,
                "start": match.start() + line_start_pos,
                "end": match.end() + line_start_pos,
                "meta": meta
            })
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

def tokenize_block(text_line: str, line:int) -> Dict[str, Any]:
    for token_type in BLOCK_FLUSH_PRIORITY:
        pattern = PRECOMPILED_TOKEN_PATTERNS[token_type]
        match = pattern.match(text_line)
        if match:
            meta = match.groupdict()
            meta = apply_block_meta_transforms(token_type, meta)
            return {
                "type": token_type,
                "line": line,
                "meta": meta
            }
    return None

def tokenize(file_path: str):
    logging_utils.log_info("LEXER", f"Starting tokenization: {file_path}", "tokenize")
    
    current_pos = 0
    token_count = 0
    line_count = 0
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                line_count = line_num
                line_content = line.rstrip('\n')
                token = tokenize_block(line_content, line_num)
                
                if token:
                    token_count += 1
                    if token["type"] in ["PARAGRAPH", "HEADER", "UNORDERED_LIST_ITEM", "ORDERED_LIST_ITEM"]:
                        if "content" in token["meta"]:
                            content = token["meta"]["content"]
                            inline_tokens = tokenize_inline(content, token["line"], current_pos)
                            token["meta"]["inline"] = inline_tokens
                            current_pos += len(content) + 1
                    else:
                        if "content" in token["meta"]:
                            current_pos += len(token["meta"]["content"]) + 1
                        else:
                            current_pos += 1
                    
                    yield token
                
                current_pos += len(line)
        
        logging_utils.log_info("LEXER", f"Tokenization completed: {token_count} tokens from {line_count} lines", "tokenize")
    
    except Exception as e:
        logging_utils.log_error("LEXER", f"Tokenization failed: {str(e)}", "tokenize")
        raise


"""Tokenize Markdown blocks and inline spans while preserving fenced code."""
import re
from typing import Any

import logging_utils
from specs import (
    BLOCK_FLUSH_PRIORITY,
    INLINE_FLUSH_PRIORITY,
    META_TRANSFORMS,
    META_TRANSFORMS_INLINE,
    PRECOMPILED_INLINE_PATTERNS,
    PRECOMPILED_TOKEN_PATTERNS,
)

# This is intentionally a small Markdown subset; backtick fences are supported.
FENCE_OPEN = re.compile(r"^ {0,3}```(?P<language>[\w-]*)[ \t]*$")
FENCE_CLOSE = re.compile(r"^ {0,3}```[ \t]*$")


def apply_block_meta_transforms(token_type: str, meta: dict[str, Any]) -> dict[str, Any]:
    transforms = META_TRANSFORMS.get(token_type, {})
    return {key: transforms[key](value) if key in transforms else value
            for key, value in meta.items()}


def apply_inline_meta_transforms(inline_type: str, meta: dict[str, Any]) -> dict[str, Any]:
    transforms = META_TRANSFORMS_INLINE.get(inline_type, {})
    return {key: transforms[key](value) if key in transforms else value
            for key, value in meta.items()}


def _escaped(text: str, position: int) -> bool:
    """An odd number of backslashes means the next Markdown marker is escaped."""
    count = 0
    while position > 0 and text[position - 1] == "\\":
        position -= 1
        count += 1
    return count % 2 == 1


def tokenize_inline(text: str, line: int, line_start_pos: int = 0) -> list[dict[str, Any]]:
    """Emit non-overlapping matches plus literal text in source order."""
    tokens: list[dict[str, Any]] = []
    cursor = 0

    def emit(kind: str, start: int, end: int, meta: dict[str, Any]) -> None:
        tokens.append({
            "type": kind, "line": line, "column": start + 1,
            "start": line_start_pos + start, "end": line_start_pos + end,
            "meta": meta,
        })

    while cursor < len(text):
        best = None
        for kind in INLINE_FLUSH_PRIORITY:
            pattern = PRECOMPILED_INLINE_PATTERNS[kind]
            match = pattern.search(text, cursor)
            while match and _escaped(text, match.start()):
                match = pattern.search(text, match.start() + 1)
            if match and (best is None or match.start() < best[1].start()):
                best = (kind, match)

        if best is None:
            emit("TEXT", cursor, len(text), {"content": text[cursor:]})
            break

        kind, match = best
        if match.start() > cursor:
            emit("TEXT", cursor, match.start(), {"content": text[cursor:match.start()]})
        emit(kind, match.start(), match.end(),
             apply_inline_meta_transforms(kind, match.groupdict()))
        cursor = match.end()
    return tokens


def tokenize_block(text_line: str, line: int) -> dict[str, Any]:
    for kind in BLOCK_FLUSH_PRIORITY:
        match = PRECOMPILED_TOKEN_PATTERNS[kind].match(text_line)
        if match:
            return {"type": kind, "line": line,
                    "meta": apply_block_meta_transforms(kind, match.groupdict())}
    return None


def tokenize(file_path: str):
    """Read input once; treat fenced code lines as opaque source, not Markdown."""
    logging_utils.log_info("LEXER", f"Starting tokenization: {file_path}", "tokenize")
    inside_fence = False
    count = 0
    lines = 0
    try:
        with open(file_path, "r", encoding="utf-8") as source:
            for number, raw_line in enumerate(source, 1):
                lines = number
                line = raw_line.rstrip("\r\n")
                if inside_fence:
                    if FENCE_CLOSE.fullmatch(line):
                        token = {"type": "CODE_BLOCK_END", "line": number, "meta": {}}
                        inside_fence = False
                    else:
                        token = {"type": "CODE_CONTENT", "line": number,
                                 "meta": {"content": line}}
                else:
                    opening = FENCE_OPEN.fullmatch(line)
                    if opening:
                        token = {"type": "CODE_BLOCK_START", "line": number,
                                 "meta": {"language": opening.group("language") or ""}}
                        inside_fence = True
                    else:
                        token = tokenize_block(line, number)
                        if token and token["type"] in {
                            "PARAGRAPH", "HEADER", "UNORDERED_LIST_ITEM", "ORDERED_LIST_ITEM"
                        }:
                            content = token["meta"].get("content", "")
                            token["meta"]["inline"] = tokenize_inline(content, number)
                if token is not None:
                    count += 1
                    yield token
        logging_utils.log_info("LEXER", f"Tokenization completed: {count} tokens from {lines} lines", "tokenize")
    except Exception as exc:
        logging_utils.log_error("LEXER", f"Tokenization failed: {exc}", "tokenize")
        raise

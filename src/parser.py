from __future__ import annotations

import lexer
import logging_utils
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from specs import TOKEN_GROUPING_STRATEGY

def count_nodes(node: Dict[str, Any]) -> int:
    """Cuenta recursivamente el número de nodos en el AST"""
    count = 1
    if "children" in node:
        for child in node["children"]:
            count += count_nodes(child)
    return count


def parse(tokens: List[Dict[str, Any]]) -> Dict[str, Any]:
    logging_utils.log_info("PARSER", "Starting AST generation", "parse")
    try:
        ast = consume_tokens(tokens)
        node_count = count_nodes(ast)
        logging_utils.log_info("PARSER", f"AST generation completed: {node_count} nodes created", "parse")
        return ast
    except Exception as e:
        logging_utils.log_error("PARSER", f"AST generation failed: {str(e)}", "parse")
        raise


def consume_tokens(tokens: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Each conversion must own a fresh document, not reuse module-level children.
    document = {"type": "document", "children": []}
    
    # Buffers para acumulación
    paragraph_buffer: List[Dict[str, Any]] = []
    list_buffer: List[Dict[str, Any]] = []
    
    # Estado para code blocks
    code_block_state: Dict[str, Any] = {
        "active": False,
        "start_token": None,
        "content": []
    }
    
    # Tipo de buffer activo para series (para detectar cambios de tipo)
    current_list_type: str | None = None
    
    # Consumir tokens de la lista
    for token in tokens:
        token_type = token["type"]
        strategy = TOKEN_GROUPING_STRATEGY.get(token_type, {})
        strategy_type = strategy.get("type")
        
        # Verificar buffers activos
        if paragraph_buffer:
            if token_type != "PARAGRAPH":
                paragraph_buffer, list_buffer, current_list_type = flush_buffer("paragraph", document, paragraph_buffer, list_buffer, current_list_type)
        
        if list_buffer:
            buffer_token = TOKEN_GROUPING_STRATEGY.get(current_list_type or "", {}).get("buffer_token")
            if token_type != buffer_token:
                paragraph_buffer, list_buffer, current_list_type = flush_buffer("list", document, paragraph_buffer, list_buffer, current_list_type)
        
        if code_block_state["active"]:
            if token_type == "CODE_BLOCK_END":
                start = code_block_state["start_token"]
                lang = start["meta"].get("language", "") if start else ""
                document["children"].append(make_code_block(lang, code_block_state["content"], start))
                code_block_state = {"active": False, "start_token": None, "content": []}
            else:
                # CODE_CONTENT keeps the entire original line, including # and list markers.
                code_block_state["content"].append(token.get("meta", {}).get("content", ""))
            continue
        
        # o2o
        if strategy_type == "o2o":
            paragraph_buffer, list_buffer, current_list_type = flush_buffer("all", document, paragraph_buffer, list_buffer, current_list_type)
            node_type = strategy.get("node_type")
            
            if node_type == "heading":
                node = make_heading(token)
            elif node_type == "hr":
                node = make_hr()
            else:
                node = {"type": node_type, "children": []}
            
            document["children"].append(node)
        
        # m2o
        elif strategy_type == "m2o":
            paragraph_buffer, list_buffer, current_list_type = flush_buffer("list", document, paragraph_buffer, list_buffer, current_list_type)
            buffer_token = strategy.get("buffer_token")
            
            if token_type == buffer_token:
                paragraph_buffer.append(token)
            else:
                paragraph_buffer, list_buffer, current_list_type = flush_buffer("paragraph", document, paragraph_buffer, list_buffer, current_list_type)
        
        # stateful
        elif strategy_type == "stateful":
            paragraph_buffer, list_buffer, current_list_type = flush_buffer("all", document, paragraph_buffer, list_buffer, current_list_type)
            
            if token_type == strategy.get("start_token"):
                code_block_state["active"] = True
                code_block_state["start_token"] = token
                code_block_state["content"] = []
        
        # series
        elif strategy_type == "series":
            paragraph_buffer, list_buffer, current_list_type = flush_buffer("paragraph", document, paragraph_buffer, list_buffer, current_list_type)
            
            buffer_token = strategy.get("buffer_token")
            
            if token_type == buffer_token:
                if current_list_type is None:
                    current_list_type = token_type
                elif current_list_type != token_type:
                    paragraph_buffer, list_buffer, current_list_type = flush_buffer("list", document, paragraph_buffer, list_buffer, current_list_type)
                    current_list_type = token_type
                
                list_buffer.append(token)
            else:
                paragraph_buffer, list_buffer, current_list_type = flush_buffer("list", document, paragraph_buffer, list_buffer, current_list_type)
        
        # new_line
        elif strategy_type == "new_line":
            paragraph_buffer, list_buffer, current_list_type = flush_buffer("all", document, paragraph_buffer, list_buffer, current_list_type)
    
    paragraph_buffer, list_buffer, current_list_type = flush_buffer("all", document, paragraph_buffer, list_buffer, current_list_type)
    
    if code_block_state["active"]:
        lang = code_block_state["start_token"]["meta"].get("language", "") if code_block_state["start_token"] else ""
        node = make_code_block(
            lang,
            code_block_state["content"],
            code_block_state["start_token"],
            closed=False,
        )
        document["children"].append(node)
    
    return document


def flush_buffer(buffer_type: str, document: Dict[str, Any], 
                  paragraph_buffer: List[Dict[str, Any]], 
                  list_buffer: List[Dict[str, Any]], 
                  current_list_type: str | None) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], str | None]:
    
    if buffer_type == "paragraph" or buffer_type == "all":
        if paragraph_buffer:
            node = make_paragraph(paragraph_buffer)
            document["children"].append(node)
            paragraph_buffer = []
    
    if buffer_type == "list" or buffer_type == "all":
        if list_buffer:
            node = make_list(list_buffer, current_list_type)
            document["children"].append(node)
            list_buffer = []
            current_list_type = None
    
    return paragraph_buffer, list_buffer, current_list_type


def make_inline_nodes(content: str, line: int) -> List[Dict[str, Any]]:
    """Convert inline tokens to AST nodes without classes or hidden shared state.

    Supported syntax is deliberately a subset of Markdown: one inline level,
    links, images, bold, emphasis and inline code.
    """
    nodes: List[Dict[str, Any]] = []
    for token in lexer.tokenize_inline(content, line):
        kind, meta = token["type"], token["meta"]
        if kind == "TEXT":
            nodes.append({"type": "text", "value": meta["content"], "line": line})
        elif kind == "CODE_INLINE":
            nodes.append({"type": "code_inline", "value": meta["content"], "line": line})
        elif kind in ("STRONG", "EMPHASIS"):
            nodes.append({
                "type": kind.lower(),
                "line": line,
                "children": [{"type": "text", "value": meta["content"], "line": line}],
            })
        elif kind == "LINK":
            nodes.append({
                "type": "link", "url": meta["url"], "line": line,
                "children": [{"type": "text", "value": meta["text"], "line": line}],
            })
        elif kind == "IMAGE":
            nodes.append({"type": "image", "url": meta["url"], "alt": meta["alt"], "line": line})
    return nodes


def make_heading(token: Dict[str, Any]) -> Dict[str, Any]:
    level = token["meta"]["level"]
    content = token["meta"].get("content", "")
    line = token.get("line", 0)
    
    return {
        "type": "heading",
        "level": level,
        "line": line,
        "children": [
            *make_inline_nodes(content, line)
        ]
    }


def make_paragraph(buffer: List[Dict[str, Any]]) -> Dict[str, Any]:
    lines = []
    line_num = 0
    for token in buffer:
        if "content" in token.get("meta", {}):
            lines.append(token["meta"]["content"])
        if not line_num:
            line_num = token.get("line", 0)
    
    content = " ".join(lines)
    
    return {
        "type": "paragraph",
        "line": line_num,
        "children": [
            *make_inline_nodes(content, line_num)
        ]
    }


def make_list(buffer: List[Dict[str, Any]], list_type: str | None) -> Dict[str, Any]:
    if not buffer:
        return {"type": "list", "children": [], "line": 0}
    
    # Determinar si es ordered o unordered
    strategy = TOKEN_GROUPING_STRATEGY.get(list_type or buffer[0]["type"], {})
    ordered = strategy.get("ordered", False)
    
    # Obtener línea del primer token
    line_num = buffer[0].get("line", 0) if buffer else 0
    
    # Crear items
    items = []
    for token in buffer:
        content = token["meta"].get("content", "")
        item_line = token.get("line", 0)
        item = {
            "type": "list_item",
            "line": item_line,
            "children": [
                *make_inline_nodes(content, item_line)
            ]
        }
        items.append(item)
    
    return {
        "type": "list",
        "line": line_num,
        "meta": {"ordered": ordered},
        "children": items
    }


def make_code_block(
    lang: str,
    content_lines: List[str],
    start_token: Dict[str, Any] | None = None,
    closed: bool = True,
) -> Dict[str, Any]:
    line_num = start_token.get("line", 0) if start_token else 0
    return {
        "type": "code_block",
        "line": line_num,
        "meta": {
            "lang": lang or "",
            "content": "\n".join(content_lines),
            "closed": closed,
        },
        "children": []
    }


def make_hr() -> Dict[str, Any]:
    return {
        "type": "hr",
        "children": []
    }


def save_ast_to_file(ast: Dict[str, Any], output_dir: str = None) -> str:
    if output_dir is None:
        # Determine project root (parent of src)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, "AST_GEN")

    logging_utils.log_info("PARSER", f"Saving AST to {output_dir}", "save_ast_to_file")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"ast_{date_str}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(ast, f, indent=2, ensure_ascii=False)
        
        logging_utils.log_info("PARSER", f"AST saved successfully: {filename}", "save_ast_to_file")
        return filepath
    
    except Exception as e:
        logging_utils.log_error("PARSER", f"Failed to save AST: {str(e)}", "save_ast_to_file")
        raise

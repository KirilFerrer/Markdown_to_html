from specs import VALIDATION_RULES, VALIDATION_CONSTRAINTS
import logging_utils
from typing import List, Dict, Any, Callable

# Dispatch table: mapea tipos de nodo a sus funciones de validación
VALIDATORS: Dict[str, Callable[[Dict[str, Any], Dict[str, Any]], List[Dict[str, Any]]]] = {}


def create_error(error_code: str, line: int = 0) -> Dict[str, Any]:
    rule = VALIDATION_RULES.get(error_code, {})
    return {
        "code": error_code,
        "message": rule.get("description", ""),
        "severity": rule.get("severity", "error"),
        "line": line
    }


def has_text_content(node: Dict[str, Any]) -> bool:
    children = node.get("children", [])
    
    for child in children:
        if child.get("type") == "text":
            value = child.get("value", "").strip()
            if value:
                return True
    
    return False


def has_inline_content(text_value: str) -> bool:
    return bool(text_value.strip())


def validate_heading(node: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    errors = []
    
    if node["type"] != "heading":
        return errors
    
    level = node.get("level", 0)
    line = node.get("line", 0)
    
    # MD001: heading-increment
    if level > ctx["previous_heading_level"] + 1:
        errors.append(create_error("MD001", line))
    
    # MD002: heading-level-range
    min_level = VALIDATION_CONSTRAINTS.get("MIN_HEADING_LEVEL", 1)
    max_level = VALIDATION_CONSTRAINTS.get("MAX_HEADING_LEVEL", 6)
    if level < min_level or level > max_level:
        errors.append(create_error("MD002", line))
    
    # MD003: heading-content-required
    if not has_text_content(node):
        errors.append(create_error("MD003", line))
    
    # Actualizar contexto
    ctx["previous_heading_level"] = level
    
    return errors


def validate_list(node: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    errors = []
    
    if node["type"] != "list":
        return errors
    
    line = node.get("line", 0)
    children = node.get("children", [])
    
    # MD005: list-has-items
    min_items = VALIDATION_CONSTRAINTS.get("MIN_LIST_ITEMS", 1)
    if len(children) < min_items:
        errors.append(create_error("MD005", line))
    
    return errors


def validate_list_item(node: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    errors = []
    
    if node["type"] != "list_item":
        return errors
    
    line = node.get("line", 0)
    
    # MD006: list-item-has-content
    if not has_text_content(node):
        errors.append(create_error("MD006", line))
    
    return errors


def validate_paragraph(node: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    errors = []
    
    if node["type"] != "paragraph":
        return errors
    
    line = node.get("line", 0)
    
    # MD007: paragraph-has-content
    if not has_text_content(node):
        errors.append(create_error("MD007", line))
    
    return errors


def validate_code_block(node: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    errors = []
    
    if node["type"] != "code_block":
        return errors
    
    line = node.get("line", 0)
    meta = node.get("meta", {})
    content = meta.get("content", "")
    
    # MD010: code-block-has-content
    if not content or not content.strip():
        errors.append(create_error("MD010", line))
    
    # MD004: code-block-closed
    # Nota: Si el code_block existe en el AST, significa que fue cerrado correctamente
    # por el parser. Esta validación es informativa.
    
    return errors


def validate_text(node: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    errors = []
    
    if node["type"] != "text":
        return errors
    
    line = node.get("line", 0)
    
    # Nota: Los links e imágenes se procesan durante el parsing
    # Esta validación es un placeholder para cuando se implemente
    # el procesamiento de inline elements
    
    return errors


def validate_hr(node: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    return []


def validate_document(node: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    return []


def _validate_node(node: Dict[str, Any], ctx: Dict[str, Any], errors: List[Dict[str, Any]]) -> None:
    node_type = node.get("type")
    validator = VALIDATORS.get(node_type)
    
    if validator:
        node_errors = validator(node, ctx)
        errors.extend(node_errors)


def iterate_ast(node: Dict[str, Any], ctx: Dict[str, Any], errors: List[Dict[str, Any]]) -> None:
    # Validar nodo actual
    _validate_node(node, ctx, errors)
    
    # Recorrer hijos recursivamente
    children = node.get("children", [])
    for child in children:
        iterate_ast(child, ctx, errors)


def validate(ast: Dict[str, Any], rules: Dict[str, Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    logging_utils.log_info("VALIDATOR", "Starting document validation", "validate")
    
    errors: List[Dict[str, Any]] = []
    ctx: Dict[str, Any] = {
        "previous_heading_level": 0,
        "parent": None,
        "depth": 0,
        "in_list": False,
        "in_code_block": False
    }
    
    try:
        iterate_ast(ast, ctx, errors)
        
        error_count = len([e for e in errors if e.get("severity") == "error"])
        warning_count = len([e for e in errors if e.get("severity") == "warning"])
        
        if errors:
            logging_utils.log_warning("VALIDATOR", f"Validation completed: {error_count} errors, {warning_count} warnings", "validate")
        else:
            logging_utils.log_info("VALIDATOR", "Validation completed: document is valid", "validate")
        
        return errors
    
    except Exception as e:
        logging_utils.log_error("VALIDATOR", f"Validation failed: {str(e)}", "validate")
        raise


# Registrar validadores en el dispatch table
VALIDATORS["heading"] = validate_heading
VALIDATORS["list"] = validate_list
VALIDATORS["list_item"] = validate_list_item
VALIDATORS["paragraph"] = validate_paragraph
VALIDATORS["code_block"] = validate_code_block
VALIDATORS["text"] = validate_text
VALIDATORS["hr"] = validate_hr
VALIDATORS["document"] = validate_document

import html
import logging_utils
import utils
from typing import Dict, Any, Optional

def to_html(node: Dict[str, Any], indent: int = 0, css_file: Optional[str] = None) -> str:
    # Log solo en la raíz (indent == 0 y tipo == document)
    if indent == 0 and node.get("type") == "document":
        if css_file:
            logging_utils.log_info("RENDERER", f"Starting HTML generation with CSS: {css_file}", "to_html")
        else:
            logging_utils.log_info("RENDERER", "Starting HTML generation", "to_html")
    
    indent_str = "    " * indent
    node_type = node.get("type")
    
    if node_type == "text":
        return html.escape(node.get("value", ""))
    
    if node_type == "heading":
        level = node.get("level", 1)
        children_html = [to_html(child, indent + 1, css_file) for child in node.get("children", [])]
        content = "".join(children_html)
        return f"{indent_str}<h{level}>{content}</h{level}>"
    
    if node_type == "paragraph":
        children_html = [to_html(child, 0, css_file) for child in node.get("children", [])]
        content = "".join(children_html)
        return f"{indent_str}<p>{content}</p>"
    
    if node_type == "list":
        ordered = node.get("meta", {}).get("ordered", False)
        tag = "ol" if ordered else "ul"
        children_html = [to_html(child, indent + 1, css_file) for child in node.get("children", [])]
        items = "\n".join(children_html)
        return f"{indent_str}<{tag}>\n{items}\n{indent_str}</{tag}>"
    
    if node_type == "list_item":
        children_html = [to_html(child, 0, css_file) for child in node.get("children", [])]
        content = "".join(children_html)
        return f"{indent_str}<li>{content}</li>"
    
    if node_type == "code_block":
        lang = node.get("meta", {}).get("lang", "")
        code = html.escape(node.get("meta", {}).get("content", ""))
        class_attr = f' class="language-{lang}"' if lang else ""
        return f"{indent_str}<pre><code{class_attr}>{code}</code></pre>"
    
    if node_type == "hr":
        return f"{indent_str}<hr>"
    
    if node_type == "document":
        children_html = [to_html(child, 1, css_file) for child in node.get("children", [])]
        content = "\n".join(children_html)
        
        # Construir link CSS si está especificado
        css_link = ""
        if css_file:
            css_path = utils.get_css_path(css_file)
            css_link = f'\n    <link rel="stylesheet" href="{css_path}">'
        
        html_output = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Document</title>{css_link}
</head>
<body>
{content}
</body>
</html>'''
        
        html_size = len(html_output)
        logging_utils.log_info("RENDERER", f"HTML generation completed: {html_size} characters", "to_html")
        return html_output
    
    if "children" in node:
        children_html = [to_html(child, indent, css_file) for child in node["children"]]
        return "".join(children_html)
    
    return ""

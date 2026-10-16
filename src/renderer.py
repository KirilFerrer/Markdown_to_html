"""Render the project's Markdown AST as an escaped, standalone HTML document."""
import html

import logging_utils
import utils


def _children(node: dict, indent: int, css_file: str | None) -> str:
    return "".join(to_html(child, indent, css_file) for child in node.get("children", []))


def to_html(node: dict, indent: int = 0, css_file: str | None = None) -> str:
    kind = node.get("type")
    prefix = "    " * indent

    if kind == "text":
        return html.escape(str(node.get("value", "")))
    if kind == "code_inline":
        return f"<code>{html.escape(str(node.get('value', '')))}</code>"
    if kind in {"strong", "emphasis"}:
        tag = "strong" if kind == "strong" else "em"
        return f"<{tag}>{_children(node, 0, css_file)}</{tag}>"
    if kind == "link":
        label = _children(node, 0, css_file)
        url = node.get("url", "")
        if not utils.is_safe_url(url):
            return label  # Never create a clickable javascript:/data: URL.
        return f'<a href="{html.escape(url, quote=True)}">{label}</a>'
    if kind == "image":
        alt = str(node.get("alt", ""))
        url = node.get("url", "")
        if not utils.is_safe_url(url):
            return html.escape(alt)
        return f'<img src="{html.escape(url, quote=True)}" alt="{html.escape(alt, quote=True)}">'
    if kind == "heading":
        level = int(node.get("level", 1))
        if not 1 <= level <= 6:
            level = 1
        return f"{prefix}<h{level}>{_children(node, 0, css_file)}</h{level}>"
    if kind == "paragraph":
        return f"{prefix}<p>{_children(node, 0, css_file)}</p>"
    if kind == "list":
        tag = "ol" if node.get("meta", {}).get("ordered") else "ul"
        items = "\n".join(to_html(child, indent + 1, css_file) for child in node.get("children", []))
        return f"{prefix}<{tag}>\n{items}\n{prefix}</{tag}>"
    if kind == "list_item":
        return f"{prefix}<li>{_children(node, 0, css_file)}</li>"
    if kind == "code_block":
        meta = node.get("meta", {})
        language = str(meta.get("lang", ""))
        # Even language names are escaped before entering an HTML attribute.
        class_name = f' class="language-{html.escape(language, quote=True)}"' if language else ""
        code = html.escape(str(meta.get("content", "")))
        return f"{prefix}<pre><code{class_name}>{code}</code></pre>"
    if kind == "hr":
        return f"{prefix}<hr>"
    if kind == "document":
        logging_utils.log_info("RENDERER", "Starting HTML generation", "to_html")
        children = "\n".join(to_html(child, 1, css_file) for child in node.get("children", []))
        link = ""
        if css_file:
            css_path = html.escape(utils.get_css_path(css_file), quote=True)
            link = f'\n    <link rel="stylesheet" href="{css_path}">'
        output = (f'<!DOCTYPE html>\n<html lang="es">\n<head>\n'
                  f'    <meta charset="UTF-8">\n'
                  f'    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                  f'    <title>Markdown Document</title>{link}\n'
                  f'</head>\n<body>\n{children}\n</body>\n</html>')
        logging_utils.log_info("RENDERER", f"HTML generation completed: {len(output)} characters", "to_html")
        return output
    return _children(node, indent, css_file)

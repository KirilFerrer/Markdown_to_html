"""Small, shared transformations and safe HTML resource helpers."""
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


def transform_level(value: str) -> int:
    return len(value) if value else 0


def transform_to_int(value: str) -> int:
    return int(value) if value else 0


def transform_indent_level(value: str) -> int:
    return len(value) if value else 0


def transform_normalize_rule(value: str) -> str:
    return value.strip()[0] * 3 if value and value.strip() else ""


def transform_identity(value: Any) -> Any:
    return value


def transform_link_text(value: str) -> str:
    return value.strip() if value else ""


def transform_url(value: str) -> str:
    return value.strip() if value else ""


def list_css_files(css_dir: str | None = None) -> list[str]:
    """Return local CSS names for the GUI style selector."""
    default_dir = Path(__file__).resolve().parent.parent / "css"
    directory = Path(css_dir) if css_dir else default_dir
    if not directory.is_dir():
        return []
    return sorted(file.stem for file in directory.glob("*.css") if file.is_file())


def get_css_path(css_name: str) -> str:
    """Only reference styles bundled alongside this project."""
    if css_name not in list_css_files():
        raise ValueError(f"Unknown CSS style: {css_name}")
    return f"../css/{css_name}.css"


def is_safe_url(url: str) -> bool:
    """Allow relative paths and HTTP(S)/mailto links, but not script/data URLs."""
    if not isinstance(url, str) or not url.strip():
        return False
    candidate = url.strip()
    if candidate.startswith("//") or any(character.isspace() for character in candidate):
        return False
    parsed = urlsplit(candidate)
    if parsed.scheme:
        return parsed.scheme.lower() in {"http", "https", "mailto"}
    return ":" not in candidate.split("/", 1)[0]

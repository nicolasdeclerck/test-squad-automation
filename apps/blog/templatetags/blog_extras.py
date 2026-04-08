import json

from django import template

register = template.Library()


@register.filter
def blocknote_plaintext(value):
    """Extract plain text from BlockNote JSON content.

    If the value is valid BlockNote JSON, recursively extracts text from all
    blocks. Otherwise, returns the value as-is (legacy plain text content).
    """
    if not value:
        return ""
    try:
        blocks = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

    if not isinstance(blocks, list):
        return value

    return _extract_text(blocks)


def _extract_text(blocks):
    parts = []
    for block in blocks:
        if isinstance(block, dict):
            # Extract from inline content array
            for inline in block.get("content", []):
                if isinstance(inline, dict):
                    parts.append(inline.get("text", ""))
                elif isinstance(inline, str):
                    parts.append(inline)
            # Recurse into children blocks
            for child in block.get("children", []):
                if isinstance(child, dict):
                    parts.append(_extract_text([child]))
    return " ".join(part for part in parts if part)

import json
from html import escape


def _render_inline_content(inline_content):
    """Render BlockNote inline content items to HTML."""
    if not inline_content:
        return ""

    parts = []
    for item in inline_content:
        if isinstance(item, str):
            parts.append(escape(item))
            continue

        item_type = item.get("type", "text")

        if item_type == "text":
            text = escape(item.get("text", ""))
            styles = item.get("styles", {})
            if styles.get("bold"):
                text = f"<strong>{text}</strong>"
            if styles.get("italic"):
                text = f"<em>{text}</em>"
            if styles.get("underline"):
                text = f"<u>{text}</u>"
            if styles.get("strikethrough"):
                text = f"<s>{text}</s>"
            if styles.get("code"):
                text = f"<code>{text}</code>"
            parts.append(text)

        elif item_type == "link":
            href = escape(item.get("href", ""))
            content = _render_inline_content(item.get("content", []))
            parts.append(f'<a href="{href}">{content}</a>')

    return "".join(parts)


def _render_block(block):
    """Render a single BlockNote block to HTML."""
    block_type = block.get("type", "paragraph")
    props = block.get("props", {})
    content = _render_inline_content(block.get("content", []))
    children = block.get("children", [])
    children_html = "".join(_render_block(child) for child in children)

    if block_type == "paragraph":
        return f"<p>{content}</p>{children_html}"

    elif block_type == "heading":
        level = props.get("level", 1)
        level = min(max(int(level), 1), 6)
        return f"<h{level}>{content}</h{level}>{children_html}"

    elif block_type == "bulletListItem":
        return f"<li>{content}{children_html}</li>"

    elif block_type == "numberedListItem":
        return f"<li>{content}{children_html}</li>"

    elif block_type == "checkListItem":
        checked = "checked" if props.get("checked") else ""
        return (
            f'<li><input type="checkbox" disabled {checked}/>'
            f" {content}{children_html}</li>"
        )

    elif block_type == "codeBlock":
        return f"<pre><code>{content}</code></pre>{children_html}"

    elif block_type == "image":
        url = escape(props.get("url", ""))
        alt = escape(props.get("caption", ""))
        return f'<img src="{url}" alt="{alt}" />{children_html}'

    elif block_type == "table":
        rows = block.get("content", {})
        if isinstance(rows, dict):
            rows = rows.get("rows", [])
        table_html = "<table>"
        for row in rows:
            table_html += "<tr>"
            cells = row.get("cells", [])
            for cell in cells:
                cell_content = _render_inline_content(cell)
                table_html += f"<td>{cell_content}</td>"
            table_html += "</tr>"
        table_html += "</table>"
        return table_html + children_html

    return f"<p>{content}</p>{children_html}"


def _wrap_list_items(html_blocks):
    """Wrap consecutive <li> items in <ul> or <ol> tags."""
    result = []
    i = 0
    while i < len(html_blocks):
        block = html_blocks[i]
        block_type = block["type"]
        html = block["html"]

        if block_type == "bulletListItem":
            ul_items = [html]
            i += 1
            while i < len(html_blocks) and html_blocks[i]["type"] == "bulletListItem":
                ul_items.append(html_blocks[i]["html"])
                i += 1
            result.append(f"<ul>{''.join(ul_items)}</ul>")
        elif block_type == "numberedListItem":
            ol_items = [html]
            i += 1
            while (
                i < len(html_blocks)
                and html_blocks[i]["type"] == "numberedListItem"
            ):
                ol_items.append(html_blocks[i]["html"])
                i += 1
            result.append(f"<ol>{''.join(ol_items)}</ol>")
        elif block_type == "checkListItem":
            ul_items = [html]
            i += 1
            while i < len(html_blocks) and html_blocks[i]["type"] == "checkListItem":
                ul_items.append(html_blocks[i]["html"])
                i += 1
            result.append(f"<ul>{''.join(ul_items)}</ul>")
        else:
            result.append(html)
            i += 1

    return "".join(result)


def blocknote_json_to_html(json_data):
    """Convert BlockNote JSON data to HTML string.

    Args:
        json_data: BlockNote document as a list of blocks (or a dict/string).

    Returns:
        HTML string representation of the document.
    """
    if not json_data:
        return ""

    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    if isinstance(json_data, dict):
        json_data = json_data.get("blocks", json_data.get("content", [json_data]))

    if not isinstance(json_data, list):
        return ""

    html_blocks = []
    for block in json_data:
        block_type = block.get("type", "paragraph")
        html = _render_block(block)
        html_blocks.append({"type": block_type, "html": html})

    return _wrap_list_items(html_blocks)

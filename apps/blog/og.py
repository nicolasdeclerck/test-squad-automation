"""Open Graph meta tags helpers for article sharing (LinkedIn, Twitter…)."""

import json
from html import escape
from urllib.parse import urljoin

EXCERPT_MAX_CHARS = 200


def extract_excerpt(content, max_chars=EXCERPT_MAX_CHARS):
    """Return a plain-text excerpt from a post content (BlockNote JSON or text)."""
    if not content:
        return ""

    try:
        blocks = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        text = str(content).strip()
    else:
        texts = []

        def walk(items):
            if not isinstance(items, list):
                return
            for item in items:
                if not isinstance(item, dict):
                    continue
                for c in item.get("content", []) or []:
                    if isinstance(c, dict) and c.get("type") == "text":
                        texts.append(c.get("text", ""))
                walk(item.get("children", []) or [])

        walk(blocks)
        text = " ".join(t for t in texts if t).strip()

    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rsplit(" ", 1)[0]
    return f"{truncated}…"


def _absolute(url, base_url):
    if not url:
        return ""
    if url.startswith(("http://", "https://")):
        return url
    return urljoin(base_url.rstrip("/") + "/", url.lstrip("/"))


def build_meta_tags(post, canonical_url, default_image_url, base_url):
    """Render the Open Graph / Twitter meta tags block for a published post."""
    title = post.title or ""
    description = extract_excerpt(post.content)
    image_url = ""
    if post.cover_image:
        try:
            image_url = post.cover_image.url
        except ValueError:
            image_url = ""
    if not image_url:
        image_url = default_image_url
    image_url = _absolute(image_url, base_url)
    canonical_url = _absolute(canonical_url, base_url)

    tags = [
        f'<meta property="og:type" content="article">',
        f'<meta property="og:title" content="{escape(title, quote=True)}">',
        f'<meta property="og:description" content="{escape(description, quote=True)}">',
        f'<meta property="og:url" content="{escape(canonical_url, quote=True)}">',
        f'<meta property="og:image" content="{escape(image_url, quote=True)}">',
        f'<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{escape(title, quote=True)}">',
        f'<meta name="twitter:description" content="{escape(description, quote=True)}">',
        f'<meta name="twitter:image" content="{escape(image_url, quote=True)}">',
        f'<link rel="canonical" href="{escape(canonical_url, quote=True)}">',
    ]
    return "\n    ".join(tags)


def inject_into_head(html, injected):
    """Insert a block just before the closing </head> tag."""
    lower = html.lower()
    idx = lower.rfind("</head>")
    if idx == -1:
        return html
    return f"{html[:idx]}    {injected}\n  {html[idx:]}"


def replace_title(html, new_title):
    """Replace the first <title>…</title> tag content."""
    import re

    return re.sub(
        r"<title>.*?</title>",
        f"<title>{escape(new_title)}</title>",
        html,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )

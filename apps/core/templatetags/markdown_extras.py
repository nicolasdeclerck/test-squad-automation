import markdown
import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

ALLOWED_TAGS = {
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr",
    "ul", "ol", "li",
    "strong", "em", "code", "pre",
    "blockquote",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
    "div", "span",
}

ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title"},
    "div": {"class"},
    "span": {"class"},
    "td": {"class"},
    "th": {"class"},
    "pre": {"class"},
    "code": {"class"},
}


@register.filter(name="render_markdown")
def render_markdown(value):
    html = markdown.markdown(
        value,
        extensions=["codehilite", "fenced_code", "tables"],
    )
    clean_html = nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
    )
    return mark_safe(clean_html)

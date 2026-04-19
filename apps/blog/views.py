from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.views import View

from .models import Post
from .og import build_meta_tags, inject_into_head, replace_title


def _read_index_html():
    path = Path(settings.FRONTEND_INDEX_HTML)
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, FileNotFoundError):
        return ""


class ArticleOGView(View):
    """Serve the SPA index.html with Open Graph meta tags for a published post.

    Crawlers (LinkedIn, Twitter, …) fetch HTML without executing JS, so the
    meta tags must be present in the initial response. For drafts or unknown
    slugs, we fall back to the plain index.html (React Router handles routing).
    """

    def get(self, request, slug):
        html = _read_index_html()
        if not html:
            return HttpResponse(status=503)

        post = (
            Post.objects.filter(slug=slug, status=Post.STATUS_PUBLISHED)
            .only("title", "slug", "content", "cover_image")
            .first()
        )
        if post is None:
            return HttpResponse(html, content_type="text/html; charset=utf-8")

        base_url = settings.SITE_URL.rstrip("/")
        canonical_url = f"{base_url}/articles/{post.slug}/"
        meta = build_meta_tags(
            post=post,
            canonical_url=canonical_url,
            default_image_url=settings.DEFAULT_OG_IMAGE_URL,
            base_url=base_url,
        )
        html = replace_title(html, post.title)
        html = inject_into_head(html, meta)
        return HttpResponse(html, content_type="text/html; charset=utf-8")

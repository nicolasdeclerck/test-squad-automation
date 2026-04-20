from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.views import View

from .models import Post
from .og import build_meta_tags, inject_into_head, replace_title

SPA_RESERVED_SLUGS = frozenset({"creer", "mes-brouillons"})


@lru_cache(maxsize=1)
def _read_index_html(path_str):
    try:
        return Path(path_str).read_text(encoding="utf-8")
    except OSError:
        return ""


class ArticleOGView(View):
    """Serve the SPA index.html with Open Graph meta tags for a published post.

    Crawlers (LinkedIn, Twitter, …) fetch HTML without executing JS, so the
    meta tags must be present in the initial response. For drafts, reserved
    slugs or unknown slugs we fall back to the plain index.html and flag
    the response with a noindex header so crawlers don't index it.
    """

    PUBLISHED_CACHE_CONTROL = "public, max-age=300"
    FALLBACK_CACHE_CONTROL = "no-store"

    def get(self, request, slug):
        html = _read_index_html(settings.FRONTEND_INDEX_HTML)
        if not html:
            return HttpResponse(status=503)

        if slug in SPA_RESERVED_SLUGS:
            return self._fallback(html)

        post = (
            Post.objects.filter(slug=slug, status=Post.STATUS_PUBLISHED)
            .only("title", "slug", "content", "cover_image")
            .first()
        )
        if post is None:
            return self._fallback(html)

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
        response = HttpResponse(html, content_type="text/html; charset=utf-8")
        response["Cache-Control"] = self.PUBLISHED_CACHE_CONTROL
        return response

    def _fallback(self, html):
        response = HttpResponse(html, content_type="text/html; charset=utf-8")
        response["Cache-Control"] = self.FALLBACK_CACHE_CONTROL
        response["X-Robots-Tag"] = "noindex"
        return response

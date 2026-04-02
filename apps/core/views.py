import logging
import re

import requests
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


def text_color_for_bg(hex_color):
    """Retourne '#1f2937' (dark) ou '#ffffff' (white) selon la luminance du fond."""
    try:
        r = int(hex_color[:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "#1f2937" if luminance > 0.5 else "#ffffff"
    except (ValueError, IndexError):
        return "#1f2937"


class ComingSoonView(TemplateView):
    template_name = "core/coming_soon.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Coming Soon"
        context["meta_description"] = (
            "Notre blog arrive bientôt. Restez connectés !"
        )
        return context


class AboutView(TemplateView):
    template_name = "core/about.html"


class ContactView(TemplateView):
    template_name = "core/contact.html"


class DevTrackingView(LoginRequiredMixin, TemplateView):
    template_name = "core/dev_tracking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Suivi des devs"
        context["meta_description"] = (
            "Suivez l'avancement des développements en cours."
        )
        issues = cache.get("github_issues")
        api_error = False
        if issues is None:
            try:
                url = f"{settings.GITHUB_REPO_API_URL}/issues?state=open"
                headers = {"Accept": "application/vnd.github.v3+json"}
                token = getattr(settings, "GITHUB_API_TOKEN", "")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=10,
                )
                if response.status_code == 200:
                    issues = [
                        {
                            "title": issue["title"],
                            "labels": [
                                {
                                    "name": label["name"],
                                    "color": label["color"]
                                    if re.match(
                                        r"^[0-9a-fA-F]{6}$",
                                        label.get("color", ""),
                                    )
                                    else "cccccc",
                                    "text_color": text_color_for_bg(
                                        label.get("color", "")
                                    ),
                                }
                                for label in issue.get("labels", [])
                            ],
                        }
                        for issue in response.json()
                    ]
                    cache.set("github_issues", issues, timeout=300)
                else:
                    logger.warning(
                        "GitHub API returned status %s", response.status_code
                    )
                    api_error = True
            except requests.RequestException as exc:
                logger.warning("GitHub API request failed: %s", exc)
                api_error = True
            if issues is None:
                issues = []
        context["issues"] = issues
        context["api_error"] = api_error
        return context
